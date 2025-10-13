#pragma once
#include <SFML/Graphics.hpp>
#include <string>
#include <vector>

class Car;

class Node;  // forward declaration

class Way {
 public:
  std::string id;
  int index;
  bool oneway;
  int lanes;
  std::vector<std::vector<std::string>> turn_lanes;
  std::vector<std::string> turn_restrictions;
  int speed;
  std::vector<Node*> nodes;
  std::vector<std::vector<Car*>> cars;
  float length;
  bool blocked = false;

  Way(std::string id, int index, bool oneway, int lanes,
      std::vector<std::vector<std::string>> turn_lanes,
      std::vector<std::string> turn_restrictions, int speed,
      std::vector<Node*>& nodes, float length)
      : id(id),
        index(index),
        oneway(oneway),
        lanes(lanes),
        turn_lanes(turn_lanes),
        turn_restrictions(turn_restrictions),
        speed(speed),
        nodes(nodes),
        length(length) {
    cars.resize(std::max(1, lanes));
  }
};
