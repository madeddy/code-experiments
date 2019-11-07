#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Test.'''

# pylint: disable=w0511, C0103, C0301, r1710

import os
import argparse
import pickle
from heapq import heappop, heappush
import numpy as np
from math import sqrt
from graphdata.gridsize import gridsize


# def heuristic(cell, goal):
#     return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])
# i_val = abs(source[0] - target[0])
# j_val = abs(source[1] - target[1])
# orth = 1
# diag = sqrt(2) - 2
# orth * (dx + dy) + (diag - 2 * orth) * min(dx, dy)
# orthogonal move is 1; multiply with 1 is pointless


# def find_path_astar(mask_array, graphdict):
#     '''A star search (A*)'''
#     # To get the correct goal coords it must be -2 used. Gridsize is given
#     # with e.g. 20x20, but counts from 0 to 19. To get 18x18(goal coords)
#     # we need to do 20 -2 here.
#     # start, goal = (1, 1), (len(mask_array) - 2, len(mask_array[0]) - 2)
#     start, goal = (1, 1), (gridsize[0] - 2, gridsize[1] - 2)
#     print(f'ST: {start} GO: {goal}')
#     pr_queue = []
#     heappush(pr_queue, (0 + heuristic(start, goal), 0, '', start))
#     visited = set()
#
#     while pr_queue:
#         _, cost, path, current = heappop(pr_queue)
#         print(f'Heuristic_cost: {_} cost: {cost}')
#         if current == goal:
#             # print('A * solution return: ', path)
#             # # return path
#             save_path(path)
#         if current in visited:
#             continue
#         visited.add(current)
#
#         for neighbour, dir in graphdict[current]:
#             heappush(pr_queue, (cost + heuristic(neighbour, goal),
#                                 cost + 1, f'{path} {dir}', neighbour))
#
#     return 'ERROR: No path to goal found!'

class GraphPathSearch(object):
    '''Class for all graph building related functionality.'''

    def __init__(self, graphdict, start, goal):
        self.graph = graphdict
        self.start = start
        self.goal = goal
        self.explored = {}
        self.path = []

        # self.x_sg = self.start[0] - self.goal[0]
        # self.y_sg = self.start[1] - self.goal[1]

    def heuristic(self, source, target):
        '''
        Heuristic func for 8-direction movement.
        The formula for diagonal distance:
        orth * (dx + dy) + (diag - 2 * orth) * min(dx, dy)
        orth = 1
        diag = sqrt(2) - 2
        Our orthogonal move cost is 1; multiply with 1 is pointless
        '''
        diag = -0.5857864376269049
        x_dif = abs(source[0] - target[0])
        y_dif = abs(source[1] - target[1])
        return (x_dif + y_dif) + diag * min(x_dif, y_dif)
        #
        # x_cg = self.current[0] - self.goal[0]
        # y_cg = self.current[1] - self.goal[1]
        # xy_cross = abs(x_cg * self.y_sg - y_cg * self.x_sg)
        # heur += xy_cross * 0.001

    def a_star_pathsearch(self):
        '''A-star search'''

        frontier = []
        heappush(frontier, (0, self.start))
        self.explored = {self.start: None}
        cur_cost = {self.start: 0}

        while frontier:
            current = heappop(frontier)[1]

            if current == self.goal:
                break

            # instead node_dir could the wheight be taken from there
            for nxt_node, _node_dir in self.graph[current]:
                # replace the + 1/heur. in the next line with wheight costs
                new_cost = cur_cost[current] + self.heuristic(current, nxt_node)
                if nxt_node not in cur_cost or new_cost < cur_cost[nxt_node]:
                    cur_cost[nxt_node] = new_cost
                    priority = new_cost + self.heuristic(nxt_node, self.goal)
                    # print(f'new_cost: {new_cost}  prio: {priority}')
                    heappush(frontier, (priority, nxt_node))
                    self.explored[nxt_node] = current

        self.reconstruct_path()
        return self.path, cur_cost

    def reconstruct_path(self):
        '''
        This reconstructs the path from the explored list of the a_star_search
        and returns it.
        '''
        cur_node = self.goal
        while cur_node != self.start:
            self.path.append(cur_node)
            cur_node = self.explored[cur_node]
        self.path.append(self.start)  # optional
        self.path.reverse()  # optional


def save_path(path):
    '''This writes the found path to a file.'''
    with open('graphdata/pathsearch_sol.txt', 'w') as nfi:
        print('A* solution return: ', path, file=nfi)


def get_args():
    '''This is the parser function'''
    def valid_file(infilename):
        '''Help function to test the given string for the infilename.'''
        if os.path.isfile(infilename):
            if not infilename.endswith('.pickle'):
                raise parser.error('Input must be a pickled file.')
            return infilename
        else:
            raise parser.error('Input file not found.')

    parser = argparse.ArgumentParser(description='Finds path from a source point to a target in the stored graph.')
    parser.add_argument('graph_file', action='store', type=valid_file,
                        metavar='Graph file',
                        help='File with graph for processing.')
    return parser.parse_args()


def main(cfg):
    '''main func'''
    # array spacesaving in np file; re-usable
    # with open('control/maskarray.npy', 'rb') as nfi:
    #     mask_array = np.load(nfi)
    # graphdict = dd.io.load(cfg.graph_file)
    with open(cfg.graph_file, 'rb') as nfi:
        graphdict = pickle.load(nfi)

    # pathfinding
    # find_path_bfs(mask_array, graphdict)
    # find_path_astar(mask_array, graphdict)

    import time
    t = time.process_time()
    start, goal = (1, 1), (gridsize[0] - 2, gridsize[1] - 2)
    gps = GraphPathSearch(graphdict, start, goal)

    found_path, cost = gps.a_star_pathsearch()

    # found_path = reconstruct_path(explored, start, goal)

    print(time.process_time() - t)

    save_path(found_path)
    # print(found_path, cost)


if __name__ == '__main__':
    main(get_args())
