from __future__ import (absolute_import, division, print_function, unicode_literals)
import copy
import numpy as np
import networkx as nx

def wikipedia_graph():
    return nx.Graph()

def get_communities(graph):
    return []

class CommunityDetector(object):
    def __init__(self, adj_dict):
        """
        adj_dict is an adjacency list of node: neighbors.
        make sure adj_dict has no duplicates.

        num_stubs = 2 * number of edges.
        In this algorithm, we think in terms of stubs
        instead of in terms of edges.

        node_comm_associations is a list containing
        jwhich nodes are in which communities
        e.g say node 1 and 2 are in a community and node 3 in a diff. community
        then node_comm_associations = [[1,2], [3]]
        """
        self.adj_dict = {k : list(set(v)) for (k,v) in adj_dict.items()}

        # flatten the adjacency dict to get a list of all nodes.
        flat_vals = [x for xs in adj_dict.values() for x in xs]
        self.nodes = sorted(list(set(list(adj_dict.keys()) + flat_vals)))
        self.A = self.get_adjacency_matrix(self.nodes, directed=False)

        # initialize S such that each node is in its own community
        self.S = np.zeros((len(self.nodes), len(self.nodes)))
        np.fill_diagonal(self.S, 1)

        self.node_comm_associations = [[i] for i in range(len(self.nodes))]
    @property
    def num_stubs(self):
        return np.sum(self.A)

    def get_adjacency_matrix(self, nodes, directed=False):
        """
        converts an adjacency dictionary into a symmetric adjacency matrix,
        if the directed flag is False, otherwise not.
        """
        A = np.zeros((len(nodes), len(nodes)))
        for i, _ in enumerate(A):
            for j in range(i+1):
                node1 = nodes[i]
                node2 = nodes[j]
                flag = False
                if node1 in self.adj_dict and node2 in self.adj_dict[node1]:
                        flag = True
                elif node2 in self.adj_dict and node1 in self.adj_dict[node2]:
                        flag = True
                if not directed:
                    A[i,j] = A[j,i] = 1 if flag else 0
                else:
                    if flag:
                        A[i,j] = 1
        return A

    def delta_modularity(self, node_i, community):
        """
        formula:
        sum over all nodes j in community
        (1/num_stubs) * (2 * (A_ij - (k_i * k_j) / num_stubs) + (A_ii - (k_i*k_i)/num_stubs))

        returns the value of adding node_i to community
        simply multiply the value by negative 1 to get the value
        of removing node i from the community
        """

        k_dict = {}
        def k(node_idx):
            """
            returns k_i, the number of stubs that a node has, aka its outdegree
            """
            return np.sum(self.A[node_idx])
            # if node_idx in k_dict:
            #     return k_dict[node_idx]
            # else:
            #     val =  np.sum(self.A[node_idx])
            #     k_dict[node_idx] = val
            #     return val

        # loop over members of community and get cumulative sum
        cum_sum = 2 * sum(self.A[node_i,j] - ((k(node_i) * k(j)) / self.num_stubs)\
                          for j in np.nonzero(self.S[:,community])[0])
        cum_sum += self.A[node_i, node_i] - ((k(node_i)**2) / self.num_stubs)

        # add in value for node_i
        cum_sum = cum_sum / self.num_stubs
        return cum_sum

    def phase1(self):
        """
        phase1 takes the graph A and S and returns a better S
        phase2 then takes S and squashes communities, returning a new S and A

        S[i,c] = 1 if node i belongs to community c else 0
        """
        # loop over nodes, finding a local max of Q
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

    def phase2(self):
        """
        squash communities
        """

        #print('    starting phase2')
        # So S = num_nodes by num_communities
        # so we are going to have

        # define node_comm_associations
        num_communities = self.S.shape[1]
        new_A = np.zeros((num_communities, num_communities))

        # fill new_A
        for i, row in enumerate(new_A):
            for j, _ in enumerate(row):
                # get set of nodes in community i and
                comm_i_nodes = np.nonzero(self.S[:,i])[0]
                comm_j_nodes = np.nonzero(self.S[:,j])[0]

                # get number of edge intersections
                edge_sum = 0
                for comm_i_node in comm_i_nodes:
                    for comm_j_node in comm_j_nodes:
                        edge_sum += self.A[comm_i_node, comm_j_node]
                new_A[i,j] = edge_sum
            # I think this should be commented out
            new_A[i,i] = 0.5 * new_A[i,i]

        # update node_comm_associations
        new_node_comm_associations = []

        # loop over columns
        self.S = np.transpose(self.S)
        for row in self.S:
            nodes = np.nonzero(row)[0]
            # combine old nodes of node_comm_associations
            temp_list = [x for y in nodes for x in self.node_comm_associations[y]]
            new_node_comm_associations.append(temp_list)

        # also need a list of all original nodes associated with each community
        new_S = np.zeros((num_communities, num_communities))
        for i, _ in enumerate(new_S):
            new_S[i,i] = 1

        self.A = new_A
        self.S = new_S
        self.node_comm_associations = new_node_comm_associations

        return self.A, self.S, self.node_comm_associations

    def run(self, node_names=True, verbose=False):
        counter = 0
        while True:
            #print ('go counter: %d' % counter)
            counter+=1
            wasChanged = self.phase1()
            if wasChanged == False:
                break
            self.phase2()
        self.communities = copy.deepcopy(self.node_comm_associations)

        if node_names:
            self.communities = [
                list(map(
                    lambda x: self.nodes[x],
                    community))
                for community in self.communities
            ]

        if verbose:
            for c in self.communities:
                print(c)
        return self.communities



