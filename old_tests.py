import numpy as np
# from community.detect import get_num_stubs, get_adjacency_matrix, get_initial_S

def modularity(A, S):
    """
    computes modularity, Q, where Q = 1/2m * Tr(S^t B S)
    """
    B = get_B(A)
    num_stubs = get_num_stubs(A)
    return float(1 / num_stubs) * np.trace(np.dot(np.transpose(S), np.dot(B,S)))

def get_B(A):
    """
    make B, the modularity matrix, which has dimensions num_nodes by num_nodes.
    B[i,j] = A[i,j] - ((k_i * k_j) / (2m))
    where m is the number of edges (2m = num_stubs)
    and where A is adjacency matrix and k_i is degree.
    """

    def edge_deg(node_idx):
        return np.sum(A[node_idx])

    num_stubs = get_num_stubs(A)
    num_nodes = A.shape[0]
    B = np.zeros((num_nodes, num_nodes))
    for i, row in enumerate(B):
        for j in range(i+1):
            B[i,j] = B[j,i] = A[i,j] - float((edge_deg(i) * edge_deg(j)) / (num_stubs))
    return B

def get_test_initial_S(which_set, num_nodes):
    S = None
    if which_set == 'generic':
        S = np.zeros((num_nodes, num_nodes))
        np.fill_diagonal(S, 1)
    elif which_set == 'wikipedia':
        S = np.zeros((num_nodes, 3))
        a = [1,0,0]
        b = [0,1,0]
        c = [0,0,1]
        for i, _ in enumerate(S):
            if i in [0,1,2]:
                S[i] = a
            elif i in [3,4,5]:
                S[i] = b
            else:
                S[i] = c
    elif which_set == 'tester':
        S = np.zeros((6,2))
        S[1,0] = 1
        S[2,0] = 1
        S[3,1] = 1
        S[4,1] = 1
        S[5,1] = 1
    else:
        raise RuntimeError('no such condition %s' % which_set)
    return S

def get_test_adj_dict(which_dict):
    if which_dict == 'wikipedia':
        # from the wikipedia on modularity
        adj_dict = {
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
        return adj_dict
    elif which_dict == 'tester':
        adj_dict = {
                1: [2,3,4],
                2: [1,3],
                3: [1,2],
                4: [1,5,6],
                5: [4,6],
                6: [4,5]
                }
        return adj_dict
    else:
        raise RuntimeError('%s is not a set we have' % which_dict)

