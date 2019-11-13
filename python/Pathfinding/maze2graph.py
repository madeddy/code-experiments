#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
A program that converts the input image file into a numpy array and
constructs from it a graph representation of the the walkable area.
'''

# pylint: disable=w0511, C0103, C0301, r1710


import argparse
import pprint
import sys
from pathlib import Path
from textwrap import dedent
import numpy as np
from PIL import Image
import dill as pickle

__title__ = 'maze2graph'
__license__ = 'MIT'
__author__ = 'madeddy'
__status__ = 'Development'
__version__ = '0.22.0-alpha'


def control(mtrx_arr, graphdict):
    '''Control: Maze array and graph printed in txt files for easy checking.'''

    # for color coding use:
    rep = [(225, 1), (15, 2), (40, 3), (45, 4), (190, 5), (195, 6), (220, 7)]
    arr_copy = np.copy(mtrx_arr)

    for (o_val, n_val) in rep:
        mtrx_arr[arr_copy == o_val] = n_val

    if not Path('control').exists():
        Path('control').mkdir(parents=True, exist_ok=True)
    # array human readable in txtfile
    with open('control/array.txt', 'w') as nfi:
        np.savetxt(nfi, mtrx_arr, fmt='%03u')
    with open('control/array_changed.txt', 'w') as nfi:
        np.savetxt(nfi, mtrx_arr, fmt='%u')
    # array spacesaving in np file; reusable
    with open('control/matrixarr.npy', 'wb') as nfi:
        np.save(nfi, mtrx_arr)
    # graph human readable in txtfile
    with open('control/graph.txt', 'w') as nfi:
        pprint.pprint(graphdict, stream=nfi, width=160, compact=True)


class M2G:
    '''Main class for all graph building related functionality.'''

    def __init__(self, maskimg):
        self.mtrx = np.array([[]])
        self.gsy, self.gsx = 0, 0
        self.graph = {}
        self.img_mask2matrix(maskimg)

    def img_mask2matrix(self, maskimg):
        '''This reads a given image in, converting it to 8 bit RGB(from 24bit)
           and then into a numpy array.
        '''
        imgread = Image.open(maskimg)
        # Convert colors to 8 bit
        mask_img256 = imgread.convert('P')
        self.mtrx = np.array(mask_img256)
        self.gsy, self.gsx = self.mtrx.shape

    def add_node(self, node):
        """Adds the given node to the graph if containment check is negativ. Format is e.g.: {(12, 654), []}"""
        if not self.has_node(node):
            self.graph[node] = []

    def has_node(self, node):
        """Checks if the given node is in the graph."""
        # print(node)
        if node not in self.graph.keys():
            return False
        return True

    @staticmethod
    def tup_add(tup1, tup2):
        '''This is a helper to add int values in two tuples up.'''
        return tuple(x + y for x, y in zip(tup1, tup2))

    def chk_pos(self, node):
        '''Helper to check the status of the the given node.'''
        if not self.gsy > node[0] and not node[0] > 0 and not self.gsx > node[1] and not node[1] > 0:
            return False
        return True

    def add_link(self, src_n):
        '''This adds the found links between nodes to the graph.
        The direction(dir) table setup is:
        ('dir name', (coord change value), 'reverse dir name')'''
        dirs = (('NE', (-1, 1), 'SW'),
                ('E', (0, 1), 'W'),
                ('SE', (1, 1), 'NW'),
                ('S', (1, 0), 'N'))
        for d1_name, dir_val, d2_name in dirs:
            dest_n = self.tup_add(src_n, dir_val)

            if self.chk_pos(dest_n) and self.has_node(dest_n):
                self.graph[src_n].append((dest_n, d1_name))
                self.graph[dest_n].append((src_n, d2_name))

    def maze2graph(self):
        '''
        Builds a simple graph dict from a maze/map array. The cells of
        the walkable area are noted as "keys"; their neighbor nodes as
        list of linked "values" with a direction info.

        The structure looks like this:
        {(23, 8): [((23, 9), 'E'), ((24, 9), 'SE'), ...],
        (23, 9): [(23, 8)...], ...}
        '''

        for i in range(self.gsy):
            for j in range(self.gsx):
                # filter unwalkable cells out
                if self.mtrx[i][j] != 0:
                    self.add_node((i, j))

        for node in self.graph:
            self.add_link(node)

        keycount = (len(self.graph.keys()))
        valcount = (sum(map(len, self.graph.values())))
        # return of matrix is only for control used
        return self.graph, (self.gsy, self.gsx), self.mtrx, keycount, valcount


def store_data(graphdict, gridsize, keycount, valcount):
    """Writes the graph and the variable `gridsize´ to files."""

    if not Path('graphdata').exists():
        Path('graphdata').mkdir(parents=True, exist_ok=True)
    with open('graphdata/graph.pickle', 'wb') as nfi:
        pickle.dump(graphdict, nfi, protocol=pickle.HIGHEST_PROTOCOL)

    filehead = (f"""\
    # -*- coding: utf-8 -*-

    \"\"\"Module for reusable storage of a variable.\"\"\"

    gridsize = {gridsize}
    key_count = {keycount}
    value_count = {valcount}""")
    with open('graphdata/graphinfo.py', 'w') as nfi:
        print(dedent(filehead), file=nfi)


def get_args():
    '''This is the parser function'''

    def valid_img(in_file):
        '''Help function to test the given string for the in_file.'''

        for char in [':', ' ']:
            if char in in_file:
                raise parser.error(f'{in_file} contains unallowed character.')
        try:
            with Image.open(in_file) as img:
                print(
                    f'Imagefile: {in_file} with characteristics:\nFormat: {img.format}, Size: {img.size}, Mode: {img.mode}')
        except IOError:
            print('Input must be a PIL supported image file.')
        return in_file

    parser = argparse.ArgumentParser(
        description='Turns a image used as mask into a pickel file with the stored graph.')
    parser.add_argument('imgfile', action='store', type=valid_img,
                        metavar='Image file',
                        help='Image file for processing.')
    return parser.parse_args()


def main(cfg):
    '''... main function.'''

    m2g = M2G(cfg.imgfile)
    graphdict, gridsize, mtrx_arr, keycount, valcount = m2g.maze2graph()

    control(mtrx_arr, graphdict)
    store_data(graphdict, gridsize, keycount, valcount)


if __name__ == '__main__':
    if not sys.version_info >= (3, 6):
        raise ValueError("Python 3.6 or higher needet.")
    main(get_args())
