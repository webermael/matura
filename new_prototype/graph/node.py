

class Node:
    def __init__(self, id:str, pos:list[float], display_pos:list[float], street_count:int, ways:list[dict[str, str|int]], ways_in:list[str|int]):
        self.id:str = id
        self.pos:list[float] = pos
        self.street_count:int = street_count
        self.ways:list[list[str|int]] = ways
        # -> [{"way_id: "3242346", "segment_index": 2}, {"way_id": "435325r", "segment_id": 0}]
        self.ways_in:list[list[str|int]] = ways_in
        self.display_pos:list[float] = display_pos
        self.is_visible:bool = True

    def test_visible(self, screen_size:list[int]):
        if 0 < self.display_pos[0] < screen_size[0] and 0 < self.display_pos[1] < screen_size[1]:
            self.is_visible = True
        else:
            self.is_visible = False