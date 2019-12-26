#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Program for converting the input image file into a numpy array and
constructing from it a graph representation of the the walkable area.
'''

# pylint: disable=w0511, C0103, C0301, r1710

import os
import argparse
import pprint
import pickle
# import lzma
import timeit

# import deepdish as dd
import numpy as np
from PIL import Image
# from natsort import humansorted


# import matplotlib.pyplot as plt


def control(mask_array, graphdict):
    '''Maze array and graph printed in txt files for easy checking'''

    arr = np.asarray(mask_array, dtype='uint8')
    # for color coding use:
    # Create an empty matrix with the same shape as x
    newarr = np.empty_like(arr)
    for i, _i in enumerate(arr):
        for j, _j in enumerate(arr[i]):
            if arr[i][j] == 0:  # black
                newarr[i][j] = 0
            elif arr[i][j] == 225:  # white
                newarr[i][j] = 1
            elif arr[i][j] == 15:  # red
                newarr[i][j] = 2
            elif arr[i][j] == 40:  # green
                newarr[i][j] = 3
            elif arr[i][j] == 45:  # yellow
                newarr[i][j] = 4
            elif arr[i][j] == 190:  # blue
                newarr[i][j] = 5
            elif arr[i][j] == 195:  # magenta
                newarr[i][j] = 6
            elif arr[i][j] == 220:  # cyan
                newarr[i][j] = 7
            else:
                newarr[i][j] = 0

    if not os.path.exists('control'):
        os.makedirs('control')
    # array human readable in txtfile
    with open('control/array_old.txt', 'w') as nfi:
        np.savetxt(nfi, arr, fmt='%03d')
    # array spacesaving in np file; re-usable
    with open('control/maskarray_old.npy', 'wb') as nfi:
        np.save(nfi, mask_array)
    # graph human readable in txtfile
    with open('control/graph_old.txt', 'w') as nfi:
        pprint.pprint(graphdict, stream=nfi, width=160, compact=True)


class M2G(object):
    '''Class for all graph building related functionality.'''
    imgmask = None
    mask = np.array
    graph = {}

    @classmethod
    def img_mask2array(cls):
        '''
        This reads a given image in, converting it to 8 bit RGB(from 24bit) and
        then into a numpy array.
        '''
        imgread = Image.open(cls.imgmask)
        # imgread = Image.open(imgmask)
        # Convert colors to 8 bit
        mask_img256 = imgread.convert('P')
        cls.mask = np.array(mask_img256)
        # return np.array(mask_img256)

    @classmethod
    def add_neighbor(cls, row, col):
        '''This helper adds the current cells walkable neighbors.'''
        if cls.mask[row - 1][col + 1] != 0:
            cls.graph[(row, col)].append(('NE', (row - 1, col + 1)))
            cls.graph[(row - 1, col + 1)].append(('SW', (row, col)))
        if cls.mask[row][col + 1] != 0:
            cls.graph[(row, col)].append(('EE', (row, col + 1)))
            cls.graph[(row, col + 1)].append(('WW', (row, col)))
        if cls.mask[row + 1][col + 1] != 0:
            cls.graph[(row, col)].append(('SE', (row + 1, col + 1)))
            cls.graph[(row + 1, col + 1)].append(('NW', (row, col)))
        if cls.mask[row + 1][col] != 0:
            cls.graph[(row, col)].append(('SS', (row + 1, col)))
            cls.graph[(row + 1, col)].append(('NN', (row, col)))

    @classmethod
    def maze2graph(cls):
        '''
        Builds a graph dict from a maze array. The cells of the walkable
        area is noted as keys along with their direct reachable neighbors as
        list of values.
        '''
        cls.img_mask2array()
        # height, width = mask.shape
        height, width = cls.mask.shape
        print(height, width)
        # collect cell cordinates as dict keys
        # graph = {}
        for i in range(height):
            for j in range(width):
                # filter unwalkable cells out
                if cls.mask[i][j] != 0:
                    cls.graph[(i, j)] = []

        for row, col in sorted(cls.graph.keys()):
            # print('current pos: ', row, col)
            # movement cost orthogonal 1, diagonal  1,41421
            if row in range(height)[1:-1] and col in range(width)[1:-1]:
                cls.add_neighbor(row, col)

        print(len(cls.graph.keys()))
        print(sum(map(len, cls.graph.values())))
        return cls.mask, cls.graph


def wrapper(func, *args, **kwargs):
    """Measures time."""
    def wrapped():
        """Helper."""
        return func(*args, **kwargs)
    return wrapped


def save_graph(graphdict):
    """Stores the graph to file."""

    # dd.io.save('graph/graph_dd.h5', graphdict)
    # with open('graph/graph.pickle', 'wb') as nfi:
    #     pickle.dump(graphdict, nfi)
    with open('graph/graph.pickle', 'wb') as nfi:
        pickle.dump(graphdict, nfi)


def get_args():
    '''This is the parser function'''
    def valid_img(infilename):
        '''Help function to test the given string for the infilename.'''
        # for char in ['/', ':', ' ']:
        for char in [':', ' ']:
            if char in infilename:
                raise parser.error('\'{}\' contains unallowed character.'.format(infilename))
        try:
            with Image.open(infilename) as img:
                print('Imagefile: \'{}\' with characteristics:\nFormat: {}, Size: {}, Mode: {}'.format(infilename, img.format, img.size, img.mode))
        except IOError:
            print('Input must be a PIL supported image file.')
        return infilename

    parser = argparse.ArgumentParser(description='Turns a image used as mask into a compressed h5 file with the stored graph.')
    parser.add_argument('imgfile', action='store',  # dest='imgfile',
                        type=valid_img, metavar='Image file',
                        help='Image file for processing.')
    return parser.parse_args()


def main(cfg):
    '''main func'''
    M2G.imgmask = cfg.imgfile
    # mask_array = M2G().img_mask2array()
    mask_array, graphdict = M2G().maze2graph()
    # mask_array = img_mask2array(cfg.imgfile)
    # graphdict = maze2graph(mask_array)

    if not os.path.exists('graph'):
        os.makedirs('graph')
    # graph space saving in hdf5 file; re-usable
    # dd.io.save('graph_dd.h5', graphdict)
    # dd.io.save('graph_dd_zl.h5', graphdict, compression=('zlib', 5))
    # dd.io.save('graph_dd_bl.h5', graphdict, compression=('blosc', 5))

    # with open('graph.pickle', 'wb') as nfi:
    # with lzma.open('graph/graph.pickle.xz', 'wb') as nfi:
    #     pickle.dump(graphdict, nfi)

    wrapped = wrapper(save_graph, graphdict)
    print(timeit.timeit(wrapped, number=1000))

    # save_graph(graphdict)
    control(mask_array, graphdict)


if __name__ == '__main__':
    main(get_args())
