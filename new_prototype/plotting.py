import pygame
import json
import random
import time
from graph.way import Way
from graph.node import Node
from Astar import Astar


def normalize(point: list[float]) -> list[float]:
    """
    Takes in coordinates from real world data and translates them to on screen data
    """
    return [
        (point[0] - translation[0]) * transformation[0],
        (point[1] - translation[1]) * transformation[1]
    ]


def scale(point: list[float], center: list[float], factor: float, offset: list[float]) -> list[float]:
    return [
        (point[0] - center[0]) * factor + center[0] + offset[0],
        (point[1] - center[1]) * factor + center[1] + offset[1]
    ]


with open("matura\\new_prototype\\graph.json", "r") as file:
    file_content = json.load(file)
file.close()

screen_size = [1920, 1080]
screen_center = [screen_size[0] / 2, screen_size[1] / 2]

transformation = [(min(screen_size) / (file_content["bounds"]["east"] - file_content["bounds"]["west"])), -(min(screen_size) / (file_content["bounds"]["north"] - file_content["bounds"]["south"]))]
translation = [file_content["bounds"]["west"], 
            file_content["bounds"]["south"]]


nodes:dict[str,Node] = {id:Node(id, node["pos"], node["street_count"], node["ways"]) for id, node in file_content["nodes"].items()}
ways:dict[str,Way] = {id:Way(id, way["lanes"], way["speed"], way["nodes"], way["weights"]) for id, way in file_content["ways"].items()}
a_star = Astar(random.choice(list(id for id, node in nodes.items() if node.ways != [])), random.choice(list(id for id, node in nodes.items() if node.ways == [] and node.street_count == 1)))

pygame.init()
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()
zoom = 1
offset = [480, 1080]


dt = 0
running = True
starttime = time.perf_counter()
ways_found = 0
while running:
    center = [-offset[0] + screen_center[0], -offset[1] + screen_center[1]]
    transformation = [(min(screen_size) / (file_content["bounds"]["east"] - file_content["bounds"]["west"])), (min(screen_size) * (1 - 1 / (file_content["bounds"]["north"] - file_content["bounds"]["south"])))]
    translation = [file_content["bounds"]["west"], file_content["bounds"]["south"]]
    
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if pygame.key.get_pressed()[pygame.K_UP]:
        zoom += dt * zoom
    if pygame.key.get_pressed()[pygame.K_DOWN]:
        zoom -= dt * zoom
    
    for way in ways.values():
        line = []
        for segment in way.nodes:
            line += segment
        pygame.draw.lines(screen, (255, 255, 255), False, [scale(normalize(nodes[node].pos), center, zoom, offset) for node in line], 2*int(way.lanes))

    start = time.perf_counter()
    while a_star.active and time.perf_counter() - start < 1:
        a_star.step(nodes, ways)
        if not a_star.active:
            if a_star.end in a_star.explored_nodes:
                ways_found += 1
            a_star.start = random.choice(list(id for id, node in nodes.items() if node.ways != []))
            a_star.end = random.choice(list(id for id, node in nodes.items() if node.street_count > 2))
            a_star.active_nodes = [a_star.start]
            a_star.explored_nodes = {a_star.start: {"weight": 0, "path":[]}}
            a_star.time_searching = 0
            a_star.active = True
    running = False
    print(f"\nTime elapsed: {round(time.perf_counter() - starttime, 3)}s\nTotal ways found: {ways_found}")

    a_star.render(screen, scale, normalize, nodes, center, zoom, offset)

    if pygame.key.get_pressed()[pygame.K_a]:
        offset[0] += dt * 500 / zoom
    if pygame.key.get_pressed()[pygame.K_d]:
        offset[0] -= dt * 500 / zoom
    if pygame.key.get_pressed()[pygame.K_w]:
        offset[1] += dt * 500 / zoom
    if pygame.key.get_pressed()[pygame.K_s]:
        offset[1] -= dt * 500 / zoom

    dt = clock.tick() / 1000
    pygame.display.flip()
pygame.quit()