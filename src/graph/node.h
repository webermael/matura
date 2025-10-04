#pragma once
#include <SFML/Graphics.hpp>
#include <string>
#include <vector>

class Way;

class Node {
 public:
  std::string id;
  sf::Vector2f pos;
  sf::Vector2f display_pos;
  int street_count;
  // std::vector<Way*> ways_out;
  // std::vector<Way*> ways_in;
  bool is_visible;

  Node(std::string id, sf::Vector2f pos, sf::Vector2f display_pos,
       int street_count/*, std::vector<Way*>& ways_out,
       std::vector<Way*>& ways_in */)
      : id(id),
        pos(pos),
        display_pos(display_pos),
        street_count(street_count)/*,
        ways_out(ways_out),
        ways_in(ways_in) */{
    is_visible = true;
  }

  void test_visible(sf::Vector2u screen_size) {
    if (0 < display_pos.x < screen_size.x &&
        0 < display_pos.y < screen_size.y) {
      is_visible = true;
    } else {
      is_visible = true;
    }
  }
};
