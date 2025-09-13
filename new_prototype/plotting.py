import pygame
import json
import random

with open("matura\\new_prototype\\graph.json", "r") as file:
    file_content = json.load(file)
file.close()

screen_size = [1920, 1080]
screen_center = [screen_size[0] / 2, screen_size[1] / 2]

transformation = [(min(screen_size) / (file_content["bounds"]["east"] - file_content["bounds"]["west"])), -(min(screen_size) / (file_content["bounds"]["north"] - file_content["bounds"]["south"]))]
translation = [file_content["bounds"]["west"], 
            file_content["bounds"]["south"]]

nodes = file_content["nodes"]

ways = file_content["ways"]

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
    
    for id, way in ways.items():
        line = []
        for segment in way["nodes"]:
            line += segment
        #pygame.draw.lines(screen, (255 - min(255, 255 / 120 * way["speed"]), min(255, 255 / 120 * way["speed"]), 0), False, [scale(normalize(nodes[node]["pos"]), center, zoom, offset) for node in line], 2*int(way["lanes"]))
        pygame.draw.lines(screen, (255, 255, 255), False, [scale(normalize(nodes[node]["pos"]), center, zoom, offset) for node in line], 2*int(way["lanes"]))

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