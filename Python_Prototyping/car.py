import pygame
import math
import random
import time
from big_dijkstra import Dijkstra
from node import Node
from edge import Edge
from waypoint import Waypoint
from way import Way

class Car:
    def __init__(self, start_node_id: int, target_node_id: int, nodes: dict[int, Node], waypoints:dict[int, Waypoint], ways: list[Way]):
        self.speed: int = 100
        self.target_id: int = target_node_id
        self.target: list[int] = nodes[start_node_id].pos.copy()
        self.pos: list[int] = nodes[start_node_id].pos.copy()
        self.path: list[int] = []
        self.path_edges: list[int] = []
        self.dijkstra: Dijkstra = Dijkstra(waypoints, ways, start_node_id, target_node_id)
        self.path_progress: int = 0
        self.color: tuple[int, int, int] = tuple(255 - color for color in self.dijkstra.highlight_color)
    
    """
    def update_old(self, nodes: dict[int, Node], edges: dict[int, Edge], dt: float):
        dist = math.sqrt((self.pos[0] - self.target[0]) ** 2 + (self.pos[1] - self.target[1]) ** 2)
        if dist > self.speed * dt:
            self.pos[0] += (self.target[0] - self.pos[0]) / dist * self.speed * dt
            self.pos[1] += (self.target[1] - self.pos[1]) / dist * self.speed * dt
        else:
            self.pos[0] += self.target[0] - self.pos[0]
            self.pos[1] += self.target[1] - self.pos[1]
            tp = False
            if len(nodes[self.target_id].edges) == 0:
                edge = list(edges.keys())[random.randint(0, len(edges) - 1)]
                tp = True
            else:
                edge = random.choice([edge for edge in nodes[self.target_id].edges if len(nodes[self.target_id].edges) == 1 or edges[edge].get_origin(self.target_id) != self.previous_id])

            self.speed = edges[edge].speed / 5
            self.previous_id = self.target_id
            self.target_id = edges[edge].get_end(self.target_id)
            self.target = nodes[self.target_id].pos.copy()
            if tp:
                self.pos[0] += self.target[0] - self.pos[0]
                self.pos[1] += self.target[1] - self.pos[1]
     """

    def set_target(self, nodes: dict[int, Node], edges: dict[int, Edge]):
        if self.path_progress > len(self.path) - 1:
            self.path = []
            self.path_edges = []
            self.path_progress = 0
            return
        edge = self.path_edges[self.path_progress - 1]
        #self.target_id = edges[edge].get_end(self.target_id)
        self.target_id = self.path[self.path_progress]
        self.speed = edges[edge].speed
        self.target = nodes[self.target_id].pos.copy()
        self.path_progress += 1

    def update(self, nodes: dict[int, Node], edges: dict[int, Edge], waypoints, dt: float):
        if self.dijkstra.active:
            start = time.perf_counter()
            while time.perf_counter() - start < 0.00001:
                self.dijkstra.step()

        elif self.path == []:
            for way in self.dijkstra.found["path"]:
                for node in self.dijkstra.edges[way].nodes:
                    if node != self.dijkstra.edges[way].nodes[-1] or way == self.dijkstra.found["path"][-1]:
                        self.path.append(node)
                for edge in self.dijkstra.edges[way].edges:
                    self.path_edges.append(edge)
            self.set_target(nodes, edges)
            self.dijkstra.start = self.dijkstra.end
            self.dijkstra.active = True
            self.dijkstra.explored_nodes = {self.dijkstra.end: {
            "path": [],
            "weight": 0
            }}
            self.dijkstra.active_nodes = [self.dijkstra.end]
            self.dijkstra.end = random.choice([id for id, wp in waypoints.items() if len(wp.edges) >= 2])
            self.dijkstra.found = {"weight": math.inf, "path": []}
            return

        dist = math.sqrt((self.pos[0] - self.target[0]) ** 2 + (self.pos[1] - self.target[1]) ** 2)
        budget = self.speed * dt
        while budget > dist and dist != 0:
            self.pos[0] += self.target[0] - self.pos[0]
            self.pos[1] += self.target[1] - self.pos[1]
            self.set_target(nodes, edges)
            budget -= dist
            dist = math.sqrt((self.pos[0] - self.target[0]) ** 2 + (self.pos[1] - self.target[1]) ** 2)
        
        if dist > 0:
            self.pos[0] += (self.target[0] - self.pos[0]) * budget / dist
            self.pos[1] += (self.target[1] - self.pos[1]) * budget / dist


    def _scale(self, center: list[float], factor: float, offset: list[float]) -> list[float]:
        return [
            (self.pos[0] - center[0]) * factor + center[0] + offset[0],
            (self.pos[1] - center[1]) * factor + center[1] + offset[1]
        ]

    def render(self, screen: pygame.Surface, center: list[float], zoom: float, offset: list[float], screen_size: list[int], nodes) -> None:
        self.dijkstra.render(screen, center, zoom, offset, nodes)
        #if len(self.path) > 1:
        #    pygame.draw.lines(screen, self.color, False, [self.dijkstra.nodes[self.dijkstra.edges[edge].end_id]._scale(center, zoom, offset) for edge in self.path] + [self.dijkstra.nodes[self.dijkstra.start]._scale(center, zoom, offset)], 3)

        pos = self._scale(center, zoom, offset)
        if not (0 < pos[0] < screen_size[0] and 0 < pos[1] < screen_size[1]):
            return 
        pygame.draw.circle(screen, self.dijkstra.highlight_color, pos, 5)

