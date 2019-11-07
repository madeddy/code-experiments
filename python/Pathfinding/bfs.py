#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Test.'''

# pylint: disable=w0511, C0103, C0301, r1710

import argparse
# import pprint
# import pickle
# import lzma
from collections import deque
from heapq import heappop, heappush
import deepdish as dd
import numpy as np
from math import sqrt


# def heuristic(cell, goal):
#     return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])
def heuristic(source, goal):
    '''Heuristic diagonal test'''
    # orth = 1
    # diag = sqrt(2) - 2
    diag = -0.5857864376269049
    i_val = abs(source[0] - goal[0])
    j_val = abs(source[1] - goal[1])
    # return orth * (dx + dy) + (diag - 2 * orth) * min(dx, dy)
    # orthogonal move is 1; multiply with 1 is pointless
    return (i_val + j_val) + diag * min(i_val, j_val)


def find_path_astar(mask_array, graphdict):
    '''A star search (A*)'''

    start, goal = (1, 1), (len(mask_array) - 2, len(mask_array[0]) - 2)
    pr_queue = []
    heappush(pr_queue, (0 + heuristic(start, goal), 0, '', start))
    visited = set()

    while pr_queue:
        _, cost, path, current = heappop(pr_queue)

        if current == goal:
            print('A * solution return: ', path)
            return path
        if current in visited:
            continue
        visited.add(current)

        for direction, neighbour in graphdict[current]:
            heappush(pr_queue, (cost + heuristic(neighbour, goal),
                                cost + 1, path + direction, neighbour))


    return 'NO WAY!'


def find_path_bfs(mask_array, graphdict):
    '''Breadth-first search (BFS)'''
    # start, goal = (970, 186), (284, 1393)
    start, goal = (1, 1), (len(mask_array) - 2, len(mask_array[0]) - 2)
    queue = deque([('', start)])

    explored = set()
    # graph = maze2graph(mask_array)

    while queue:
        path, current = queue.popleft()
        # with open('bfs_path.txt', 'a+') as nfi:
        #     print('queue: ', queue, 'path, current: ', path, current, file=nfi)

        if current == goal:
            print('BFS solution return: ', path)
            return path

        if current in explored:
            continue
        explored.add(current)

        for direction, neighbour in graphdict[current]:
            queue.append((path + direction, neighbour))

            # print('path, neighbor: ', path + direction, neighbour)

    return 'Was unable to calculate a way to target coordinate.'


def get_args():
    '''This is the parser function'''
    def valid_h5(infilename):
        '''Help function to test the given string for the infilename.'''
        if infilename.endswith('.h5'):
            for char in ['/', ':', ' ']:
                if char in infilename:
                    raise parser.error('\'{}\' contains unallowed character.'.format(infilename))
            return infilename
        else:
            raise parser.error('Input must be a h5 file.')

    parser = argparse.ArgumentParser(description='Turns a image used as mask into a compressed h5 file with the stored graph.')
    parser.add_argument('graph_file', action='store',# dest='h5file',
                        type=valid_h5, metavar='HDF5 file',
                        help='HDF5 file with graph for processing.')
    return parser.parse_args()


def main(cfg):
    '''main func'''
    # array spacesaving in np file; re-usable
    with open('array_old.npy', 'rb') as nfi:
        mask_array = np.load(nfi)
    # graphdict = dd.io.load(cfg.graph_file)
    graphdict = pickle.load(cfg.graph_file)

    #pathfinding
    # find_path_bfs(mask_array, graphdict)
    find_path_astar(mask_array, graphdict)


if __name__ == '__main__':
    main(get_args())
