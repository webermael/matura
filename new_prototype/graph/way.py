
# or edge idk
class Way:
    def __init__(self, id:int, oneway:bool, lanes:int, speed:int, nodes:list[list[str]], weights:list[float]):
        self.id:int = id
        self.oneway:bool = oneway
        self.lanes:int = lanes
        self.speed:int = speed
        self.nodes:list[list[str]] = nodes
        self.weights:list[float] = weights
    

    def get_segment_end(self, segment):
        return self.nodes[segment][-1]

    def get_segment_weight(self, segment):
        return self.lengths[segment] / self.speed