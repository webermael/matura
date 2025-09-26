import pygame
import math
import time

from graph.node import Node
from graph.way import Way

class Astar:
    def __init__(self, start_node:Node, end_node:Node):
        self.reset(start_node, end_node)
    
    def reset(self, start_node:Node, end_node:Node):
        self.start:Node = start_node
        self.end:Node = end_node
        self.explored_nodes:dict[Node, dict[str,int|list[Way]]] = {self.start: {"weight": 0, "path": []}}
        self.active_nodes:list[Node] = [self.start]
        self.time_searching:float = 0.0
        self.active:bool = True

    def get_dot_product(self, node:Node, way:list[str|int], direction:str):
        old_way = self.explored_nodes[node]["path"][-1]
        old_node = old_way.nodes[-2].pos
        first_node = way.nodes[1].pos
        forward = [first_node[0] - node.pos[0], first_node[1] - node.pos[1]]
        backward = self.get_target_vector(direction, [node.pos[0] - old_node[0], node.pos[1] - old_node[1]])
        return self.dot_product(forward, backward)
    
    def get_target_vector(self, direction:str, vector:list[float]):
        # rotate target vector according to direction given
        match direction:
            case "through":
                return vector
            case "left":
                return [-vector[1], vector[0]]
            case "right":
                return [vector[1], -vector[0]]
    
    def dot_product(self, vector1:list[float], vector2:list[float]):
        return (vector1[0] * vector2[0] + vector1[1] * vector2[1]) / (math.sqrt(vector1[0] ** 2 + vector1[1] ** 2) * math.sqrt(vector2[0] ** 2 + vector2[1] ** 2))


    def step(self):
        start = time.perf_counter()

        if not self.active:
            return
        
        if self.end in self.explored_nodes or self.active_nodes == []:
            self.active = False
            return
        
        min_dist = math.inf
        node = None
        for node_check in self.active_nodes:
            dist = math.hypot(node_check.pos[0] - self.end.pos[0], node_check.pos[1] - self.end.pos[1]) + self.explored_nodes[node_check]["weight"] ** 1.8
            if  dist < min_dist:
                min_dist = dist
                node = node_check
        if not node:
            return
        
        for way in node.ways_out:
            dot_product = 1
            if self.explored_nodes[node]["path"] != [] and self.explored_nodes[node]["path"][-1].turns != []:
                dot_product = -1
                for direction in self.explored_nodes[node]["path"][-1].turns:
                    dot_product = max(dot_product, self.get_dot_product(node, way, direction))
            if dot_product > 0.5:
                new_node = way.nodes[-1]
                if new_node not in self.explored_nodes or (new_node in self.explored_nodes and self.explored_nodes[node]["weight"] + way.length < self.explored_nodes[new_node]["weight"]):
                    
                    self.active_nodes.append(new_node)
                    self.explored_nodes[new_node] = {
                        "weight":self.explored_nodes[node]["weight"] + way.length,
                        "path":self.explored_nodes[node]["path"] + [way]
                    }
        self.active_nodes.remove(node)
        self.time_searching += (time.perf_counter() - start)

    def render(self, screen:pygame.Surface, to_screen):
        for node in self.explored_nodes:
            pygame.draw.circle(screen, (250, 150, 0), to_screen(node.pos), 5)
        for node in self.active_nodes:
            pygame.draw.circle(screen, (50, 150, 0), to_screen(node.pos), 5)

        pygame.draw.circle(screen, (255, 0, 0), to_screen(self.start.pos), 5)
        pygame.draw.circle(screen, (0, 255, 150), to_screen(self.end.pos), 5)
        if self.end in self.explored_nodes:
            [pygame.draw.lines(screen, (0, 255, 255), False, [to_screen(node.pos) for node in way.nodes], 5) for way in self.explored_nodes[self.end]["path"]]