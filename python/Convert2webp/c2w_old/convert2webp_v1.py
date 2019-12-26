#!/usr/bin/env python3

"""This app is a mass converter for the most common image formats to webp."""
# Converting is resticted to the possible input formats png, jpeg, tiff,
# gif for webp.

# pylint: disable=c0301, w0612
# too many variables R0914 # to many branchces R0914

import os
import sys
import argparse
from pathlib import Path
import shutil
import magic
from PIL import Image


def backup_originals(src_file, conv_dir):
    """Clones the dir structure in a bup dir and moves given files there."""

    # bup_dir = Path(Path(conv_dir).parent).joinpath('img_bup')
    bup_dir = Path(conv_dir).joinpath('img_bup')

    dest_file = Path(bup_dir).joinpath(Path(src_file).relative_to(conv_dir))
    dest_file_par = Path(dest_file).parent

    if not Path(dest_file_par).exists():
        Path(dest_file_par).mkdir(exist_ok=True)

    shutil.move(src_file, dest_file)


def test_gifani(filename):
    """Tests if a gif is animated."""

    return Image.open(filename).is_animated


def get_mimetype(filename):
    """Returns the mime type of a file."""

    return magic.from_file(str(filename), mime=True).split('/')


def dirwalker(conv_dir, recode_webp):
    """Walks the given dir and returns a list of images to convert."""

    file_count = [0, 0]
    img_list = []
    ext_list = ['png', 'jpeg', 'jpg', 'gif', 'tiff', 'tif']
    if recode_webp is True:
        ext_list.append('webp')

    for path, dirs, files in os.walk(conv_dir):
        if 'img_backup' in dirs:
            dirs.remove('img_backup')

        for fln in files:

            # in_f = os.path.join(path, fln)
            in_f = Path(path).joinpath(fln)
            m_type, f_type = get_mimetype(in_f)

            if m_type != 'image' or f_type not in ext_list:
                file_count[1] += 1
                continue

            if f_type == 'gif' and test_gifani(in_f) is True:
                # Skip animated gifs; convert is broken
                # file_count[0] += 1
                # img_list[1].append(in_f)
                file_count[1] += 1
                continue

            else:
                img_list.append(in_f)

    return img_list, file_count


def convert_img(conv_dir, recode_webp, quali, treat_orgs=None):
    """Converts/recodes images to webp and handles orginal files."""

    imgconv_list, file_count = dirwalker(conv_dir, recode_webp)

    # if treat_orgs == 'backup':
    #     out_dir = Path(conv_dir).joinpath('img_backup')
    #
    #     if not Path.exists(out_dir):
    #         Path.mkdir(out_dir)
    #     else:
    #         raise OSError('Backup dir already exist.')

    for in_f in imgconv_list:

        out_f = Path(in_f).with_suffix('.webp')

        try:
            Image.open(in_f).save(out_f, 'webp', lossless=quali[0], quality=quali[1], method=3)
            file_count[0] += 1
        except IOError:
            print(f'"Could not convert:" {in_f}')

        # Skip animated gifs; convert is broken
        # (produces stills or unreadables jun'2019)

        # try:
        #     Image.open(in_f).save(out_f, 'webp', save_all=True, lossless=loss, quality=quali, method=3)
        #     file_count[0] += 1
        # except IOError:
        #     print(f'"cannot convert" {in_f}')

        if treat_orgs == 'backup':
            backup_originals(in_f, conv_dir)

            # shutil.move(in_f, PurePath(out_dir).joinpath(Path(in_f).relative_to(conv_dir)))
            # shutil.move(in_f, os.path.join(out_dir, os.path.relpath(in_f, conv_dir)))

        if treat_orgs == 'erase' and in_f != out_f:
            Path(in_f).unlink()

    print(f'\nCompleted. {file_count[0]!s} images where converted and {file_count[1]!s} files omitted.')


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
    convert_img(cfg.dir, cfg.r_webp, (cfg.loss, cfg.qua), cfg.treat_orgs)


if __name__ == '__main__':
    assert sys.version_info >= (3, 6), \
        f"Must be run in Python 3.6 or later. You are running {sys.version}"
    main(parse_args())
