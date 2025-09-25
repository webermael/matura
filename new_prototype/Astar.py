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

    
    def reset(self, start_id:int, end_id:int):
        self.start:int = start_id
        self.end:int = end_id
        self.explored_nodes:dict[int,dict[str,float|list[str]]] = {self.start: {"weight": 0, "path": []}}
        self.active_nodes:list[int] = [self.start]
        self.time_searching = 0
        self.active:bool = True


    def get_dot_product(self, node:Node, way:list[str|int], nodes:dict[str,Node], ways:dict[str,Way], direction:str):
        old_way = self.explored_nodes[node]["path"][-1]
        old_node = nodes[ways[old_way[0]].nodes[old_way[1]][-2]].pos
        first_node = nodes[ways[way[0]].nodes[way[1]][1]].pos
        forward = [first_node[0] - nodes[node].pos[0], first_node[1] - nodes[node].pos[1]]
        backward = self.get_target_vector(direction, [nodes[node].pos[0] - old_node[0], nodes[node].pos[1] - old_node[1]])
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


    def step(self, nodes:dict[int,Node], ways:dict[str,Way]):
        start = time.perf_counter()
        # don't run if not active
        if not self.active:
            return
        # check if still active
        if self.end in self.explored_nodes or self.active_nodes == []:# or self.time_searching > 0.3:
            self.active = False
            return
        # get node with best weight
        min_dist = math.inf
        node = None
        for node_check in self.active_nodes[:]:
            #dist = self.explored_nodes[node_check]["weight"]
            dist = math.sqrt((nodes[node_check].pos[0] - nodes[self.end].pos[0]) ** 2 + (nodes[node_check].pos[1] - nodes[self.end].pos[1]) ** 2) + self.explored_nodes[node_check]["weight"] ** 2
            if  dist < min_dist:
                min_dist = dist
                node = node_check
        if not node:
            return
        # check ways connected to selected node
        for way in nodes[node].ways:
            # check if turn is extremely sharp
            dot_product = 1
            if self.explored_nodes[node]["path"] != [] and ways[self.explored_nodes[node]["path"][-1][0]].turns[self.explored_nodes[node]["path"][-1][1]] != []:
                dot_product = -1
                for direction in ways[self.explored_nodes[node]["path"][-1][0]].turns[self.explored_nodes[node]["path"][-1][1]]:
                    dot_product = max(dot_product, self.get_dot_product(node, way, nodes, ways, direction))
            if dot_product > 0.5:
                new_node = ways[way[0]].nodes[way[1]][-1]
                if new_node not in self.explored_nodes or (new_node in self.explored_nodes and self.explored_nodes[node]["weight"] + ways[way[0]].weights[way[1]] < self.explored_nodes[new_node]["weight"]):
                    # (over)write path and weight for the node (if it's valid)
                    self.active_nodes.append(new_node)
                    self.explored_nodes[new_node] = {"weight":self.explored_nodes[node]["weight"] + ways[way[0]].weights[way[1]],
                                                    "path":self.explored_nodes[node]["path"] + [way]}
        self.active_nodes.remove(node)
        self.time_searching += (time.perf_counter() - start)


    def render(self, screen:pygame.Surface, nodes:dict[str,Node], ways:dict[str,Way]):
        for node in self.explored_nodes:
            pygame.draw.circle(screen, (250, 150, 0), nodes[node].display_pos, 5)
        for node in self.active_nodes:
            #[pygame.draw.lines(screen, (0, 0, 255), False, [nodes[node].display_pos for node in ways[way[0]].nodes[way[1]]], 5) for way in self.explored_nodes[node]["path"]] + [nodes[self.start].display_pos]
            pygame.draw.circle(screen, (180, 0, 200), nodes[node].display_pos, 5)
        pygame.draw.circle(screen, (255, 0, 0), nodes[self.start].display_pos, 5)
        pygame.draw.circle(screen, (0, 255, 0), nodes[self.end].display_pos, 5)
        if self.end in self.explored_nodes:
            [pygame.draw.lines(screen, (0, 0, 255), False, [nodes[node].display_pos for node in ways[way[0]].nodes[way[1]]], 5) for way in self.explored_nodes[self.end]["path"]]
