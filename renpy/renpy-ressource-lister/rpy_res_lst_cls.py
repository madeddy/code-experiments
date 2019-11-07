#!/usr/bin/env python3

"""
A program for listing defined ren'py ressourses.

It is intended to be executed in the renpy's game directory below the asset
dirs (images, audio).
The subdirectories will be searched and the content written to a file.
"""

# pylint: disable=w0511, C0103, C0301

import os
import sys
from pathlib import Path
import argparse
from time import localtime, strftime, sleep
import textwrap
import magic
from natsort import humansorted

__title__ = 'RenPy Ressource Lister'
__license__ = 'MIT'
__author__ = 'madeddy'
__status__ = 'Development'
__version__ = '0.13.0-alpha'

# INFOS:
# python version 3.6 or higher required
# python packages needet: natsort, python-magic
#
# Works with my Linux distro. Untested in other OS; however it should with few
# changes.
# For working format recognition in win/mac look at the installation notes at
# https://github.com/ahupp/python-magic
#
# This builds on the work and knowledge of thousands of people all over the
# world. Thanks!
#
# Try to organize your directories cleanly to make it as usable as possible
# for the script!

# # # # # # # # # # # # # # # # # # # #


class RRL:
    """The class for all ressource defining related functionality."""

    tmp_lst = []

    def __init__(self, chkdir, typus, outfile, verbosity=1):
        self.chkdir = chkdir
        try:
            assert typus in ['image', 'audio', 'video']
        except AssertionError as error:
            print('Wrong type given.', error)
        self.typus = typus.lower()
        self.outfile = outfile
        self.verbosity = verbosity

        self.valid_path()
        self.valid_outfile()
        self.check_defaults()
        # needs before open or hits old file (if exist)
        self.init_register_file()
        self.open_of = open(outfile, 'w')

    def inf(self, verbose_level, message, warn=False):
        """Outputs the infos allowed for the current verbosity level."""

        if self.verbosity >= verbose_level:
            mes_sort = 'INFO'
            if warn:
                mes_sort = 'WARNING'
            print(f'RRL {mes_sort}: {message}')

    def valid_path(self):
        """This tests if the given directory exists."""

        if not Path(self.chkdir).is_dir():
            raise OSError(f'Directory \"{self.chkdir}\" does not exist.')

    def valid_outfile(self):
        """This tests if the given output filename is acceptable."""

        if not self.outfile.endswith('.rpy'):
            raise ValueError('Output filename must have rpy extension.')

        for char in [':', ' ']:
            if char in self.outfile:
                raise OSError(f'\"{self.outfile}\" contains unallowed charakter.')

    def check_defaults(self):
        """Checks if default values are used and informs if verbosity=2."""

        if self.outfile == 'ressource_def.rpy':
            self.inf(2, f'>> Output filename set to default: <{self.outfile}>.')
        # FIXME: Used like this the dirs can be mixed up with the type
        if self.chkdir == 'images' or self.chkdir == 'audio' or self.chkdir == 'video':
            self.inf(2, f'{self.typus.title()} directory set to default: <{self.chkdir}>.')

    def init_register_file(self):
        """
        Tests if a file with the given output filename already exists and
        if true makes a backup.
        """

        if Path(self.outfile).is_file():
            timestamp = strftime('%d%b%Y_%H:%M:%S', localtime())
            Path(self.outfile).rename(Path(self.outfile).with_suffix('.' + timestamp + '.bup'))

            self.inf(1, f'>> Target file {self.outfile} already exists. Performed backup. Original file has now extension <bup>.')
            sleep(1)

    def write_register_list(self):
        """
        Writes a intro message and the content of the register list to
        the file.
        """

        header_text = ("""\
        # REN'PY ASSET LIST
        # Below are the project assets with the renpy <asset_type>
        # declaration. e.g.:
        # image sally tired = "images/char/sally/tired.webp"
        # Ready for use with alias like known or changeable like wanted.""")

        print(textwrap.dedent(header_text), file=self.open_of)
        print(*self.tmp_lst, sep='\n', file=self.open_of)

        self.inf(2, f'>> List was written to file {self.outfile} in directory\n{os.getcwd()}')

        # with open(self.outfile, 'w') as ofi:
        #     print(textwrap.dedent(header_text), file=ofi)
        #     print (*self.tmp_lst, sep='\n', file=ofi)

        print(*self.tmp_lst, sep='\n')

    def format_test(self, testobj):
        """
        This determines if the input file is a known format of the given media
        type. Negatives are skipped, positives again checked if their extension
        is supported or not. Returns this status.
        """

        supp_state = None
        if Path(testobj).is_file():
            m_type, f_type = magic.from_file(
                str(testobj), mime=True).split('/')

            # print('get mime_type', m_type)

            if self.typus not in m_type:
                return supp_state

            if '-' in f_type:
                f_type = f_type.split('-')[1]

            # print('guess extension', f_type)

            supp_ext = ['webp', 'png', 'jpeg', 'jpg', 'opus', 'ogg', 'mp3', 'wav', 'webm', 'mkv', 'ogv', 'avi', 'mpeg', 'mpeg2', 'mpeg4', 'mp4']
            if f_type in supp_ext:
                supp_state = 'supported'
            else:
                supp_state = 'unsupported'

        return supp_state

    def typus_statement(self, cur_dir, rel_path, fn_base):
        """
        This supports the dir lister by constructing the define statements for
        the actual asset typus.
        """

        dcl_base = 'image '
        alias_sep = '_'
        if self.typus == 'audio':
            dcl_base = 'define audio.'

        if cur_dir not in self.chkdir:
            dcl_left = dcl_base + cur_dir + alias_sep + fn_base
        else:
            dcl_left = dcl_base + fn_base

        dcl_right = rel_path
        if self.typus == 'video':
            dcl_right = f'Movie(play="{rel_path}")'

        return f'{dcl_left} = "{dcl_right}"'

    def dir_lister(self):
        """This finds, filters and lists all elements in the given path."""

        self.tmp_lst.append(f'\n\n# {self.typus.title()} section {"#" * 64}\n')

        unsupp_count = 0
        for path, dirs, files in os.walk(self.chkdir):
            dirs = humansorted(dirs)
            subdirs = f' with subdirectorys: {", ".join(dirs)}'
            self.tmp_lst.append(f'# ### Current directory: {path}/{subdirs if dirs else ""}')

            files = humansorted(files)
            cur_dir = Path(path).name
            for fn in files:
                fullpath = Path(path).joinpath(fn)
                format_status = self.format_test(fullpath)

                if format_status == 'supported':
                    fn_base = Path(fn).stem.lower()
                    rel_path = Path(fullpath).relative_to(self.chkdir)
                    self.tmp_lst.append(
                        self.typus_statement(cur_dir, rel_path, fn_base))

                elif format_status == 'unsupported':
                    unsupp_count += 1
                else:
                    continue

        if unsupp_count > 0:
            self.inf(1, f'The directory contains {unsupp_count!s} {self.typus} file(s) of non-supported type.')

        self.write_register_list()


def parse_args():
    """
    Standard argument parser. Checks if at least one of the required
    switches is present.
    """

    def check_dir_path(dir_path):
        """Helper for check if given path is a dir."""
        if not Path(dir_path).exists():
            raise FileNotFoundError(dir_path)
        if not Path(dir_path).is_dir():
            raise NotADirectoryError(dir_path)
        return dir_path

    def valid_switch():
        """Help function to determine if a switch is set."""
        if not args.def_img and not args.def_aud and not args.def_vid:
            parser.print_help()
            raise parser.error('\nNo task requested; either -i, -a or -v is required.')

    parser = argparse.ArgumentParser(
        add_help=False, description='A program for listing ren`py ressources.\nEXAMPLE USAGE: res_def.py -i -idir all_img -o mylist.rpy',
        epilog='One of the switches must be set or the program exits. The other options have default values which are used if they are not set.')

    switch = parser.add_argument_group('Switches', 'Activate search and listing of the respective filetype.\nOne is at least required!')
    switch.add_argument('-i', nargs='?', dest='def_img',
                        const='images', default=None,
                        help='Activate image file search')
    switch.add_argument('-a', nargs='?', dest='def_aud',
                        const='audio', default=None,
                        help='Activate audio file search')
    switch.add_argument('-v', nargs='?', dest='def_vid',
                        const='video', default=None,
                        help='Activate video file search')

    parser.add_argument('-dir', type=check_dir_path,
                        help='Directory path to search.')
    parser.add_argument('-o', action='store', dest='outfile',
                        default='ressource_def.rpy',
                        metavar='Output file',
                        help='Name for the output file')
    parser.add_argument('--verbose', dest='verbosity',
                        default=1, type=int, choices=range(0, 3),
                        metavar='Verbosity level [0-2]',
                        help='Amount of info output. default:1')
    parser.add_argument('--version', action='version',
                        version=f'%(prog)s : { __title__} {__version__}')
    parser.add_argument('--help', '-h', action='help',
                        help='Show this help message and exit')
    args = parser.parse_args()
    valid_switch()
    return args


def rrl_main(cfg):
    """
    This executes all program steps, does some valitity checks on the args and
    prints some infos messages if the default args are used.
    """

    print(sys.version, f'\n\n{__title__} {__version__}\n')

    print('configs', cfg.def_img, cfg.def_aud, cfg.def_vid)

    if cfg.def_img:
        rrl_img = RRL(cfg.def_img, 'image', cfg.outfile, cfg.verbosity)
        rrl_img.dir_lister()

    if cfg.def_aud:
        rrl_aud = RRL(cfg.def_aud, 'audio', cfg.outfile, cfg.verbosity)
        rrl_aud.dir_lister()

    if cfg.def_vid:
        rrl_vid = RRL(cfg.def_vid, 'video', cfg.outfile, cfg.verbosity)
        rrl_vid.dir_lister()

    print('\n>> Completed!\n')


if __name__ == '__main__':
    if not sys.version_info >= (3, 6):
        raise ValueError("Python 3.6 or higher needet.")
    rrl_main(parse_args())
