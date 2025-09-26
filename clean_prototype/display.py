from graph.node import Node
from graph.way import Way
from graph.plot import Plot

class Display:
    def __init__(self, plot:Plot):
        self.plot:Plot = plot



    def reset_view(self, nodes:list[Node], ways:list[Way]):
        self.plot.reset_values()
        for node in nodes:
            node.display_pos = self.plot.to_screen_space(node.pos)
            node.test_visible(self.plot.screen_size)
        for way in ways:
            way.test_visible()
            way.display_way = [node.display_pos for node in way.nodes]
    
    def set_view(self, nodes:list[Node], ways:list[Way], rect_value:list[float]):
        self.plot.set_values(rect_value[0], rect_value[1], rect_value[2], rect_value[3])
        for node in nodes:
            node.display_pos = self.plot.to_screen_space(node.pos)
            node.test_visible(self.plot.screen_size)
        for way in ways:
            way.test_visible()
            way.display_way = [node.display_pos for node in way.nodes]