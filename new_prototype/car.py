from graph.node import Node
from graph.way import Way
import math
import pygame

class Car:
    def __init__(self, nodes:dict[int,Node], ways:dict[int,Way], path:list[list[int]]):
        self.pos:list[float] = nodes[ways[path[0][0]].nodes[path[0][1]][0]].pos.copy()
        self.target_speed:float = ways[path[0][0]].speed
        self.speed:float = ways[path[0][0]].speed / 10
        self.max_accel:float = 2.0
        self.max_decel:float = 4.0
        self.curr_target:list[float] = nodes[ways[path[0][0]].nodes[path[0][1]][1]].pos.copy()
        self.way_index:int = 0
        self.node_index:int = 2
        self.path:list[list[int]] = path
        self.active:bool = True
    
    def update(self, nodes:dict[int,Node], ways:dict[int,Way], dt:float):
        if not self.active:
            return
        budget = self.speed * dt
        while budget > 0:
            dist = math.sqrt((self.curr_target[0] - self.pos[0]) ** 2 + (self.curr_target[1] - self.pos[1]) ** 2)
            if dist <= budget:
                self.pos = self.curr_target.copy()
                self.node_index += 1
                if self.node_index >= len(ways[self.path[self.way_index][0]].nodes[self.path[self.way_index][1]]):
                    self.way_index += 1
                    self.node_index = 0
                    if self.way_index >= len(self.path):
                        self.active = False
                        return
                self.curr_target = nodes[ways[self.path[self.way_index][0]].nodes[self.path[self.way_index][1]][self.node_index]].pos.copy()
                self.speed = ways[self.path[self.way_index][0]].speed / 10
                budget -= dist 
            elif dist > budget:
                ratio = budget / dist
                direction = [(self.curr_target[0] - self.pos[0]) * ratio, (self.curr_target[1] - self.pos[1]) * ratio]
                self.pos[0] += direction[0]
                self.pos[1] += direction[1]
                budget = 0
    
    def render(self, screen:pygame.Surface, scale, center, zoom, offset):
        pygame.draw.circle(screen, (255, 0, 255), scale(self.pos, center, zoom, offset), math.sqrt(zoom) * 3)