#pragma once
#include <cmath>

enum Highlight { ACCELERATION, SPEED, OFF };
enum State { BRAKE, ACCELERATE, COAST, CRUISE, STANDSTILL };
enum PathFinding { ASTAR, DIJKSTRA };

struct DriveSettings {
  float car_gap_target = 1.f;
  bool multiply_by_speed = true;
  float curvature_slowdown = 0.75f;
  float speed_cap = INFINITY;
};

struct SimSettings {
  float game_speed = 1.f;
  float car_spawn_time = 0.5f;
  PathFinding pathfinding = ASTAR;
  int pathfinder_step_count = 10;
};

struct VisualSettings {
  Highlight highlight_mode = OFF;
  sf::Color road_color = sf::Color{60, 60, 60};
  sf::Color car_color = {140, 130, 150};
};

struct DebugSettings {};

struct Settings {
  DriveSettings driving;
  DebugSettings debug;
  SimSettings sim;
  VisualSettings visual;
};