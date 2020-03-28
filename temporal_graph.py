from itertools import dropwhile
from math import inf

import networkx as nx
import numpy as np


class TemporalGraph:
    """
    Representation of a temporal graph.

    Temporal data must be given in the form of a file which has data in the form
    of `(src, dst, time)` to build a temporal graph. Temporal graph is built as
    described in https://arxiv.org/ftp/arxiv/papers/0807/0807.2357.pdf
    """

    def __init__(self, filename):
        self.filename = filename
        self._versions = {}
        self._information = list(self._get_data())
        self.last_seen = {}
        self._graph = None

    def _get_data(self):
        """ Yield each line of dataset one at a time. """
        with open(self.filename, 'r') as ifile:
            for f in ifile:
                f = f.strip().split(' ')
                yield (f[0], f[1], int(f[2]))

    @property
    def information(self):
        """ Return the data read from `filename` """
        return self._information

    @property
    def graph(self):
        """ Return the built graph (builds anew, if doesn't exist) """
        if not self._graph:
            self.build()
        return self._graph

    def build(self, max_time=inf):
        """
        Build a temporal graph until the max_time message from the dataset.

        Iterates through (src, dst, time) tuples and creates an zero weight edge
        between the temporal nodes (src, time) and (dst, time). Adds a
        special edge from the previous version of src and/or dst to current src
        and/or dst, with a weight corresponding to time difference between
        current time and last seen time of src and/or dst. Also updates the last
        seen of src and dst.

        Params
        ------
        max_time : time upto which the temporal graph must be built.
        """
        g = nx.DiGraph()
        for m in self.information:
            src = m[0]
            dst = m[1]
            time = m[2]
            if time <= max_time:
                g.add_edge((src, time), (dst, time), weight=0)
                if src in self.last_seen:
                    last_seen_src_time = self.last_seen[src]
                    g.add_edge((src, last_seen_src_time), (src, time),
                               weight=time - last_seen_src_time)
                if dst in self.last_seen:
                    last_seen_dst_time = self.last_seen[dst]
                    g.add_edge((dst, last_seen_dst_time), (dst, time),
                               weight=time - last_seen_dst_time)
                self.last_seen[src] = time
                self.last_seen[dst] = time
            else:
                break
        self._graph = g

    def versions(self, src, start=0):
        """ Return versions of `src` disregarding versions prior to start. """
        if not self._versions.get(src):
            self._versions[src] = sorted(
                set(t for (s, d, t) in self.information if
                    s == src or d == src))
        return dropwhile(lambda v: v < start, self._versions[src])

    def temporal_proximity(self, node1, node2, t):
        """
        Return the temporal proximity of node1 to node2, given time t.

        Temporal proximity is defined as the shortest path length between
        (node1, t) and any version of node2.

        Params
        ------
        node1 : str denoting first node.
        node2 : str denoting second node.
        t     : version of node1, which serves as source node.
        """
        v = self._anchor(node1, node2, t, t)
        return v - t

    def _anchor(self, node1, node2, t, anchor):
        """
        Return the next node2 anchor from node1 from time t.

        An anchor is the earliest version of node2, accessible from node1, when
        searching from time t. Once an anchor has been discovered, with node1,
        node2 and t as parameters, instead of searching for the shortest paths
        from the earliest version of node2 after time t, it has been found to
        substantially reduce the number of no-path failures, if we start
        searching only from the anchored version of node2. In other words,
        search for paths from (node1, node2, anchor) instead of (node1, node2,
        t).

        Params
        ------
        node1  : str denoting first node.
        node2  : str denoting second node.
        t      : version of node1, which serves as source node.
        anchor : version of node2, from which destinations must be searched.
        """
        if self.last_seen[node2] < t:
            return inf
        elif self.last_seen[node2] == t:
            return t
        for v in self.versions(node2, start=anchor):
            if nx.has_path(self.graph, (node1, t), (node2, v)):
                return v
        return inf

    def average_temporal_proximity(self, node1, node2):
        """
        Arithmetic mean of temporal proximities of all versions of node1.

        Iterates through all versions of node1 and if the version is prior to
        the anchor, it updates the anchor and finds the temporal proximity. This
        is appended to a list temp. The arithmetic mean of all the finite values
        of temp is returned. If temp is empty, because node2 is completely
        unreachable from node1, an infinity is returned.

        Params
        ------
        node1  : str denoting first node.
        node2  : str denoting second node.
        """
        if node1 == node2:
            return 0
        temp = []
        anchor = 0
        for time in self.versions(node1):
            if anchor > time:
                anchor = self._anchor(node1, node2, time, anchor)
            else:
                anchor = self._anchor(node1, node2, time, time)
            y = anchor - time
            if y != inf:
                temp.append(y)
            else:
                break
        if temp:
            return sum(temp) / len(temp)
        else:
            return np.inf
