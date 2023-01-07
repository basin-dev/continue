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

import pytest

from djikstra import Dijkstra


@pytest.mark.parametrize("start", [0, 1, 2, 3])
def test_single_vert_single_path(start):
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijkstra(0, 0) == [0, 0, 0]
    assert Dijk