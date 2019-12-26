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
from multiprocessing import Pool
from pathlib import Path
import shutil
import magic
from PIL import Image


class Conv2webp(object):
    """The class for converting images to webp."""

    def __init__(self, conv_dir, recode_webp, quali, treat_orgs=None):
        self.conv_dir = conv_dir
        self.recode_webp = recode_webp
        self.quali = quali
        self.treat_orgs = treat_orgs

        self.src_f = ''
        self.file_count = [0, 0]

    def backup_originals(self, src_file):
        """Clones the dir structure in a bup dir and moves given files there."""

        bup_dir = Path(self.conv_dir).joinpath('img_backup')
        dest_file = Path(bup_dir).joinpath(Path(src_file).relative_to(self.conv_dir))
        dest_file_par = Path(dest_file).parent

        if not Path(dest_file_par).exists():
            Path(dest_file_par).mkdir(exist_ok=True)

        shutil.move(src_file, dest_file)

    def test_gifani(self):
        """Tests if a gif is animated."""

        return Image.open(self.src_f).is_animated

    def get_mimetype(self):
        """Returns the mime type of a file."""

        return magic.from_file(str(self.src_f), mime=True).split('/')

    def dirwalker(self):
        """Walks the given dir and returns a list of images to convert."""

        conv_img_list = []
        ext_list = ['png', 'jpeg', 'jpg', 'gif', 'tiff', 'tif']
        if self.recode_webp is True:
            ext_list.append('webp')

        for path, dirs, files in os.walk(self.conv_dir):
            if 'img_backup' in dirs:
                dirs.remove('img_backup')

            for fln in files:

                # in_f = os.path.join(path, fln)
                self.src_f = Path(path).joinpath(fln)
                m_type, f_type = self.get_mimetype()

                if m_type != 'image' or f_type not in ext_list:
                    self.file_count[1] += 1
                    continue

                if f_type == 'gif' and self.test_gifani() is True:
                    # Skip animated gifs; convert is broken
                    # file_count[0] += 1
                    # img_list[1].append(in_f)
                    self.file_count[1] += 1
                    continue

                else:
                    conv_img_list.append(self.src_f)

        return conv_img_list

    def convert_img(self, in_f):
        """Multiprocess function for the fileconvert."""

        out_f = Path(in_f).with_suffix('.webp')
        try:
            Image.open(in_f).save(out_f, 'webp', lossless=self.quali[0], quality=self.quali[1], method=3)
        except IOError:
            print(f'"Could not convert:" {in_f}')

    def work_manager(self):
        """Converts/recodes images to webp and handles orginal files."""

        conv_img_list = self.dirwalker()
        Pool(3).map(self.convert_img, conv_img_list)

        for conv_src_f in conv_img_list:

            self.file_count[0] += 1

            # Skip animated gifs; convert is broken
            # (produces stills or unreadables jun'2019)
            #
            # try:
            #     Image.open(in_f).save(out_f, 'webp', save_all=True, lossless=loss, quality=quali, method=3)
            #     file_count[0] += 1
            # except IOError:
            #     print(f'"cannot convert" {in_f}')

            if self.treat_orgs == 'backup':
                self.backup_originals(conv_src_f)

            if self.treat_orgs == 'erase' and \
                    Path(conv_src_f).suffix != 'webp':
                Path(conv_src_f).unlink()

        print(f'\nCompleted. {self.file_count[0]!s} images where converted and {self.file_count[1]!s} files omitted.')


def parse_args():
    """Gets the arguments."""

    def check_dir_path(dir_path):
        """Helper for check if given path is a dir."""
        if not Path(dir_path).is_dir:
            raise NotADirectoryError(dir_path)
        return dir_path

    def valid_nr(inp):
        """Function for validating the users input of a number."""
        input_nr = int(inp)
        if not 0 <= input_nr <= 100:
            raise ValueError('Invalid input. Use a number between 0 and 100.')
        return input_nr

    parser = argparse.ArgumentParser(description='A program for converting tiff, png, jpeg, gif images to webp or encode webp anew.\nEXAMPLE USAGE: convert_to_webp.py -q 90', epilog='The switches are optional. Without one of them the default quality is lossy -q 75 and the orginal files will be keeped.')
    parser.add_argument('-dir', type=check_dir_path,
                        help='Directory path with images for processing.')
    switch = parser.add_mutually_exclusive_group()
    switch.add_argument('-l', action='store_true', dest='loss', default=False,
                        help='Set quality to lossless.')
    switch.add_argument('-q', type=valid_nr, dest='qua', default=80,
                        help='Set quality to lossy. Value 0-100')
    org = parser.add_mutually_exclusive_group()
    org.add_argument('-e', action='store_const', dest='treat_orgs',
                     const='erase', help='Erase orginal files.')
    org.add_argument('-b', action='store_const', dest='treat_orgs',
                     const='backup', help='Backup orginal files.')
    # parser.set_defaults(treat_orgs='keep')
    parser.add_argument('-w', action='store_true', dest='r_webp',
                        default=False,
                        help='Re-/Encode also webp images.')
    parser.add_argument('--version', action='version',
                        version='%(prog)s 0.7.0-alpha')
    return parser.parse_args()


def main(cfg):
    """Main function with some checks for the convert process."""

    if not cfg.loss and cfg.qua == 80:
        print(f'Encoding stays at standard: lossy, with quality 80.')
    elif cfg.loss:
        print('Encoding is set to lossless.')
    elif cfg.qua != 80:
        print(f'Quality factor set to: {cfg.qua!s}')

    import timeit
    from datetime import timedelta
    start_t = timeit.default_timer()

    Conv2webp(cfg.dir, cfg.r_webp, (cfg.loss, cfg.qua), cfg.treat_orgs).work_manager()

    print(str(timedelta(seconds=timeit.default_timer() - start_t)))

    # c2w = Conv2webp(cfg.dir, cfg.r_webp, (cfg.loss, cfg.qua), cfg.treat_orgs)
    # c2w.convert_img()


if __name__ == '__main__':
    assert sys.version_info >= (3, 6), \
        f"Must be run in Python 3.6 or later. You are running {sys.version}"
    main(parse_args())
