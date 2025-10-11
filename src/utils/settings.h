#pragma once
#include <cmath>

enum Highlight { ACCELERATION, SPEED, OFF };
enum State { BRAKE, ACCELERATE, COAST, CRUISE, STANDSTILL };
enum PathFinding { ASTAR, DIJKSTRA };

struct DriveSettings {
  float car_gap_target = 1.f;
  bool multiply_by_speed = true;
  float curvature_slowdown = 0.7f;
  int speed_cap = 200;
};

struct SimSettings {
  float game_speed = 1.f;
  float car_spawn_time = 0.5f;
  int car_cap = 2000;
  PathFinding pathfinding = ASTAR;
  int pathfinder_step_count = 10;
};

struct VisualSettings {
  Highlight highlight_mode = OFF;
  float road_width = 7.f;
  bool draw_cars = true;
  sf::Color bg_color = sf::Color{0, 0, 0};
  sf::Color road_color = sf::Color{60, 60, 60};
  sf::Color car_color = {140, 130, 150};
};

struct DebugSettings {
  bool draw_node_connections = false;
  bool draw_pathfinder = false;
  bool draw_start_nodes = false;
  bool draw_end_nodes = false;
};

struct Settings {
  DriveSettings driving;
  DebugSettings debug;
  SimSettings sim;
  VisualSettings visual;
};