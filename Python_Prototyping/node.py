import pygame 
import random

class Node:
    def __init__(self, id: int, pos: list[float], edges: list[int], edges_in: list[int], all_edges: list[int], tags: dict[str, bool]):
        self.id: int = id
        self.pos: list[float] = pos
        self.edges: list[int] = edges
        self.edges_in: list[int] = edges_in
        self.all_edges: list[int] = all_edges
        self.tags: dict[str, bool] = tags
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    def _scale(self, center: list[float], factor: float, offset: list[float]) -> list[float]:
        return [
            (self.pos[0] - center[0]) * factor + center[0] + offset[0],
            (self.pos[1] - center[1]) * factor + center[1] + offset[1]
        ]

    def render(self, screen: pygame.Surface, center: list[float], zoom: float, offset: list[float], screen_size: list[int]) -> None:
        pos = self._scale(center, zoom, offset)
        if not (0 < pos[0] < screen_size[0] and 0 < pos[1] < screen_size[1]):
            return 
        #pygame.draw.circle(screen, self.color, pos, 3)

        if self.tags.get("in_queue"):
            pygame.draw.circle(screen, (255, 255, 0), pos, 5)
        if self.tags.get("active"):
            pygame.draw.circle(screen, (255, 0, 0), pos, 5)
        if self.tags.get("searching"):
            pygame.draw.circle(screen, (0, 255, 255), pos, 3)
        if self.tags.get("debug"):
            pygame.draw.circle(screen, self.tags["debug"], pos, 8)