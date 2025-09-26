from graph.node import Node
from graph.way import Way
from graph.plot import Plot

import pygame

class Display:
    def __init__(self, plot:Plot):
        self.plot:Plot = plot


    def reset_view(self, road_surface:pygame.Surface, ways:list[Way]):
        self.plot.reset_values()
        road_surface.fill((0, 0, 0))
        for way in ways:
            pygame.draw.lines(road_surface, (100, 100, 100), False, [self.plot.to_screen_space(node.pos) for node in way.nodes], max(1, way.lanes*int(12 * self.plot.scale)))


    def set_view(self, road_surface:pygame.Surface, ways:list[Way], rect_value:list[float]):
        self.plot.set_values(rect_value[0], rect_value[1], rect_value[2], rect_value[3])
        road_surface.fill((0, 0, 0))
        for way in ways:
            pygame.draw.lines(road_surface, (100, 100, 100), False, [self.plot.to_screen_space(node.pos) for node in way.nodes], max(1, way.lanes*int(12 * self.plot.scale)))
