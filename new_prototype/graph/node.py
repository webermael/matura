

class Node:
    def __init__(self, id:str, pos:list[float], street_count:int, ways:list[dict[str, str|int]], ways_in:list[str|int]):
        self.id:str = id
        self.pos:list[float] = pos
        self.street_count:int = street_count
        self.ways:list[list[str|int]] = ways
        # -> [{"way_id: "3242346", "segment_index": 2}, {"way_id": "435325r", "segment_id": 0}]
        self.ways_in:list[list[str|int]] = ways_in