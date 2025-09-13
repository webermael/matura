import pygame
import json
import random
from graph.way import Way
from graph.node import Node

with open("matura\\new_prototype\\graph.json", "r") as file:
    file_content = json.load(file)
file.close()

screen_size = [1920, 1080]
screen_center = [screen_size[0] / 2, screen_size[1] / 2]

transformation = [(min(screen_size) / (file_content["bounds"]["east"] - file_content["bounds"]["west"])), -(min(screen_size) / (file_content["bounds"]["north"] - file_content["bounds"]["south"]))]
translation = [file_content["bounds"]["west"], 
            file_content["bounds"]["south"]]

node_objects:dict[str,Node] = {id:Node(id, node["pos"], node["street_count"], node["ways"]) for id, node in file_content["nodes"].items()}
way_objects:dict[str,Way] = {id:Way(id, way["lanes"], way["speed"], way["nodes"], way["lengths"]) for id, way in file_content["ways"].items()}

def normalize(point: list[float]) -> list[float]:
    """
    Takes in coordinates from real world data and translates them to on screen data
    """
    return [
        (point[0] - translation[0]) * transformation[0],
        (point[1] - translation[1]) * transformation[1]
    ]


pygame.init()
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()
zoom = 1
offset = [480, 1080]

def scale(point: list[float], center: list[float], factor: float, offset: list[float]) -> list[float]:
    return [
        (point[0] - center[0]) * factor + center[0] + offset[0],
        (point[1] - center[1]) * factor + center[1] + offset[1]
    ]


dt = 0
running = True
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
    
    for way in way_objects.values():
        line = []
        for segment in way.nodes:
            line += segment
        pygame.draw.lines(screen, (255, 255, 255), False, [scale(normalize(node_objects[node].pos), center, zoom, offset) for node in line], 2*int(way.lanes))


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