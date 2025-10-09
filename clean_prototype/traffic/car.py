import math
import pygame

from graph.node import Node
from graph.way import Way
from display import Display

class Car:
    def __init__(self, path:list[Way]):
        self.pos:list[float] = path[0].nodes[0].pos.copy()
        self.target_pos:list[float] = path[0].nodes[1].pos.copy()
        self.node_index:int = 1
        self.target_speed:float = path[0].speed
        self.speed:float = path[0].speed
        self.car_dist:float = 1.5
        self.accel:float = 20.0
        self.coast:float = -10.0
        self.brake:float = -30.0
        self.path:list[Way] = path
        self.curr_way:Way = path[0]
        self.curr_way.cars.append(self)
        self.active:bool = True
        self.direction:list[float] = self._get_direction(self.pos, self.target_pos, self._get_dist(self.pos, self.target_pos))
        self.highlight_mode:str = "speed"
        self.state_to_color:dict[str,list[int]] = {
            "standstill": [200, 200, 200],
            "cruise": [50, 200, 255],
            "accelerate": [0, 255, 0],
            "brake": [255, 50, 50],
            "coast": [200, 150, 50]
        }
        self.color:list[float] = [0, 255, 255]
        #self.speed = path[0].speed * min(self.car_lookahead(), self._turn_lookahead())


    def _get_dist(self, point1:list[float], point2:list[float]) -> list[float]:
        return math.hypot(point1[0] - point2[0], point1[1] - point2[1])
    
    def _dot_product(self, vector1:list[float], vector2:list[float]) -> float:
        return (vector1[0] * vector2[0] + vector1[1] * vector2[1]) / (math.sqrt(vector1[0] ** 2 + vector1[1] ** 2) * math.sqrt(vector2[0] ** 2 + vector2[1] ** 2))

    def _get_dot_product(self, pos1:list[float], pos2:list[float], pos3:list[float]):
        vector1 = [pos2[0] - pos1[0], pos2[1] - pos1[1]]
        vector2 = [pos3[0] - pos2[0], pos3[1] - pos2[1]]
        return self._dot_product(vector1, vector2)

    def _set_speed(self, dt:float, slowdown:float) -> str:
        slowed_target = self.target_speed * slowdown
        state = "standstill"
        if abs(self.speed - slowed_target) < 0.03:
            self.speed = slowed_target
            if slowed_target != 0:
                state = "cruise"
        elif self.speed < slowed_target:
            self.speed += self.accel * dt
            state = "accelerate"
        elif self.speed > slowed_target + 5:
            self.speed += self.brake * dt
            state = "brake"
        elif self.speed > slowed_target + 0.1:
            self.speed += self.coast * dt
            state = "coast"
        self.speed = max(0, self.speed)
        return state

    def _next_target(self, node_index:int, way:Way) -> tuple[int, Way, bool]:
        new_way = way
        end = False
        node_index += 1
        if node_index >= len(way.nodes) and self.path.index(way) + 1 < len(self.path):
            new_way = self.path[self.path.index(way) + 1]
            node_index = 1
        elif node_index >= len(way.nodes) and self.path.index(way) + 1 >= len(self.path):
            node_index -= 1
            end = True
        return node_index, new_way, end 

    def _get_direction(self, point1:list[float], point2:list[float], length:float) -> list[float]:
        return [(point2[0] - point1[0]) / length, (point2[1] - point1[1]) / length]

    def _move_toward(self, budget:float, distance:float) -> None:
        direction = self._get_direction(self.pos, self.target_pos, distance)
        self.direction = direction
        self.pos[0] += direction[0] * budget
        self.pos[1] += direction[1] * budget

    def _move(self, dt:float) -> None:
        budget = self.speed * dt

        while budget > 0 and self.active:
            distance = self._get_dist(self.pos, self.target_pos)
            if budget >= distance:
                self.pos = self.target_pos.copy()
                if self in self.curr_way.nodes[self.node_index].claimed_car:
                    self.curr_way.nodes[self.node_index].claimed_car = []
                next_target = self._next_target(self.node_index, self.curr_way)

                self.node_index = next_target[0]
                if next_target[1] != self.curr_way:
                    self.curr_way.cars.remove(self)
                    self.curr_way = next_target[1]
                    self.curr_way.cars.append(self)
                self.active = not next_target[2]

                if self.active:
                    self.target_pos = self.curr_way.nodes[self.node_index].pos.copy()
                    self.target_speed = self.curr_way.speed
                    
                else:
                    self.curr_way.cars.remove(self)
                budget -= distance
            
            elif budget < distance:
                self._move_toward(budget, distance)
                budget = 0

    def _turn_lookahead(self, surface, to_screen):
        max_dist = self.speed * 5
        lookahead = max_dist - self._get_dist(self.pos, self.target_pos)
        curvature = 0
        # first node setup
        old_node = self.pos
        node = self.target_pos
        index, way, end = self._next_target(self.node_index, self.curr_way)

        while lookahead > 0 and not end:
            new_node = way.nodes[index].pos
            # add curve of node
            curvature += math.acos(max(-1, min(1, self._get_dot_product(old_node, node, new_node)))) * (lookahead / max_dist)
            #pygame.draw.line(surface, (255, 0, 0), to_screen(old_node), to_screen(node))
            #pygame.draw.line(surface, (255, 0, 0), to_screen(node), to_screen(new_node))
            old_node = node
            node = new_node
            index, way, end = self._next_target(index, way)
            lookahead -= self._get_dist(old_node, node)
        if 1 / (1 + curvature * 0.25) < 0.5:
            pygame.draw.circle(surface, (255, 0, 0), to_screen(self.pos), 4)
        # get exponential falloff with increasing angle
        return 1 / (1 + curvature * 0.5)

    def car_lookahead(self, surface, to_screen):
        max_dist = self.target_speed * 5
        lookahead = 0
        # first node setup
        old_node = self.pos
        new_node = self.target_pos
        index = self.node_index
        way = self.curr_way
        end = False
        next_car = None

        while lookahead < max_dist and not end and not next_car:
            if (self in way.cars and way.cars.index(self) != 0):
                next_car = way.cars[way.cars.index(self) - 1]
                lookahead += self._get_dist(old_node, next_car.pos)

            elif (way.cars != [] and self not in way.cars):
                next_car = way.cars[-1]
                lookahead += self._get_dist(old_node, next_car.pos)

            else:
                index, way, end = self._next_target(index, way)
                old_node = new_node
                new_node = way.nodes[index].pos
                dist = self._get_dist(old_node, new_node)
                lookahead += dist

        if next_car:
            if max(0, min(1, (lookahead - self.car_dist * max(8, self.speed)))) ** 2 < 0.5:
                pygame.draw.line(surface, (0, 255, 255), to_screen(self.pos), to_screen(next_car.pos))
            return max(0, min(1, (lookahead - self.car_dist * max(8, self.speed)))) ** 2
        return 1

    def intersection_lookahead(self, surface, to_screen):
        return 1
        lookahead = self._get_dist(self.pos, self.target_pos)
        max_dist = max(20, self.target_speed)
        end = False
        old_node = self.pos
        new_node = self.target_pos
        index = self.node_index
        way = self.curr_way
        intersections:dict[Node,float] = {}

        while lookahead < max_dist and not end:
                #pygame.draw.circle(surface, (255 - 255 * lookahead / max_dist, 0, 0), to_screen(new_node), 5)
                if way.nodes[index].street_count > 2:
                    intersections[way.nodes[index]] = lookahead 
                index, way, end = self._next_target(index, way)
                old_node = new_node
                new_node = way.nodes[index].pos
                dist = self._get_dist(old_node, new_node)
                lookahead += dist
        for intersection, distance in intersections.items():
            if intersection.claimed_car and intersection.claimed_car[0] != self:
                angle = abs(self._dot_product(self.direction, intersection.claimed_car[1]))
                if angle < 0.3:
                    pygame.draw.line(surface, (0, 255, 255), to_screen(self.pos), to_screen(intersection.pos))
                    return 0
            else:
                intersection.claimed_car = [self, self.direction]
        return 1



    def update(self, dt:float, surface, to_screen) -> None:
        if not self.active:
            return
        
        turn_multiplier = self._turn_lookahead(surface, to_screen)
        car_multiplier = self.car_lookahead(surface, to_screen)
        intersection_multiplier = self.intersection_lookahead(surface, to_screen)
        state = self._set_speed(dt, min(turn_multiplier, car_multiplier, intersection_multiplier))
        if self.highlight_mode == "acceleration":
            self.color = self.state_to_color[state]
        elif self.highlight_mode == "speed":
            self.color = [max(0, 255 - min(255, self.speed * 2)), 50 + min(205, self.speed * 4), 0]
        self._move(dt)
        

    def render(self, surface:pygame.Surface, display:Display):
        offset = (self.curr_way.lanes - 1) * 4 * display.plot.scale
        displacement = [self.direction[1] * offset, self.direction[0] * offset]
        display_pos = display.plot.to_screen_space(self.pos)
        display_pos = [display_pos[0] + displacement[0], display_pos[1] + displacement[1]]
        front = [display_pos[0] + self.direction[0] * 5 * display.plot.scale, display_pos[1] - self.direction[1] * 5 * display.plot.scale]
        back = [display_pos[0] - self.direction[0] * 5 * display.plot.scale, display_pos[1] + self.direction[1] * 5 * display.plot.scale]
        pygame.draw.line(surface, self.color, front, back, max(2, int(5 * display.plot.scale)))
        #pygame.draw.circle(surface, self.color, display.plot.to_screen_space(self.pos), max(2, int(display.plot.scale * 5)))
