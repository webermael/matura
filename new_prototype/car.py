from graph.node import Node
from graph.way import Way
import math
import pygame

class Car:
    def __init__(self, nodes:dict[int,Node], ways:dict[int,Way], path:list[list[int]]):
        self.pos:list[float] = nodes[ways[path[0][0]].nodes[path[0][1]][0]].pos.copy()
        self.target_speed:float = ways[path[0][0]].speed
        self.speed:float = ways[path[0][0]].speed / 10
        self.desired_gap:float = 2.0
        self.max_accel:float = 1.0
        self.max_decel:float = 4.0
        self.curr_target:list[float] = nodes[ways[path[0][0]].nodes[path[0][1]][1]].pos.copy()
        self.way_index:int = 0
        self.node_index:int = 1
        self.path:list[list[int]] = path
        self.active:bool = True
        ways[self.path[self.way_index][0]].cars[self.path[self.way_index][1]].append(self)
    
    def update(self, nodes:dict[int,Node], ways:dict[int,Way], dt:float):
        if not self.active:
            return
        index = ways[self.path[self.way_index][0]].cars[self.path[self.way_index][1]].index(self)
        multiplier = 1
        if index != 0:
            leading_car = ways[self.path[self.way_index][0]].cars[self.path[self.way_index][1]][index - 1]
            gap_vector = ((leading_car.pos[0] - self.pos[0]), (leading_car.pos[1] - self.pos[1]))
            direction_vector = ((self.curr_target[0] - self.pos[0]), (self.curr_target[1] - self.pos[1]))
            dot_product = (gap_vector[0] * direction_vector[0] + gap_vector[1] * direction_vector[1])
            if dot_product > 0:
                gap = math.sqrt(gap_vector[0] ** 2 + gap_vector[1] ** 2)
                if self.speed > 0:
                    multiplier = max(0, min(1, gap / (self.desired_gap * self.speed)))
        if self.speed < self.target_speed * multiplier:
            self.speed += self.max_accel * dt
        elif self.speed > self.target_speed * multiplier:
            self.speed -= self.max_decel * dt
        self.speed = max(0, self.speed)
        budget = self.speed * dt
        while budget > 0:
            dist = math.sqrt((self.curr_target[0] - self.pos[0]) ** 2 + (self.curr_target[1] - self.pos[1]) ** 2)
            if dist <= budget:
                self.pos = self.curr_target.copy()
                self.node_index += 1
                if self.node_index >= len(ways[self.path[self.way_index][0]].nodes[self.path[self.way_index][1]]):
                    ways[self.path[self.way_index][0]].cars[self.path[self.way_index][1]].remove(self)
                    self.way_index += 1
                    self.node_index = 0
                    if self.way_index >= len(self.path):
                        self.active = False
                        return
                    ways[self.path[self.way_index][0]].cars[self.path[self.way_index][1]].append(self)
                self.curr_target = nodes[ways[self.path[self.way_index][0]].nodes[self.path[self.way_index][1]][self.node_index]].pos.copy()
                self.target_speed = ways[self.path[self.way_index][0]].speed / 10
                budget -= dist 
            elif dist > budget:
                ratio = budget / dist
                direction = [(self.curr_target[0] - self.pos[0]) * ratio, (self.curr_target[1] - self.pos[1]) * ratio]
                self.pos[0] += direction[0]
                self.pos[1] += direction[1]
                budget = 0
    
    def render(self, screen:pygame.Surface, scale, center, zoom, offset):
        pygame.draw.circle(screen, (255 - min(self.speed * 10, 255), min(self.speed * 30, 255), 0), scale(self.pos, center, zoom, offset), math.sqrt(zoom) * 3)