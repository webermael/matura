import pygame
import json
import time

from graph.node import Node
from graph.way import Way
from graph.plot import Plot
from display import Display

with open("matura\\new_prototype\\Aarau.json", "r") as file:
    file_content:dict = json.load(file)
file.close()

screen_size:list[int] = [1920, 1080]
screen_center:list[int] = [screen_size[0] // 2, screen_size[1] // 2]

display = Display(Plot(screen_size, screen_center, file_content["bounds"]))


nodes:dict[str,Node] = {id:Node(id, node["pos"], display.plot.to_screen_space(node["pos"]), node["street_count"]) for id, node in file_content["nodes"].items()}
ways:list[Way] = [Way(id, way["nodes"].index(segment), way["oneway"], way["lanes"], way["turns"][way["nodes"].index(segment)], way["speed"], [nodes[id] for id in segment], way["weights"][way["nodes"].index(segment)]) for id, way in file_content["ways"].items() for segment in way["nodes"]]
nodes:list[Node] = list(nodes.values())
for way in ways:
    way.nodes[0].ways_out.append(way)
    way.nodes[-1].ways_in.append(way)


pygame.init() 
screen:pygame.Surface = pygame.display.set_mode(screen_size)
clock:pygame.time.Clock = pygame.time.Clock()

dt:float = 0.0
running:bool = True
selecting:bool = False
selection_start:list[float] = [0.0, 0.0]
rect_value:list[float]

while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # reset zoom
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                display.reset_view(nodes, ways)
    
    for way in ways:
        if way.is_visible:
            pygame.draw.lines(screen, (100, 100, 100), False, way.display_way, max(1, way.lanes*int(12 * display.plot.scale)))

    # selection/zoom handling + drawing
    if pygame.mouse.get_pressed()[0]:
        mouse_pos = list(pygame.mouse.get_pos())
        if not selecting:
            selecting = True
            selection_start = mouse_pos
        # create rectangle with selection data
        t = min(selection_start[1], mouse_pos[1])
        l = min(selection_start[0], mouse_pos[0])
        b = max(selection_start[1], mouse_pos[1])
        r = max(selection_start[0], mouse_pos[0])
        rect_value = [t, l, b, r]
        pygame.draw.rect(screen, (255, 0, 0), ((l, t), (r-l, b-t)), 2)
    else:
        if selecting:
            selecting = False
            display.set_view(nodes, ways, rect_value)

    dt = clock.tick() / 1000
    pygame.display.flip()
pygame.quit()