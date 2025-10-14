#pragma once
#include <SFML/Graphics.hpp>
#include <string>
#include <vector>

class Way;

class Node {
 public:
  std::string id;
  float spawn_weight = 0.f;
  sf::Vector2<double> pos;
  int street_count;
  std::vector<Way*> ways_out;
  std::vector<Way*> ways_in;

  Node(std::string id, sf::Vector2<double> pos, int street_count,
       std::vector<Way*>& ways_out, std::vector<Way*>& ways_in)
      : id(id),
        pos(pos),
        street_count(street_count),
        ways_out(ways_out),
        ways_in(ways_in) {}
};
