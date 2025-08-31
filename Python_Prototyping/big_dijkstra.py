from node import Node
from edge import Edge
import math
import pygame
import random

class Dijkstra:
    def __init__(self, nodes: list[Node], edges: list[Edge], start: int, end: int):
        self.nodes: list[Node] = nodes
        self.edges: list[Edge] = edges
        self.start: int = start
        self.end: int = end
        self.explored_nodes: dict[int, dict[str, list[int]|int]] = {start: {
            "path": [],
            "weight": 0
        }}
        self.active_nodes: list[int] = [start]
        self.found: dict[str, list[int]] = {"weight": math.inf, "path": []}
        self.active: bool = True
        self.color: tuple[int, int, int] = (random.randint(20, 81), random.randint(20, 81), random.randint(20, 81))
        self.highlight_color: tuple[int, int, int] = tuple(color * 3 for color in self.color)


    def step(self):
        if not self.active:
            return
        if self.found["weight"] < math.inf:
            for node in self.active_nodes[:]:
                if self.explored_nodes[node]["weight"] > self.found["weight"]:
                    self.active_nodes.remove(node)
            if len(self.active_nodes) == 0:
                self.active = False
                self.active_nodes = []
                self.explored_nodes = {}
                return

        for node in self.active_nodes[:]:
            data = self.explored_nodes[node]
            for edge in self.nodes[node].edges:
                weight = self.edges[edge].length / self.edges[edge].speed + data["weight"]

                if self.edges[edge].get_end(node) not in self.explored_nodes.keys():
                    self.explored_nodes[self.edges[edge].get_end(node)] = {
                        "path": data["path"] + [edge],
                        "weight": weight
                    }
                    self.active_nodes.append(self.edges[edge].get_end(node))

                elif weight < self.explored_nodes[self.edges[edge].get_end(node)]["weight"]:
                    self.explored_nodes[self.edges[edge].get_end(node)]["weight"] = weight
                    self.explored_nodes[self.edges[edge].get_end(node)]["path"] = data["path"] + [edge]
                    self.active_nodes.append(self.edges[edge].get_end(node))
                if self.edges[edge].get_end(node) == self.end:
                    if weight < self.found["weight"]:
                        self.found["weight"] = weight
                        self.found["path"] = self.explored_nodes[self.edges[edge].get_end(node)]["path"]
            if node in self.active_nodes:
                self.active_nodes.remove(node)

    
    def render(self, screen: pygame.Surface, center: list[float], zoom: float, offset: list[float], nodes: dict[int,Node]):
        #for node in self.explored_nodes.keys():
        #    pygame.draw.circle(screen, (0, 255, 255), nodes[node]._scale(center, zoom, offset), 3)
        #    path = []
        #    for way in self.explored_nodes[node]["path"]:
        #        path += self.edges[way].nodes
        #    if len(path) > 1:
        #        pygame.draw.lines(screen, (0, 255, 255), False, [nodes[node]._scale(center, zoom, offset) for node in path], 4)

        for node in self.active_nodes:
            pygame.draw.circle(screen, (255, 0, 0), nodes[node]._scale(center, zoom, offset), 5)
        if self.found["weight"] < math.inf:
            for path in [self.found["path"]]:
                path = []
                for way in self.found["path"]:
                    path += self.edges[way].nodes
                if len(path) > 1:
                    pygame.draw.lines(screen, (0, 255, 255), False, [nodes[node]._scale(center, zoom, offset) for node in path], 4)
        pygame.draw.circle(screen, (0, 0, 255), nodes[self.start]._scale(center, zoom, offset), 8)
        pygame.draw.circle(screen, (0, 0, 255), nodes[self.end]._scale(center, zoom, offset), 8)