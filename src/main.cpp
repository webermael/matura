#include <SFML/Graphics.hpp>
#include <fstream>
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

    nodes.emplace(node_id, Node(node_id, pos, display_pos, street_count));
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

  // for (auto& way : ways) {
  //   way.nodes[0].ways_out.push_back(way)
  //   way.nodes[-1].ways_out.push_back(way)
  // }

  // --- GAME LOOP ---
  auto window = sf::RenderWindow(sf::VideoMode({screen_size}), "Matura");
  window.setFramerateLimit(144);

  float dt = 0.0;
  bool running = true;
  bool selecting = false;
  sf::Vector2f selection_start = {0.0f, 0.0f};
  std::vector<float> rect_value;

  while (window.isOpen()) {
    while (const std::optional event = window.pollEvent()) {
      if (event->is<sf::Event::Closed>()) {
        window.close();
      } else if (const auto* keyPressed =
                     event->getIf<sf::Event::KeyPressed>()) {
        if (keyPressed->scancode == sf::Keyboard::Scancode::Escape) {
          display.reset_view(nodes, ways);
        }
      }
    }

    // --- current translation status ---
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

    window.display();
  }
}