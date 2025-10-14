#pragma once
#include <cmath>
#include <vector>

#include "../simulation/car.h"
#include "../simulation/node.h"
#include "../simulation/pathfinder.h"
#include "../simulation/way.h"
#include "../utils/event_handler.h"
#include "../utils/settings.h"
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
  sf::Sprite static_debug_sprite;
  sf::RenderTexture car_texture;
  sf::RenderTexture ui_texture;
  sf::RenderTexture static_debug_texture;
  sf::RenderTexture dynamic_debug_texture;
  sf::Color road_color = {70, 70, 70};
  bool camera_moved = true;
  Display(const Plot& plot) : plot(plot), rect_value(4) {
    road_texture.create(plot.screen_size.x, plot.screen_size.y);
    car_texture.create(plot.screen_size.x, plot.screen_size.y);
    ui_texture.create(plot.screen_size.x, plot.screen_size.y);
    static_debug_texture.create(plot.screen_size.x, plot.screen_size.y);
    dynamic_debug_texture.create(plot.screen_size.x, plot.screen_size.y);
  }

  void draw_cars(std::vector<std::unique_ptr<Car>>& cars,
                 VisualSettings settings) {
    car_texture.clear(sf::Color::Transparent);
    if (!settings.draw_cars) {
      return;
    }
    // create rectangle
    float size = std::max(3.f, 6.f * plot.scale);
    sf::RectangleShape shape(sf::Vector2f(size, size * 0.5f));
    // use minimum size so they are visible enough in the big picture
    for (auto& car : cars) {
      // offset to the right side
      float car_offset =
          (1.5f * plot.scale) +                       // car width center
          (settings.road_width * plot.scale * 0.5f);  // center car on road
      float road_offset = car->lane_index * settings.road_width * plot.scale;
      if (car->path->ways[car->way_index]->oneway) {
        road_offset -= car->path->ways[car->way_index]->lanes *
                       settings.road_width * plot.scale *
                       0.5f;  // if center move over by half the road width
      }
      shape.setOrigin(size / 2, car_offset + road_offset);
      // rotate according to direction
      shape.setRotation(std::atan2(car->direction.y, car->direction.x) * 180.f /
                        3.1415926f);
      shape.setPosition(plot.to_screen_space(car->pos));
      shape.setFillColor(car->color);
      car_texture.draw(shape);
    }
  }

  void draw_polyline(Way& way, float thickness, sf::Color color,
                     sf::RenderTexture& texture) {
    if (way.nodes.size() < 2) {
      return;
    }
    // guarantee lines to be visible
    thickness = std::max(2.0f, thickness * plot.scale * (float)way.lanes);
    for (size_t i = 1; i < way.nodes.size(); i++) {
      sf::Vector2f pos1 = plot.to_screen_space(way.nodes[i - 1]->pos);
      sf::Vector2f pos2 = plot.to_screen_space(way.nodes[i]->pos);

      sf::Vector2f direction = pos2 - pos1;
      float length =
          std::sqrt(direction.x * direction.x + direction.y * direction.y);
      float angle = std::atan2(direction.y, direction.x) * 180.f / 3.14159265f;

      sf::RectangleShape segment(sf::Vector2f(length, thickness));
      segment.setFillColor(color);
      if (!way.oneway) {
        segment.setOrigin(0.f, thickness);
      } else {
        segment.setOrigin(0.f, thickness * 0.5f);  // center vertically
      }

      segment.setPosition((sf::Vector2f)pos1);
      segment.setRotation(angle);

      texture.draw(segment);
    }
  }

  void draw_roads(std::vector<Way>& ways, VisualSettings settings) {
    road_texture.clear(settings.bg_color);
    for (auto& way : ways) {
      draw_polyline(way, settings.road_width, settings.road_color,
                    road_texture);
    }
    // draw blocked roads on top
    for (auto& way : ways) {
      if (way.blocked) {
        draw_polyline(way, settings.road_width, settings.blocked_road_color,
                      road_texture);
      }
    }
    road_sprite = sf::Sprite(road_texture.getTexture());
  }

  void debug_draw_node_connections(std::vector<Way>& ways) {
    for (auto& way : ways) {
      sf::VertexArray line(sf::PrimitiveType::LineStrip, way.nodes.size());
      for (size_t i = 0; i < way.nodes.size(); i++) {
        line[i].position = plot.to_screen_space(way.nodes[i]->pos);
        line[i].color = sf::Color::White;
      }
      static_debug_texture.draw(line);
    }
  }

  void draw_nodes(const std::vector<Node*>& nodes, sf::Color color) {
    // draw the input group of nodes with color
    sf::CircleShape node_shape(std::max(1.5f, 6.f * plot.scale));
    node_shape.setOrigin(std::max(1.5f, 6.f * plot.scale),
                         std::max(1.5f, 6.f * plot.scale));
    node_shape.setFillColor(color);
    for (auto& node : nodes) {
      node_shape.setPosition(plot.to_screen_space(node->pos));
      static_debug_texture.draw(node_shape);
    }
  }

  void debug_draw_pathfinder(Pathfinder& pathfinder) {
    sf::CircleShape node_shape(5.0f);
    node_shape.setOrigin(2.5f, 2.5f);
    for (const auto& node : pathfinder.explored_nodes) {
      node_shape.setPosition(plot.to_screen_space(node.first->pos));
      node_shape.setFillColor({250, 150, 0});  // orange explored nodes
      dynamic_debug_texture.draw(node_shape);
    }
    for (const auto& node : pathfinder.active_nodes) {
      node_shape.setPosition(plot.to_screen_space(node->pos));
      node_shape.setFillColor({0, 150, 150});  // cyan active nodes
      dynamic_debug_texture.draw(node_shape);
    }

    if (pathfinder.explored_nodes.count(pathfinder.end)) {
      for (const auto& way : pathfinder.explored_nodes[pathfinder.end].path) {
        node_shape.setPosition(plot.to_screen_space(way->nodes[0]->pos));
        node_shape.setFillColor(
            {250, 0, 250});  // purple start to end path nodes
        dynamic_debug_texture.draw(node_shape);
      }
    }
    // Start and end nodes
    node_shape.setPosition(plot.to_screen_space(pathfinder.end->pos));
    node_shape.setFillColor({0, 255, 0});
    dynamic_debug_texture.draw(node_shape);

    node_shape.setPosition(plot.to_screen_space(pathfinder.start->pos));
    node_shape.setFillColor({255, 0, 0});
    dynamic_debug_texture.draw(node_shape);
  }

  void reset_view(std::vector<Way>& ways, VisualSettings settings) {
    // reset values to values from import
    plot.reset_values();
    camera_moved = true;
  }

  void set_view(std::vector<Way>& ways, std::vector<float>& rect_value,
                VisualSettings settings) {
    // set the display parameters
    plot.set_values(rect_value[0], rect_value[1], rect_value[2], rect_value[3]);
    camera_moved = true;
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

  void draw_zoom_rect() {
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

  void static_debug_draw(std::vector<Node*> start_nodes,
                         std::vector<Node*> end_nodes, std::vector<Way>& ways,
                         Settings& settings) {
    // debugs that stay in same position/are bound to the roads
    static_debug_texture.clear(sf::Color::Transparent);
    if (settings.debug.draw_node_connections) {
      debug_draw_node_connections(ways);
    }
    if (settings.debug.draw_start_nodes) {
      draw_nodes(start_nodes, sf::Color(180, 0, 0));
    }
    if (settings.debug.draw_end_nodes) {
      draw_nodes(end_nodes, sf::Color(0, 180, 0));
    }
    static_debug_sprite = sf::Sprite(static_debug_texture.getTexture());
  }

  void dynamic_debug_draw(Pathfinder pathfinder, Settings& settings) {
    // debug for things that move
    dynamic_debug_texture.clear(sf::Color::Transparent);
    if (settings.debug.draw_pathfinder) {
      debug_draw_pathfinder(pathfinder);
    }
  }

  void selection_draw(Settings& settings, std::vector<Node>& nodes) {
    sf::CircleShape node_shape(std::max(1.5f, 6.f * plot.scale));
    node_shape.setOrigin(std::max(1.5f, 6.f * plot.scale),
                         std::max(1.5f, 6.f * plot.scale));
    if (settings.selection.active) {
      for (auto node : settings.selection.eligible_nodes) {
        node_shape.setPosition(plot.to_screen_space(node->pos));
        // no selected node
        if (node == settings.selection.closest_node) {
          node_shape.setFillColor(sf::Color(0, 100, 200));
        } else if (settings.selection.start_node != nullptr &&
                   node == settings.selection.start_node) {
          node_shape.setFillColor(sf::Color(0, 200, 100));
        } else if (settings.selection.end_node != nullptr &&
                   node == settings.selection.end_node) {
          node_shape.setFillColor(sf::Color(200, 0, 100));
        } else {
          node_shape.setFillColor(sf::Color(100, 0, 0));
        }
        ui_texture.draw(node_shape);
      }
      // draw selected way
      if (settings.selection.selected_way) {
        draw_polyline(*settings.selection.selected_way,
                      settings.visual.road_width, sf::Color(50, 200, 100),
                      ui_texture);
      }
    }
  }

  void draw(std::vector<Node*> start_nodes, std::vector<Node*> end_nodes,
            std::vector<Node>& nodes, std::vector<Way>& ways,
            Pathfinder pathfinder, std::vector<std::unique_ptr<Car>>& cars,
            Settings& settings, InputState& input) {
    if (camera_moved || input.camera_settings_changed) {
      camera_moved = false;
      input.camera_settings_changed = false;
      // update statics if camera changes
      draw_roads(ways, settings.visual);
      static_debug_draw(start_nodes, end_nodes, ways, settings);
    }
    // dynamic Textures
    draw_cars(cars, settings.visual);
    draw_zoom_rect();
    selection_draw(settings, nodes);
    dynamic_debug_draw(pathfinder, settings);
  }

  void push_to_window(sf::RenderWindow& window) {
    window.draw(road_sprite);
    window.draw(sf::Sprite(car_texture.getTexture()));
    window.draw(sf::Sprite(ui_texture.getTexture()));
    window.draw(static_debug_sprite);
    window.draw(sf::Sprite(dynamic_debug_texture.getTexture()));
  }

  void node_selection_update(Settings& settings, std::vector<Node>& nodes,
                             std::vector<Way>& ways,
                             InputState input) {  // Node/Way selection handling
    if (settings.selection.active) {
      settings.selection.eligible_nodes.clear();
      if (settings.selection.start_node == nullptr) {
        for (auto& node : nodes) {  // every node
          if (node.ways_out.size() > 0) {
            settings.selection.eligible_nodes.push_back(&node);
          }
        }
      } else {  // only neighboring nodes
        for (auto& way : settings.selection.start_node->ways_out) {
          settings.selection.eligible_nodes.push_back(way->nodes.back());
        }  // and start node
        settings.selection.eligible_nodes.push_back(
            settings.selection.start_node);
      }
      float min_dist = INFINITY;
      sf::Vector2<double> real_mouse_pos(
          plot.from_screen_space(sf::Vector2f(input.mouse_pos)));
      // get the closest node to mouse
      for (auto& node : settings.selection.eligible_nodes) {
        if (hypot(real_mouse_pos.x - node->pos.x,
                  real_mouse_pos.y - node->pos.y) < min_dist) {
          min_dist = hypot(real_mouse_pos.x - node->pos.x,
                           real_mouse_pos.y - node->pos.y);
          settings.selection.closest_node = node;
        }
      }
      // handle right click
      if (input.right_mouse_just_pressed &&
          input.mouse_pos.x < road_texture.getSize().x) {
        if (settings.selection.start_node == nullptr) {  // set to closest
          settings.selection.start_node = settings.selection.closest_node;
        } else if (settings.selection.start_node ==
                   settings.selection.closest_node) {  // reset
          settings.selection.start_node = nullptr;
        } else {  // set end node
          settings.selection.end_node = settings.selection.closest_node;
          for (auto& way : ways) {
            if (way.nodes.front()->id == settings.selection.start_node->id &&
                way.nodes.back()->id == settings.selection.end_node->id) {
              settings.selection.selected_way = &way;
              break;
            }
          }
          if (settings.selection.selected_way == nullptr) {
            settings.selection = SelectionSettings{};
          }
        }
      }
    }
  }

  void update(InputState input, std::vector<Node>& nodes,
              std::vector<Way>& ways, Settings& settings) {
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
        set_view(ways, rect_value, settings.visual);
      }
    }
    if (settings.selection.selected_way == nullptr) {
      node_selection_update(settings, nodes, ways, input);
    } else {
      settings.selection.eligible_nodes.clear();
    }
  }
};