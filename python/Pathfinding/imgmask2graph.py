#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Program for converting the input image file into a numpy array and
constructing from it a graph representation of the the walkable area.
'''

# pylint: disable=w0511, C0103, C0301, r1710

import os
import argparse
import pickle
import pprint
import numpy as np
from PIL import Image
# from natsort import humansorted


# import matplotlib.pyplot as plt
# import pickle
# import lzma


def control(mask_array, graph_nodes, graph_edges):
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
    with open('control/array.txt', 'w') as nfi:
        np.savetxt(nfi, arr, fmt='%03d')
    # array spacesaving in np file; re-usable
    with open('control/array.npy', 'wb') as nfi:
        np.save(nfi, mask_array)
    # graph human readable in txtfile
    with open('control/graph.txt', 'w') as nfi:
        pprint.pprint(graph_nodes, stream=nfi, width=160, compact=True)
        pprint.pprint(graph_edges, stream=nfi, width=160, compact=True)


class M2G():
    '''Class for all graph building related functionality.'''
    mask_img = None
    mask = np.array
    graph_nodes = {}
    graph_edges = {}
    n_idcount = 0
    e_idcount = 0
    s_node = None
    # t_node = None

    def img_mask2array(self):
        '''
        This reads a given image in, converting it to 8 bit RGB and
        then into a numpy array.
        '''
        imgread = Image.open(self.mask_img)
        # Convert colors to 8 bit
        mask_img256 = imgread.convert('P')
        self.mask = np.array(mask_img256)
        # self.mask = np.asanyarray(arr)

    def get_nodeid(self, pos):
        '''This returns the id of the given cell coordinates.'''

        for node_id, ((node_pos), _) in self.graph_nodes.items():
            if pos in node_pos:
                return node_id

    def add_node(self, cur_row, cur_col):
        '''This adds the edges.'''

        self.n_idcount += 1
        if self.mask[cur_row][cur_col] == 225:
            self.graph_nodes['n{}'.format(
                self.n_idcount)] = ((cur_row, cur_col), 0)
        if self.mask[cur_row][cur_col] == 195:
            self.graph_nodes['n{}'.format(
                self.n_idcount)] = ((cur_row, cur_col), 1)

    def add_edge(self, t_row, t_col):
        '''This adds the edges.'''

        t_node = self.get_nodeid((t_row, t_col))
        self.e_idcount += 1
        self.graph_edges['e{}'.format(self.e_idcount)] = (
            self.s_node, t_node)

    def makegraph(self):
        '''
        Builds a graph dict from a maze array. The cells of the walkable
        area are noted as keys along with their direct reachable neighbors as
        list of values.
        '''

        self.img_mask2array()
        # arrmask = self.mask
        # height, width = arrmask.shape
        gridsize = self.mask.shape

        # collect cell cordinates as dict keys
        for i in range(gridsize[0]):
            for j in range(gridsize[1]):
                # filter unwalkable cells out
                if self.mask[i][j] != 0:
                    self.add_node(i, j)

        # the var "cross" is a node with more as 2 accessible neighbors
        # e.g backward (where we came from) and forward/another
        # accessible node
        for self.s_node, ((row, col), cross) in self.graph_nodes.items():
            # print('Current pos: ', row, col, cross, 'node: ', self.s_node)
            if row in range(gridsize[0])[1:-1] and col in range(gridsize[1])[1:-1]:
                # NE SW
                if self.mask[row - 1][col + 1] != 0:
                    self.add_edge(row - 1, col + 1)
                # E W
                if self.mask[row][col + 1] != 0:
                    self.add_edge(row, col + 1)
                # SE NW
                if self.mask[row + 1][col + 1] != 0:
                    self.add_edge(row + 1, col + 1)
                # S N
                if self.mask[row + 1][col] != 0:
                    self.add_edge(row + 1, col)

        print('Graph edge: ', self.graph_edges)

        print(len(self.graph_nodes.keys()))
        print(len(self.graph_edges.keys()))
        # print(sum(map(len, graph_edges.values())))
        return self.mask, self.graph_nodes, self.graph_edges


def get_args():
    '''This is the parser function'''

    def valid_img(infilename):
        '''Help function to test the given string for the infilename.'''

        for char in ['/', ':', ' ']:
            if char in infilename:
                raise parser.error(f'{infilename} contains unallowed character.')
        try:
            with Image.open(infilename) as img:
                print(f'Imagefile: {infilename} with characteristics:\nFormat: {img.format}, Size: {img.size}, Mode: {img.mode}')
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

    M2G.mask_img = cfg.imgfile
    # mask_array = M2G().img_mask2array()

    mask_array, graph_nodes, graph_edges = M2G().makegraph()

    # graph space saving in pickle file; re-usable
    if not os.path.exists('graph'):
        os.makedirs('graph')
    with open('graph/graph_n.pickle', 'wb') as nfi:
        pickle.dump(graph_nodes, nfi)
    with open('graph/graph_e.pickle', 'wb') as nfi:
        pickle.dump(graph_edges, nfi)

    control(mask_array, graph_nodes, graph_edges)


if __name__ == '__main__':
    main(get_args())
