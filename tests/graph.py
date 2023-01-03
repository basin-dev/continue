# This file contains graph algorithms, including Djikstra's algorithm, and a graph class.

from collections import defaultdict
from heapq import heappush, heappop

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = defaultdict(list)

    def add_edge(self, u, v, w):
        self.graph[u].append((v, w))
        self.graph[v].append((u, w))

    def dijkstra(self, src):
        dist = [float("Inf")] * self.V
        dist[src] = 0
        pq = []
        heappush(pq, (0, src))

        while pq:
            u = heappop(pq)[1]
            for v, w in self.graph[u]:
                if dist[v] > dist[u] + w:
                    dist[v] = dist[u] + w
                    heappush(pq, (dist[v], v))

        return dist


# Copyright (c) 2020, Mark A. Yoder. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import pytest

from graph import Graph

@pytest.fixture(scope='module')
def g():
    return Graph(["a", "b", "c"], [0, 1, 2])


@pytest.fixture(scope='module')
def g2():
    return g


def test_add_edge_invokes_add_edge():
    g = g2()
    g.add_edge(0, 1)
    assert g.add_edge(0, 2)


def test_add_edge_invokes_add_edge_slow():
    g = g2()
    g.add_edge(0, 1)
    g.add_edge(1, 2)
    assert g.add_edge(0, 2)
    assert g.add_edge(1, 2)
