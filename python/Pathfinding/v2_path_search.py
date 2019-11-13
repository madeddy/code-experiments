#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Test.'''

# pylint: disable=w0511, C0103, C0301, r1710


import argparse
import pprint
# import pickle
# import lzma
from collections import deque, namedtuple
from heapq import heappush, heappop

import deepdish as dd
# import tables
import numpy as np


class BFS(object):
    '''Class for pathfinding related functionality.'''
    mask_array = {}
    graph_nodes = {}
    graph_edges = {}

    mask = None

    @classmethod
    def get_nodeid(cls, pos):
        '''This returns the id of the given cell coordinates.'''
        for node_id, ((node_pos), _) in cls.graph_nodes.items():
            if pos == node_pos:
                return node_id

    @classmethod
    def find_path_bfs(cls):
        '''Breadth-first search (BFS)'''

        start = cls.get_nodeid((1, 1))
        goal = cls.get_nodeid((
            len(cls.mask_array) - 2, len(cls.mask_array[0]) - 2))
        print(start, goal)
        queue = deque([('', start)])

        visited = set()

        while queue:
            path, current = queue.popleft()
            print('Path, Current: ', path, current)
            # control
            with open('pathtry.txt', 'a+') as nfi:
                pprint.pprint(path, stream=nfi)

            if current == goal:
                # control
                pathnew = cls.split2waypoints(path)
                with open('path.txt', 'a+') as nfi:
                    pprint.pprint(pathnew, stream=nfi, width=80, compact=True)
                return path

            if current in visited:
                continue

            visited.add(current)

            for direct, neighbour in cls.graph_edges[current]:
                queue.append((path + direct, neighbour))

        return 'Was unable to calculate a way to target coordinate.'

    @staticmethod
    def split2waypoints(seq):
        '''A generator to divide a sequence into chunks of n units.'''

        lst = []
        while seq:
            lst.append(seq[:2])
            seq = seq[2:]
        return lst


def get_args():
    '''This is the parser function'''
    def valid_h5(infilename):
        '''Help function to test the given string for the infilename.'''
        if infilename.endswith('.h5'):
            for char in [':', ' ']:
                if char in infilename:
                    raise parser.error('\'{}\' contains unallowed character.'.format(infilename))
            return infilename
        else:
            raise parser.error('Input must be a h5 file.')

    parser = argparse.ArgumentParser(description='Turns a image used as mask into a compressed h5 file with the stored graph.')
    parser.add_argument('graph_file_n', action='store',  # dest='h5file',
                        type=valid_h5, metavar='HDF5 nodes file',
                        help='HDF5 file with graph for processing.')
    parser.add_argument('graph_file_e', action='store',
                        type=valid_h5, metavar='HDF5 edges file',
                        help='HDF5 file with graph for processing.')
    return parser.parse_args()


def main(cfg):
    '''main func'''

    # array spacesaving in np file; re-usable
    with open('array2.npy', 'rb') as nfi:
        BFS.mask_array = np.load(nfi)
    BFS.graph_nodes = dd.io.load(cfg.graph_file_n)
    BFS.graph_edges = dd.io.load(cfg.graph_file_e)

    # pathfinding
    BFS().find_path_bfs()


if __name__ == '__main__':
    main(get_args())
