#include <imgui-SFML.h>
#include <imgui.h>

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
#include "interface/ui.h"
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
  auto window = sf::RenderWindow(sf::VideoMode(1800, 900), "Matura");
  sf::Vector2u interface_size = {400u, window.getSize().y};
  sf::Vector2u screen_size(window.getSize().x - interface_size.x,
                           window.getSize().y);
  window.setFramerateLimit(144);

  // Initialize ImGui-SFML
  if (!ImGui::SFML::Init(window)) {
    std::cerr << "Failed to initialize ImGui-SFML!\n";
    return -1;  // or handle error
  }

  // Create Simulation with json data
  Simulation sim("./src/Aarau.json", screen_size);

  sf::Clock clock;
  float dt = 0.f;

  // --- GAME LOOP ---
  while (window.isOpen()) {
    dt = clock.restart().asSeconds();
    input.dt = dt;
    // - Events -
    handle_events(window, input);

    // - Updating -
    ImGui::SFML::Update(window, sf::seconds(dt));
    create_settings_menu(sim.settings, window, interface_size, sim, input);

    sim.update(input);

    // - Drawing -
    window.clear(sf::Color::White);

    sim.draw(window, input);
    ImGui::SFML::Render(window);

    window.display();
  }
  ImGui::SFML::Shutdown();
};