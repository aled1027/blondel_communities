from __future__ import (absolute_import, division, print_function, unicode_literals)
import copy
import numpy as np
import networkx as nx
from pprint import pprint

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
    The change in modularity from moving isolated node node in community community.
    For best communities, want to maximize modularity.
    Q is another name for modularity.

    delta_Q = [((sigma_in + k_i_in)/(2*m)) - ((sigma_tot + k_i)/ (2 * m))^2
            - [(sigma_in / 2 * m) - (sigma_tot / 2 * m)^2 - (k_i / 2 * m)^2]

    sigma_in = sum of weights of edges inside community
    sigma_tot = sum of weights of edges indicident to nodes in C
    k_i = sum of weights of edges incident to node
    k_i_in = sum of weights of edges between node and community members
    m = sum of all weights in network
    """

    # Can make assumption that node is not in target community
    assert(node not in communities[community])
    m = graph.number_of_edges()
    sigma_in = graph.subgraph(communities[community]).number_of_edges()
    sigma_tot = sigma_in + sum(graph.number_of_edges(com_node, nbr) \
            for com_node in communities[community] \
            for nbr in graph.neighbors_iter(com_node) \
            if nbr not in communities[community])
    a_ij = sum(graph.number_of_edges(com_node) for com_node in communities[community])
    k_i_in  = sum(graph.number_of_edges(node, com_node) for com_node in communities[community])
    k_i = graph.degree(node)

    delta_q_left = (((sigma_in + k_i_in) / (2 * m)) - ((sigma_tot + k_i) / (2 * m))**2)
    delta_q_right = (sigma_in / (2 * m)) - ((sigma_tot / (2 * m))**2) - ((k_i / (2 * m))**2)
    delta_q = delta_q_left - delta_q_right

    return delta_q

def phase1(graph):
    """Performs phase 1 of algorithm
    Loops over each node
        Loops over each neighbor
            Find delta_mod of moving node into nbr's community
        Move node into that community
    """

    # initialize each node to its own community
    communities = {i: [node] for i, node in enumerate(graph.nodes_iter())}
    which_community = {val: key for key, value in communities.items() for val in value}
    was_changed_global = False
    was_changed_local = True

    # Continue loop until no nodes change their community
    while was_changed_local:
        was_changed_local = False
        for node in graph.nodes_iter():

            # Isolate node, use current community as baseline for comparison
            old_community = which_community[node]
            communities[old_community].remove(node)
            best_delta = delta_modularity(graph, communities, node, old_community)
            best_com = old_community

            # Loop through neighbors to find best community (if better than old one)
            for nbr in graph.neighbors_iter(node):
                if nbr == node or node in communities[which_community[nbr]]:
                    continue
                # compute delta_mod of node putting node into nbr's community
                delta_q = delta_modularity(graph, communities, node, which_community[nbr])
                if best_delta < delta_q:
                    best_delta = delta_q
                    best_com = which_community[nbr]

            # put node in the community
            if best_com != old_community:
                print("Moving node {} from communmity {} to community {}"\
                      .format(node, old_community, best_com))
                was_changed_local = True
                was_changed_global = True

            # Update community and which_community data-structures
            which_community[node] = best_com
            communities[best_com].append(node)
            if not communities[old_community]:
                communities.pop(old_community, None)
    return was_changed_global, communities

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
