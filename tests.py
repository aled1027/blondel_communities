from __future__ import print_function

import unittest
import networkx as nx
import blondel_communities as co
import matplotlib.pyplot as plt
from pprint import pprint

class TestStringMethods(unittest.TestCase):
    def test_delta_modularity(self):
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
        graph = nx.MultiGraph(wiki_adj_dict)
        communities = {1: [2,3,10], 2: [4,5,6], 3: [7,8,9]}
        delta_mod = co.delta_modularity(graph, communities, 1, 1)
        self.assertGreater(delta_mod, 0.06)
        self.assertLess(delta_mod, 0.063)

    def test_phase1(self):
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
        graph = nx.MultiGraph(wiki_adj_dict)
        was_changed, communities = co.phase1(graph)

        ideal_communities = {1: [10], 2:[1,2,3], 5: [4,5,6], 8: [7,8,9]}
        self.assertEqual(communities, ideal_communities)

    def test_phase2(self):
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
        graph = nx.MultiGraph(wiki_adj_dict)
        communities = {1: [10], 2:[1,2,3], 5: [4,5,6], 8: [7,8,9]}
        new_graph = co.phase2(graph, communities)

        ideal_edges = [(8, 8), (8, 8), (8, 8), (8, 1), (1, 2), (1, 5),\
                       (2, 2), (2, 2), (2, 2), (5, 5), (5, 5), (5, 5)]
        self.assertEqual(new_graph.edges(), ideal_edges)
if __name__ == '__main__':
    unittest.main()
