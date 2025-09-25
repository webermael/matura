import pygame
import json

from graph.node import Node
from graph.way import Way


with open("matura\\new_prototype\\Aarau.json", "r") as file:
    file_content:dict = json.load(file)
file.close()

screen_size:list[int] = [1920, 1080]
screen_center:list[int] = [screen_size[0] // 2, screen_size[1] // 2]


translation:list[float] = [file_content["bounds"]["west"], file_content["bounds"]["south"]]
graph_size:list[float] = [file_content["bounds"]["east"] - file_content["bounds"]["west"], file_content["bounds"]["north"] - file_content["bounds"]["south"]]
scale:float = min(screen_size[0] / graph_size[0], screen_size[1] / graph_size[1])

def to_screen_space(position:list[float]) -> list[float]:
    return [
        (position[0] - translation[0] - graph_size[0] / 2) * scale + screen_center[0],
        (position[1] - translation[1] - graph_size[1] / 2) * -scale + screen_center[1]
    ]

def from_screen_space(position:list[float]) -> list[float]:
    return [
        (position[0] - screen_center[0]) / scale + translation[0] + graph_size[0] / 2,
        (position[1] - screen_center[1]) / -scale + translation[1] + graph_size[1] / 2
    ]


nodes:dict[str,Node] = {id:Node(id, node["pos"], to_screen_space(node["pos"]), node["street_count"], node["ways"], node["ways_in"]) for id, node in file_content["nodes"].items()}
ways:dict[str,Way] = {id:Way(id, way["oneway"], way["lanes"], way["turns"], way["speed"], way["nodes"], way["weights"]) for id, way in file_content["ways"].items()}


pygame.init() 
screen:pygame.Surface = pygame.display.set_mode(screen_size)
clock:pygame.time.Clock = pygame.time.Clock()


dt:float = 0.0
running:bool = True
selecting:bool = False
selection_start:list[float] = [0.0, 0.0]

while running:
    screen.fill((0, 0, 0))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # reset zoom
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                translation = [file_content["bounds"]["west"], file_content["bounds"]["south"]]
                graph_size = [file_content["bounds"]["east"] - file_content["bounds"]["west"], file_content["bounds"]["north"] - file_content["bounds"]["south"]]
                scale = min(screen_size[0] / graph_size[0], screen_size[1] / graph_size[1])
                # update values in graph objects
                for node in nodes.values():
                    node.display_pos = to_screen_space(node.pos)
                    node.test_visible(screen_size)
                for way in ways.values():
                    way.test_visible(nodes)
    
    for way in ways.values():
        if way.is_visible:
            line:list[int] = []
            for segment in way.nodes:
                line += segment
                for node in segment:
                    if nodes[node].is_visible:
                        pygame.draw.circle(screen, (100, 100, 100), nodes[node].display_pos, way.lanes*6*scale)
            pygame.draw.lines(screen, (100, 100, 100), False, [nodes[node].display_pos for node in line], max(1, way.lanes*int(12 * scale)))



    # selection/zoom handling + drawing
    if pygame.mouse.get_pressed()[0]:
        if not selecting:
            selecting = True
            selection_start = list(pygame.mouse.get_pos())
        mouse_pos = list(pygame.mouse.get_pos())
        selection_size = [mouse_pos[0] - selection_start[0], mouse_pos[1] - selection_start[1]]
        # create rectangle with selection data
        l = min(selection_start[0], selection_start[0] + selection_size[0])
        r = max(selection_start[0], selection_start[0] + selection_size[0])
        t = min(selection_start[1], selection_start[1] + selection_size[1])
        b = max(selection_start[1], selection_start[1] + selection_size[1])
        rect_value = [l, t, r, b]
        pygame.draw.rect(screen, (255, 0, 0), ((l, t), (r-l, b-t)), 2)
    else:
        if selecting:
            selecting = False
            # save new zoom settings
            offset = from_screen_space((rect_value[0], rect_value[3]))
            selection_corner = from_screen_space((rect_value[2], rect_value[1]))
            size = [selection_corner[0] - offset[0], selection_corner[1] - offset[1]]
            
            # only apply if an actual area was selected 
            if size[0] > 0 and size[1] > 0:
                translation = offset
                graph_size = size

                scale = min(screen_size[0] / graph_size[0], screen_size[1] / graph_size[1])
                # apply changes to mouse effects
                for node in nodes.values():
                    node.display_pos = to_screen_space(node.pos)
                    node.test_visible(screen_size)
                for way in ways.values():
                    way.test_visible(nodes)

    dt = clock.tick() / 1000
    pygame.display.flip()
pygame.quit()