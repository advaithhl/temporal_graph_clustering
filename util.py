import json
import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from community_detector import find_communities
from data_splitter import getnodes
from dirs import CONVERTED_DIR, RESULTS_DIR


def load_result(partno):
    """
    Returns communities of partno, loaded from the results, as nested lists.

    Params
    ------
    partno: part, whose community must be loaded as nested list
    """
    with open(f'{RESULTS_DIR}/communities{partno:03}.txt') as infile:
        l = json.load(infile)
    return l


def flatten_community(community):
    """
    Return a list of all identified communities, removing hierarchy.

    Params
    ------
    community: hierarchichal nested lists representing communities.
    """
    if community:
        flat_communities = []

        def _util(_comm):
            if len(_comm) == 2 and isinstance(_comm[0], list) and isinstance(
                    _comm[1], list):
                _util(_comm[0])
                _util(_comm[1])
            else:
                flat_communities.append(_comm)

        _util(community)
        return flat_communities
    return []


# Credits to https://stackoverflow.com/a/14019260
def random_color():
    """ Returns a random color hex. """
    r = lambda: random.randint(0, 255)
    return '#%02X%02X%02X' % (r(), r(), r())


def visualise(partno):
    """
    Draw the communities of part `partno`.

    Params
    ------
    partno: The part number whose communities are to be visualised.
    """
    matrix_file = f'{CONVERTED_DIR}/part{partno:03}.npy'
    A = np.load(matrix_file)
    A = 1 / A
    A[A == np.inf] = 0
    nodes = getnodes(partno)
    G = nx.from_numpy_matrix(A, create_using=nx.DiGraph)
    G = nx.relabel_nodes(G, dict(enumerate(nodes)))
    communities = flatten_community(find_communities(partno))
    pos = nx.spring_layout(G)
    if not communities:
        return
    for community in communities:
        nx.draw_networkx_nodes(G, pos, nodelist=community,
                               node_color=random_color(), node_size=500)
    nx.draw_networkx_edges(G, pos, edgelist=G.edges, edge_color='#7d8572',
                           alpha=0.6)
    nx.draw_networkx_labels(G, pos, font_size=7)
    fig = plt.gcf()
    fig.set_size_inches(12, 12)
    plt.savefig(f'communities{partno:03}', dpi=300)
