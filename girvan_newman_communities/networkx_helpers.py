"""Utilty functions for working with networkx"""

from __future__ import with_statement, print_function, generators
import networkx as nx
import community_louvain as com_l
import community_girvan_newman.detect as com_gn

def find_shortest_paths(graph, out_filename, sources, targets, k_paths):
    """ Use pathlinker to find shortest paths

    Args:
        graph: a networkx graph
        out_filename: file to print paths to (is a temporary file)
        sources: a list of source nodes
        targets: a list of target nodes
        k_paths: number of shortest paths to find

    Returns:
        List of networkx graphs, which should be thought of as paths.
        If sources are not connect to targets, then returns empty list.
    """
    assert(k_paths > 0)
    edgelist_filename = out_filename + "edgelist.temp"
    srctgt_filename = out_filename + "srctgt.temp"
    nx.write_edgelist(graph, edgelist_filename)

    with open(srctgt_filename, 'w') as f:
        for node in graph.nodes():
            if node in sources:
                f.write(str(node) + '\tsource\n')
            elif node in targets:
                f.write(str(node) + '\ttarget\n')

    s = "python PathLinker/PathLinker.py {} {} -o {} --write-paths --k-param={}"\
            .format(edgelist_filename, srctgt_filename, out_filename, k_paths)
    try:
        os.system(s)
        return read_paths(out_filename + "k_100-paths.txt")
    except Exception as e:
        print(e)
        return []


def get_adj_dict(graph):
    """ returns adjacency dictionary of graph
    """
    ret_dict = {}
    for node in graph:
        ret_dict[node] = graph.neighbors(node)
    return ret_dict

def get_communities(graph):
    """returns list of communities"""
    return get_gn_communities(graph)
    #return get_louv_communities(graph)

def get_louv_communities(graph):
    """returns list of communities according to louvain algorithm"""
    # "node: community" where community is an integer between 0 and len(com_dict) - 1
    com_dict = com_l.best_partition(graph)

    """convert com_dict to list format"""
    num_communities = len(set(com_dict.values()))
    com_list = [[] for _ in range(num_communities)]
    for node, com in com_dict.iteritems():
        com_list[com].append(node)
    return com_list


def get_gn_communities(graph):
    """ returns list of communities according
    to the girvan-newman algorithm
    """
    adj_dict = get_adj_dict(graph)
    detector = com_gn.CommunityDetector(adj_dict)
    return detector.run()

def remove_nodes(graph, remove_set):
    """removes nodes specified in remove_set from graph
    """
    for node in remove_set:
        try:
            graph.remove_node(node)
        except:
            pass
    return graph

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

def path_distance(p1, p2):
    """The distance between two paths p1 and p2.
    Returns number of edges shared between two paths divided by size of union
    """

    num_intersect_nodes = float(len(set(p1.nodes()).intersection(set(p2.nodes()))))
    tot_nodes = float(len(set(p1.nodes()).union(set(p2.nodes()))))
    return 1.0 - (num_intersect_nodes / tot_nodes)

def rgb_to_hex(rgb):
    """Given an RGB value (0-255), return the HEX equivalent
    """
    return '#%02x%02x%02x' % rgb

def generate_colors(n):
    """Generate n colors and returns a list in hex format
    http://www.mc706.com/tip_trick_snippets/1/python-color-wheel/
    """
    import colorsys

    # use HSV colors to find equidistant colors on color wheel
    hsv_tuples = [(x*1.0 / n + .5, 1.0, 1.0) for x in range(n)]
    rgb_tuples = [colorsys.hsv_to_rgb(*x) for x in hsv_tuples]
    rgb_set = [(int(r*255), int(g*255), int(b*255)) for r, g, b in rgb_tuples]
    hex_set = ["#%02x%02x%02x" % tup for tup in rgb_set]

    # reorder list so each subsequent color is farthest distance from adjacent colors
    return_set = []
    i = 0
    while len(hex_set) > 0:
        if i % 2 == 0:
            return_set.append(hex_set.pop(0))
        else:
            return_set.append(hex_set.pop())
    return return_set

def postToGS(alignededges, overlaps, leftcoords, graphid):
    """Post graph to graphspace
    """

    import graphspace_interface as interface

    maxleftcoord = max([leftcoords[c] for c in leftcoords])
    minleftcoord = min([leftcoords[c] for c in leftcoords])
    for c in leftcoords:
        leftcoords[c] = int(float(leftcoords[c]-minleftcoord)\
                / float(maxleftcoord-minleftcoord)*255)
    user = 'annaritz@vt.edu'
    password = 'platypus'
    group = 'SVLocalAssembly'
    outfile = graphid+'.json'

    #Graph 1 (tmp): read edges in from a file.
    #Take the first two columns of the file as the edges.

    #Make a directed graph NetworkX object.
    #A directed graph will work even if we
    #want to show an undirected graph, since
    #each edge has a "directed" attribute that
    #determines whether the edge is drawn with an
    #arrow or not.
    graph = nx.DiGraph(alignededges, directed=False)

    for n in graph.nodes():
        label = '%s' % (n)
        interface.add_node_label(graph, n, label)
        interface.add_node_wrap(graph, n, 'wrap')
        interface.add_node_color(graph, n, rgb_to_hex((0, leftcoords[n], 255-leftcoords[n])))
        interface.add_node_shape(graph, n, 'ellipse')
        interface.add_node_height(graph, n, None, label)
        interface.add_node_width(graph, n, None, label)

    trueedges = [[u, v] for u, v, t in overlaps]
    for t, h in graph.edges():
        interface.add_edge_directionality(graph, t, h, False)
        if [t, h] in trueedges or [h, t] in trueedges:
            # true edges are blue
            #print 'Blue'
            interface.add_edge_color(graph, t, h, '#6666FF')
        else:
            # false edges are black
            interface.add_edge_color(graph, t, h, '#000000')
        interface.add_edge_width(graph, t, h, 2)

    metadata = {'description': 'example1', 'title': graphid, 'tags': []}
    print(graph, graphid, outfile, user, password, metadata)
    interface.postGraph(graph, graphid, outfile=outfile, user=user,\
            password=password, metadata=metadata)
    if group != None:
        interface.shareGraph(graphid, user=user, password=password, group=group)
    return

