#pragma once
#include <vector>

#include "graph/node.h"
#include "graph/plot.h"
#include "graph/way.h"

class Display {
 public:
  Plot plot;
  Display(const Plot& plot) : plot(plot) {}

  /*
  Pointers and References
  - &: argument is passed "by reference" -> the object is not copied but could
  be modified (to avoid use "const")

  - *: here "way.nodes" is no longer a vector of objects, but a vector of
  pointers (Node*) (for the same reason, its attribute has to be acessed using
  "->")
  */
  void reset_view(std::unordered_map<std::string, Node>& nodes,
                  std::vector<Way>& ways) {
    plot.reset_values();

    for (auto& [id, node] : nodes) {
      node.display_pos = plot.to_screen_space(node.pos);
      node.test_visible(plot.screen_size);
    }

    for (auto& way : ways) {
      way.test_visible();

      way.display_way.clear();
      for (auto* node : way.nodes) {
        way.display_way.push_back(node->display_pos);
      }
    }
  };

  void set_view(std::unordered_map<std::string, Node>& nodes,
                std::vector<Way>& ways, std::vector<float>& rect_value) {
    plot.set_values(rect_value[0], rect_value[1], rect_value[2], rect_value[3]);

    for (auto& [id, node] : nodes) {
      node.display_pos = plot.to_screen_space(node.pos);
      node.test_visible(plot.screen_size);
    }

    for (auto& way : ways) {
      way.test_visible();

      way.display_way.clear();
      for (auto* node : way.nodes) {
        way.display_way.push_back(node->display_pos);
      }
    }
  };
};