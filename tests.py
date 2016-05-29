from __future__ import print_function

import unittest
import networkx as nx
import girvan_newman_communities as co
import matplotlib.pyplot as plt

class TestStringMethods(unittest.TestCase):
    def test_number_self_loops(self):
        graph = nx.MultiGraph()
        graph.add_edges_from([(1, 1), (1, 2), (2, 2), (2, 2), (2, 2), (2, 1)])
        num_self_loops = co.number_self_loops(graph, 2)
        self.assertEqual(num_self_loops, 3)

    def test_delta_mod2(self):
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
        wiki_graph = nx.MultiGraph(wiki_adj_dict)
        communities = {1: [2,3,10], 2: [4,5,6], 3: [7,8,9]}
        delta_mod = co.delta_modularity(wiki_graph, communities, 1, 1)
        self.assertGreater(delta_mod, 0.06)
        self.assertLess(delta_mod, 0.063)

    def test_basic(self):
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
        wiki_graph = nx.MultiGraph(wiki_adj_dict)

        ideal_communities = {1: [1,2,3,10], 2: [4,5,6], 3: [7,8,9]}
        wiki_communities = []

        was_changed = co.phase1(wiki_graph)
        #communities = co.get_communities(wiki_graph)
        #self.assertEqual(communities, wiki_communities)

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()
