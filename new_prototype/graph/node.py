

class Node:
    def __init__(self, id:int, pos:list[float], street_count:int, ways:list[dict[str, str|int]]):
        self.id:int = id
        self.pos:list[float] = pos
        self.street_count:int = street_count
        self.ways:list[dict[str, str|int]] = ways
        # -> [{"way_id: "3242346", "segment_index": 2}, {"way_id": "435325r", "segment_id": 0}]