import pygame 
from node import Node

class Edge:
    def __init__(self, id: int, start_id: int, end_id: int, speed: int, length: float, tags: dict[str, bool|int]):
        self.id: int = id
        self.start_id: int = start_id
        self.end_id: int  = end_id
        self.speed: int = speed
        self.length: float = length
        self.tags: dict[str, bool|int] = tags
        self.tags["lanes"] = round(float(self.tags["lanes"]))
    

    def get_end(self, start_id: int):
        if start_id == self.start_id:
            return self.end_id
        elif start_id == self.end_id:
            return self.start_id
        else:
            return self.end_id
    
    def get_origin(self, end_id: int):
        if end_id == self.start_id:
            return self.end_id
        elif end_id == self.end_id:
            return self.start_id

    def render(self, screen: pygame.Surface, center: list[float], zoom: float, offset: list[float], nodes: dict[int, 'Node'], screen_size: list[int]) -> None:
        start = nodes[self.start_id]._scale(center, zoom, offset)
        end = nodes[self.end_id]._scale(center, zoom, offset)
        if (not 0 < start[0] < screen_size[0] and not 0 < start[1] < screen_size[1]) and (not 0 < end[0] < screen_size[0] and not 0 < end[1] < screen_size[1]):
            return
        
        if self.tags["roundabout"]:        
            left = [start[0] + (end[1] - start[1]) / self.length*2,
                    start[1] - (end[0] - start[0]) / self.length*2]
            
            right = [start[0] - (end[1] - start[1]) / self.length*2,
                    start[1] + (end[0] - start[0]) / self.length*2]
            
            #pygame.draw.polygon(screen, (200, 40, 250), (left, right, end))
            pygame.draw.polygon(screen, (150, 150, 150), (left, right, end))
            #pygame.draw.line(screen, (250, 190, 0), start, end, self.tags["lanes"])

        elif not self.tags["twoway"]:       
            left = [start[0] + (end[1] - start[1]) / self.length*self.tags["lanes"],
                    start[1] - (end[0] - start[0]) / self.length*self.tags["lanes"]]
            
            right = [start[0] - (end[1] - start[1]) / self.length*self.tags["lanes"],
                    start[1] + (end[0] - start[0]) / self.length*self.tags["lanes"]]

            #pygame.draw.line(screen, (200, 40, 50), start, end, self.tags["lanes"])            
            #pygame.draw.line(screen, (100, 100, 100), start, end, self.tags["lanes"])
            #pygame.draw.polygon(screen, (200, 40, 250), (left, right, end))
            pygame.draw.polygon(screen, (200, 200, 200), (left, right, end))
        else:
            #pygame.draw.line(screen, (100, 0, 255), start, end, self.tags["lanes"])
            pygame.draw.line(screen, (255, 255, 255), start, end, self.tags["lanes"])