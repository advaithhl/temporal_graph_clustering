import json
import warnings
from os import mkdir
from subprocess import run

import numpy as np

from data_splitter import getnodes
from dirs import CONVERTED_DIR, RESULTS_DIR

Q = 0


def maximise_modularity(B):
    """
    Split into two communities and return those and modularity justifying the
    split.

    Params
    ------
    B : a modularity matrix.
    """
    w, v = np.linalg.eig(B + B.T)
    community1 = np.where(np.asarray(v[:, np.argmax(w)] > 0).reshape(-1))[0]
    community2 = np.where(np.asarray(v[:, np.argmax(w)] <= 0).reshape(-1))[0]
    NODE_COUNT = B.shape[0]
    s = np.ones(NODE_COUNT).reshape(-1, 1)
    s[community2] = -1
    global m
    q = np.dot(s.T, B + B.T)
    q = np.dot(q, s)
    q /= 4 * m
    return community1, community2, np.asscalar(q)


def find_subcommunities(labels, community):
    """
    Recursively find natural sub communities in community.

    Repeatedly split each community into 2 communities each, whenever gain in
    modularity is possible. Use the split community indices for recursive
    calls, and return labels in case a split doesn't yield a modularity gain.

    Params
    ------
    labels    : str values of nodes that the indices of community correspond to.
    community : the indices of B matrix, which forms a community.
    """
    global B
    B_g = np.asmatrix(B[np.ix_(community, community)])
    np.fill_diagonal(B_g, np.diag(B_g) - np.sum(B_g, axis=1).reshape(-1))
    community1, community2, delta_q = maximise_modularity(B_g)
    if delta_q > 1e-10:
        global Q
        Q += delta_q
        sub_communities1 = find_subcommunities(labels[community1], community1)
        sub_communities2 = find_subcommunities(labels[community2], community2)
        return [sub_communities1, sub_communities2]
    else:
        return list(labels)


def find_communities(partno, converted_dir=CONVERTED_DIR):
    """ Recursively find all natural communities of a part. """
    matrix_file = f'{converted_dir}/part{partno:03}.npy'
    A = np.load(matrix_file)
    A = 1 / A
    A[A == np.inf] = 0
    NODE_COUNT = A.shape[0]
    k_in = np.sum(A, axis=0).reshape(1, NODE_COUNT)
    k_out = np.sum(A, axis=1).reshape(NODE_COUNT, 1)
    global m
    m = np.sum(A) / 2
    if m:
        global B
        B = A - (k_out * k_in) / m
        l = np.array(getnodes(partno))
        global Q
        community1, community2, Q = maximise_modularity(B)
        if Q > 0:
            sub_communities1 = find_subcommunities(l[community1], community1)
            sub_communities2 = find_subcommunities(l[community2], community2)
            return [sub_communities1, sub_communities2]
        else:
            print(f'- No community structure detected in {matrix_file}')
    else:
        print(f'- There are no edges in {matrix_file}. Skipping...')
    return []


def find_all_communities(out_dir=RESULTS_DIR, in_dir=CONVERTED_DIR):
    """ Find communities of all parts. """
    warnings.filterwarnings('ignore')
    result = run(['rm', '-r', out_dir])
    if result.returncode == 0:
        print('Removed old results.')
    mkdir(out_dir)
    modularities = np.zeros(194)
    for i in range(1, 195):
        final_communities = find_communities(i, in_dir)
        if final_communities:
            filename = f'{out_dir}/communities{i:03}.txt'
            with open(filename, 'w') as comm_file:
                json.dump(final_communities, comm_file)
                print(f'+ Wrote communities to {filename}')
        modularities[i - 1] = Q
    np.save(f'{out_dir}/modularities', modularities)


if __name__ == '__main__':
    find_all_communities()
