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



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def test_dijkstra(self, src):
        assert len(self.dijkstra(src)) == 1, "Expected 1 edge"
        assert self.dijkstra(src[0]) == src[0]
        assert self.dijkstra(src[1]) == src[1]

    def test_add_edge(self, src):
        assert len(self.add_edge(src, (0, 1), (2, 3))) == 2, "Expected 2 edges"
        assert self.add_edge(src[0], src[1], src[2])
        assert self.add_edge(src[0], (2, 3), (4, 5))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def test_dijkstra_heappop(self, src):
        assert len(self.dijkstra(src)) == 1, "Expected 1 edge"
        assert heappop(self.dijkstra(src[0])) == src[0], "Dijkstra should return self"
        assert self.dijkstra(src[0]) == src[0]
        assert heappop(self.dijkstra(src[0])) == src[0], "Dijkstra should return self"

def test_dijkstra_