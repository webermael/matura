class Plot:
    def __init__(self, screen_size:list[float], screen_center:list[float], bounds:dict[str,float]):
        self.screen_size:list[float] = screen_size
        self.screen_center:dict[str,float] = screen_center
        self.bounds:list[float] = bounds
        self.translation:list[float] = [self.bounds["west"], self.bounds["south"]]
        self.graph_size:list[float] = [self.bounds["east"] - self.bounds["west"], self.bounds["north"] - self.bounds["south"]]
        self.scale:float = min(self.screen_size[0] / self.graph_size[0], self.screen_size[1] / self.graph_size[1])

    def reset_values(self):
        self.translation:list[float] = [self.bounds["west"], self.bounds["south"]]
        self.graph_size:list[float] = [self.bounds["east"] - self.bounds["west"], self.bounds["north"] - self.bounds["south"]]
        self.scale:float = min(self.screen_size[0] / self.graph_size[0], self.screen_size[1] / self.graph_size[1])

    def set_values(self, top:float, left:float, bottom:float, right:float):
        if abs(bottom - top) > 0 and abs(right - left) > 0:
            temp_translation = self.from_screen_space([left, bottom])
            temp_corner = self.from_screen_space([right, top])
            self.translation = temp_translation
            self.graph_size = [temp_corner[0] - temp_translation[0], temp_corner[1] - temp_translation[1]]
            self.scale = min(self.screen_size[0] / self.graph_size[0], self.screen_size[1] / self.graph_size[1])

    def to_screen_space(self, position:list[float]) -> list[float]:
        return [
            (position[0] - self.translation[0] - self.graph_size[0] / 2) * self.scale + self.screen_center[0],
            (position[1] - self.translation[1] - self.graph_size[1] / 2) * -self.scale + self.screen_center[1]
        ]

    def from_screen_space(self, position:list[float]) -> list[float]:
        return [
            (position[0] - self.screen_center[0]) / self.scale + self.translation[0] + self.graph_size[0] / 2,
            (position[1] - self.screen_center[1]) / -self.scale + self.translation[1] + self.graph_size[1] / 2
        ]