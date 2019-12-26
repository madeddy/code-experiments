#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
'''
A simple script for listing defined ren'py ressourses.

It is intended to be executed in the renpy's game directory below the asset
dirs (images, audio).
It will search the subdirectories and write the content to a file.
'''

# pylint: disable=w0511, C0103, C0301


import os
import os.path
import sys
import argparse
import textwrap
from time import localtime, strftime, sleep
from natsort import humansorted

__title__ = 'RenPy Ressource Lister'
__license__ = 'MIT'
__author__ = 'madeddy'
__status__ = 'Development'
__version__ = '0.7.0-alpha'

# Infos:
# python version 2.7 or higher required
# also: natsort
# Works with my Linux distro. Untestet with other OS; however should
# work with few changes.
# This script builds on the work of thousands of people all over the world.
# Thanks!
#
# Try to organize your directories cleanly to make it as usable as possible
# for the script!

#-#-#-#-#-#-#-#-#-#-


list_store = []


def check_register_file(nrf):
    '''Create renpy script with given name and backups if existing already.'''

    if os.path.isfile(nrf):
        time_stamp = strftime('%d%b%Y_%H:%M:%S', localtime())
        os.rename(nrf, os.path.splitext(nrf)[0] + '.' + time_stamp + '.bup')
        print('>> Target file', nrf, 'already exists. Performed backup.',
              'Original file has now extension <bup>.', sep=' ')
        sleep(1)

    intro_text = ('''\
    # REN'PY RESSOURCE DEFINES
    # Below are the project assets with the renpy <ressource_type>
    # declaration. e.g.:
    # image sally tired = 'images/char/sally/tired.webp'
    # Ready for use with alias like known or changeable like wanted.''')

    with open(nrf, 'w') as nfi:
        print(textwrap.dedent(intro_text), file=nfi)


# FIXME Find way to pass list without global list variable
def build_register(nrf):
    '''Writes register content to file.'''

    with open(nrf, 'a+') as nfi:
        print(*list_store, sep='\n', file=nfi)
    print('>> List was written to file', nrf, 'in directory\n',
          os.getcwd(), sep=' ')


def format_test(filename, typus):
    '''
    Determines if input file is a image-/audioformat, supported or other.
    Returns status.
    '''
    # NOTE Possible use of imghdr. However ident. webp requires python 3.5 !
    img_ext = ['webp', 'png', 'jpeg', 'jpg',
               'gif', 'bmp', 'svg', 'tiff', 'tif']
    aud_ext = ['opus', 'ogg', 'mp3', 'wav', 'webm', 'flac',
               'wma', 'aac', 'm4a', 'mp4', 'mka', 'aiff', 'aif']
    ext = os.path.splitext(filename)[1][1:].lower()
    if (typus == 'Image' and ext in img_ext) or (typus == 'Audio' and ext in aud_ext):
        if ext in ['webp', 'png', 'jpeg', 'jpg', 'opus', 'ogg', 'mp3', 'wav']:
            return 'supported'
        return 'unsupported'
    return


def dir_lister(check_dir, typus):
    '''Finds, filters and lists all elements in the images directory.'''

    unsup_form = 0
    if typus == 'Image':
        alias = 'image '
        al_sep = ' '
    elif typus == 'Audio':
        alias = 'define audio.'
        al_sep = '_'
    list_store.append('\n\n# ' + typus + ' section '.ljust(64, '#') + '\n')

    for path, dirs, files in os.walk(check_dir):
        dirs = humansorted(dirs)
        subdirs = ' with subdirectorys: ' + ', '.join(dirs)
        list_store.append('# ### Current directory: ' + path
                          + os.path.sep + (subdirs if dirs else ''))

        cur_dir = os.path.basename(path)
        if cur_dir not in check_dir:
            dec_ln1 = alias + cur_dir + al_sep
        else:
            dec_ln1 = alias

        files = humansorted(files)
        for fn in files:
            checked_form = format_test(fn, typus)
            if checked_form == 'supported':
                fn_base = os.path.splitext(fn)[0].lower()
                dec_ln2 = fn_base + ' = ' + \
                    os.path.relpath(os.path.join(path, fn), '.')
                # dec_ln2 = fn_base + ' = ' + dec_ln2
                list_store.append(dec_ln1 + dec_ln2)
            elif checked_form == 'unsupported':
                unsup_form += 1
            else:
                continue

    if unsup_form > 0:
        print('INFO: The directory contains', str(unsup_form), typus.lower(), 'file(s) of non-supported type.', sep=' ')


def get_args():
    '''Argument parser...'''

    parser = argparse.ArgumentParser(add_help=False, description='A program for listing ren`py ressources.\nEXAMPLE USAGE: res_def.py -i -idir all_img -o mylist.rpy', epilog='One of the switches must be set or the program exits. The other options have default values which are used if they are not set.')
    switch = parser.add_argument_group('Switches', 'One of them is required.')
    switch.add_argument('-i', action='store_true', dest='define_images',
                        default=False,
                        help='Activate search and listing of images')
    switch.add_argument('-a', action='store_true', dest='define_audio',
                        default=False,
                        help='Activate search and listing of audio')
    parser.add_argument('-idir', action='store', dest='image_res_dir',
                        default='images',
                        help='Name of the image folder')
    parser.add_argument('-adir', action='store', dest='audio_res_dir',
                        default='audio',
                        help='Name of the audio folder')
    parser.add_argument('-o', action='store', dest='output_file',
                        default='ressource_def.rpy',
                        help='Name for the output file')
    parser.add_argument('--version', action='version',
                        version='%(prog)s 0.7.0-alpha')
    parser.add_argument('--help', '-h', action='help',
                        help='Show this help message and exit')
    return parser.parse_args()


def main(cfg):
    '''Executes all function steps. Some checks for set args.'''

    print(sys.version)

    if cfg.define_images is True or cfg.define_audio is True:
        if cfg.output_file == 'ressource_def.rpy':
            print('>> Output filename set to default: <ressource_def.rpy>.')
            sleep(1)
        check_register_file(cfg.output_file)
    else:
        raise SystemExit('\nERROR: None of the required switches set! No task to perform. Use -h or --help option.\nExiting.\n')

    if cfg.define_images is True and os.path.isdir(cfg.image_res_dir):
        if cfg.image_res_dir == 'images':
            print('>> Image directory set to default: <images>.')
            sleep(1)
        dir_lister(cfg.image_res_dir, 'Image')
    else:
        os.remove(cfg.output_file)
        raise SystemExit('\nERROR: Image directory \'' + cfg.image_res_dir + '\' does not exist.\nExiting.\n')

    if cfg.define_audio is True and os.path.isdir(cfg.audio_res_dir):
        if cfg.audio_res_dir == 'audio':
            print('>> Audio directory set to default: <audio>.')
            sleep(1)
        dir_lister(cfg.audio_res_dir, 'Audio')
    else:
        os.remove(cfg.output_file)
        raise SystemExit('\nERROR: Audio directory \'' + cfg.audio_res_dir + '\' does not exist.\nExiting.\n')

    build_register(cfg.output_file)
    print('\n>> Completed!\n')


def messenger(msgt, arg=None):
    '''Prints the message for the chosen type.'''
    if msgt in ('req_opt', 'idir_miss', 'adir_miss'):
        if msgt == 'req_opt':
            # messenger('req_opt')
            msg = ('\nERROR: None of the required options given! ' + 'No action to perform. Use -h or --help option.' + '\nExiting.\n')
        elif msgt == 'idir_miss':
            # messenger('idir_miss', cfg.image_res_dir)
            msg = ('\nERROR: Image directory ' + arg + ' does not exist. ' + '\nExiting.\n')
        elif msgt == 'adir_miss':
            # messenger('adir_miss', cfg.audio_res_dir)
            msg = ('\nERROR: Audio directory ' + arg + ' does not exist. ' + '\nExiting.\n')
        print(msg, file=sys.stderr)
    else:
        if msgt == '':
            msg = '>> '
        elif msgt == '':
            msg = '>> '
        elif msgt == '':
            msg = ''
        elif msgt == '':
            msg = ''
        print(msg)


if __name__ == '__main__':
    main(get_args())
