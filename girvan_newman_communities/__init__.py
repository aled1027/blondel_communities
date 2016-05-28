from __future__ import (absolute_import, division, print_function, unicode_literals)
import copy
import numpy as np
import networkx as nx

def merge_nodes(graph, merge_set, new_node):
    """
    Squahes all nodes in merge_set into a node called new_node
    Works for digraphs where all edges go in both directs,
    because that works best for PathLinker
    """
    graph.add_node(new_node)
    for node in merge_set:
        for edge in graph.edges(node):
            if edge[0] == node:
                graph.add_edge(new_node, edge[1])
                graph.add_edge(edge[1], new_node)
            elif edge[1] == node:
                graph.add_edge(edge[0], new_node)
                graph.add_edge(new_node, edge[0])

    # remove merge_set nodes
    for node in merge_set:
        if node in graph.nodes():
            graph.remove_node(node)
    return graph

def delta_modularity(graph, communities, node, community):
    """
    formula:
    sum over all nodes j in community
    (1/num_stubs) * (2 * (A_ij - (k_i * k_j) / num_stubs) + (A_ii - (k_i*k_i)/num_stubs))

    returns the value of adding node_i to community
    simply multiply the value by negative 1 to get the value
    of removing node i from the community
    """

    ret_val = 0
    # (2 * (A_ij - (k_i * k_j) / num_stubs)

    A_ij = sum(graph.number_of_edges(com_node) for com_node in communities[community])
    k_i_in  = sum(graph.number_of_edges(node, come_node) for com_node in communities[community])
    k_i = graph.degree(node)
    return 0




def number_self_loops(graph, node):
    """returns number of self loops of node"""
    return graph.number_of_edges(node, node)

def phase1(graph):
    was_changed = False
    for node in graph.nodes_iter():
        for nbr in graph.neighbors_iter(node):
            pass
    return was_changed

def old_phase1():
    # S[i,c] = 1 if node i belongs to community c else 0
    counter = 0
    wasChangedInFunction = False
    wasChangedInLoop = True
    while wasChangedInLoop:
        wasChangedInLoop = False
        #print('    phase1 counter: %d' % counter)
        counter+=1

        # loop over each node
        # this for loop takes fooooorever
        for i, S_row in enumerate(self.S):
            cur_community = best_community = np.nonzero(S_row)[0][0]

            # remove node from its former community
            self.S[i, cur_community] = 0

            best_delta_Q = self.delta_modularity(i, cur_community)

            # find best delta Q for all other communities
            for j, _ in enumerate(S_row):
                delta_Q = self.delta_modularity(i, j)
                if delta_Q > best_delta_Q:
                    best_delta_Q = delta_Q
                    best_community = j
            if cur_community != best_community:
                wasChangedInLoop= True
                wasChangedInFunction= True
            self.S[i, best_community] = 1

    # remove columns that are all zeros via a mask
    # this removes irrelevant communities
    self.S = np.transpose(self.S)
    self.S = np.transpose(self.S[(self.S!=0).any(axis=1)])
    return wasChangedInFunction


def phase2():
    return None

def get_communities(graph):
    """
    Main function of package.
    Alternates between phase1 and phase2 until the graph goes unchanged.
    """

    communities = None
    while True:
        was_changed = phase1()
        if was_changed == False:
            break
        phase2()

    #communities = copy.deepcopy(node_comm_associations)
    communities = []
    return communities
