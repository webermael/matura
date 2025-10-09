from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from graph.way import Way

class Node:
    def __init__(self, id:str, pos:list[float], street_count:int):
        self.id:str = id
        self.pos:list[float] = pos
        self.street_count:int = street_count
        self.ways_out:list['Way'] = []
        self.ways_in:list['Way'] = []
        self.is_visible:bool = True
        self.claimed_car:dict[list[float]] = {}

    def test_visible(self, screen_size:list[int]):
        if 0 < self.display_pos[0] < screen_size[0] and 0 < self.display_pos[1] < screen_size[1]:
            self.is_visible = True
        else:
            self.is_visible = False