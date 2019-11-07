#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Short program for changing matching lines of a file inplace.'''

import os
import re
import fileinput


def correct_showtext():
    """
    Walks in all directorys, finds .rpy files and corrects the 'displayable
    text lines'. The ren`py translation system can recognize them then as
    dialog and include this lines.
    Example: show text "str" -> show text (_("str"))
    """

    com_rmv = '# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc'

    for path, _, files in os.walk('.'):
        for afile in files:
            if afile.endswith('rpy'):
                fpath = os.path.join(path, afile)
                with fileinput.input(fpath, inplace=True) as ofi:
                # with open(fpath, mode='r+') as ofi:
                #     line_in = ofi.readlines()
                    for line in ofi:
                        # regex = r'( +?show text )\"(.+?)\" '
                        # subst = '\\1(_(\"\\2\")) '
                        regex = r'(show text )\"(.+?)\"( |\n)'
                        subst = '\\1(_(\"\\2\"))\\3'
                        newline = re.sub(regex, subst, line, 0)
                        print(line.replace(line, newline), end='')

                        if com_rmv in line:
                            print(line.replace(com_rmv, ''), end='')


if __name__ == '__main__':
    correct_showtext()
