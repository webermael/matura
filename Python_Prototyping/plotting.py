import pygame
import json
from node import Node
from waypoint import Waypoint
from edge import Edge
from way import Way
from car import Car
from edge_merger import EdgeMerger
from big_dijkstra import Dijkstra
import time
import random

with open("graph.json", "r") as file:
    file_content = json.load(file)
file.close()

screen_size = [1920, 1080]
screen_center = [screen_size[0] / 2, screen_size[1] / 2]

#transformation = [(min(screen_size) / (file_content["world"]["east"] - file_content["world"]["west"])), (min(screen_size) * (1 - 1 / (file_content["world"]["north"] - file_content["world"]["south"])))]
transformation = [(min(screen_size) / (file_content["world"]["east"] - file_content["world"]["west"])), -(min(screen_size) / (file_content["world"]["north"] - file_content["world"]["south"]))]

translation = [file_content["world"]["west"], 
            file_content["world"]["south"]]

def normalize(point: list[float]) -> list[float]:
    """
    Takes in coordinates from real world data and translates them to on screen data
    """
    return [
        (point[0] - translation[0]) * transformation[0],
        (point[1] - translation[1]) * transformation[1]
    ]

nodes = {int(node["id"]) : Node(int(node["id"]), normalize([node["x"], node["y"]]), node["edges"], node["edges_in"], node["all_edges"], node["tags"]) for node in file_content["nodes"].values()}
edges = {int(edge["id"]) : Edge(int(edge["id"]), edge["start_id"], edge["end_id"], edge["speed"], edge["length"], edge["tags"]) for edge in file_content["edges"]}
cars = []
ways = None
waypoints = None
EM = EdgeMerger()
D = None


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

EM.find_start(nodes)
timeout = 0
timer = timeout

dt = 0
running = True
while running:

    center = [
        -offset[0] + screen_center[0],
        -offset[1] + screen_center[1]
    ]
    transformation = [(min(screen_size) / (file_content["world"]["east"] - file_content["world"]["west"])), (min(screen_size) * (1 - 1 / (file_content["world"]["north"] - file_content["world"]["south"])))]
    translation = [file_content["world"]["west"], 
                file_content["world"]["south"]]
    
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if pygame.key.get_pressed()[pygame.K_UP]:
        zoom += dt * zoom
    if pygame.key.get_pressed()[pygame.K_DOWN]:
        zoom -= dt * zoom

    if pygame.key.get_pressed()[pygame.K_a]:
        offset[0] += dt * 500 / zoom
    if pygame.key.get_pressed()[pygame.K_d]:
        offset[0] -= dt * 500 / zoom
    if pygame.key.get_pressed()[pygame.K_w]:
        offset[1] += dt * 500 / zoom
    if pygame.key.get_pressed()[pygame.K_s]:
        offset[1] -= dt * 500 / zoom


    #for edge in edges.values():
    #    edge.render(screen, center, zoom, offset, nodes, screen_size)

    for car in cars:
        car.update(nodes, edges, waypoints, dt)
        car.render(screen, center, zoom, offset, screen_size, nodes)

    timer -= dt
    start = time.perf_counter()
    while EM.active and time.perf_counter() - start < 0.1:
        EM.step(nodes, edges)        
    #if timer <= 0:
    #    EM.step(nodes, edges)
    #    timer += timeout


    if D != None:
        start = time.perf_counter()
        while D.active and time.perf_counter() - start < 0.01:
            D.step()
        D.render(screen, center, zoom, offset, nodes)
        if not D.active:
            D = Dijkstra(waypoints, ways, D.end, random.choice([id for id, wp in waypoints.items() if len(wp.edges) >= 2]))

    if not EM.active:
        if ways == None:
            data = EM.get_results()
            waypoints = {wp_id: Waypoint(wp_id, waypoint_edges) for wp_id, waypoint_edges in data["waypoints"].items()}
            ways = [Way(way["nodes"], way["edges"], way["speed"], way["length"], way["twoway"]) for way in data["ways"]]
            D = Dijkstra(waypoints, ways, random.choice([id for id, wp in waypoints.items() if len(wp.edges) == 2]), random.choice([id for id, wp in waypoints.items() if len(wp.edges) == 2]))
            #cars = [Car(random.choice([id for id, wp in waypoints.items() if len(wp.edges) >= 2]), random.choice([id for id, wp in waypoints.items() if len(wp.edges) >= 2]), nodes, waypoints, ways) for i in range(1)]

    #for node in nodes.values():
    #    node.render(screen, center, zoom, offset, screen_size)
    EM.render(nodes, edges, screen, center, zoom, offset, screen_size)


    dt = clock.tick() / 1000
    pygame.display.flip()

pygame.quit()