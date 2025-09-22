from graph.node import Node
# or edge idk
class Way:
    def __init__(self, id:int, oneway:bool, lanes:int, turns:str, speed:int, nodes:list[list[str]], weights:list[float]):
        self.id:int = id
        self.oneway:bool = oneway
        self.lanes:int = lanes
        self.turns:str = turns
        self.speed:int = speed
        self.nodes:list[list[str]] = nodes
        self.cars:list[list] = [[] for i in nodes]
        self.weights:list[float] = weights
        self.is_visible:bool = True
    

    def test_visible(self, screen_size:list[int], nodes:dict[str,Node]):
        self.is_visible = False
        for segment in self.nodes:
            for node in segment:
                if 0 < nodes[node].display_pos[0] < screen_size[0] and 0 < nodes[node].display_pos[1] < screen_size[1]:
                    self.is_visible = True
                    break

    def get_segment_end(self, segment):
        return self.nodes[segment][-1]

    def get_segment_weight(self, segment):
        return self.lengths[segment] / self.speed