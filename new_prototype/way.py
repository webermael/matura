
# or edge idk
class Way:
    def __init__(self, id:int, lanes:int, speed:int, nodes:list[list[str]], lengths:list[float]):
        self.id:int = id
        self.lanes:int = lanes
        self.speed:int = speed
        self.nodes:list[list[str]] = nodes
        self.lengths:list[float]