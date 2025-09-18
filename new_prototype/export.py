import osmnx as ox
import json
import re

city = "Aargau, Switzerland"

G = ox.graph_from_place(city, network_type="drive", simplify=False)

lats = [data["y"] for _, data in G.nodes(data=True)]
lons = [data["x"] for _, data in G.nodes(data=True)]

north, south = max(lats), min(lats)
east, west = max(lons), min(lons)



export = {}
export["bounds"] = {
    "north": north,
    "east": east,
    "south": south,
    "west": west
}

export["nodes"] = {}
for id, data in G.nodes(data=True):
    export["nodes"][str(id)] = {
        "pos": (data["x"], data["y"]),
        "street_count": data["street_count"],
        "ways": [],
        "ways_in": []
        }


export["ways"] = {}

for start, end, data in G.edges(data=True):
    data["osmid"] = str(data["osmid"])
    if data["reversed"]:
        data["osmid"] += "r"
    print(data.get("maxspeed", "50"))
    speed = int(''.join(re.findall(r'\d+', str(data.get("maxspeed", "50").replace("rural", "80").replace("urban", "50").replace("signals", "50")))))
    if data["osmid"] not in export["ways"]:
        export["ways"][data["osmid"]] = {
        "id": data["osmid"],
        "reversed": data["reversed"],
        "lanes": int(data.get("lanes", 2)),
        "oneway": data.get("oneway", False),
        "speed": speed,
        "nodes": [[str(start), str(end)]],
        "weights": [data["length"] / speed],
        "unconnected": []
        }
    else:
        if export["ways"][data["osmid"]]["nodes"][0][0] == str(end):
            if export["nodes"][str(end)]["street_count"] > 2:
                export["ways"][data["osmid"]]["nodes"].insert(0, [str(start), str(end)])
                export["ways"][data["osmid"]]["weights"].insert(0, data["length"] / speed)
            
            else:
                export["ways"][data["osmid"]]["nodes"][0].insert(0, str(start))
                export["ways"][data["osmid"]]["weights"][0] += data["length"] / speed

        elif export["ways"][data["osmid"]]["nodes"][-1][-1] == str(start):
            if export["nodes"][str(start)]["street_count"] > 2:
                export["ways"][data["osmid"]]["nodes"].append([str(start), str(end)])
                export["ways"][data["osmid"]]["weights"].append(data["length"] / speed)
            else:
                export["ways"][data["osmid"]]["nodes"][-1].append(str(end))
                export["ways"][data["osmid"]]["weights"][-1] += data["length"] / speed
        else:
            export["ways"][data["osmid"]]["unconnected"].append([str(start), str(end), data["length"] / speed])

for id, way in export["ways"].items():
    while way["unconnected"]:
        connected = False
        for edge in way["unconnected"]:

            if export["ways"][id]["nodes"][0][0] == str(edge[1]):
                if export["nodes"][str(edge[1])]["street_count"] > 2:
                    export["ways"][id]["nodes"].insert(0, [str(edge[0]), str(edge[1])])
                    export["ways"][id]["weights"].insert(0, edge[2])
                else:
                    export["ways"][id]["nodes"][0].insert(0, str(edge[0]))
                    export["ways"][id]["weights"][0] += edge[2]
                way["unconnected"].remove(edge)
                connected = True

            elif export["ways"][id]["nodes"][-1][-1] == str(edge[0]):
                if export["nodes"][str(edge[0])]["street_count"] > 2:
                    export["ways"][id]["nodes"].append([str(edge[0]), str(edge[1])])
                    export["ways"][id]["weights"].append(edge[2])
                else:
                    export["ways"][id]["nodes"][-1].append(str(edge[1]))
                    export["ways"][id]["weights"][-1] += edge[2]
                way["unconnected"].remove(edge)
                connected = True
        if not connected:
            way["unconnected"] = []

    export["ways"][id].pop("unconnected")
    for segment in range(len(way["nodes"])):
        export["nodes"][way["nodes"][segment][0]]["ways"].append([id, segment])
        export["nodes"][way["nodes"][segment][-1]]["ways_in"].append([id, segment])

with open("matura\\new_prototype\\graph.json", "w") as f:
    json.dump(export, f, indent=2)
    f.close()