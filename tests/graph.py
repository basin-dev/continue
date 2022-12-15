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



def test_add_edge():
    assert len(g.graph[0]) == 1
    assert len(g.graph[1]) == 1
    assert len(g.graph[2]) == 2
    assert len(g.graph[3]) == 2
    assert len(g.graph[4]) == 2
    assert len(g.graph[5]) == 2
    assert len(g.graph[6]) == 2
    assert len(g.graph[7]) == 2
    assert len(g.graph[8]) == 2

def test_dijkstra():
    assert g.dijkstra(0) == 0
    assert g.dijkstra(1) == 1
    assert g.dijkstra(2) == 3
    assert g.dijkstra(3) == 4
    assert g.dijkstra(4) == 5
    assert g.dijkstra(5) == 6
    assert g.dijkstra(6) == 7
    assert g.dijkstra(7) == 8
    assert g.dijkstra(8) == 9

def test_dijkstra_single_source():
    assert g.dijkstra(0) == 0
    assert g.dijkstra(1) == 1
    assert g.dijkstra(2) == 3
    assert g.dijkstra(3) == 4
    assert g.dijkstra(4) == 5
    assert g.dijkstra(5) == 6
    assert g.dijkstra(6) == 7
    assert g.dijkstra(7) == 8
    assert g.dijkstra(8) == 9

def test_dijkstra_single_dest():
    assert g.dijkstra(0, 8) == 9
    assert g.dijkstra(1, 8) == 9
    assert g.dijkstra(2, 8) == 9