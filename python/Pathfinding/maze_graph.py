#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Program for converting the input image file into a numpy array and
constructing from it a graph representation of the the walkable area.
'''

# pylint: disable=w0511, C0103, C0301, r1710

import os
import sys
import argparse
import pprint
import pickle
# import lzma
import timeit
from textwrap import dedent

import numpy as np
from PIL import Image

# from natsort import humansorted


def control(mask_array, graphdict):
    '''Maze array and graph printed in txt files for easy checking.'''

    # for color coding use:
    rep = [(225, 1), (15, 2), (40, 3), (45, 4), (190, 5), (195, 6), (220, 7)]
    arr_copy = np.copy(mask_array)

    for (o_val, n_val) in rep:
        mask_array[arr_copy == o_val] = n_val

    if not os.path.exists('control'):
        os.makedirs('control')
    # array human readable in txtfile
    with open('control/array.txt', 'w') as nfi:
        np.savetxt(nfi, mask_array, fmt='%03u')
    with open('control/array_changed.txt', 'w') as nfi:
        np.savetxt(nfi, mask_array, fmt='%u')
    # array spacesaving in np file; reusable
    with open('control/maskarray.npy', 'wb') as nfi:
        np.save(nfi, mask_array)
    # graph human readable in txtfile
    with open('control/graph.txt', 'w') as nfi:
        pprint.pprint(graphdict, stream=nfi, width=160, compact=True)


class M2G(object):
    '''Class for all graph building related functionality.'''

    def __init__(self, maskimg):
        self.mask_img = maskimg
        self.mask = np.array
        self.gridsize = ()
        self.graph = {}
        self.img_mask2array()

    def img_mask2array(self):
        '''
        This reads a given image in, converting it to 8 bit RGB(from 24bit) and
        then into a numpy array.
        '''
        imgread = Image.open(self.mask_img)

        # Convert colors to 8 bit
        mask_img256 = imgread.convert('P')
        self.mask = np.array(mask_img256)
        self.gridsize = self.mask.shape
        # print(f'np type: {np.dtype(self.mask)}')
        # return self.mask, self.gridsize

    def add_node(self, node):
        """ If the "node" is not in graph, a key with the node coordinates and
            an empty list as a value is added.
        """
        if node not in self.graph:
            self.graph[node] = []

    def add_link(self, src_n):
        '''This adds the edges.'''
        dirs = [['NE', (-1, 1)], ['SW', (1, -1)],
                ['E', (0, 1)], ['W', (0, -1)],
                ['SE', (1, 1)], ['NW', (-1, -1)],
                ['S', (1, 0)], ['N', (-1, 0)]]

        for dir_name, dir_val in dirs:
            dest_n = (src_n[0] + dir_val[0], src_n[1] + dir_val[1])

            if 0 < dest_n[0] < self.gridsize[0] and 0 < dest_n[1] < self.gridsize[1] and dest_n in self.graph:

                self.graph[src_n].append((dest_n, dir_name))

        # dirs = [[-1, 1], [0, 1], [1, 1], [1, 0]]
        # for _dir in dirs:
        #     dest_n = (src_n[0] + _dir[0], src_n[1] + _dir[1])
        #
        #     if 0 < dest_n[0] < self.gridsize[0] and 0 < dest_n[1] < self.gridsize[1] and dest_n in self.graph:
        #
        #         self.graph[src_n].append(dest_n)
        #         self.graph[dest_n].append(src_n)

    def maze2graph(self):
        '''
        Builds a simple graph dict from a maze/map array. The cells of the
        walkable area is noted as node keys; their neighbor nodes as list
        of linked values with a direction info.

        The structure looks like this:
        {(23, 8): [((23, 9), 'E'), ((24, 9), 'SE'), ...],
        [(23, 9): [...], ...}
        '''
        # print(f'gridsize: {self.gridsize}')
        # collect cell cordinates as dict keys
        for i in range(self.gridsize[0]):
            for j in range(self.gridsize[1]):
                # filter unwalkable cells out
                if self.mask[i][j] != 0:
                    self.add_node((i, j))

        start = timeit.default_timer()
        #
        for node in sorted(self.graph.keys()):
            self.add_link(node)

        print(timeit.default_timer() - start)

        print(len(self.graph.keys()))
        print(sum(map(len, self.graph.values())))

        return self.graph, self.gridsize, self.mask


def wrapper(func, *args, **kwargs):
    """Measures time."""
    def wrapped():
        """Helper."""
        return func(*args, **kwargs)
    return wrapped


def store_data(graphdict, gridsize):
    """Writes the graph and the variable `gridsize´ to files."""

    if not os.path.exists('graphdata'):
        os.makedirs('graphdata')
    with open('graphdata/graph.pickle', 'wb') as nfi:
        pickle.dump(graphdict, nfi)

    filehead = ("""\
    # -*- coding: utf-8 -*-

    \"\"\"Module for reusable storage of a variable.\"\"\"

    gridsize =""")
    with open('graphdata/gridsize.py', 'w') as nfi:
        print(dedent(filehead), gridsize, file=nfi)


def get_args():
    '''This is the parser function'''

    def valid_img(in_file):
        '''Help function to test the given string for the in_file.'''

        for char in [':', ' ']:
            if char in in_file:
                raise parser.error(f'{in_file} contains unallowed character.')
        try:
            with Image.open(in_file) as img:
                print(f'Imagefile: {in_file} with characteristics:\nFormat: {img.format}, Size: {img.size}, Mode: {img.mode}')
        except IOError:
            print('Input must be a PIL supported image file.')
        return in_file

    parser = argparse.ArgumentParser(description='Turns a image used as mask into a pickel file with the stored graph.')
    parser.add_argument('imgfile', action='store', type=valid_img, metavar='Image file', help='Image file for processing.')
    return parser.parse_args()


def main(cfg):
    '''... main function.'''

    # M2G.mask_img = cfg.imgfile
    m2g = M2G(cfg.imgfile)
    graphdict, gridsize, mask_array = m2g.maze2graph()


    # graph space saving in pickle file; re-usable
    # with open('graph.pickle', 'wb') as nfi:
    #     pickle.dump(graphdict, nfi)

    # wrapped = wrapper(store_data, graphdict, gridsize)
    # print(timeit.timeit(wrapped, number=1000))
    store_data(graphdict, gridsize)

    control(mask_array, graphdict)


if __name__ == '__main__':
    if not sys.version_info >= (3, 6):
        raise ValueError("Python 3.6 or higher needet.")
    main(get_args())
