#include <SFML/Graphics.hpp>
#include <chrono>
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <random>
#include <string>
#include <unordered_map>
#include <vector>

#include "interface/display.h"
#include "interface/plot.h"
#include "simulation/car.h"
#include "simulation/node.h"
#include "simulation/pathfinder.h"
#include "simulation/simulation.h"
#include "simulation/way.h"
#include "utils/event_handler.h"
#include "utils/settings.h"

using json = nlohmann::json;

int main() {
  // randomize seed
  srand(std::chrono::system_clock::now().time_since_epoch().count());

  // for input handling in main loop
  InputState input;

  // create main display window
  auto window = sf::RenderWindow(sf::VideoMode(1200, 600), "Matura");
  sf::Vector2u interface_size = {200u, window.getSize().y};
  sf::Vector2u screen_size(window.getSize().x - interface_size.x,
                           window.getSize().y);
  window.setFramerateLimit(144);

  // Create Simulation with json data
  Simulation sim("./src/Aarau.json", screen_size);

  sf::Clock clock;
  float dt = 0.0f;

  // --- GAME LOOP ---
  while (window.isOpen()) {
    handle_events(window, input);

    sim.update(input);

    window.clear(sf::Color::White);
    sim.draw(window);

    dt = clock.restart().asSeconds();
    input.dt = dt;
    window.display();
  }
};