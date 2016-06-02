#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
communities.py
~~~~~~~~
This module computes the communities of a graph.
"""

from __future__ import (absolute_import, division, print_function, unicode_literals)
import networkx as nx

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

    TODO can remove communities and community from arguments, and just have community as list of nodes in target community.
    """

    # Can make assumption that node is not in target community
    #assert node not in communities[community]
    m = graph.number_of_edges()
    sigma_in = graph.subgraph(communities[community]).number_of_edges()

    sigma_tot = sigma_in + \
                sum(
                    graph.number_of_edges(com_node, nbr) \
                    for com_node in communities[community] \
                    for nbr in graph.neighbors_iter(com_node) \
                    if nbr not in communities[community]
                )

    k_i_in = sum(graph.number_of_edges(node, com_node) for com_node in communities[community])
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
    communities = {i: [node] for i, node in enumerate(graph)}
    which_community = {val: key for key, value in communities.items() for val in value}
    was_changed_global = False
    was_changed_local = True

    # Continue loop until no nodes change their community
    max_iters = nx.number_of_nodes(graph)
    counter = 0
    while was_changed_local and counter < max_iters:
        counter += 1
        was_changed_local = False
        for node in graph:
            # use current community as baseline for comparison
            best_com = old_community = which_community[node]
            best_delta = -1 * delta_modularity(graph, communities, node, old_community)
            communities[old_community].remove(node) # isolate node

            # Loop through neighbors to find best community (if better than old one)
            for nbr in graph.neighbors_iter(node):
                if nbr == node or node in communities[which_community[nbr]]:
                    continue

                # compute change in modularity of putting node into nbr's community
                delta_q = delta_modularity(graph, communities, node, which_community[nbr])
                if delta_q > best_delta:
                    best_delta = delta_q
                    best_com = which_community[nbr]

            # put node into best community
            if best_com != old_community:
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
    Returns the communities of the graph by running the Blondel et al. algorithm.

    In summary, alternates between phase1 and phase2 until the graph goes unchanged.

    Parameters
    ----------
    graph : networkx Graph
        Graph to find communities of
    Returns
    -------
    communities : list
        A list of lists. Each sublist is a list of nodes which part of a community.
    """
    # TODO improve and clean this up

    # Force graph to be a multigraph
    graph = nx.MultiGraph(graph)

    # node representation keeps track of which nodes have been squished into communities
    # So if nodes 1 and 2 are squashed into community 3, then com_node_dict = {3: [1,2]}
    com_node_dict = {node: [node] for node in graph}
    while True:
        was_changed, communities = phase1(graph)

        # break if no nodes moved communities in phase1
        if not was_changed:
            break

        # update com_node_dict based on the received communities
        # essentially, we map over the values of the communities, transforming
        # each "node" into the actual nodes that it represents
        _flatten = lambda li: [item for sublist in li for item in sublist]
        _update = lambda node: com_node_dict[node]
        com_node_dict = {com: _flatten(map(_update, nodes))\
                for com, nodes in communities.items()}

        # run phase2 and loop
        graph = phase2(graph, communities)

    return list(com_node_dict.values())
