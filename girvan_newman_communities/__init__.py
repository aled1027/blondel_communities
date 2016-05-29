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
                #print("Moving node {} from communmity {} to community {}"\
                #      .format(node, old_community, best_com))
                was_changed_local = True
                was_changed_global = True

            # Update community and which_community data-structures
            which_community[node] = best_com
            communities[best_com].append(node)
            if not communities[old_community]:
                communities.pop(old_community, None)
    return was_changed_global, communities

def phase2(graph, communities):
    """
    Build a new graph whose nodes are now communities found during the first phase
    I.e. squashes nodes in a community into a single node, and preserve edges, so that
    edges between nodes in a community become loops, and edges between nodes in two different
    communities become edges between the community-nodes.
    """

    ret_graph = nx.MultiGraph()
    ret_graph.add_nodes_from(communities.keys())
    which_community = {val: key for key, value in communities.items() for val in value}
    for n1, n2 in graph.edges_iter():
        ret_graph.add_edge(which_community[n1], which_community[n2])
    return ret_graph

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

    communities = []
    return communities
