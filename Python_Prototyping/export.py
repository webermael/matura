import osmnx as ox
import json

city = "Zürich, Switzerland"
ox.settings.all_oneway=True
G = ox.graph_from_place(city, network_type="drive", simplify=False)

print("graph loaded")
gdf = ox.geocode_to_gdf(city)
west, south, east, north = gdf.total_bounds
nodes, edges = ox.graph_to_gdfs(G)
print("data loaded")
data: dict = {}
data["world"] = {
        "west": west,
        "south": south,
        "east": east,
        "north": north
    }
data["nodes"] = {
        node :
        {
        "id": node,
        "x": data["x"],
        "y": data["y"],
        "edges": [],
        "edges_in": [],
        "all_edges": [],
        "tags": {
            "intersection": data.get("street_count") > 2,
            "dead_end": data.get("street_count", 2) in (0, 1)
            }
        } 
    for node, data in G.nodes(data=True)
    }

data["edges"] = [
        {
        "start_id": start,
        "end_id": end,
        "speed": data.get("maxspeed", 50),
        "length": data.get("length"),
        "tags": {
            "twoway": data.get("oneway", "no") == "no" and not data.get("junction", False) == "roundabout",
            "roundabout": data.get("junction", False) == "roundabout",
            "lanes": data.get("lanes", "2"),
            }
        }
    for start, end, data in G.edges(data=True)
    ]


def get_end(edge_id, start_id):
    if start_id == data["edges"][edge_id]["start_id"]:
        return data["edges"][edge_id]["end_id"]
    elif start_id == data["edges"][edge_id]["end_id"]:
        return data["edges"][edge_id]["start_id"]


edge_id = 0
for edge in data["edges"]:
    edge["id"] = edge_id
    edge_id += 1
    edge["speed"] = str(edge["speed"]).replace(" mph", "")
    edge["speed"] = edge["speed"].replace("walk", "3")
    edge["speed"] = edge["speed"].replace("FR:zone", "")
    edge["speed"] = edge["speed"].replace("IT:urban", "50")
    edge["speed"] = edge["speed"].replace("AT:urban", "50")
    edge["speed"] = int(edge["speed"].replace("AT:rural", "80"))
    edge["tags"]["lanes"] = int(edge["tags"]["lanes"].replace("2;1", "2"))

    data["nodes"][edge["start_id"]]["edges"].append(edge["id"])
    data["nodes"][edge["end_id"]]["edges_in"].append(edge["id"])
    data["nodes"][edge["start_id"]]["all_edges"].append(edge["id"])
    data["nodes"][edge["end_id"]]["all_edges"].append(edge["id"])
    if edge["tags"]["twoway"]:
        data["nodes"][edge["start_id"]]["edges_in"].append(edge["id"])
        data["nodes"][edge["end_id"]]["edges"].append(edge["id"])


print(f"Nodes: {len(data['nodes'])} \nEdges: {len(data['edges'])}")
with open("matura\\python_prototyping\\graph.json", "w") as f:
    json.dump(data, f, indent=2)
    f.close()