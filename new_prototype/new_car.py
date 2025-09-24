from graph.node import Node
from graph.way import Way
import math
import pygame

class Car:
    def __init__(self, nodes:dict[int,Node], ways:dict[int,Way], path:list[list[int]]):
        self.pos:list[float] = nodes[ways[path[0][0]].nodes[path[0][1]][0]].pos.copy()
        self.target_speed:float = ways[path[0][0]].speed
        self.speed:float = ways[path[0][0]].speed
        self.desired_gap:float = 2.0
        self.max_accel:float = 10.0
        self.max_decel:float = 40.0
        self.curr_target:list[float] = nodes[ways[path[0][0]].nodes[path[0][1]][1]].pos.copy()
        self.way_index:int = 0
        self.node_index:int = 1
        self.path:list[list[int]] = path
        self.active:bool = True
    

    def dot_product(self, vector1:list[float], vector2:list[float]) -> float:
        return (vector1[0] * vector2[0] + vector1[1] * vector2[1]) / (math.sqrt(vector1[0] ** 2 + vector1[1] ** 2) * math.sqrt(vector2[0] ** 2 + vector2[1] ** 2))


    def move_toward_target(self, ratio:float):
        direction = [(self.curr_target[0] - self.pos[0]) * ratio, (self.curr_target[1] - self.pos[1]) * ratio]
        self.pos[0] += direction[0]
        self.pos[1] += direction[1]


    def next_road_node(self, way_index:int, node_index:int, ways:dict[str,Way]) -> None|tuple[int,int]:
        node_index += 1
        if node_index >= len(ways[self.path[way_index][0]].nodes[self.path[way_index][1]]):
            way_index += 1
            node_index = 0
            if way_index >= len(self.path):
                self.active = False
                return None
        return way_index, node_index


    def update(self, nodes:dict[int,Node], ways:dict[int,Way], dt:float) -> None:
        if not self.active:
            return
        if self.speed < self.target_speed:
            self.speed += self.max_accel * dt
        elif self.speed > self.target_speed:
            self.speed -= self.max_decel * dt
        self.speed = max(0, self.speed)
        budget = self.speed * dt
        while budget > 0:
            dist = math.sqrt((self.curr_target[0] - self.pos[0]) ** 2 + (self.curr_target[1] - self.pos[1]) ** 2)
            if dist <= budget:
                self.pos = self.curr_target.copy()
                next_node = self.next_road_node(self.way_index, self.node_index, ways)
                if not next_node:
                    return
                else:
                    self.way_index, self.node_index = next_node
                self.curr_target = nodes[ways[self.path[self.way_index][0]].nodes[self.path[self.way_index][1]][self.node_index]].pos.copy()
                self.target_speed = ways[self.path[self.way_index][0]].speed
                budget -= dist 
            elif dist > budget:
                ratio = budget / dist
                self.move_toward_target(ratio)
                budget = 0
    
    def render(self, screen:pygame.Surface, to_screen_space, scale) -> None:
        pygame.draw.circle(screen, (255 - min(self.speed, 255), min(self.speed * 3, 255), 0), to_screen_space(self.pos), max(2, int(scale * 5)))