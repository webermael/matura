#pragma once
#include <vector>

#include "../simulation/car.h"
#include "../simulation/node.h"
#include "../simulation/way.h"
#include "../utils/event_handler.h"
#include "plot.h"

enum RECT_EDGES { TOP, LEFT, BOTTOM, RIGHT };

class Display {
 public:
  Plot plot;
  bool selecting = false;
  sf::Vector2i selection_start;
  std::vector<float> rect_value;
  sf::RenderTexture road_texture;
  sf::Sprite road_sprite;
  sf::RenderTexture car_texture;
  sf::RenderTexture ui_texture;
  sf::Color road_color = {70, 70, 70};
  Display(const Plot& plot) : plot(plot), rect_value(4) {
    road_texture.create(plot.screen_size.x, plot.screen_size.y);
    car_texture.create(plot.screen_size.x, plot.screen_size.y);
    ui_texture.create(plot.screen_size.x, plot.screen_size.y);
  }

  void draw_cars(std::vector<std::unique_ptr<Car>>& cars) {
    car_texture.clear(sf::Color::Transparent);
    float size = 6.f * plot.scale;
    sf::RectangleShape shape(
        sf::Vector2f(std::max(size, 3.f), std::max(size, 3.f) / 2));
    for (auto& car : cars) {
      shape.setOrigin(std::max(size, 3.f) / 2,
                      size / 4 + (((float)car->curr_way->lanes - 1) / 2) *
                                     plot.scale * 7.f);
      shape.setRotation(std::atan2(car->direction.y, car->direction.x) * 180.f /
                        static_cast<float>(M_PI));
      shape.setPosition(plot.to_screen_space(car->pos));
      shape.setFillColor(car->color);
      car_texture.draw(shape);
    }
  }

  void draw_polyline(Way& way, float thickness, sf::Color color) {
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

      road_texture.draw(segment);
    }
  }

  void reset_view(std::vector<Node>& nodes, std::vector<Way>& ways,
                  VisualSettings settings) {
    // reset values to values from import
    plot.reset_values();
    // display the map
    road_texture.clear(sf::Color::Black);
    for (auto& way : ways) {
      draw_polyline(way, 7.f * plot.scale * (float)way.lanes,
                    settings.road_color);
    }
    road_sprite = sf::Sprite(road_texture.getTexture());
  }

  void set_view(std::vector<Node>& nodes, std::vector<Way>& ways,
                std::vector<float>& rect_value, VisualSettings settings) {
    // set the display parameters
    plot.set_values(rect_value[0], rect_value[1], rect_value[2], rect_value[3]);
    // display the map
    road_texture.clear(sf::Color::Black);
    for (auto& way : ways) {
      draw_polyline(way, 7.f * plot.scale * (float)way.lanes,
                    settings.road_color);
    }
    road_sprite = sf::Sprite(road_texture.getTexture());
  }

  void calc_rect_value(sf::Vector2i mouse_pos) {
    // clamp the position onto the display
    mouse_pos.x = std::clamp(mouse_pos.x, 0, (int)road_texture.getSize().x);
    mouse_pos.y = std::clamp(mouse_pos.y, 0, (int)road_texture.getSize().y);

    // get bounds of selection area
    float t = std::min(selection_start.y, mouse_pos.y);
    float l = std::min(selection_start.x, mouse_pos.x);
    float b = std::max(selection_start.y, mouse_pos.y);
    float r = std::max(selection_start.x, mouse_pos.x);

    // save bounds
    rect_value[TOP] = t;
    rect_value[LEFT] = l;
    rect_value[BOTTOM] = b;
    rect_value[RIGHT] = r;
  }

  void draw_selection_rect() {
    if (!selecting) {
      return;
    }
    // draw selecion area outline
    sf::RectangleShape rectangle({rect_value[RIGHT] - rect_value[LEFT],
                                  rect_value[TOP] - rect_value[BOTTOM]});
    rectangle.setPosition(
        {rect_value[LEFT], ui_texture.getSize().y - rect_value[TOP]});
    rectangle.setFillColor(sf::Color::Transparent);
    rectangle.setOutlineThickness(2.0f);
    rectangle.setOutlineColor(sf::Color::Red);
    ui_texture.draw(rectangle);
  }

  void draw_to_window(sf::RenderWindow& window) {
    window.draw(road_sprite);
    sf::Sprite car_sprite(car_texture.getTexture());
    window.draw(car_sprite);
    sf::Sprite ui_sprite(ui_texture.getTexture());
    window.draw(ui_sprite);
  }

  void update(InputState input, std::vector<Node>& nodes,
              std::vector<Way>& ways, VisualSettings settings) {
    ui_texture.clear(sf::Color::Transparent);
    // while button down, show rectangle
    if (input.left_mouse_pressed) {
      if (!selecting && input.left_mouse_just_pressed &&
          input.mouse_pos.x <= road_texture.getSize().x) {
        // if mouse pos is on the display and freshly pressed, start selecting
        selecting = true;
        selection_start = input.mouse_pos;
      }
      if (selecting) {
        calc_rect_value(input.mouse_pos);
      }
    }
    if (input.left_mouse_just_released) {
      // when mouse is released, apply new values
      if (selecting) {
        selecting = false;
        set_view(nodes, ways, rect_value, settings);
      }
    }
  }
};