#include <SFML/Graphics.hpp>
#include <algorithm>
#include <cmath>
#include <map>
#include <vector>

#include "node.h"
#include "way.h"

struct node_properties {
  float weight;
  std::vector<Way*> path;
};

class Astar {
 public:
  Node* start;
  Node* end;
  std::map<Node*, node_properties> explored_nodes;
  std::vector<Node*> active_nodes;
  float time_searching;
  bool active;

  void reset(Node* start_node, Node* end_node) {
    start = start_node;
    end = end_node;
    explored_nodes.clear();
    explored_nodes[start] = {0.0f, {}};
    active_nodes.clear();
    active_nodes.push_back(start);
    time_searching = 0.0f;
    active = true;
  }

  Astar(Node* start_node, Node* end_node)
      : start(start_node),
        end(end_node),
        explored_nodes() {  // in initializer list to avoid default construction
    reset(start_node, end_node);
  }

  float get_dot_product(Node* node, Way* way, std::string direction) {
    Way* old_way = explored_nodes[node].path.back();
    sf::Vector2f old_node = old_way->nodes.at(old_way->nodes.size() - 2)->pos;
    sf::Vector2f first_node = way->nodes[1]->pos;
    sf::Vector2f forward(first_node.x - node->pos.x,
                         first_node.y - node->pos.y);
    sf::Vector2f backward = get_target_vector(
        direction,
        sf::Vector2f{node->pos.x - old_node.x, node->pos.y - old_node.y});
    return dot_product(forward, backward);
  }

  sf::Vector2f get_target_vector(std::string direction, sf::Vector2f vector) {
    // rotate target vector according to direction given
    if (direction == "through") {
      return vector;
    } else if (direction == "left") {
      return sf::Vector2f(-vector.y, vector.x);
    } else if (direction == "right") {
      return sf::Vector2f(vector.y, -vector.x);
    }
  }

  float dot_product(sf::Vector2f v1, sf::Vector2f v2) {
    return (v1.x * v2.x + v1.y * v2.y) /
           (std::sqrtf(std::powf(v1.x, 2.0f) + std::powf(v1.y, 2.0f)) +
            std::sqrtf(std::powf(v2.x, 2.0f) + std::powf(v2.y, 2.0f)));
  }

  void step() {
    // start = time.perf_counter();

    if (!active) {
      return;
    }

    if (explored_nodes.count(end) > 0 || active_nodes.empty()) {
      active = false;
      return;
    }

    float min_dist = INFINITY;
    Node* node = nullptr;

    for (Node* node_check : active_nodes) {
      float dist = std::powf(explored_nodes[node_check].weight, 2.0f) +
                   std::hypot(node_check->pos.x - end->pos.x,
                              node_check->pos.y - end->pos.y);
      if (dist < min_dist) {
        min_dist = dist;
        node = node_check;
      }
    }
    if (!node) {
      return;
    }

    for (Way* way : node->ways_out) {
      float dot_product = -1.0f;
      if (!explored_nodes[node].path.empty() &&
          !explored_nodes[node].path.back()->turns.empty()) {
        dot_product = -1.0f;
        for (auto direction : explored_nodes[node].path.back()->turns) {
          dot_product = 0.0f;  // check out, use sf::dot ?
        }
        if (dot_product > 0.5f) {
          Node* new_node = way->nodes.back();
          if (explored_nodes.count(new_node) > 0 ||
              (explored_nodes.count(new_node) > 0 &&
               (explored_nodes[node].weight + way->length) <
                   explored_nodes[new_node].weight)) {
            active_nodes.push_back(new_node);
            std::vector<Way*> path_ways(explored_nodes[node].path);
            path_ways.push_back(way);
            explored_nodes[new_node] = {
                explored_nodes[node].weight + way->length, path_ways};
          }
        }
      }
    }

    active_nodes.erase(
        std::remove(active_nodes.begin(), active_nodes.end(), node),
        active_nodes.end());
    // time_searching += (time.perf_counter() - start);
  }

  void render(sf::RenderWindow window) {
    for (const auto& node : explored_nodes) {
      sf::CircleShape node_shape(5.0f);
      node_shape.setPosition(node.first->display_pos);
      node_shape.setFillColor({250, 150, 0});
      window.draw(node_shape);
    }
    sf::CircleShape start_shape(5.0f), end_shape(5.0f);
    start_shape.setPosition(start->display_pos);
    start_shape.setFillColor({255, 0, 0});
    window.draw(start_shape);
    end_shape.setPosition(end->display_pos);
    end_shape.setFillColor({0, 255, 0});
    window.draw(end_shape);
  }
};
