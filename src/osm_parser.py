import osmnx as ox
import json
import re
import math
import pyproj
import sys

def parse_maxspeed(speed_tag):
    # remove any letters and replace "urban", "walk", etc. with speeds
    s = str(speed_tag).lower()
    s = s.replace("rural", "80").replace("urban", "50").replace("walk", "10").replace("signals", "50")
    s = re.sub(r'^[a-z]{2}:', '', s)
    nums = re.findall(r'\d+', s)
    return int(nums[0]) if nums else 50

def parse_turn_lanes(turn_lanes_tag):
    """
    Converts OSM turn:lanes tag into a list of lanes with allowed directions.
    Each lane is a list of directions. Example output:
      [["through"], ["left", "through"], ["right"]]
    Empty list [] means unrestricted (car can go any direction).
    """
    if not turn_lanes_tag:
        return []  # no info -> unrestricted
    lanes = []
    for lane in turn_lanes_tag.split("|"):
        lane = lane.strip().lower()

        if lane in ["slight_left", "slight_right"]:
            directions = ["through"]
        elif lane == "none":
            directions = []  # unrestricted
        else:
            # keep only left, right, through
            directions = [d for d in re.findall(r"left|right|through", lane)]
            if not directions:
                directions = []  # fallback to unrestricted
        lanes.append(directions)
    return lanes

def parse_turn_restrictions(lanes):
    """
    Converts per-lane turn directions into a single pathfinding restriction list.
    Example:
      lanes = [["through"], ["left", "through"], ["right"]]
      returns ["through", "left", "right"]
    Empty list [] means unrestricted.
    """
    if not lanes:
        return []  # unrestricted
    
    restriction_set = set()
    for lane in lanes:
        if not lane:
            # lane allows all -> unrestricted
            return []
        restriction_set.update(lane)

    return list(restriction_set)

def get_lanes_forward(data, forward_tag, backward_tag):
    if data.get(forward_tag):
        return int(data.get(forward_tag))
    elif data.get("lanes"):
        if data["oneway"]:
            return int(data.get("lanes"))
        else:
            if data.get(backward_tag):
                return max(1, int(data.get("lanes")) - int(data.get(backward_tag)))
            else:
                return max(1, int(data.get("lanes")) // 2)
    else:
        return 1


def split_way(edge, node_index):
    return (export["nodes"][edge["nodes"][node_index]]["street_count"] > 2)

# --- ENTRY POINT ---
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python osm_parser.py <City> <Country> <OutputPath>")
        sys.exit(1)



    city = sys.argv[1]
    country = sys.argv[2]
    output_path = sys.argv[3]


    ox.settings.useful_tags_way += ["lanes",
        "lanes:forward", "turn:lanes:forward",
        "lanes:backward", "turn:lanes:backward"
    ]

    G = ox.graph_from_place(city + ", " + country, network_type="drive", simplify=False)
    proj = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    print("Loaded Graph")

    # all coordinates
    lats = [data["y"] for _, data in G.nodes(data=True)]
    lons = [data["x"] for _, data in G.nodes(data=True)]
    # get boundaries
    north, south = max(lats), min(lats)
    east, west = max(lons), min(lons)
    # transform them
    x_min, y_min = proj.transform(west, south)
    x_max, y_max = proj.transform(east, north)
    # save them
    export = {}
    export["bounds"] = {
        "north": y_max,
        "east": x_max,
        "south": y_min,
        "west": x_min
    }
    # get node pos and street count
    export["nodes"] = {}
    for id, data in G.nodes(data=True):
        x, y = proj.transform(data["x"], data["y"])
        export["nodes"][str(id)] = {
            "pos": (x, y),
            "street_count": data["street_count"]
            }
    print("Finished Nodes")

    export["ways"] = {}

    for start, end, data in G.edges(data=True):
        # set id based on direction
        if not data["reversed"]:
            osmid = str(data["osmid"])
        else:
            osmid = str(data["osmid"]) + "r"
        # save edge data
        turn_lanes = parse_turn_lanes(data.get("turn:lanes:forward", None)) if not data["reversed"] else parse_turn_lanes(data.get("turn:lanes:backward", None))
        edge = {
            "nodes": [str(start), str(end)],
            "speed": parse_maxspeed(data.get("maxspeed", "50")),
            "length": math.hypot(export["nodes"][str(start)]["pos"][0] - export["nodes"][str(end)]["pos"][0],
                                export["nodes"][str(start)]["pos"][1] - export["nodes"][str(end)]["pos"][1]),
            "reversed": data["reversed"],
            "oneway": data.get("oneway", False),
            "lanes": max(len(turn_lanes), get_lanes_forward(data, "lanes:forward", "lanes:backward") if not data["reversed"]
                        else get_lanes_forward(data, "lanes:backward", "lanes:forward")),
            "turn_lanes": turn_lanes,
            "turn_restrictions": parse_turn_restrictions(parse_turn_lanes(data.get("turn:lanes:forward", None))) if not data["reversed"] 
            else parse_turn_restrictions(parse_turn_lanes(data.get("turn:lanes:backward", None)))
            
        }

        # add id with first edges data
        if osmid not in export["ways"]: 
            
                export["ways"][osmid] = {
                    "id": osmid,
                    "speed": edge["speed"],
                    "length": [edge["length"]],
                    "reversed": edge["reversed"],
                    "oneway": edge["oneway"],
                    "lanes": edge["lanes"],
                    "turn_lanes": edge["turn_lanes"],
                    "turn_restrictions": edge["turn_restrictions"],
                    "nodes": [[edge["nodes"][0], edge["nodes"][1]]],
                    "edges": []
                }
        else:
            # add edge to list
            export["ways"][osmid]["edges"].append(edge)

    print("Finished Edges, Building Ways")

    for osmid, way_data in export["ways"].items():
        stitched = True
        while len(way_data["edges"]) > 0 and stitched:
            stitched = False
            for edge in way_data["edges"]:
                if edge["nodes"][0] == edge["nodes"][1] or len(edge["nodes"]) < 2:
                    stitched = True
                    way_data["edges"].remove(edge)
                # if front attaches
                if edge["nodes"][0] == way_data["nodes"][-1][-1]:
                    # if new segment
                    if split_way(edge, 0):
                        # add edge as (new) last segment
                        way_data["nodes"].append([edge["nodes"][0], edge["nodes"][1]])
                        way_data["length"].append(edge["length"])
                    else:
                        # add end node to end segment
                        way_data["nodes"][-1].append(edge["nodes"][1])
                        way_data["length"][-1] += edge["length"]
                    stitched = True
                    way_data["edges"].remove(edge)
                # end nodes attaches    
                elif edge["nodes"][1] == way_data["nodes"][0][0]:
                    # if new segment
                    if split_way(edge, 1):
                        # add edge as (new) first segment
                        way_data["nodes"].insert(0, [edge["nodes"][0], edge["nodes"][1]])
                        way_data["length"].insert(0, edge["length"])
                    else:
                        # insert start node at start of first segment
                        way_data["nodes"][0].insert(0, edge["nodes"][0])
                        way_data["length"][0] += edge["length"]

                    stitched = True
                    way_data["edges"].remove(edge)

        way_data.pop("edges")

    # output to json file
    with open(output_path, "w") as f:
        json.dump(export, f, indent=2)
        f.close()

    print("Done.")