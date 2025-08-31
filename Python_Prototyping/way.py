import pygame

class Way:
    def __init__(self, nodes:list[int], edges:list[int], speed:float, length:int, tags:dict[str,int|bool]):
        self.nodes = nodes
        self.start_id = nodes[0]
        self.end_id = nodes[-1]
        self.edges = edges
        self.speed: float = speed
        self.length: float = length
        self.tags: dict[str, bool|int] = tags


    def get_end(self, start_id: int):
        if start_id == self.start_id:
            return self.end_id
        elif start_id == self.end_id:
            return self.start_id
        
    
    def render(self ,screen, nodes, center, zoom, offset):
        pygame.draw.lines(screen, (0, 255, 255), False, [nodes[node]._scale(center, zoom, offset) for node in self.nodes], 4)