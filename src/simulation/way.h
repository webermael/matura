#pragma once
#include <SFML/Graphics.hpp>
#include <string>
#include <vector>

class Car;

class Node;  // forward declaration

enum Turn : uint8_t { THROUGH, LEFT_TURN, RIGHT_TURN };

class Way {
 public:
  std::string id;
  int index;
  bool oneway;
  int lanes;
  std::vector<std::vector<Turn>> turn_lanes;
  std::vector<std::string> turn_restrictions;
  int speed;
  std::vector<Node*> nodes;
  std::vector<std::vector<Car*>> cars;
  float length;
  bool blocked = false;

  Way(std::string id, int index, bool oneway, int lanes,
      std::vector<std::vector<std::string>> turn_lanes_str,
      std::vector<std::string> turn_restrictions, int speed,
      std::vector<Node*>& nodes, float length)
      : id(id),
        index(index),
        oneway(oneway),
        lanes(lanes),
        turn_lanes(turn_lanes_str.size()),
        turn_restrictions(turn_restrictions),
        speed(speed),
        nodes(nodes),
        length(length),
        cars(std::max(1, lanes)) {
    // convert string turn lanes to enum
    for (size_t i = 0; i < turn_lanes_str.size(); ++i) {
      turn_lanes[i].reserve(turn_lanes_str[i].size());
      for (const auto& s : turn_lanes_str[i]) {
        turn_lanes[i].push_back(string_to_turn(s));
      }
    }
  }

  Turn string_to_turn(const std::string& s) {
    if (s == "left") return Turn::LEFT_TURN;
    if (s == "right") return Turn::RIGHT_TURN;
    return Turn::THROUGH;
  }
};
