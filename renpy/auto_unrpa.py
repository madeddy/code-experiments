#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""App that searches RPA files and uses UnRPA to unpack them in a new directory."""

# pylint: disable=c0301, w0612

import os
from pathlib import Path
import sys
import argparse
from unrpa.unrpa import UnRPA


def auto_unrpa(search_dir):
    """Searches and unpacks RPA files."""

    out_dir = Path(Path(search_dir).parent).joinpath('rpa_extract')
    if not Path(out_dir).exists():
        Path(out_dir).mkdir(parents=True, exist_ok=True)
    rpa_count = 0
    rpa_list = []

    for entry in os.scandir(path=search_dir):
        # if Path(entry).is_file() and Path(entry).suffix == '.rpa':
        if Path(entry).is_file() and Path(entry).suffix in ['.rpa', '.rpc', '.rpi']:

            UnRPA(entry, path=out_dir, verbosity=0).extract_files()
            rpa_count += 1
            rpa_list.append(entry.name)

    if rpa_count > 0:
        print(f'Unpacked {rpa_count} RPA files:', *rpa_list, sep='\n\u2022 ')
    else:
        print("No RPA files found.")


def parse_args():
    """Gets the arguments."""

    def check_dir_path(dir_path):
        """Helper for check if given path is a dir."""
        if not Path(dir_path).exists():
            raise FileNotFoundError(dir_path)
        if not Path(dir_path).is_dir():
            raise NotADirectoryError(dir_path)
        return dir_path

    parser = argparse.ArgumentParser(
        description='Mini-app for finding and unpacking RPA files.\nEXAMPLE USAGE: rpa_unp.py -d /home/USER/somedir',
        epilog='A `rpa_extract` dir will be made in the given path.')
    parser.add_argument('-dir', type=check_dir_path,
                        help='Directory path to search for RPA.')
    parser.add_argument('--version', action='version',
                        version='%(prog)s 0.1.0-alpha')
    return parser.parse_args()


def main(cfg):
    """Standard main function."""
    print(f'Searching for RPA in {cfg.dir} and below.')
    auto_unrpa(cfg.dir)


if __name__ == '__main__':
    assert sys.version_info >= (3, 6), \
        f"Must be run in Python 3.6 or later. You are running {sys.version}"
    main(parse_args())
