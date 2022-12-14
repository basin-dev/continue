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



def test_graph():
    g = Graph(4)
    g.add_edge(0, 1, 1)
    g.add_edge(0, 2, 2)
    g.add_edge(1, 2, 3)
    g.add_edge(2, 3, 4)
    g.add_edge(3, 0, 5)
    assert g.dijkstra(0) == [0, 1, 2, 6]

def test_graph2():
    g = Graph(4)
    g.add_edge(0, 1, 1)
    g.add_edge(0, 2, 2)
    g.add_edge(1, 2, 3)
    g.add_edge(2, 3, 4)
    g.add_edge(3, 0, 5)
    assert g.dijkstra(1) == [float("Inf"), 0, 3, 7]

def test_graph3():
    g = Graph(4)
    g.add_edge(0, 1, 1)
    g.add_edge(0, 2, 2)
    g.add_edge(1, 2, 3)
    g.add_edge(2, 3, 4)
    g.add_edge(3, 0, 5)
    assert g.dijkstra(2) == [float("Inf"), float("Inf"), 0, 4]

def test_graph4():
    g = Graph(4)
    g.add_edge(0, 1, 1)
    g.add_edge(0, 2, 2)
    g.add_edge(1, 2, 3)
    g.add_edge(2, 3, 4)
    g.add_edge(3, 0, 5)
    assert g.dijkstra(3) == [5, 6, 10, 0]

def test_graph5():
    g = Graph(4)
    g.add_edge(0, 1, 1)
    g.add_edge(0, 2, 2)
    g.add_edge(1, 2, 3)
    g.add_edge(