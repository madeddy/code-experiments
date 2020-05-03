#!/usr/bin/env python3

"""This app is a mass converter for the most common image formats to webp."""

# If subprocess is used converting is resticted to the possible input formats
# for the webp CLI tools (png, jpeg, tiff, gif, webp, raw Ycbcr)

# pylint: disable=c0301, w0511, c0123, w1510


import os
import sys
import argparse
import shutil
from pathlib import Path as pt
import multiprocessing as mp
import textwrap
try:
    from PIL import Image
    Image.warnings.simplefilter('ignore', Image.DecompressionBombWarning)

    import magic
    from tqdm import tqdm
except ImportError:
    raise f"The packages 'Pillow', 'python-magic' and 'tqdm' must be installed " \
           "to run this program."

__title__ = 'Convert to Webp'
__license__ = 'MIT'
__author__ = 'madeddy'
__status__ = 'Development'
__version__ = '0.26.0-alpha'


class C2wCommon:
    """Provides some shared methods and variables for the main class."""

    name = 'Convert to Webp'
    verbosity = 1
    file_count = {
        'stl_f_found': 0,
        'ani_f_found': 0,
        'fle_skip': 0,
        'stl_f_done': 0,
        'ani_f_done': 0}
    mp_stl_count = mp.Value('i', 0)
    mp_ani_count = mp.Value('i', 0)

    quali = {'quality': 80}
    quali_ani = quali
    ani_ext = ['webp', 'gif']

    def __str__(self):
        return f"{self.__class__.__name__}({self.name!r})"

    @classmethod
    def inf(cls, inf_level, msg, m_sort=None):
        """Outputs by the current verboseness level allowed infos."""
        if cls.verbosity >= inf_level:  # TODO: use self.tty ?
            ind1 = f"{cls.name}:\x1b[32m >> \x1b[0m"
            ind2 = " " * 12
            if m_sort == 'note':
                ind1 = f"{cls.name}:\x1b[93m NOTE \x1b[0m> "
                ind2 = " " * 16
            elif m_sort == 'warn':
                ind1 = f"{cls.name}:\x1b[31m WARNING \x1b[0m> "
                ind2 = " " * 20
            elif m_sort == 'raw':
                print(ind1, msg)
                return
            print(textwrap.fill(msg, width=90, initial_indent=ind1, subsequent_indent=ind2))

    @classmethod
    def make_dirstruct(cls, dst):
        """Constructs any needet output directorys if they not already exist."""
        if not dst.exists():
            cls.inf(2, f"Creating directory structure for: {dst}")
            dst.mkdir(parents=True, exist_ok=True)


class C2wPathWork(C2wCommon):
    """Support class which checks input and prepairs the image filelist."""

    def __init__(self):
        super().__init__()
        self.bup_pth = None
        self.inpath = None
        self.src_file = None
        self.recode_webp = None
        self.conv_ani = None

    def check_inpath(self):
        """Helper to check if given input path exist."""
        if not self.inpath.is_dir() or self.inpath.is_symlink():
            raise NotADirectoryError(f"Could the input path object >{self.inpath}<" \
                                    "not find! Assert given path.")
        self.inpath = self.inpath.resolve(strict=True)

    def check_bup(self):
        """Helper to check if the backup directory already exists."""
        self.bup_pth = self.inpath.joinpath('c2w_img_backup')
        if self.bup_pth.is_dir() and any(self.bup_pth.iterdir()):
            raise FileExistsError("Backup dir already exists and has content. Stoping.")

    def test_ani(self, f_type):
        """Tests if a gif is animated."""
        return f_type in self.ani_ext and Image.open(self.src_file).is_animated

    def skip_check(self, m_type, f_type):
        """Different tests wich can cause to skip the file."""
        bool(m_type != 'image' or f_type == 'webp' and self.recode_webp is False)

    def get_mimetype(self):
        """Returns the mime type of a file."""
        return magic.from_file(str(self.src_file), mime=True).split('/')

    def big_img_assert(self, err):
        """Ask's user if to proceed on huge files (DecompressionBombError)."""
        self.inf(0, f"{err}\n", m_sort='warn')
        que = f"Type `yes` to proceed or `no` to skip the file. \
        \x1b[93mThats a serious risk, so be sure!\x1b[0m"
        ans = str(input(que)).lower()
        while True:
            if "no" in ans.lower():
                self.inf(0, f"Skipping very big file {self.src_file}.")
                C2wMain.file_count['fle_skip'] += 1
                return False
            if "yes" in ans.lower():
                self.inf(0, f"Proceeding with file {self.src_file}.")
                return True

    def dirwalker(self):
        """Searches a directory for images, filters and provides them as a list."""

        img_list = list()
        for path, dirs, files in os.walk(self.inpath):
            if 'img_backup' in dirs:
                dirs.remove('img_backup')

            for fln in files:
                self.src_file = pt(path).joinpath(fln)

                m_type, f_type = self.get_mimetype()
                if self.skip_check(m_type, f_type):
                    C2wMain.file_count['fle_skip'] += 1
                    continue
                # assert format support early
                try:
                    Image.open(self.src_file)
                except Image.UnidentifiedImageError as err:
                    self.inf(1, f"{err}"
                             "Format is not supported by Pillow. Skipped.")
                    C2wMain.file_count['fle_skip'] += 1
                    continue
                except Image.DecompressionBombError as err:
                    if not self.big_img_assert(err):
                        continue

                if self.test_ani(f_type) is False:
                    C2wMain.file_count['stl_f_found'] += 1
                    img_list.append((self.src_file, "stl"))
                else:
                    if self.conv_ani is True:
                        # placing counter in worker funcs doesn't work
                        C2wMain.file_count['ani_f_found'] += 1
                        img_list.append((self.src_file, "ani"))
                    else:
                        C2wMain.file_count['fle_skip'] += 1
                        continue

        return img_list


class C2wMain(C2wPathWork):
    """Main class with all functionality for converting images to webp."""

    def __init__(self, inp, quali, ani_mix=False, verbose=None, **kwargs):
        if verbose:
            C2wCommon.verbosity = verbose
        super().__init__()
        self.inpath = pt(inp)
        self.set_quali(quali, ani_mix)
        self.recode_webp = kwargs.get('recode_webp')
        self.conv_ani = kwargs.get('conv_ani')
        self.handle_src = kwargs.get('handle_src')

    # TODO: Quali setting in init... overhaul it
    def set_quali(self, quali, ani_mix):
        """Sets the quali state."""
        if quali is True:
            self.quali = {'lossless': quali}
        elif type(quali) is int:
            if not 0 <= quali <= 100:
                raise ValueError("Invalid number input for quality argument.")
            self.quali = {'quality': quali}

        self.quali_ani = {'allow_mixed': True} if ani_mix else self.quali

    def begin_msg(self):
        """Outputs a info about the start state if verbosity is high."""
        if self.quali['quality'] == 80:
            self.inf(2, f"Encoding stays at standard: lossy, with quality 80.")
        elif 'lossless' in self.quali.keys():
            self.inf(2, "Encoding is set to lossless.")
        elif type(self.quali['quality']) is int:
            self.inf(1, f"Quality factor is set to: {self.quali['quality']!s}")

    @classmethod
    def trans_count(cls):
        """Transfers the multprocessing counters to the counter dict."""
        cls.file_count['stl_f_done'] = cls.mp_stl_count.value
        cls.file_count['ani_f_done'] = cls.mp_ani_count.value

    def orgs_bup(self, src_f):
        """Clones the dir structure in a bup dir and moves given files there."""
        dst_f = self.bup_pth.joinpath(src_f.relative_to(self.inpath))
        dst_f_par = dst_f.parent
        self.make_dirstruct(dst_f_par)
        shutil.move(str(src_f), dst_f)

    def orgs_switch(self, src_f):
        """Handles the orginal files if option is given."""
        if self.handle_src == 'backup':
            self.orgs_bup(src_f)
        elif self.handle_src == 'erase' and pt(src_f).suffix != 'webp':
            pt(src_f).unlink()

    def mp_worker(self, inp):
        """Convert method for still images with multiprocessing capapility."""
        mp_conv_f, img_state = inp
        dst_f = pt(mp_conv_f).with_suffix('.webp')

        try:
            if img_state == "stl":
                with Image.open(mp_conv_f) as ofi:
                    ofi.save(dst_f, 'webp', **self.quali, method=3)
                with C2wMain.mp_stl_count.get_lock():
                    C2wMain.mp_stl_count.value += 1

            elif img_state == "ani":
                # NOTE: needs duration arg or the conv. anim. files play too slow
                with Image.open(mp_conv_f) as ofi:
                    ofi.save(dst_f, 'webp', **self.quali_ani, duration=ofi.info['duration'], save_all=True, method=3)
                with C2wMain.mp_ani_count.get_lock():
                    C2wMain.mp_ani_count.value += 1

        except OSError:
            self.inf(1, f"Image {mp_conv_f} could not be converted.")

        if self.handle_src:
            self.orgs_switch(mp_conv_f)

    @staticmethod
    def set_cpu_num():
        """Sets the number of used CPUs."""
        num_cpu = mp.cpu_count()
        return round(num_cpu * 0.75) if num_cpu > 2 else 1

    def c2w_control(self):
        """This manages all processing steps."""
        self.begin_msg()
        self.check_inpath()
        self.check_bup()

        img_list = self.dirwalker()
        item_count = C2wMain.file_count['stl_f_found'] + C2wMain.file_count['ani_f_found']

        mp_count = self.set_cpu_num()
        with mp.Pool(mp_count) as pool:
            for _ in tqdm(pool.imap_unordered(self.mp_worker, img_list), total=item_count, unit='files'):
                pass
            pool.close()
            pool.join()

        self.trans_count()
        self.inf(1, f"\nCompleted.\n{C2wMain.file_count['stl_f_done']!s} still images where converted and {C2wMain.file_count['fle_skip']!s} files omitted.")


def parse_args():
    """
    Argument parser and test for input path to provide functionality for the
    command line interface. Also ensures that at least one of the required switches
    is present.
    """
    def valid_nr(inp):
        """Validates the users input of a number."""
        input_nr = int(inp)
        if not 0 <= input_nr <= 100:
            raise ValueError("Invalid number input for quality argument.")
        return input_nr

    aps = argparse.ArgumentParser(
        description='A program for converting tiff, png, jpeg, gif images to webp or encode webp anew.\nEXAMPLE USAGE: convert_to_webp.py -q 90',
        epilog='The switches are optional. Without one of them the default quality is lossy -q 80 and the orginal files will be retained.')
    aps.add_argument('inp',
                     metavar='Target directory',
                     action='store',
                     type=str,
                     help='Directory path with images for processing.')
    switch = aps.add_mutually_exclusive_group()
    switch.add_argument('-l',
                        action='store_true',
                        dest='qua',
                        help='Set quality to lossless.')
    switch.add_argument('-q',
                        type=valid_nr,
                        dest='qua',
                        help='Set quality to lossy. Value 0-100')
    aps.add_argument('-m',
                     action='store_true',
                     dest='ani_m',
                     help='Set mixed quality mode for animated images.')
    orginal = aps.add_mutually_exclusive_group()
    orginal.add_argument('-e',
                         action='store_const',
                         dest='orgs',
                         const='erase',
                         help='Erase orginal files.')
    orginal.add_argument('-b',
                         action='store_const',
                         dest='orgs',
                         const='backup',
                         help='Backup orginal files.')
    aps.add_argument('-webp',
                     action='store_true',
                     dest='r_webp',
                     help='Re-/Encode also webp images. e.g lossless to lossy')
    aps.add_argument('-ani',
                     action='store_true',
                     dest='c_ani',
                     help='Convert animated gif images to webp.')
    aps.add_argument('--verbose',
                     metavar='level [0-2]',
                     type=int,
                     choices=range(0, 3),
                     help='Amount of info output. 0:none, 2:much, default:1')
    aps.add_argument('--version',
                     action='version',
                     version=f'%(prog)s : { __title__} {__version__}')
    return aps.parse_args()


def main(cfg):
    """This checks if the required Python version runs, instantiates the class,
    delivers the parameters to its init and executes the program from CLI.
    """
    if not sys.version_info[:2] >= (3, 6):
        raise Exception("Must be executed in Python 3.6 or later.\n"
                        f"You are running {sys.version}")
    c2w = C2wMain(cfg.inp, cfg.qua, cfg.ani_m, cfg.verbose,
                  recode_webp=cfg.r_webp, conv_ani=cfg.c_ani, handle_src=cfg.orgs)
    c2w.c2w_control()


if __name__ == '__main__':
    main(parse_args())
