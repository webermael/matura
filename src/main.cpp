#include <SFML/Graphics.hpp>
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <string>
#include <unordered_map>
#include <vector>

#include "display.h"
#include "graph/node.h"
#include "graph/plot.h"
#include "graph/way.h"

using json = nlohmann::json;

int main() {
  std::ifstream file("./src/Aarau.json");

  json file_content = json::parse(file);

  sf::Vector2u screen_size = {1920u, 1080u};
  sf::Vector2f screen_center = {(float)screen_size.x / 2,
                                (float)screen_size.y / 2};

  // --- IMPORT (maybe own file?) ---
  Plot plot(screen_size, screen_center, file_content["bounds"]);
  Display display(plot);

  std::unordered_map<std::string, Node> nodes;

  for (auto& [node_id, node] : file_content["nodes"].items()) {
    sf::Vector2f pos = {node["pos"][0], node["pos"][1]};
    sf::Vector2f display_pos = display.plot.to_screen_space(pos);
    int street_count = node["street_count"];

    std::vector<Way*> ways_in;
    std::vector<Way*> ways_out;

    nodes.emplace(node_id, Node(node_id, pos, display_pos, street_count,
                                ways_in, ways_out));
  }

  std::vector<Way> ways;
  for (auto& [way_id, way] : file_content["ways"].items()) {
    for (size_t i = 0; i < way["nodes"].size(); i++) {
      const auto& segment = way["nodes"][i];

      std::vector<Node*> segment_nodes;  // pointer vector
      segment_nodes.reserve(segment.size());

      for (const auto& node_id : segment) {
        segment_nodes.push_back(&nodes.at(node_id));
      }

      ways.emplace_back(way_id, i, way["oneway"], way["lanes"], way["turns"][i],
                        way["speed"], segment_nodes, way["weights"][i]);
    }
  }

  for (auto& way : ways) {
    way.nodes[0]->ways_out.push_back(&way);  // push back adress (&) of way
    way.nodes.back()->ways_in.push_back(&way);
  }

  // --- GAME LOOP ---
  auto window = sf::RenderWindow(sf::VideoMode({screen_size}), "Matura");
  window.setFramerateLimit(144);
  sf::Clock clock;

  float dt = 0.0f;
  bool running = true;
  bool selecting = false;
  sf::Vector2i selection_start;
  std::vector<float> rect_value(4);

  while (running) {  // window.isOpen()
    while (const std::optional event = window.pollEvent()) {
      if (event->is<sf::Event::Closed>()) {
        window.close();
        running = false;
      } else if (const auto* keyPressed =
                     event->getIf<sf::Event::KeyPressed>()) {
        if (keyPressed->scancode == sf::Keyboard::Scancode::Escape) {
          display.reset_view(nodes, ways);
        }
      }
    }

    window.clear(sf::Color::Black);

    for (auto& way : ways) {
      if (way.is_visible) {
        sf::VertexArray draw_way(sf::PrimitiveType::LineStrip);
        for (auto& point : way.display_way) {
          draw_way.append(sf::Vertex({point}));
        }
        window.draw(draw_way);
      }
    }

    if (sf::Mouse::isButtonPressed(sf::Mouse::Button::Left)) {
      sf::Vector2i mouse_pos = sf::Mouse::getPosition(window);
      if (!selecting) {
        selecting = true;
        selection_start = mouse_pos;
      }
      float t = std::min(selection_start.y, mouse_pos.y);
      float l = std::min(selection_start.x, mouse_pos.x);
      float b = std::min(selection_start.y, mouse_pos.y);
      float r = std::min(selection_start.x, mouse_pos.x);

      rect_value[0] = t;
      rect_value[1] = l;
      rect_value[2] = b;
      rect_value[3] = r;

      sf::RectangleShape rectangle({r - l, b - t});
      rectangle.setPosition({l, t});
      rectangle.setFillColor(sf::Color::Red);
      rectangle.setOutlineThickness(10.0f);
      window.draw(rectangle);
      std::cout << "Drew Rect" << std::endl;
    } else {
      if (selecting) {
        selecting = false;
        display.set_view(nodes, ways, rect_value);
      }
    }
    // --- current translation status ---

    dt = clock.restart().asSeconds();

    window.display();
  }
}