#!/usr/bin/env python3

"""
A small program for listing defined Ren'Py ressourses.

It is intended to be executed in the Ren'pys game directory below the asset
dirs (images, audio).
The subdirectories will be searched and the content written to a file.

INFOS:
python 3.6+ required
python package dependencys: natsort, python-magic

Works with my Linux distro. Untested in other OS; however it should with few
changes.
For working format recognition in win/mac look at the installation notes at
https://github.com/ahupp/python-magic

This builds on the work and knowledge of many people all over the
world. Thanks!

Try to organize your directories cleanly to make it as usable as possible
for the script!
"""

# pylint: disable=w0511, C0103, C0301
# TODO:
    # Move outfile default from argparse to class
    # move check_dir_path from argparse to class
    # rework init assert test to normal test method
    # test if pathlike changes all correct working (no missing pt(...))



import os
import sys
from pathlib import Path as pt
import argparse
from time import localtime, strftime, sleep
import textwrap
import magic
from natsort import humansorted

__title__ = 'RenPy Ressource Lister'
__license__ = 'MIT'
__author__ = 'madeddy'
__status__ = 'Development'
__version__ = '0.16.0-alpha'



class RRL:
    """The class for all ressource defining related functionality."""
    name = 'RenPy Ressource Lister'
    verbosity = 1
    tmp_lst = []
    supp_ext = ['webp', 'png', 'jpeg', 'jpg', 'opus', 'ogg', 'mp3', 'wav',
                'webm', 'mkv', 'ogv', 'avi', 'mpeg', 'mpeg2', 'mpeg4', 'mp4']

    def __init__(self, inp, outfile, verbose=None):
        self.inpdir = pt(inp[0])
        try:
            assert inp[1] in ['image', 'audio', 'video']
        except AssertionError as error:
            print('Wrong type given.', error)
        self.typus = inp[1].lower()
        self.outfile = pt(outfile)
        if verbose:
            RRL.verbosity = verbose

    @classmethod
    def inf(cls, inf_level, message, warn=False):
        """Outputs the infos allowed for the current verbosity level."""

        if cls.verbosity >= inf_level:
            mes_sort = 'INFO'
            if warn:
                mes_sort = 'WARNING'
            print(f"RRL {mes_sort}: {message}")

    def valid_path(self):
        """This tests if the given directory exists."""
        if not self.inpdir.is_dir():
            raise OSError(f"Directory {self.inpdir!r} does not exist.")

    def valid_outfile(self):
        """This tests if the given output filename is acceptable."""

        if self.outfile.suffix != '.rpy':
            raise ValueError("Output filename must have rpy extension.")

        for char in [':', ' ']:
            if char in str(self.outfile):
                raise OSError(f"\"{self.outfile}\" contains unallowed charakter.")

    def check_defaults(self):
        """Checks if default values are used and informs if verbosity=2."""

        if self.outfile == 'ressource_def.rpy':
            self.inf(2, f">> Output filename set to default: <{self.outfile}>.")
        # FIXME: Used like this the dirs can be mixed up with the type
        if self.inpdir.name in ['images', 'audio', 'video']:
            self.inf(2, f"{self.typus.title()} directory set to default: <{self.inpdir}>.")

    def test_register_file(self):
        """Tests if the given output filename already exists and makes
        a backup.
        """

        if self.outfile.is_file():
            timest_suff = f".{strftime('%d%b%Y_%H:%M:%S', localtime())}.bup"
            self.outfile.rename(self.outfile.with_suffix(timest_suff))

            self.inf(1, f">> Target file {self.outfile} already exists. Performed " \
                     "backup. Original file has now extension <bup>.")
            sleep(1)

    def write_register_list(self):
        """Writes a intro and the content of the register list to the file."""

        header_text = ("""\
        # REN'PY ASSET LIST
        # Below are the project assets with the renpy <asset_type>
        # declaration. e.g.:
        # image sally tired = "images/char/sally/tired.webp"
        # Ready for use with alias like known or changeable like wanted.""")

        # print(textwrap.dedent(header_text), file=self.open_of)
        # print(*self.tmp_lst, sep='\n', file=self.open_of)
        with self.outfile.open('w') as ofi:
            print(textwrap.dedent(header_text), file=ofi)
            print(*self.tmp_lst, sep='\n', file=ofi)

        # print(*self.tmp_lst, sep='\n')
        self.inf(2, f">> List was written to file {self.outfile!r} in directory\n{pt.cwd()}")

    @staticmethod
    def get_mimetype(inp):
        """Returns the mime type of a file."""
        return magic.from_file(str(inp), mime=True).split('/')

    def format_test(self, testobj): # pylint: disable=r1710
        """
        This determines if the input file is a known format of the given media
        type. Negatives are skipped, positives again checked if their extension
        is supported or not. Returns this status.
        """

        if testobj.is_file():
            m_type, f_type = self.get_mimetype(testobj)

            # print('get mime_type', m_type)
            if self.typus not in m_type:
                return None
            if '-' in f_type:
                f_type = f_type.split('-')[1]
            # print('guess extension', f_type)
            return bool(f_type in RRL.supp_ext)

    def typus_statement(self, cur_dir, rel_path, fn_base):
        """
        This supports the dir lister by constructing the define statements for
        the actual asset typus.
        """

        alias_sep = '_'
        if self.typus == 'image':
            dcl_base = 'image '
        elif self.typus == 'audio':
            dcl_base = 'define audio.'

        if cur_dir not in self.inpdir.name:
            dcl_left = dcl_base + cur_dir + alias_sep + fn_base
        else:
            dcl_left = dcl_base + fn_base

        dcl_right = rel_path
        if self.typus == 'video':
            dcl_right = f"Movie(play='{rel_path}')"

        return f"{dcl_left} = '{dcl_right}'"

    def dir_lister(self):
        """This finds, filters and lists all elements in the given path."""

        self.tmp_lst.append(f"\n\n# {self.typus.title()} section {'#' * 64}\n")

        unsup_count = 0
        for path, dirs, files in os.walk(self.inpdir):
            dirs = humansorted(dirs)
            subdirs = f" with subdirectorys: {', '.join(dirs)}"
            # TODO: rrl should not write empty dirs in the outfile
            self.tmp_lst.append(f"# ### Current directory: {path}/{subdirs if dirs else None}")

            files = humansorted(files)
            cur_dir = pt(path).name

            for fn in files:
                fullpath = path.joinpath(fn)
                format_status = self.format_test(fullpath)

                if format_status is True:
                    fn_base = fn.stem.lower()
                    rel_path = fullpath.relative_to(self.inpdir)
                    self.tmp_lst.append(
                        self.typus_statement(cur_dir, rel_path, fn_base))

                elif format_status is False:
                    unsup_count += 1
                else:
                    continue

        if unsup_count > 0:
            self.inf(1, f"The directory contains {unsup_count!s} {self.typus} file(s) of non-supported type.")


    def rrl_control(self):
        """Central method to execute all steps."""
        self.valid_path()
        self.valid_outfile()
        self.check_defaults()
        # needs before open or hits old file (if exist)
        self.test_register_file()
        # self.open_of = open(outfile, 'w')
        self.dir_lister()
        self.write_register_list()


def parse_args():
    """
    Argument parser and test for input path to provide functionality for the
    command line interface. Also ensures that at least one of the required switches
    is present.
    """

    def check_dir_path(dir_path):
        """Helper function to make sure given path is a dir."""
        if not pt(dir_path).is_dir() or pt(dir_path).is_symlink():
            raise NotADirectoryError(dir_path)
        return dir_path

    def valid_switch():
        """Helper function to determine if a switch is set."""
        if not args.def_img and not args.def_aud and not args.def_vid:
            aps.print_help()
            raise argparse.ArgumentError('', "\nNo task requested; either -i, -a or -v is required.")

    aps = argparse.ArgumentParser(
        add_help=False,
        description='A program for listing ren`py ressources.\nEXAMPLE USAGE: res_def.py -i -idir all_img -o mylist.rpy',
        epilog='One of the switches must be set or the program exits. The other options have default values which are used if they are not set.')

    switch = aps.add_argument_group('Switches', 'Activate search and listing of the respective filetype.\nOne is at least required!')
    switch.add_argument('-i', nargs='?',
                        dest='def_img',
                        const='images',
                        default=None,
                        help='Activate image file search')
    switch.add_argument('-a', nargs='?',
                        dest='def_aud',
                        const='audio',
                        default=None,
                        help='Activate audio file search')
    switch.add_argument('-v', nargs='?',
                        dest='def_vid',
                        const='video',
                        default=None,
                        help='Activate video file search')
    aps.add_argument('-dir',
                     type=check_dir_path,
                     help='Directory path to search.')
    aps.add_argument('-o',
                     action='store',
                     dest='outfile',
                     default='ressource_def.rpy',
                     metavar='Output file',
                     help='Name for the output file')
    aps.add_argument('--verbose',
                     type=int,
                     choices=range(0, 3),
                     metavar='Verbosity level [0-2]',
                     help='Amount of info output. default:1')
    aps.add_argument('--version',
                     action='version',
                     version=f"%(prog)s : { __title__} {__version__}")
    aps.add_argument('--help', '-h',
                     action='help',
                     help='Show this help message and exit')
    args = aps.parse_args()
    valid_switch()
    return args


def rrl_main(cfg):
    """This executes all program steps, validity checks on the args and prints
    infos messages if the default args are used.
    """
    if not sys.version_info[:2] >= (3, 6):
        raise Exception("Must be executed in Python 3.6 or later.\n"
                        f"You are running {sys.version}")

    print("configs", cfg.def_img, cfg.def_aud, cfg.def_vid)
    # if cfg.def_img:
    #     rrl_img = RRL(cfg.def_img, 'image', cfg.outfile, cfg.verbosity)
    #     rrl_img.dir_lister()
    # if cfg.def_aud:
    #     rrl_aud = RRL(cfg.def_aud, 'audio', cfg.outfile, cfg.verbosity)
    #     rrl_aud.dir_lister()
    # if cfg.def_vid:
    #     rrl_vid = RRL(cfg.def_vid, 'video', cfg.outfile, cfg.verbosity)
    #     rrl_vid.dir_lister()
    if cfg.def_img:
        med_arg = cfg.def_img, 'image'
    elif cfg.def_aud:
        med_arg = cfg.def_aud, 'audio'
    elif cfg.def_vid:
        med_arg = cfg.def_vid, 'video'
    rrl = RRL(med_arg, cfg.outfile, cfg.verbose)
    rrl.rrl_control()

    print("\n>> Completed!\n")


if __name__ == '__main__':
    rrl_main(parse_args())
