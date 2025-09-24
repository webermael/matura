import pygame
import json
import random
import math
import time

from Astar import Astar
from graph.way import Way
from graph.node import Node
from new_car import Car


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

def normalize_node_scores(node_dict:dict[Node,int]) -> dict[Node,float]:
    total:int = 0
    for score in node_dict.values():
        total += score
    return {node: score / total for node, score in node_dict.items()}

def weighted_choice(weighted_dict:dict[Node,float]) -> Node:
    start:float = random.random()
    for key, weight in weighted_dict.items():
        start -= weight
        if start <= 0:
            return key

nodes:dict[str,Node] = {id:Node(id, node["pos"], to_screen_space(node["pos"]), node["street_count"], node["ways"], node["ways_in"]) for id, node in file_content["nodes"].items()}
ways:dict[str,Way] = {id:Way(id, way["oneway"], way["lanes"], way["turns"], way["speed"], way["nodes"], way["weights"]) for id, way in file_content["ways"].items()}

start_nodes:dict[Node,float] = normalize_node_scores({node:ways[node.ways[0][0]].speed ** 2 for node in nodes.values() if node.street_count == 2 and len(node.ways) == 1 and (len(node.ways_in) == 0 or (len(node.ways_in) == 1 and not ways[node.ways[0][0]].oneway))})
end_nodes:dict[Node,float] = normalize_node_scores({node:ways[node.ways_in[0][0]].speed ** 2 for node in nodes.values() if node.street_count == 2 and len(node.ways_in) == 1 and (len(node.ways) == 0 or (len(node.ways) == 1 and not ways[node.ways_in[0][0]].oneway))})

astar = Astar(
    weighted_choice(start_nodes).id,
    weighted_choice(end_nodes).id
)
paths:dict[tuple[str,str],list[list[str]]] = {}
path_weights:dict[tuple[str,str],float] = {}

cars: list[Car] = []

pygame.init() 
screen:pygame.Surface = pygame.display.set_mode(screen_size)
clock:pygame.time.Clock = pygame.time.Clock()
edge_start:list[float] = None

 
car_timeout:float = 0.01
car_spawner:float = car_timeout

dt:float = 0.0
running:bool = True
selecting:bool = False
selection_start:list[float] = [0.0, 0.0]
while running:
    screen.fill((0, 0, 0))
    
    mouse = pygame.mouse.get_pos()
    min_dist = math.inf
    for node in nodes.values():
        if len(node.ways) > 0 and  math.hypot(mouse[0] - node.display_pos[0], mouse[1] - node.display_pos[1]) < min_dist:
            min_dist = math.hypot(mouse[0] - node.display_pos[0], mouse[1] - node.display_pos[1])
            highlight = node

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
        # selecting a start node (for edge selection)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[2]:
                if edge_start == None:
                    edge_start = highlight.id
                elif edge_start != None:
                    found = False
                    # checking if the selected edge (segment) exist in a way
                    for way in ways.values():
                        for segment in way.nodes:
                            if segment[0] == edge_start and segment[-1] == highlight.id:
                                found = True
                                print(way.id, way.nodes.index(segment))
                                input_direction = input("Enter turn restrictions (comma seperated): ").replace(" ", "").split(",")
                                if input_direction != [""]:
                                    way.turns = [[] for _ in way.nodes]
                                    way.turns[way.nodes.index(segment)] = input_direction
                                    file_content["ways"][way.id]["turns"] = [[] for _ in way.nodes]
                                    file_content["ways"][way.id]["turns"][way.nodes.index(segment)] = input_direction 
                                # set the turn values to the input and save them in the save data
                                print(way.turns)
                                break
                    if not found:
                        print("No edge found")
                    edge_start = None
    # drawing visible ways
    for way in ways.values():
        if way.is_visible:
            line:list[int] = []
            for segment in way.nodes:
                line += segment
            pygame.draw.lines(screen, (100, 100, 100), False, [nodes[node].display_pos for node in line], max(1, int(15 * scale)))

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

    # A* testing
    start = time.perf_counter()
    while time.perf_counter() - start < 0.015:
        astar.step(nodes, ways)
        if not astar.active:
            if astar.end in astar.explored_nodes and astar.start != astar.end:
                paths[(astar.start, astar.end)] = astar.explored_nodes[astar.end]["path"]
                path_weights[(astar.start, astar.end)] = start_nodes[nodes[astar.start]] + end_nodes[nodes[astar.end]]
                #cars.append(Car(nodes, ways, astar.explored_nodes[astar.end]["path"]))
            else:
                paths[(astar.start, astar.end)] = []
                path_weights[(astar.start, astar.end)] = 0
            astar.reset(
            weighted_choice(start_nodes).id,
            weighted_choice(end_nodes).id
            )
    #astar.render(screen, nodes, ways)

    car_spawner -= dt
    if car_spawner <= 0:
        if paths:
            path_nodes = weighted_choice(normalize_node_scores(path_weights))
            if path_nodes:
                cars.append(Car(nodes, ways, paths[path_nodes]))
        car_spawner %= car_timeout



    for car in cars[:]:
        car.update(nodes, ways, dt)
        car.render(screen, to_screen_space, scale)
        if not car.active:
            cars.remove(car)
    #pygame.draw.circle(screen, (255, 0, 255), highlight.display_pos, 5)

    dt = clock.tick() / 1000
    pygame.display.flip()
pygame.quit()