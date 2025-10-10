#pragma once
#include <SFML/Graphics.hpp>
#include <vector>

#include "../utils/settings.h"
#include "node.h"
#include "way.h"

struct new_target {
  int new_index;
  Way* new_way;
  bool end_of_path;
};

class Car {
 public:
  sf::Vector2<double> pos;
  sf::Vector2<double> target_pos;
  float speed;
  float target_speed;
  float accel = 20.f;
  float decel = 40.f;
  float coast_decel = 10.f;
  std::vector<Way*> path;
  int node_index;
  Way* curr_way;
  float way_progress = 0.f;
  sf::Vector2<double> direction;
  bool active = true;
  sf::Color color;
  Car(std::vector<Way*> path, Settings settings) : path(path) {
    pos = path[0]->nodes[0]->pos;
    target_pos = path[0]->nodes[1]->pos;
    target_speed = path[0]->speed;
    node_index = 1;
    curr_way = path[0];
    curr_way->add_car(this);
    direction = get_direction(pos, target_pos, get_dist(pos, target_pos));
    // set start speed
    float turn_multiplier = turn_lookahead(settings.driving);
    float car_multiplier = car_lookahead(settings.driving);
    speed = target_speed * std::min({1.f, turn_multiplier, car_multiplier});
    set_color(settings.visual, COAST);
  }
  // distance between two points
  float get_dist(sf::Vector2<double> pos1, sf::Vector2<double> pos2) {
    return std::sqrtf(std::powf((pos1.x - pos2.x), 2.f) +
                      std::powf((pos1.y - pos2.y), 2.f));
  }
  // dot product of two vectors
  float dot_product(sf::Vector2<double> vector1, sf::Vector2<double> vector2) {
    return (vector1.x * vector2.x + vector1.y * vector2.y) /
           (get_dist(sf::Vector2<double>(0.f, 0.f), vector1) *
            get_dist(sf::Vector2<double>(0.f, 0.f), vector2));
  }
  // dot product of vectors connecting three points
  float get_dot_product(sf::Vector2<double> pos1, sf::Vector2<double> pos2,
                        sf::Vector2<double> pos3) {
    sf::Vector2<double> vector1(pos2.x - pos1.x, pos2.y - pos1.y);
    sf::Vector2<double> vector2(pos3.x - pos2.x, pos3.y - pos2.y);
    return dot_product(vector1, vector2);
  }
  // change speed and return current state
  State set_speed(float dt, float multiplier, DriveSettings settings) {
    State state = COAST;
    float target = target_speed * multiplier;
    // set immediately on very small difference
    if (abs(speed - target) < 0.03) {
      speed = target;
      if (target == 0) {
        state = STANDSTILL;
      } else {
        state = CRUISE;
      }
      // strong deceleration on big difference
    } else if (target < speed) {
      speed -= decel * dt;
      state = BRAKE;
      // weak deceleration on small difference
    } else if (target + 8 < speed) {
      speed -= coast_decel * dt;
      state = COAST;
      // accelerate if too slow
    } else if (target > speed) {
      speed += accel * dt;
      state = ACCELERATE;
    }
    speed =
        std::clamp(speed, 0.f, settings.speed_cap);  // clamp to positive value
    return state;
  }
  // sets the current color depending on highlight mode and values
  void set_color(VisualSettings settings, State state) {
    switch (settings.highlight_mode) {
      case ACCELERATION:
        switch (state) {
          case CRUISE:
            color = sf::Color{0, 200, 200};
            break;
          case ACCELERATE:
            color = sf::Color{0, 200, 0};
            break;
          case BRAKE:
            color = sf::Color{200, 0, 0};
            break;
          case COAST:
            color = sf::Color{150, 100, 0};
            break;
          case STANDSTILL:
            color = settings.car_color;
            break;
          default:
            break;
        }
        break;
      case SPEED:
        color = sf::Color{
            static_cast<sf::Uint8>(std::clamp(255.f - speed * 2.f, 0.f, 255.f)),
            static_cast<sf::Uint8>(std::clamp(50.f + speed * 4.f, 0.f, 255.f)),
            0};
        break;
      case OFF:
        color = settings.car_color;
        break;
      default:
        break;
    }
  }

  // get next target way and node_index in path
  new_target next_target(int node_index, Way* way) {
    new_target output;
    output.new_way = way;
    output.end_of_path = false;
    output.new_index = node_index;
    output.new_index += 1;

    unsigned int way_index =
        std::distance(path.begin(), std::find(path.begin(), path.end(), way));
    if (output.new_index >= way->nodes.size() &&
        (way_index + 1 < path.size())) {
      output.new_way = path[way_index + 1];
      output.new_index = 1;

    } else if (output.new_index >= way->nodes.size() &&
               (way_index + 1 >= path.size())) {
      output.new_index -= 1;
      output.end_of_path = true;
    }
    return output;
  }

  // unit vector from pos1 -> pos2
  sf::Vector2<double> get_direction(sf::Vector2<double> pos1,
                                    sf::Vector2<double> pos2, double length) {
    return sf::Vector2<double>((pos2.x - pos1.x) / length,
                               (pos2.y - pos1.y) / length);
  }

  void move_toward(float budget, double distance) {
    sf::Vector2<double> direction_to_target =
        get_direction(pos, target_pos, distance);
    direction = direction_to_target;
    pos.x += direction_to_target.x * budget;
    pos.y += direction_to_target.y * budget;
  }

  void move(float dt) {
    // total move distance this frame
    float budget = speed * dt;
    // move until depleted
    while (budget > 0 && active) {
      float distance = get_dist(pos, target_pos);

      // next node is in range
      if (budget >= distance) {
        // move there, update targets
        way_progress += distance;
        pos = target_pos;
        new_target nt = next_target(node_index, curr_way);
        node_index = nt.new_index;

        if (nt.new_way != curr_way) {
          // change way that this car belongs to
          curr_way->remove_car(this);
          curr_way = nt.new_way;
          curr_way->add_car(this);
          way_progress = 0;
        }

        if (!nt.end_of_path) {
          target_pos = curr_way->nodes[node_index]->pos;
          target_speed = curr_way->speed;

        } else {
          active = false;
          curr_way->remove_car(this);
        }
        budget -= distance;

      } else if (budget < distance) {
        move_toward(budget, distance);
        way_progress += budget;
        budget = 0;
      }
    }
  }

  float turn_lookahead(DriveSettings settings) {
    float max_dist = speed * 5;
    float lookahead = max_dist - get_dist(pos, target_pos);
    float curvature = 0;

    // first node (preparation for while loop)
    sf::Vector2<double> old_node = pos;
    sf::Vector2<double> node = target_pos;
    new_target nt = next_target(node_index, curr_way);
    int index = nt.new_index;
    Way* way = nt.new_way;
    bool end = nt.end_of_path;
    // loop until lookahead distance has passed
    while (lookahead > 0 && !end) {
      sf::Vector2<double> new_node = way->nodes[index]->pos;
      curvature += acosf(std::clamp<float>(
                       get_dot_product(old_node, node, new_node), -1.f, 1.f)) *
                   (lookahead / max_dist);
      old_node = node;
      node = new_node;
      nt = next_target(index, way);
      index = nt.new_index;
      way = nt.new_way;
      end = nt.end_of_path;
      lookahead -= get_dist(old_node, node);
    }
    return 1.f / (1.f + curvature * settings.curvature_slowdown);
  }

  float car_lookahead(DriveSettings settings) {
    Car* next_car = nullptr;

    // Check current way
    for (auto car_in_way : curr_way->cars) {
      if (car_in_way == this) continue;
      if (car_in_way->way_progress > this->way_progress) {
        next_car = car_in_way;
        break;
      }
    }

    // Check forward ways if needed
    if (!next_car) {
      size_t way_index = std::distance(
          path.begin(), std::find(path.begin(), path.end(), curr_way));
      for (size_t i = way_index + 1; i < path.size(); ++i) {
        Way* fwd_way = path[i];
        if (!fwd_way->cars.empty()) {
          next_car = fwd_way->cars.front();  // sorted, nearest to start
          break;
        }
      }
    }
    if (next_car) {
      float target_gap = settings.car_gap_target;
      if (settings.multiply_by_speed) {
        target_gap *= speed;
      }
      return 1 - (target_gap / (1 + get_dist(pos, next_car->pos)));
    }
    return 1.f;
  }

  void update(float dt, Settings settings) {
    if (!active) {
      return;
    }
    float turn_multiplier = turn_lookahead(settings.driving);
    float car_multiplier = car_lookahead(settings.driving);
    State state = set_speed(
        dt, std::min({1.f, turn_multiplier, car_multiplier}), settings.driving);
    set_color(settings.visual, state);
    move(dt);
  }
};
