#!/usr/bin/env python3

"""This app is a mass converter for the most common image formats to webp."""
# Converting is resticted to the possible input formats png, jpeg, tiff,
# gif for webp.

# pylint: disable=c0301
# , w0612
# too many variables R0914 # to many branchces R0914

import os
import sys
import argparse
import shutil
from pathlib import Path
from multiprocessing import Pool
from PIL import Image
import magic
import tqdm


class C2W:
    """The class for converting images to webp."""

    src_f = ''
    file_count = [0, 0]
    ext_list = ['png', 'jpeg', 'jpg', 'gif', 'tiff', 'tif']

    def __init__(self, conv_dir, recode_webp, quali, treat_orgs=None):
        self.conv_dir = conv_dir
        self.quali = quali
        self.treat_orgs = treat_orgs

        self.bup_dir = Path(self.conv_dir).joinpath('img_backup')
        C2W.set_ext_list(recode_webp)

    @classmethod
    def set_ext_list(cls, recode_webp):
        """Sets the the file extension lists state."""
        if recode_webp:
            cls.ext_list.append('webp')

    def backup_originals(self, src_file):
        """Clones the dir structure in a bup dir and moves given files there."""

        dest_file = Path(self.bup_dir).joinpath(
            Path(src_file).relative_to(self.conv_dir))
        dest_file_par = Path(dest_file).parent

        if not Path(dest_file_par).exists():
            Path(dest_file_par).mkdir(parents=True, exist_ok=True)

        shutil.move(src_file, dest_file)

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

                C2W.src_f = Path(path).joinpath(fln)
                m_type, f_type = self.get_mimetype()

                if m_type != 'image' or f_type not in C2W.ext_list:
                    C2W.file_count[1] += 1
                    continue

                if f_type == 'gif' and self.test_gifani() is True:
                    # Skip animated gifs; convert is broken
                    # dst_f = Path(mp_conv_f).with_suffix('.webp')
                    # try:
                    #     Image.open(C2W.src_f).save(dst_f, 'webp', save_all=True, lossless=self.quali[0], quality=self.quali[1], method=3)
                    # except IOError:
                    #     print(f'"Could not convert: {C2W.src_f}')
                    # C2W.file_count[0] += 1
                    C2W.file_count[1] += 1
                    continue

                else:
                    C2W.file_count[0] += 1
                    conv_img_list.append(C2W.src_f)

        return conv_img_list

    def mp_worker(self, mp_conv_f):
        """Convert method with multiprocessing capapility."""

        mp_dst_f = Path(mp_conv_f).with_suffix('.webp')

        try:
            Image.open(mp_conv_f).save(mp_dst_f, 'webp', lossless=self.quali[0], quality=self.quali[1], method=3)
        except IOError:
            print(f'"Could not convert: "{mp_conv_f}')

        if self.treat_orgs == 'backup':
            self.backup_originals(mp_conv_f)

        if self.treat_orgs == 'erase' and \
                Path(mp_conv_f).suffix != 'webp':
            Path(mp_conv_f).unlink()

    def conv2webp(self):
        """This manages all processing steps."""

        if Path(self.bup_dir).exists():
            raise FileExistsError('Backup dir already exist.')

        conv_img_list = self.dirwalker()
        count_t = len(conv_img_list)
        print(f'{count_t} images to process.\n')

        pool = Pool(4)
        for _ in tqdm.tqdm(pool.imap_unordered(self.mp_worker, conv_img_list), total=count_t):
            pass
        pool.close()
        pool.join()

        print(f'\nCompleted.\n{C2W.file_count[0]!s} images where converted and {C2W.file_count[1]!s} files omitted.')


def parse_args():
    """Gets the arguments."""

    def check_dir_path(dir_path):
        """Check if given path exist and is a dir."""
        if not Path(dir_path).exists():
            raise FileNotFoundError(dir_path)
        if not Path(dir_path).is_dir():
            raise NotADirectoryError(dir_path)
        return dir_path

    def valid_nr(inp):
        """Validates the users input of a number."""
        input_nr = int(inp)
        if not 0 <= input_nr <= 100:
            raise ValueError('Invalid number input for quality argument.')
        return input_nr

    parser = argparse.ArgumentParser(
        description='A program for converting tiff, png, jpeg, gif images to webp or encode webp anew.\nEXAMPLE USAGE: convert_to_webp.py -q 90',
        epilog='The switches are optional. Without one of them the default quality is lossy -q 80 and the orginal files will be keeped.')
    parser.add_argument('-dir', type=check_dir_path,
                        help='Directory path with images for processing.')

    switch = parser.add_mutually_exclusive_group()
    switch.add_argument('-l', action='store_true', dest='loss',
                        default=False, help='Set quality to lossless.')
    switch.add_argument('-q', type=valid_nr, dest='qua', default=80,
                        help='Set quality to lossy. Value 0-100')

    org = parser.add_mutually_exclusive_group()
    org.add_argument('-e', action='store_const', dest='treat_orgs',
                     const='erase', help='Erase orginal files.')
    org.add_argument('-b', action='store_const', dest='treat_orgs',
                     const='backup', help='Backup orginal files.')

    parser.add_argument('-w', action='store_true', dest='r_webp',
                        default=False,
                        help='Re-/Encode also webp images. e.g lossless to lossy')
    parser.add_argument('--version', action='version',
                        version='%(prog)s 0.7.0-alpha')
    return parser.parse_args()


def main(cfg):
    """Main block with some info messages."""

    if not cfg.loss and cfg.qua == 80:
        inf_line = f'Encoding stays at standard: lossy, with quality 80.'
    elif cfg.loss:
        inf_line = 'Encoding is set to lossless.'
    elif cfg.qua != 80:
        inf_line = f'Quality factor set to: {cfg.qua!s}'
    print(f'Animated gif\'s will be skipped. Convert is broken!\n{inf_line} >> Processing starts.')

    # import timeit
    # start_t = timeit.default_timer()

    C2W(cfg.dir, cfg.r_webp, (cfg.loss, cfg.qua), cfg.treat_orgs).conv2webp()

    # print(str(timeit.default_timer() - start_t))

    # c2w = C2W(cfg.dir, cfg.r_webp, (cfg.loss, cfg.qua), cfg.treat_orgs)
    # c2w.conv2webp()


if __name__ == '__main__':
    assert sys.version_info >= (3, 6), \
        f"Must be run in Python 3.6 or later. You are running {sys.version}"
    main(parse_args())
