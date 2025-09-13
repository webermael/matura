import osmnx as ox
import json

city = "Zürich, Switzerland"

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
        "ways": []
        }


export["ways"] = {}

for start, end, data in G.edges(data=True):
    data["osmid"] = str(data["osmid"])
    if data["reversed"]:
        data["osmid"] += "r"
    if data["osmid"] not in export["ways"]:
        export["ways"][data["osmid"]] = {
        "id": data["osmid"],
        "reversed": data["reversed"],
        "lanes": int(data.get("lanes", 2)),
        "oneway": data.get("oneway", False),
        "speed": int(data.get("maxspeed", 50)),
        "nodes": [[str(start), str(end)]],
        "lengths": [data["length"]],
        "unconnected": []
        }
    else:
        if export["ways"][data["osmid"]]["nodes"][0][0] == str(end):
            if export["nodes"][str(end)]["street_count"] > 2:
                export["ways"][data["osmid"]]["nodes"].insert(0, [str(start), str(end)])
                export["ways"][data["osmid"]]["lengths"].insert(0, data["length"])
            
            else:
                export["ways"][data["osmid"]]["nodes"][0].insert(0, str(start))
                export["ways"][data["osmid"]]["lengths"][0] += data["length"]

        elif export["ways"][data["osmid"]]["nodes"][-1][-1] == str(start):
            if export["nodes"][str(start)]["street_count"] > 2:
                export["ways"][data["osmid"]]["nodes"].append([str(start), str(end)])
                export["ways"][data["osmid"]]["lengths"].append(data["length"])
            else:
                export["ways"][data["osmid"]]["nodes"][-1].append(str(end))
                export["ways"][data["osmid"]]["lengths"][-1] += data["length"]
        else:
            export["ways"][data["osmid"]]["unconnected"].append([str(start), str(end), data["length"]])

for id, way in export["ways"].items():
    while way["unconnected"]:
        for edge in way["unconnected"]:

            if export["ways"][id]["nodes"][0][0] == str(edge[1]):
                if export["nodes"][str(edge[1])]["street_count"] > 2:
                    export["ways"][id]["nodes"].insert(0, [str(edge[0]), str(edge[1])])
                    export["ways"][id]["lengths"].insert(0, edge[2])
                else:
                    export["ways"][id]["nodes"][0].insert(0, str(edge[0]))
                    export["ways"][id]["lengths"][0] += edge[2]
                way["unconnected"].remove(edge)

            elif export["ways"][id]["nodes"][-1][-1] == str(edge[0]):
                if export["nodes"][str(edge[0])]["street_count"] > 2:
                    export["ways"][id]["nodes"].append([str(edge[0]), str(edge[1])])
                    export["ways"][id]["lengths"].append(edge[2])
                else:
                    export["ways"][id]["nodes"][-1].append(str(edge[1]))
                    export["ways"][id]["lengths"][-1] += edge[2]
                way["unconnected"].remove(edge)

    export["ways"][id].pop("unconnected")
    for segment in range(len(way["nodes"])):
        export["nodes"][way["nodes"][segment][0]]["ways"].append([id, segment])

with open("matura\\new_prototype\\graph.json", "w") as f:
    json.dump(export, f, indent=2)
    f.close()