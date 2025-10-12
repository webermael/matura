#pragma once
#include <SFML/Graphics.hpp>
#include <chrono>
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <random>
#include <string>
#include <unordered_map>
#include <vector>

#include "../interface/display.h"
#include "../utils/event_handler.h"
#include "../utils/settings.h"
#include "car.h"
#include "pathfinder.h"

using json = nlohmann::json;

class Simulation {
 public:
  std::vector<Node> nodes;
  std::unordered_map<std::string, std::size_t> id_to_index;
  std::vector<Way> ways;
  Pathfinder pathfinder;
  std::vector<Node*> start_nodes;
  std::vector<Node*> end_nodes;
  std::vector<std::unique_ptr<Car>> cars = {};
  std::vector<std::vector<Way*>> paths;
  std::unique_ptr<Plot> plot;        // delayed construction
  std::unique_ptr<Display> display;  // delayed construction
  bool paused = false;
  bool car_spawning = true;
  Settings settings;
  float car_timer = settings.sim.car_spawn_time;

  Simulation(std::string json_path, sf::Vector2u screen_size) {
    json file_content(import_json(json_path));
    node_setup(file_content);
    way_setup(file_content);
    node_way_coupling();
    plot = std::make_unique<Plot>(screen_size, file_content["bounds"]);
    display = std::make_unique<Display>(*plot);
    pathfinder_node_setup();
  }

  json import_json(std::string file_path) {
    // Read file
    std::ifstream file(file_path);
    json file_content = json::parse(file);
    return file_content;
  }

  void node_setup(json file_content) {
    // create node objects
    for (auto& [node_id, node] : file_content["nodes"].items()) {
      sf::Vector2<double> pos = {node["pos"][0], node["pos"][1]};
      int street_count = node["street_count"];

      std::vector<Way*> ways_in;  // declare later
      std::vector<Way*> ways_out;
      id_to_index.emplace(node_id, (nodes.size()));
      nodes.push_back(Node(node_id, pos, street_count, ways_in, ways_out));
    }
  }

  void way_setup(json file_content) {
    // create ways
    for (auto& [way_id, way] : file_content["ways"].items()) {
      for (size_t i = 0; i < way["nodes"].size(); i++) {
        const auto& segment = way["nodes"][i];

        std::vector<Node*> segment_nodes;  // pointer vector
        segment_nodes.reserve(segment.size());
        // pick out correct node segment
        for (const auto& node_id : segment) {
          size_t index = id_to_index[node_id];
          segment_nodes.push_back(&nodes[index]);
        }

        ways.emplace_back(way_id, i, way["oneway"], way["lanes"],
                          way["turns"][i], way["speed"], segment_nodes,
                          way["weights"][i]);
      }
    }
  }

  void node_way_coupling() {
    // give way references to nodes
    for (auto& way : ways) {
      way.nodes[0]->ways_out.push_back(&way);  // push back adress (&) of way
      way.nodes.back()->ways_in.push_back(&way);
    }
  }

  void pathfinder_node_setup() {
    // create start and end node vectors
    for (size_t i = 0; i < nodes.size(); i++) {
      if (nodes[i].street_count == 2 && nodes[i].ways_out.size() == 1 &&
          (nodes[i].ways_out[0]->oneway && nodes[i].ways_in.size() == 0 ||
           !nodes[i].ways_out[0]->oneway && nodes[i].ways_in.size() == 1)) {
        start_nodes.push_back(nodes[i].ways_out[0]->nodes.front());
      }
      if (nodes[i].street_count == 2 && nodes[i].ways_in.size() == 1 &&
          (nodes[i].ways_in[0]->oneway && nodes[i].ways_out.size() == 0 ||
           !nodes[i].ways_in[0]->oneway && nodes[i].ways_out.size() == 1)) {
        end_nodes.push_back(nodes[i].ways_in[0]->nodes.back());
      }
    }
  }

  void change_pathfinder_mode(PathFinding new_mode) {
    settings.sim.pathfinding = new_mode;
    paths.clear();
    pathfinder.reset(start_nodes[rand() % start_nodes.size()],
                     end_nodes[rand() % end_nodes.size()], settings.sim);
  }

  void reset_pathfinder() {
    pathfinder.reset(start_nodes[rand() % start_nodes.size()],
                     end_nodes[rand() % end_nodes.size()], settings.sim);
  }

  void pathfinder_update() {
    // run x steps of A*
    if (pathfinder.active) {
      for (size_t i = 0; i < settings.sim.pathfinder_step_count; i++) {
        pathfinder.step();
      }
    } else {
      // if new path is found, add to list
      if (pathfinder.explored_nodes.count(pathfinder.end) &&  // end reached
          !std::count(
              paths.begin(), paths.end(),
              pathfinder.explored_nodes[pathfinder.end].path)  // no duplicates
          && !(pathfinder.start ==
               pathfinder.end)) {  // different start and end nodes
        paths.push_back(pathfinder.explored_nodes[pathfinder.end].path);
      }
      // start next search
      reset_pathfinder();
    }
  }

  void spawn_car(InputState input) {
    if (car_spawning) {
      car_timer -= input.dt;
    }
    while (car_timer < 0) {
      car_timer += settings.sim.car_spawn_time;
      if (paths.size() > 0 && cars.size() < settings.sim.car_cap) {
        // if paths are available, choose a random one
        std::vector<Way*> path = paths[rand() % paths.size()];
        cars.emplace_back(std::make_unique<Car>(path, settings));
      }
    }
  }

  void clear_cars() {
    cars.clear();
    // clean up references inside ways
    for (auto& way : ways) {
      way.cars.clear();
    }
  }

  void clear_blockades() {
    paths.clear();
    reset_pathfinder();
    for (auto& way : ways) {
      way.blocked = false;
    }
  }

  void block_way(Way* way) {
    paths.clear();
    reset_pathfinder();
    way->blocked = !way->blocked;
  }

  void update(InputState input) {
    if (paused) {
      input.dt = 0;
    } else {
      input.dt *= settings.sim.game_speed;
    }
    if (input.escape_pressed) {
      display->reset_view(ways, settings.visual);
    }
    // zoom selection
    display->update(input, nodes, ways, settings);

    pathfinder_update();

    // --- CARS ---
    // add cars based on timer
    spawn_car(input);
    // update
    for (auto& car : cars) {
      car->update(input.dt, settings);
    }
    // Remove inactive
    cars.erase(std::remove_if(cars.begin(), cars.end(),
                              [](const std::unique_ptr<Car>& car) {
                                return !car->active;
                              }),
               cars.end());
    // sort cars in each way according to their progress
    for (auto& way : ways) {
      std::sort(way.cars.begin(), way.cars.end(), [](Car* a, Car* b) {
        return a->way_progress < b->way_progress;
      });
    }
  }

  void draw(sf::RenderWindow& window, InputState& input) {
    display->draw(start_nodes, end_nodes, nodes, ways, pathfinder, cars,
                  settings, input);
    display->push_to_window(window);
  }
};