"""Blondel Communities library

Blondel Communities is a python library for computing the communities of a graph.

usage:
   >>> import networkx as nx
   >>> import blondel_communities as co
   >>> graph = nx.karate_club_graph()
   >>> communities = co.get_communities(graph)
"""

from .communities import delta_modularity, phase1, phase2, get_communities
