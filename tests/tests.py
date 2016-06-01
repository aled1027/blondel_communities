from __future__ import print_function

import unittest
from pprint import pprint
import sys

import networkx as nx
import blondel_communities as co
import matplotlib.pyplot as plt

def get_karate_graph():
    graph = nx.karate_club_graph()
    return graph

def get_wiki_graph():
    wiki_adj_dict = {
                1:  [2,3,10],
                2:  [1,3],
                3:  [1,2],
                4:  [5,6,10],
                5:  [4,6],
                6:  [4,5],
                7:  [8,9,10],
                8:  [7,9],
                9:  [7,8],
                10: [1,4,7],
                }
    graph = nx.Graph(wiki_adj_dict)
    return graph

class TestStringMethods(unittest.TestCase):
    def test_delta_modularity(self):
        graph = get_wiki_graph()
        communities = {1: [2,3,10], 2: [4,5,6], 3: [7,8,9]}
        delta_mod = co.delta_modularity(graph, communities, 1, 1)
        self.assertGreater(delta_mod, 0.06)
        self.assertLess(delta_mod, 0.063)

    def test_karate_phase1(self):
        graph = get_karate_graph()
        was_changed, communities = co.phase1(graph)
        self.assertTrue(was_changed)
        # TODO add an assert on communities

    def test_wiki_phase1(self):
        graph = get_wiki_graph()
        was_changed, communities = co.phase1(graph)
        self.assertTrue(was_changed)

        phase1_communities = {1: [10], 2:[1,2,3], 5: [4,5,6], 8: [7,8,9]}
        self.assertEqual(communities, phase1_communities)

    def test_wiki_phase2(self):
        graph = get_wiki_graph()
        communities = {1: [10], 2:[1,2,3], 5: [4,5,6], 8: [7,8,9]}
        new_graph = co.phase2(graph, communities)

        ideal_edges = [(8, 8), (8, 8), (8, 8), (8, 1), (1, 2), (1, 5),\
                       (2, 2), (2, 2), (2, 2), (5, 5), (5, 5), (5, 5)]
        self.assertEqual(new_graph.edges(), ideal_edges)

    def test_wiki_comm(self):
        graph = get_wiki_graph()
        communities = co.get_communities(graph)
        # TODO finish
        print(communities)

if __name__ == '__main__':
    unittest.main()
