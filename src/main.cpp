#include <SFML/Graphics.hpp>
#include <chrono>
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <random>
#include <string>
#include <unordered_map>
#include <vector>

#include "display.h"
#include "graph/astar.h"
#include "graph/node.h"
#include "graph/plot.h"
#include "graph/way.h"
#include "traffic/car.h"

using json = nlohmann::json;

int main() {
  // randomize seed
  srand(std::chrono::system_clock::now().time_since_epoch().count());

  // --- IMPORT (maybe own file?) ---
  std::ifstream file("./src/Aarau.json");
  json file_content = json::parse(file);

  // create nodes
  std::vector<Node> nodes;
  std::unordered_map<std::string, std::size_t>
      id_to_index;  // only for setting up ways after
  for (auto& [node_id, node] : file_content["nodes"].items()) {
    sf::Vector2<double> pos = {node["pos"][0], node["pos"][1]};
    int street_count = node["street_count"];

    std::vector<Way*> ways_in;
    std::vector<Way*> ways_out;
    id_to_index.emplace(node_id, (nodes.size()));
    nodes.push_back(Node(node_id, pos, street_count, ways_in, ways_out));
  }

  // create ways
  std::vector<Way> ways;
  for (auto& [way_id, way] : file_content["ways"].items()) {
    for (size_t i = 0; i < way["nodes"].size(); i++) {
      const auto& segment = way["nodes"][i];

      std::vector<Node*> segment_nodes;  // pointer vector
      segment_nodes.reserve(segment.size());

      for (const auto& node_id : segment) {
        size_t index = id_to_index[node_id];
        segment_nodes.push_back(&nodes[index]);
      }

      ways.emplace_back(way_id, i, way["oneway"], way["lanes"], way["turns"][i],
                        way["speed"], segment_nodes, way["weights"][i]);
    }
  }
  id_to_index.clear();

  // give way references to nodes
  for (auto& way : ways) {
    way.nodes[0]->ways_out.push_back(&way);  // push back adress (&) of way
    way.nodes.back()->ways_in.push_back(&way);
  }

  // create main display window
  auto window = sf::RenderWindow(sf::VideoMode(1800, 900), "Matura");
  sf::Vector2u interface_size = {200u, window.getSize().y};
  sf::Vector2u screen_size(window.getSize().x - interface_size.x,
                           window.getSize().y);
  sf::Vector2f screen_center(screen_size.x / 2, screen_size.y / 2);
  window.setFramerateLimit(144);

  // create surface for roads to be drawn
  sf::RenderTexture road_surface;
  road_surface.create(screen_size.x, screen_size.y);
  sf::RenderTexture ui_surface;
  ui_surface.create(screen_size.x, screen_size.y);
  sf::RenderTexture car_surface;
  car_surface.create(screen_size.x, screen_size.y);

  // set up display handler
  Plot plot(screen_size, screen_center, file_content["bounds"]);
  Display display(plot);
  display.reset_view(road_surface, window, nodes, ways);

  // boot up A*
  Astar astar;
  std::vector<Node*> start_nodes;
  std::vector<Node*> end_nodes;
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

  // get cars ready
  std::vector<std::unique_ptr<Car>> cars;
  float car_reset = 0.5f;
  float car_timer = car_reset;

  sf::Clock clock;
  float dt = 0.0f;
  std::vector<std::vector<Way*>> paths = {};
  // --- GAME LOOP ---
  while (window.isOpen()) {
    bool mouse_clicked = false;

    // --- EVENT HANDLING ---
    sf::Event event;
    while (window.pollEvent(event)) {
      if (event.type == sf::Event::Closed) {
        window.close();
      } else if (event.type == sf::Event::KeyPressed &&
                 event.key.code == sf::Keyboard::Escape) {
        // escape to reset view
        display.reset_view(road_surface, window, nodes, ways);
      }
      if (event.type == sf::Event::MouseButtonPressed &&
          event.mouseButton.button == sf::Mouse::Button::Left) {
        mouse_clicked = true;
      }
      // maybe figure out something for resizing later
    }

    // --- UPDATING ---

    // check for mouse click (zooming)
    display.update(road_surface, ui_surface, window, mouse_clicked, nodes,
                   ways);

    // run 10 steps of A*
    if (astar.active) {
      for (size_t i = 0; i < 10; i++) {
        astar.step();
      }
    } else {
      // if new path is found, add to list
      if (astar.explored_nodes.count(astar.end) &&
          !std::count(paths.begin(), paths.end(),
                      astar.explored_nodes[astar.end].path) &&
          !(astar.start == astar.end)) {
        paths.push_back(astar.explored_nodes[astar.end].path);
      }
      // start next search
      astar.reset(start_nodes[rand() % start_nodes.size()],
                  end_nodes[rand() % end_nodes.size()]);
    }

    // spawn new car if timer depletes
    car_timer -= dt;
    while (car_timer < 0) {
      car_timer += car_reset;
      if (paths.size() > 0) {
        std::vector<Way*> path = paths[rand() % paths.size()];
        cars.emplace_back(std::make_unique<Car>(path));
      }
    }
    car_surface.clear(sf::Color::Transparent);
    for (auto& car_ptr : cars) {
      car_ptr->update(dt, ACCELERATION, car_surface, display);
      car_ptr->render(car_surface, display);
    }
    // remove finished cars
    // Remove all inactive cars
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

    // --- DRAWING ---
    window.clear(sf::Color::White);
    // turn road surface into a sprite and draw it
    road_surface.clear(sf::Color::Black);
    for (auto& way : ways) {
      if (way.cars.size() > 0) {
        display.draw_polyline(
            road_surface, way,
            7.f * display.plot.scale * (float)way.lanes +
                display.plot.scale * 3.f,
            sf::Color(std::min(255ull, (way.cars.size() * 50)), 100, 100));
      } else {
        display.draw_polyline(road_surface, way,
                              7.f * display.plot.scale * (float)way.lanes,
                              sf::Color(100, 100, 100));
      }
    }
    sf::Sprite road_sprite(road_surface.getTexture());
    window.draw(road_sprite);

    sf::Sprite car_sprite(car_surface.getTexture());
    window.draw(car_sprite);
    // draw the red selection rectangle on top of everything
    sf::Sprite ui_sprite(ui_surface.getTexture());
    window.draw(ui_sprite);

    dt = clock.restart().asSeconds();
    // show the frame
    window.display();
  }
}