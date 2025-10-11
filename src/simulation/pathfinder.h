#pragma once

#include <SFML/Graphics.hpp>
#include <algorithm>
#include <cmath>
#include <map>
#include <vector>

#include "../utils/settings.h"
#include "node.h"
#include "way.h"

struct node_properties {
  float weight;
  std::vector<Way*> path;
};

class Pathfinder {
 public:
  Node* start;
  Node* end;
  std::map<Node*, node_properties> explored_nodes;
  std::vector<Node*> active_nodes;
  float time_searching;
  bool active = false;
  PathFinding pathfinding_mode = ASTAR;

  void reset(Node* start_node, Node* end_node, SimSettings settings) {
    start = start_node;
    end = end_node;
    explored_nodes.clear();
    explored_nodes[start] = {0.0f, {}};
    active_nodes.clear();
    active_nodes.push_back(start);
    time_searching = 0.0f;
    active = true;
    pathfinding_mode = settings.pathfinding;
  }

  Pathfinder()
      : explored_nodes() {  // in initializer list to avoid default construction
  }

  float get_dot_product(Node* node, Way* way, std::string direction) {
    // dot product of vector into node in "direction" and vector out of node
    // requires a way leading out of node
    Way* old_way = explored_nodes[node].path.back();
    sf::Vector2<double> old_node =
        old_way->nodes.at(old_way->nodes.size() - 2)->pos;
    sf::Vector2<double> first_node = way->nodes[1]->pos;
    sf::Vector2<double> forward(first_node.x - node->pos.x,
                                first_node.y - node->pos.y);
    sf::Vector2<double> backward = get_target_vector(
        direction, sf::Vector2<double>{node->pos.x - old_node.x,
                                       node->pos.y - old_node.y});
    return dot_product(forward, backward);
  }

  sf::Vector2<double> get_target_vector(std::string direction,
                                        sf::Vector2<double> vector) {
    // rotate target vector according to direction given
    if (direction == "through") {
      return vector;
    } else if (direction == "left") {
      return sf::Vector2<double>(-vector.y, vector.x);
    } else if (direction == "right") {
      return sf::Vector2<double>(vector.y, -vector.x);
    } else {
      return vector;
    }
  }

  float dot_product(sf::Vector2<double> v1, sf::Vector2<double> v2) {
    return (v1.x * v2.x + v1.y * v2.y) /
           (std::sqrtf(std::powf(v1.x, 2.0f) + std::powf(v1.y, 2.0f)) *
            std::sqrtf(std::powf(v2.x, 2.0f) + std::powf(v2.y, 2.0f)));
  }

  void step() {
    // start = time.perf_counter();

    if (!active) {
      return;
    }

    if (explored_nodes.count(end) != 0 || active_nodes.empty()) {
      active = false;  // finish when end found or no more places to go
      return;
    }

    float min_dist = INFINITY;
    Node* node = nullptr;

    for (Node* node_check : active_nodes) {
      float dist;
      if (pathfinding_mode == ASTAR) {
        // with added heuristic -> distance to end node
        dist = std::powf(explored_nodes[node_check].weight, 2.0f) +
               std::hypot(node_check->pos.x - end->pos.x,
                          node_check->pos.y - end->pos.y);
      } else if (pathfinding_mode == DIJKSTRA) {
        // just weight so far
        dist = explored_nodes[node_check].weight;
      }
      if (dist < min_dist) {
        min_dist = dist;
        node = node_check;  // pick node with lowest cost
      }
    }
    if (!node) {
      return;
    }

    for (Way* way : node->ways_out) {
      float dot_product = 1.0f;
      if (!explored_nodes[node].path.empty() &&
          !explored_nodes[node].path.back()->turns.empty()) {
        // if there are turnrestrictions
        dot_product = -1.0f;
        for (auto direction : explored_nodes[node].path.back()->turns) {
          dot_product =
              std::max(dot_product, get_dot_product(node, way, direction));
          // only allow a path if it meets one of the directions well enough
        }
      }
      if (dot_product > 0.6f) {
        Node* new_node = way->nodes.back();
        // add node to be explored if unexplored or already found but with
        // higher weight
        if (explored_nodes.count(new_node) == 0 ||
            (explored_nodes.count(new_node) > 0 &&
             (explored_nodes[node].weight + way->length) <
                 explored_nodes[new_node].weight)) {
          active_nodes.push_back(new_node);
          std::vector<Way*> path_ways(explored_nodes[node].path);
          path_ways.push_back(way);
          explored_nodes[new_node] = {explored_nodes[node].weight + way->length,
                                      path_ways};
        }
      }
    }
    // remove node that was checked
    active_nodes.erase(
        std::remove(active_nodes.begin(), active_nodes.end(), node),
        active_nodes.end());
    // time_searching += (time.perf_counter() - start);
  }
};
