#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''A* search implemenation over a previously constructed graph of the
 walkable area of a map.'''

# pylint: disable=w0511, C0103, C0301, r1710


import sys
from pathlib import Path
import argparse
from heapq import heappop, heappush
import dill as pickle
from graphdata.graphinfo import gridsize

__title__ = 'astar_search'
__license__ = 'MIT'
__author__ = 'madeddy'
__status__ = 'Development'
__version__ = '0.15.0-alpha'


class GraphPathSearch:
    '''Class for all graph search related functionality.'''

    diag = -0.5857864376269049

    def __init__(self, graphdict, start, goal):
        self.graph = graphdict
        self.start = start
        self.goal = goal
        self.explored = {}
        self.pathway = []

    def reconstruct_path(self):
        '''This reconstructs the pathway from the explored list of the
           A* search and returns it.'''

        cur_node = self.goal
        while cur_node != self.start:
            self.pathway.append(cur_node)
            cur_node = self.explored[cur_node]
        # These 2 are optional
        self.pathway.append(self.start)
        self.pathway.reverse()

    @classmethod
    def heuristic(cls, source, target):
        '''
        Heuristic func for 8-direction movement. Formula for diagonal
        distance: orth * (dx + dy) + (diag - 2 * orth) * min(dx, dy)
        diag = sqrt(2) - 2
        orth = 1
        Our orthogonal move cost is 1; multiply with 1 is pointless
        '''

        x_dif = abs(source[0] - target[0])
        y_dif = abs(source[1] - target[1])
        return (x_dif + y_dif) + cls.diag * min(x_dif, y_dif)

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
        return self.pathway, cur_cost


def save_path(pathway):
    '''This writes the found pathway to a file.'''
    with open('graphdata/pathsearch_sol.txt', 'w') as nfi:
        print('A* solution return: \n', pathway, file=nfi)


def get_args():
    '''Parses function: Takes just the graph file in and validates her. '''

    def valid_file(infilename):
        '''Helper to test the given string for the infilename.'''

        if not Path(infilename).is_file():
            raise parser.error('Input file not found.')
        if Path(infilename).suffix not in '.pickle':
            raise parser.error('Input must be a pickle file.')
        return infilename

    parser = argparse.ArgumentParser(description='Finds path from a source point to a target in the stored graph.')
    parser.add_argument('graph_file', action='store', type=valid_file,
                        metavar='Graph file',
                        help='File with graph for processing.')
    return parser.parse_args()


def main(cfg):
    '''...main function.'''

    with open(cfg.graph_file, 'rb') as nfi:
        graphdict = pickle.load(nfi)

    start, goal = (1, 1), (gridsize[0] - 2, gridsize[1] - 2)
    gps = GraphPathSearch(graphdict, start, goal)

    found_path, cost = gps.a_star_pathsearch()
    save_path(found_path)


if __name__ == '__main__':
    if not sys.version_info >= (3, 6):
        raise ValueError("Python 3.6 or higher needet.")
    main(get_args())
