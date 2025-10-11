#pragma once
#include <bits/stdc++.h>

#include <SFML/Graphics.hpp>
#include <cmath>
#include <string>
#include <vector>

class Plot {
 public:
  sf::Vector2u screen_size;
  sf::Vector2f screen_center;
  std::unordered_map<std::string, float> bounds;

  sf::Vector2<double> translation;
  sf::Vector2<double> graph_size;
  float scale;

  void reset_values() {
    // set values so the entire map is on screen
    translation = {bounds["west"], bounds["south"]};
    graph_size = {bounds["east"] - bounds["west"],
                  bounds["north"] - bounds["south"]};
    scale =
        std::min(screen_size.x / graph_size.x, screen_size.y / graph_size.y);
  }

  Plot(sf::Vector2u screen_size, std::unordered_map<std::string, float> bounds)
      : screen_size(screen_size), screen_center(screen_center), bounds(bounds) {
    screen_center = sf::Vector2f(screen_size.x / 2, screen_size.y / 2);
    reset_values();
  }

  sf::Vector2f to_screen_space(sf::Vector2<double> position) {
    return sf::Vector2f(
        static_cast<float>((position.x - translation.x - graph_size.x / 2.0) *
                               scale +
                           screen_center.x),
        static_cast<float>((position.y - translation.y - graph_size.y / 2.0) *
                               scale +
                           screen_center.y));
  }

  sf::Vector2<double> from_screen_space(sf::Vector2f position) {
    return {(position.x - screen_center.x) / scale + translation.x +
                graph_size.x / 2,
            (position.y - screen_center.y) / -scale + translation.y +
                graph_size.y / 2};
  }

  void set_values(float top, float left, float bottom, float right) {
    // set new values from screen_space coordinates
    sf::Vector2<double> temp_translation;
    sf::Vector2<double> temp_corner;
    if (std::abs(bottom - top) > 0 && std::abs(right - left) > 0) {
      temp_translation = from_screen_space({left, bottom});
      temp_corner = from_screen_space({right, top});
      translation = temp_translation;
      graph_size = {temp_corner.x - temp_translation.x,
                    temp_corner.y - temp_translation.y};
      scale =
          std::min(screen_size.x / graph_size.x, screen_size.y / graph_size.y);
    }
  }
};
