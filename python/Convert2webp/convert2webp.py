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
try:
    from PIL import Image
    import magic
    import tqdm
except ImportError:
    raise f"The packages 'Pillow', 'python-magic' and 'tqdm' must be installed " \
           "to run this program."

__title__ = 'Convert to Webp'
__license__ = 'MIT'
__author__ = 'madeddy'
__status__ = 'Development'
__version__ = '0.10.0-alpha'


class C2W:
    """The class for converting images to webp."""

    name = 'Convert to Webp'
    src_f = None
    file_count = {'fle_done': 0, 'fle_skip': 0, 'fle_total': 0}
    ext_list = {'png', 'jpeg', 'jpg', 'gif', 'tiff', 'tif'}

    def __init__(self, conv_dir, quali, ani_m=False, recode_webp=False, treat_orgs=None):
        self.conv_dir = conv_dir
        self.set_quali(quali, ani_m)
        self.set_ext_list(recode_webp)
        self.treat_orgs = treat_orgs
        # TODO: Move bup_dir related code to own function
        self.bup_dir = pt(self.conv_dir).joinpath('img_backup')

    @classmethod
    def set_ext_list(cls, recode_webp):
        """Sets the state of the file extension list."""
        if recode_webp:
            cls.ext_list.add('webp')

    def set_quali(self, quali, ani_m):
        """Sets the quali state."""
        self.quali = {'quality': 80}
        if quali is True:
            self.quali = {'lossless': quali}
        elif type(quali) is int:
            self.quali = {'quality': quali}

        self.quali_ani = self.quali
        if ani_m is True:
            self.quali_ani = {'allow_mixed': ani_m}

    def backup_originals(self, src_f):
        """Clones the dir structure in a bup dir and moves given files there."""
        dst_f = pt(self.bup_dir).joinpath(pt(src_f).relative_to(self.conv_dir))
        dst_f_par = pt(dst_f).parent

        if not pt(dst_f_par).exists():
            pt(dst_f_par).mkdir(parents=True, exist_ok=True)
        shutil.move(src_f, dst_f)

    def work_originals(self, src_f):
        """Handles the orginal files if option is given."""
        if self.treat_orgs == 'backup':
            self.backup_originals(src_f)

        if self.treat_orgs == 'erase' and pt(src_f).suffix != 'webp':
            pt(src_f).unlink()

        """Convert method with multiprocessing capapility."""
        mp_dst_f = pt(mp_conv_f).with_suffix('.webp')

        try:
            Image.open(mp_conv_f).save(
                mp_dst_f, 'webp', **self.quali, **self.quali_ani, method=3)
        except OSError:
            print(f"Could not convert: {mp_conv_f}")

        if self.treat_orgs:
            self.work_originals(conv_f)

        if self.treat_orgs:
            self.work_originals(mp_conv_f)

    @staticmethod
    def set_cpu_num():
        """Sets the number of used CPUs."""
        num_cpu = mp.cpu_count()
        if num_cpu > 2:
            return round(num_cpu * 0.75)
        return 1

    @classmethod
    def test_gifani(cls):
        """Tests if a gif is animated."""
        return Image.open(cls.src_f).is_animated

    @classmethod
    def get_mimetype(cls):
        """Returns the mime type of a file."""
        return magic.from_file(str(cls.src_f), mime=True).split('/')

    def dirwalker(self):
        """Searches a dir for images, filters and provides them as a list."""
        conv_img_list = []

        for path, dirs, files in os.walk(self.conv_dir):
            if 'img_backup' in dirs:
                dirs.remove('img_backup')

            for fln in files:
                C2W.src_f = pt(path).joinpath(fln)
                m_type, f_type = self.get_mimetype()

                if m_type != 'image' or f_type not in C2W.ext_list:
                    C2W.file_count['fle_skip'] += 1
                    continue

                if f_type == 'gif' and self.test_gifani() is True:
                    # FIXME: converted anim. gifs are for some reason too slow playing
                    # possible pillows fault
                    dst_f = pt(C2W.src_f).with_suffix('.webp')
                    try:
                        Image.open(C2W.src_f).save(dst_f, 'webp', **self.quali, save_all=True, method=3)
                    except OSError:
                        print(f'"Could not convert: {C2W.src_f}')
                    C2W.file_count['fle_done'] += 1

                else:
                    C2W.file_count['fle_done'] += 1
                    conv_img_list.append(C2W.src_f)
        return conv_img_list

    def conv2webp(self):
        """This manages all processing steps."""
        if pt(self.bup_dir).exists():
            raise FileExistsError("Backup dir already exist.")

        conv_img_list = self.dirwalker()
        item_count = len(conv_img_list)
        print(f"{item_count} inanimated images to process.\n")

        mp_count = self.set_cpu_num()
        pool = mp.Pool(mp_count)
        for _ in tqdm.tqdm(pool.imap_unordered(self.mp_worker, conv_img_list), total=item_count):
            pass
        pool.close()
        pool.join()

        print(f"\nCompleted.\n{C2W.file_count['fle_done']!s} images where converted and {C2W.file_count['fle_skip']!s} files omitted.")


def parse_args():
    """
    Argument parser and test for input path to provide functionality for the
    command line interface. Also ensures that at least one of the required switches
    is present.
    """
    def check_dir_path(dir_path):
        """Check if given path exist and is a dir."""
        if not pt(dir_path).is_dir() or pt(dir_path).is_symlink():
            raise NotADirectoryError(dir_path)
        return dir_path

    def valid_nr(inp):
        """Validates the users input of a number."""
        input_nr = int(inp)
        if not 0 <= input_nr <= 100:
            raise ValueError("Invalid number input for quality argument.")
        return input_nr

    aps = argparse.ArgumentParser(
        description='A program for converting tiff, png, jpeg, gif images to webp or encode webp anew.\nEXAMPLE USAGE: convert_to_webp.py -q 90',
        epilog='The switches are optional. Without one of them the default quality is lossy -q 80 and the orginal files will be keeped.')
    aps.add_argument('-dir',
                     type=check_dir_path,
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
    org = aps.add_mutually_exclusive_group()
    org.add_argument('-e',
                     action='store_const',
                     dest='treat_orgs',
                     const='erase',
                     help='Erase orginal files.')
    org.add_argument('-b',
                     action='store_const',
                     dest='treat_orgs',
                     const='backup',
                     help='Backup orginal files.')
    aps.add_argument('-w',
                     action='store_true',
                     dest='r_webp',
                     help='Re-/Encode also webp images. e.g lossless to lossy')
    aps.add_argument('--version',
                     action='version',
                     version=f'%(prog)s : { __title__} {__version__}')
    return aps.parse_args()


def main(cfg):
    """This executes all program steps, validity checks on the args and prints
    infos messages if the default args are used.
    """
    # TODO: look into adding raw Y'CbCr samples encoding
    if not cfg.qua:
        inf_line = f'Encoding stays at standard: lossy, with quality 80.'
    elif cfg.qua is True:
        inf_line = 'Encoding is set to lossless.'
    elif type(cfg.qua) is int:
        inf_line = f'Quality factor set to: {cfg.qua!s}'

    C2W(cfg.dir, cfg.qua, cfg.ani_m, cfg.r_webp, cfg.treat_orgs).conv2webp()
    print(f"{inf_line} >> Processing starts.")


if __name__ == '__main__':
    assert sys.version_info >= (3, 6), \
        f"Must be run in Python 3.6 or later. You are running {sys.version}"
    main(parse_args())
