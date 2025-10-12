#pragma once
#include <SFML/Graphics.hpp>
#include <string>
#include <vector>

class Car;

class Node;  // forward declaration

class Way {
 public:
  std::string id;
  int index;
  bool oneway;
  int lanes;
  std::vector<std::string> turns;
  int speed;
  std::vector<Node*> nodes;
  std::vector<Car*> cars;
  float length;
  bool blocked = false;

  Way(std::string id, int index, bool oneway, int lanes,
      std::vector<std::string> turns, int speed, std::vector<Node*>& nodes,
      float length)
      : id(id),
        index(index),
        oneway(oneway),
        lanes(lanes),
        turns(turns),
        speed(speed),
        nodes(nodes),
        length(length) {}

  void add_car(Car* car) {
    // prevent duplicates
    if (std::find(cars.begin(), cars.end(), car) == cars.end()) {
      cars.push_back(car);
    }
  }

  void remove_car(Car* car) {
    auto it = std::remove(cars.begin(), cars.end(), car);
    if (it != cars.end()) {
      cars.erase(it, cars.end());  // remove car if it's in the list
    }
  }
};
