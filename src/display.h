#pragma once
#include <vector>

#include "graph/node.h"
#include "graph/plot.h"
#include "graph/way.h"

class Display {
 public:
  Plot plot;
  bool selecting = false;
  sf::Vector2i selection_start;
  std::vector<float> rect_value;
  Display(const Plot& plot) : plot(plot), rect_value(4) {}

  /*
  Pointers and References
  - &: argument is passed "by reference" -> the object is not copied but could
  be modified (to avoid use "const")

  - *: here "way.nodes" is no longer a vector of objects, but a vector of
  pointers (Node*) (for the same reason, its attribute has to be acessed using
  "->")
  */
  void draw_polyline(sf::RenderTexture& road_surface, Way& way, float thickness,
                     sf::Color color) {
    if (way.nodes.size() < 2) {
      return;
    }
    thickness = std::max(1.0f, thickness);
    for (size_t i = 1; i < way.nodes.size(); i++) {
      sf::Vector2f pos1 = plot.to_screen_space(way.nodes[i - 1]->pos);
      sf::Vector2f pos2 = plot.to_screen_space(way.nodes[i]->pos);

      sf::Vector2f direction = pos2 - pos1;
      float length =
          std::sqrt(direction.x * direction.x + direction.y * direction.y);
      float angle = std::atan2(direction.y, direction.x) * 180.f / 3.14159265f;

      sf::RectangleShape segment(sf::Vector2f(length, thickness));
      segment.setFillColor(color);
      segment.setOrigin(0.f, thickness / 2.f);  // center line vertically
      segment.setPosition((sf::Vector2f)pos1);
      segment.setRotation(angle);

      road_surface.draw(segment);
    }
  }

  void reset_view(sf::RenderTexture& road_surface, sf::RenderWindow& window,
                  std::vector<Node>& nodes, std::vector<Way>& ways) {
    // reset values to values from import
    plot.reset_values();
    // display the map
    road_surface.clear(sf::Color::Black);
    for (auto& way : ways) {
      if (!way.cars.empty()) {
        draw_polyline(road_surface, way, 7.f * plot.scale * (float)way.lanes,
                      sf::Color(200, 100, 100));
      } else {
        draw_polyline(road_surface, way, 7.f * plot.scale * (float)way.lanes,
                      sf::Color(100, 100, 100));
      }
    }
  }

  void set_view(sf::RenderTexture& road_surface, sf::RenderWindow& window,
                std::vector<Node>& nodes, std::vector<Way>& ways,
                std::vector<float>& rect_value) {
    // set the display parameters
    plot.set_values(rect_value[0], rect_value[1], rect_value[2], rect_value[3]);
    // display the map
    road_surface.clear(sf::Color::Black);
    for (auto& way : ways) {
      if (!way.cars.empty()) {
        draw_polyline(road_surface, way, 7.f * plot.scale * (float)way.lanes,
                      sf::Color(200, 100, 100));
      } else {
        draw_polyline(road_surface, way, 7.f * plot.scale * (float)way.lanes,
                      sf::Color(100, 100, 100));
      }
    }
  }

  void update(sf::RenderTexture& road_surface, sf::RenderTexture& ui_surface,
              sf::RenderWindow& window, bool mouse_clicked,
              std::vector<Node>& nodes, std::vector<Way>& ways) {
    ui_surface.clear(sf::Color::Transparent);
    sf::Vector2i mouse_pos = sf::Mouse::getPosition(window);
    if (sf::Mouse::isButtonPressed(sf::Mouse::Button::Left)) {
      if (!selecting && mouse_clicked &&
          mouse_pos.x <= road_surface.getSize().x) {
        // if mouse pos is on the display, start selecting
        selecting = true;
        selection_start = mouse_pos;
      } else if (selecting) {
        // clamp the position onto the display
        mouse_pos.x = std::clamp(mouse_pos.x, 0, (int)road_surface.getSize().x);
        mouse_pos.y = std::clamp(mouse_pos.y, 0, (int)road_surface.getSize().y);

        // get bounds of selection area
        float t = std::min(selection_start.y, mouse_pos.y);
        float l = std::min(selection_start.x, mouse_pos.x);
        float b = std::max(selection_start.y, mouse_pos.y);
        float r = std::max(selection_start.x, mouse_pos.x);

        // save bounds
        rect_value[0] = t;
        rect_value[1] = l;
        rect_value[2] = b;
        rect_value[3] = r;

        // draw selecion area outline
        sf::RectangleShape rectangle({r - l, t - b});
        rectangle.setPosition({l, ui_surface.getSize().y - t});
        rectangle.setFillColor(sf::Color::Transparent);
        rectangle.setOutlineThickness(2.0f);
        rectangle.setOutlineColor(sf::Color::Red);
        ui_surface.draw(rectangle);
      }
    } else {
      // when mouse is released, turn off "selection mode" and apply new
      // values
      if (selecting) {
        selecting = false;
        set_view(road_surface, window, nodes, ways, rect_value);
      }
    }
  }
};