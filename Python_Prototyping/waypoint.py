from node import Node

class Waypoint:
    def __init__(self, id: int, edges: list[int]):
        self.id: int = id
        self.edges: list[int] = edges


    def _scale(self, center: list[float], zoom: float, offset: list[float], nodes:dict[int,Node]) -> list[float]:
        return nodes[self.id]._scale(center, zoom, offset)