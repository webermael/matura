from graph.node import Node
from graph.way import Way
import time
import pygame
import math


class Astar:
    def __init__(self, start_id:int, end_id:int):
        self.start:int = start_id
        self.end:int = end_id
        self.explored_nodes:dict[int,dict[str,float|list[str]]] = {self.start: {"weight": 0, "path": []}}
        # -> {node_id: {"weight": 1334, "path": ["412342", "123432r"]}}
        self.active_nodes:list[int] = [self.start]
        self.time_searching = 0
        self.active:bool = True
    
    def step(self, nodes:dict[int,Node], ways:dict[str,Way]):
        start = time.perf_counter()
        if not self.active:
            return
        if self.end in self.explored_nodes or self.active_nodes == [] or self.time_searching > 0.3:
            self.active = False
            return
        min_dist = math.inf
        node = None
        for node_check in self.active_nodes[:]:
            dist = math.sqrt((nodes[node_check].pos[0] - nodes[self.end].pos[0]) ** 2 + (nodes[node_check].pos[1] - nodes[self.end].pos[1]) ** 2) + self.explored_nodes[node_check]["weight"]
            if  dist < min_dist:
                min_dist = dist
                node = node_check
        if not node:
            return
        for way in nodes[node].ways:
            if self.explored_nodes[node]["path"] != []:
                old_way = self.explored_nodes[node]["path"][-1]
                old_node = nodes[ways[old_way[0]].nodes[old_way[1]][-2]].pos
                first_node = nodes[ways[way[0]].nodes[way[1]][1]].pos
                forward = [first_node[0] - nodes[node].pos[0], first_node[1] - nodes[node].pos[1]]
                backward = [nodes[node].pos[0] - old_node[0], nodes[node].pos[1] - old_node[1]]
                dot_product = forward[0] * backward[0] + forward[1] * backward[1]
                dot_product /= (math.sqrt(backward[0] ** 2 + backward[1] ** 2) * math.sqrt(forward[0] ** 2 + forward[1] ** 2))
            else:
                dot_product = 0
            if dot_product > -0.5:
                new_node = ways[way[0]].nodes[way[1]][-1]
                if new_node not in self.explored_nodes or (new_node in self.explored_nodes and self.explored_nodes[node]["weight"] + ways[way[0]].weights[way[1]] < self.explored_nodes[new_node]["weight"]):

                    self.active_nodes.append(new_node)
                    self.explored_nodes[new_node] = {"weight":self.explored_nodes[node]["weight"] + ways[way[0]].weights[way[1]],
                                                    "path":self.explored_nodes[node]["path"] + [way]}
        self.active_nodes.remove(node)
        self.time_searching += (time.perf_counter() - start)


    def render(self, screen, scale, nodes, center, zoom, offset, ways):
        for node in self.explored_nodes:
            pygame.draw.circle(screen, (255, 255, 0), scale(nodes[node].pos, center, zoom, offset), 5)
        for node in self.active_nodes:
            pygame.draw.circle(screen, (255, 0, 255), scale(nodes[node].pos, center, zoom, offset), 5)
        pygame.draw.circle(screen, (255, 0, 0), scale(nodes[self.start].pos, center, zoom, offset), 5)
        pygame.draw.circle(screen, (0, 255, 0), scale(nodes[self.end].pos, center, zoom, offset), 5)
        if self.end in self.explored_nodes:

            [pygame.draw.lines(screen, (0, 255, 255), False, [scale(nodes[node].pos, center, zoom, offset) for node in ways[way[0]].nodes[way[1]]], 5) for way in self.explored_nodes[self.end]["path"]]
