from node import Node
from edge import Edge
import pygame
import random

class EdgeMerger:
    def __init__(self):
        self.node_queue: list[int] = []
        self.explored_waypoints: dict[int, list[int]] = {}
        self.processing_nodes: dict[int, list[dict[str, list[int]|int]]] = {}
        self.ways: list[dict[str, list[int]|int]] = []
        self.waypoints: dict[int, list[int]] = {}
        self.way_colors: list[list[int]] = []
        self.active: bool = True


    def find_start(self, nodes: dict[int, Node]):
        for id, node in nodes.items():
            if node.tags["intersection"]:
                self.node_queue.append(id)
                self.explored_nodes = {id: [id]}
                nodes[id].tags["in_queue"] = True
                break



    def step(self, nodes: dict[int, Node], edges: dict[int, Edge]):
        if not self.active:
            return
        node = self.node_queue[0]
        if node not in self.processing_nodes:
            if not self.explored_waypoints.get(node):
                self.explored_waypoints[node] = []
            self.processing_nodes[node] = []
            for edge in nodes[node].all_edges:
                if edges[edge].get_end(node) not in self.explored_waypoints[node]:
                    self.processing_nodes[node].append(
                        {
                            "nodes": [node, edges[edge].get_end(node)],
                            "edges": [edge],
                            "length": edges[edge].length,
                            "speed": edges[edge].speed * edges[edge].length,
                            "twoway": True
                        })
                    
            #self.processing_nodes[node] = [[node, edges[edge].get_end(node)] for edge in nodes[node].all_edges if edges[edge].get_end(node) not in self.explored_waypoints[node]]
            for search_way in self.processing_nodes[node]:
                nodes[search_way["nodes"][-1]].tags["searching"] = True
        nodes[node].tags["active"] = True
        nodes[node].tags["in_queue"] = False

        #for way in self.processing_nodes[node]:
        if len(self.processing_nodes[node]) > 0:
            way = self.processing_nodes[node][0]
            if len(nodes[way["nodes"][-1]].all_edges) != 2 or edges[nodes[way["nodes"][-1]].all_edges[0]].tags["twoway"] != edges[nodes[way["nodes"][-1]].all_edges[1]].tags["twoway"]:
                self.node_queue.append(way["nodes"][-1])
                self.explored_waypoints[node].append(way["nodes"][-1])
                if not self.explored_waypoints.get(way["nodes"][-1]):
                    self.explored_waypoints[way["nodes"][-1]] = []
                self.explored_waypoints[way["nodes"][-1]].append(node)
                if node != way["nodes"][-2]:
                    self.explored_waypoints[way["nodes"][-1]].append(way["nodes"][-2])
                nodes[way["nodes"][-1]].tags["searching"] = False
                nodes[way["nodes"][-1]].tags["in_queue"] = True
                way["speed"] /= way["length"]
                if not edges[way["edges"][0]].tags["twoway"]:
                    way["twoway"] = False
                    if way["nodes"][0] != edges[way["edges"][0]].start_id:
                        way["nodes"].reverse()
                        way["edges"].reverse()
                    self.way_colors.append([(255 - node * 0 / len(way["edges"]), node * 255 / len(way["edges"]), 0) for node in range(len(way["nodes"]) - 1)])
                else:
                    self.way_colors.append([random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)])
                self.ways.append(way)
        
                if way["nodes"][0] not in self.waypoints:
                    self.waypoints[way["nodes"][0]] = [len(self.ways) - 1]
                else:
                    self.waypoints[way["nodes"][0]].append(len(self.ways) - 1)

                if way["nodes"][-1] not in self.waypoints:
                    if way["twoway"]:
                        self.waypoints[way["nodes"][-1]] = [len(self.ways) - 1]
                    else:
                        self.waypoints[way["nodes"][-1]] = []
                elif way["twoway"]:
                    self.waypoints[way["nodes"][-1]].append(len(self.ways) - 1)

                
                self.processing_nodes[node].remove(way)

            else:
                for new_edge in nodes[way["nodes"][-1]].all_edges:
                    new_node = edges[new_edge].get_end(way["nodes"][-1])
                    if len(nodes[new_node].all_edges) >= 0 and (new_node not in way["nodes"] or (new_node == way["nodes"][0] and len(way["nodes"]) > 3)):
                        nodes[way["nodes"][-1]].tags["searching"] = False
                        nodes[way["nodes"][-1]].tags["in_way"] = True
                        way["nodes"].append(new_node)
                        way["edges"].append(new_edge)
                        way["length"] += edges[new_edge].length
                        way["speed"] += edges[new_edge].speed * edges[new_edge].length
                        nodes[way["nodes"][-1]].tags["searching"] = True

        if len(self.processing_nodes[node]) == 0:
            self.node_queue.remove(node)
            nodes[node].tags["active"] = False
            if len(self.node_queue) == 0:
                self.active = False


    def get_results(self):
        return {"waypoints": self.waypoints, "ways": self.ways}


    def render(self, nodes: dict[int, Node], edges, screen, center, zoom, offset, screen_size):
        #for waypoint, targets in self.explored_waypoints.items():
        #    for point in targets:
        #        if len(nodes[point].all_edges) != 2:
        #            pygame.draw.line(screen, (255, 255, 0), nodes[waypoint]._scale(center, zoom, offset), nodes[point]._scale(center, zoom, offset), 3)
        for way in self.ways:
            if not way["twoway"]:
                [pygame.draw.line(screen, self.way_colors[self.ways.index(way)][node], nodes[way["nodes"][node]]._scale(center, zoom, offset), nodes[way["nodes"][node+1]]._scale(center, zoom, offset), 4*edges[way["edges"][node]].tags["lanes"]) for node in range(len(way["nodes"]) - 1)]
            else:
                pygame.draw.lines(screen, (0, 255, 0), False, [nodes[node]._scale(center, zoom, offset) for node in way["nodes"]], 4)
