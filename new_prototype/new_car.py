from graph.node import Node
from graph.way import Way
import math
import pygame

class Car:
    def __init__(self, nodes:dict[int,Node], ways:dict[int,Way], path:list[list[int]]):
        self.pos:list[float] = nodes[ways[path[0][0]].nodes[path[0][1]][0]].pos.copy()
        self.target_speed:float = ways[path[0][0]].speed
        self.speed:float = ways[path[0][0]].speed
        self.max_accel:float = 15.0
        self.cruise_decel:float = -10.0
        self.max_decel:float = -30.0
        self.curr_target:list[float] = nodes[ways[path[0][0]].nodes[path[0][1]][1]].pos.copy()
        self.way_index:int = 0
        self.node_index:int = 1
        self.path:list[list[int]] = path
        self.active:bool = True
        self.direction:list[float] = [0, 0]
        self.color = [0, 255, 255]
    
    def _get_dist(self, point1:list[float], point2:list[float]):
        return math.hypot(point1[0] - point2[0], point1[1] - point2[1])

    def _get_node_from_index(self, nodes:dict[str,Node], ways:dict[str,Way], way_index:int, node_index:int):
        return nodes[ways[self.path[way_index][0]].nodes[self.path[way_index][1]][node_index]]

    def _dot_product(self, vector1:list[float], vector2:list[float]) -> float:
        return (vector1[0] * vector2[0] + vector1[1] * vector2[1]) / (math.sqrt(vector1[0] ** 2 + vector1[1] ** 2) * math.sqrt(vector2[0] ** 2 + vector2[1] ** 2))

    def _get_dot_product(self, node1, node2, node3):
        vector1 = [node2[0] - node1[0], node2[1] - node1[1]]
        vector2 = [node3[0] - node2[0], node3[1] - node2[1]]
        return self._dot_product(vector1, vector2)

    def _move_toward_target(self, budget:float, dist:float):
        direction = [(self.curr_target[0] - self.pos[0]) / dist, (self.curr_target[1] - self.pos[1]) / dist]
        self.direction = direction
        self.pos[0] += direction[0] * budget
        self.pos[1] += direction[1] * budget

    def _next_road_node(self, way_index:int, node_index:int, nodes:dict[str,Node], ways:dict[str,Way], relevant = False) -> bool|tuple[int,int,Node]:
        node_index += 1
        if node_index >= len(ways[self.path[way_index][0]].nodes[self.path[way_index][1]]):
            way_index += 1
            node_index = 1
            if way_index >= len(self.path):
                if relevant:
                    self.active = False
                return way_index, node_index, False
        return way_index, node_index, self._get_node_from_index(nodes, ways, way_index, node_index)


    def update(self, nodes:dict[int,Node], ways:dict[int,Way], dt:float, screen, to_screen_space) -> None:
        if not self.active:
            return
        #self.speed += min(self.max_accel, max(self.max_decel, (self.target_speed - self.speed) * dt))
        curve_decrease = self._lookahead(screen, to_screen_space, nodes, ways)
        if abs(self.speed - self.target_speed * curve_decrease) < 0.1:
            self.speed = self.target_speed * curve_decrease
            self.color = [0, 255, 255]
        elif self.speed < self.target_speed * curve_decrease:
            self.speed += self.max_accel * dt
            self.color = [0, 255, 0]
        elif self.speed - self.target_speed * curve_decrease > 5:
            self.speed += self.max_decel * dt
            self.color = [255, 0, 0]
        elif self.speed - self.target_speed * curve_decrease > 0.1:
            self.speed += self.cruise_decel * dt
            self.color = [255, 150, 0]

        self.speed = max(0, self.speed)
        budget = self.speed * dt
        while budget > 0:
            dist = math.sqrt((self.curr_target[0] - self.pos[0]) ** 2 + (self.curr_target[1] - self.pos[1]) ** 2)
            if dist <= budget:
                self.pos = self.curr_target.copy()
                next_node = self._next_road_node(self.way_index, self.node_index, nodes, ways, True)
                #print(self.curr_target)
                if not next_node[2]:
                    return
                else:
                    self.way_index, self.node_index, self.curr_target = (next_node[0], next_node[1], next_node[2].pos.copy())
                #print(self.curr_target, "\n")
                self.target_speed = ways[self.path[self.way_index][0]].speed
                budget -= dist 
            elif dist > budget:
                self._move_toward_target(budget, dist)
                budget = 0


    def _lookahead(self, screen, to_screen_space, nodes, ways):
        max_dist = self.speed
        lookahead = max_dist
        dot_product = 1
        lookahead -= self._get_dist(self.pos, self.curr_target)
        if lookahead > 0:
            if self._next_road_node(self.way_index, self.node_index, nodes, ways)[2]:
                dot_product *= (self._get_dot_product(self.pos, self.curr_target, self._next_road_node(self.way_index, self.node_index, nodes, ways)[2].pos) / 2 + 0.5)
            #pygame.draw.circle(screen, (255 - dot_product * 255, dot_product * 255, 0), to_screen_space(self.curr_target), 5)
        
        prvs_node = self._get_node_from_index(nodes, ways, self.way_index, self.node_index)
        way_index, node_index, new_node = self._next_road_node(self.way_index, self.node_index, nodes, ways)

        while lookahead > 0 and new_node:
            lookahead -= self._get_dist(prvs_node.pos, new_node.pos)
            if lookahead > 0:
                if self._next_road_node(way_index, node_index, nodes, ways)[2]:
                    dot_product *= (self._get_dot_product(prvs_node.pos, new_node.pos, self._next_road_node(way_index, node_index, nodes, ways)[2].pos) / 2 + 0.5)
                #print(dot_product)
                #pygame.draw.circle(screen, (255 - dot_product * 255, dot_product * 255, 0), new_node.display_pos, 5)
                prvs_node = new_node
                way_index, node_index, new_node = self._next_road_node(way_index, node_index, nodes, ways)
        return dot_product

    def render(self, screen:pygame.Surface, to_screen_space, scale:float, ways:dict[str,Way]) -> None:
        if scale < 0.7:
            pygame.draw.circle(screen, self.color, to_screen_space(self.pos), max(2, int(scale * 5)))
            #self._lookahead(screen, to_screen_space, nodes, ways)

        else:
            offset = (ways[self.path[self.way_index][0]].lanes - 1) * int(5 * scale)
            displacement = [self.direction[1] * offset, self.direction[0] * offset]
            front = to_screen_space(self.pos)
            pygame.draw.line(screen, (255 - min(self.speed, 255), min(self.speed * 3, 255), 0), (front[0] + self.direction[0]*scale*5 + displacement[0], front[1] - self.direction[1]*scale*5 + displacement[1]), (front[0] - self.direction[0]*scale*6+ displacement[0], front[1] + self.direction[1]*scale*6 + displacement[1]), max(2, int(scale * 6)))