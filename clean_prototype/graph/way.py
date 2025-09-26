from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from graph.node import Node
    from traffic.car import Car

class Way:
    def __init__(self, id:str, index:int, oneway:bool, lanes:int, turns:str, speed:int, nodes:list['Node'], length:list[float]):
        self.id:str = id
        self.index:int = index
        self.oneway:bool = oneway
        self.lanes:int = lanes
        self.turns:str = turns
        self.speed:int = speed
        self.nodes:list['Node'] = nodes
        self.display_way:list[list[float]] = [node.display_pos for node in self.nodes]
        self.cars:list['Car'] = []
        self.length:float = length
        self.is_visible:bool = True
    

    def test_visible(self):
        for node in self.nodes:
            if node.is_visible:
                self.is_visible = True
                return
        self.is_visible = False