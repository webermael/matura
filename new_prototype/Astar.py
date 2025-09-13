from graph.node import Node
from graph.way import Way
import time
import pygame
import math


class Astar:
    def __init__(self, start_id:int, end_id:int):
        self.start:int = start_id
        self.end:int = end_id
        self.explored_nodes:dict[int,dict[str,float|list[int]]] = {self.start: {"weight": 0, "path": []}}
        # -> {node_id: {"weight": 1334, "path": [412342, 123432]}}
        self.active_nodes:list[int] = [self.start]
        self.time_searching = 0
        self.active:bool = True
    
    def step(self, nodes:dict[int,Node], ways:dict[str,Way]):
        start = time.perf_counter()
        if not self.active:
            return
        if self.end in self.explored_nodes or self.active_nodes == [] or self.time_searching > 0.1:
            self.active = False
            self.active_nodes = []
            return
        min_dist = math.inf
        node = None
        for node_check in self.active_nodes[:]:
            dist = ((nodes[node_check].pos[0] - nodes[self.end].pos[0]) ** 2 + (nodes[node_check].pos[1] - nodes[self.end].pos[1]) ** 2)# + self.explored_nodes[node_check]["weight"]
            if  dist < min_dist:
                min_dist = dist
                node = node_check
        if not node:
            return
        for way in nodes[node].ways:
            new_node = ways[way[0]].nodes[way[1]][-1]
            if new_node not in self.explored_nodes or new_node in self.explored_nodes and self.explored_nodes[node]["weight"] + ways[way[0]].weights[way[1]] < self.explored_nodes[new_node]["weight"]:

                self.active_nodes.append(new_node)
                self.explored_nodes[new_node] = {"weight":self.explored_nodes[node]["weight"] + ways[way[0]].weights[way[1]],
                                                "path":self.explored_nodes[node]["path"] + [new_node]}
        self.active_nodes.remove(node)
        self.time_searching += (time.perf_counter() - start)


    def render(self, screen, scale, normalize, nodes, center, zoom, offset):
        for node in self.explored_nodes:
            pygame.draw.circle(screen, (255, 255, 0), scale(normalize(nodes[node].pos), center, zoom, offset), 5)
        for node in self.active_nodes:
            pygame.draw.circle(screen, (255, 0, 255), scale(normalize(nodes[node].pos), center, zoom, offset), 5)
        pygame.draw.circle(screen, (255, 0, 0), scale(normalize(nodes[self.start].pos), center, zoom, offset), 5)
        pygame.draw.circle(screen, (0, 255, 0), scale(normalize(nodes[self.end].pos), center, zoom, offset), 5)
        if self.end in self.explored_nodes:
            for node in self.explored_nodes[self.end]["path"]:
                pygame.draw.circle(screen, (0, 255, 255), scale(normalize(nodes[node].pos), center, zoom, offset), 5)