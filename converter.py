from os import mkdir
from subprocess import run
from time import time

import numpy as np

from data_splitter import numbers, getnodes
from dirs import CONVERTED_DIR, SPLIT_DIR
from temporal_graph import TemporalGraph


def convert(temporal_graph, static_node_list):
    """
    Convert a temporal graph into a static graph.

    Using the average temporal proximity of 2 nodes as a distance metric between
    them, converts the temporal_graph given to static graph. Note that both the
    temporal graph must have nodes that are versions of static_node_list.
    Returns a weighted adjacency matrix.

    Params
    ------
    temporal_graph   : the TemporalGraph object to convert.
    static_node_list : list of all the nodes whose versions exist in
                       `temporal_graphs`
    """
    dimension = len(static_node_list)
    final = np.full((dimension, dimension), fill_value=np.inf)
    full_start = time()
    for row, i in enumerate(static_node_list):
        for col, j in enumerate(static_node_list):
            final[row][col] = temporal_graph.average_temporal_proximity(i, j)
    full_stop = time()
    print(f'Completed in {full_stop - full_start} seconds')
    return final


def convert_all(data_dir=SPLIT_DIR, out_dir=CONVERTED_DIR):
    """
    Build a temporal graph of each part and convert it into a static graph.
    Store each converted array as `npy` files inside the `converted` folder.

    Params
    ------
    data_dir: input directory containing temporal data of each part.
    out_dir: output directory to save the converted parts.
    """
    # Delete old directory and made new directory.
    result = run(['rm', '-r', out_dir])
    if result.returncode == 0:
        print('Removed old converted files.')
    mkdir(out_dir)
    for i in numbers():
        filename = data_dir + f'/part{i:03}.txt'
        t = TemporalGraph(filename)
        t.build()
        static_nodes = getnodes(i)
        print(f'Number of temporal nodes in part{i:03}: {len(t.graph.nodes)}')
        print(f'Number of static nodes in part{i:03}: {len(static_nodes)}')
        static_adjacency = convert(t, static_nodes)
        np.save(f'{out_dir}/part{i:03}', static_adjacency)
        print(f'Saved part{i:03}\n')


if __name__ == '__main__':
    convert_all()
