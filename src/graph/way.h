#pragma once
#include <SFML/Graphics.hpp>
#include <string>
#include <vector>

#include "../traffic/car.h"

class Node;  // forward declaration

class Way {
 private:
 public:
  std::string id;
  int index;
  bool oneway;
  int lanes;
  std::vector<std::string> turns;
  int speed;
  std::vector<Node*> nodes;
  std::vector<sf::Vector2f> display_way;
  std::vector<Car*> cars;
  float length;
  bool is_visible;

  Way(std::string id, int index, bool oneway, int lanes,
      std::vector<std::string> turns, int speed, std::vector<Node*>& nodes,
      float length)
      : id(id),
        index(index),
        oneway(oneway),
        lanes(lanes),
        turns(turns),
        speed(speed),
        nodes(nodes),
        length(length) {
    for (auto& node : nodes) {
      display_way.push_back(node->display_pos);
    }
    is_visible = true;
  }

  void test_visible() {
    for (auto* node : nodes) {
      if (node->is_visible) {
        is_visible = true;
        return;
      }
    }
    is_visible = false;
  }
};
