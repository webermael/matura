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

#include "ImGuiFileDialog.h"
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
  CurrentWindow currentwindow = START;
  // create main display window
  auto window = sf::RenderWindow(sf::VideoMode(1800, 900), "Matura");
  sf::Vector2u interface_size = {400u, window.getSize().y};
  sf::Vector2u screen_size(window.getSize().x - interface_size.x,
                           window.getSize().y);
  window.setFramerateLimit(144);

  // Initialize ImGui-SFML
  if (!ImGui::SFML::Init(window)) {
    std::cerr << "Failed to initialize ImGui-SFML!\n";
    return -1;
  }

  std::string cityStr, countryStr;
  std::string
      generated_file;  // the path to the JSON the Python script will make

  std::unique_ptr<Simulation> sim;

  sf::Clock clock;
  // --- GAME LOOP ---
  while (window.isOpen()) {
    // - Events -
    handle_events(window, input);
    ImGui::SFML::Update(window, sf::seconds(input.dt));
    window.clear(sf::Color::Black);

    switch (currentwindow) {
      case START: {
        // Quit or Load file
        StartButton output = start_window();
        if (output.pick_file) {
          currentwindow = FROM_FILE;
        } else if (output.quit) {
          window.close();
        }
        break;
      }
      case FROM_FILE: {
        // Load File (running from Start Menu)
        FilePickerFeedback output = file_picker();
        if (!output.file_path_name.empty()) {
          sim =
              std::make_unique<Simulation>(output.file_path_name, screen_size);
          currentwindow = SIMULATION;
        } else if (output.canceled) {
          currentwindow = START;
        }
        break;
      }
      case SIMULATION: {
        if (sim) {
          create_settings_menu(sim->settings, window, interface_size, *sim,
                               input, currentwindow);
          sim->update(input);
          sim->draw(window, input);
        } else {
          currentwindow = START;
        }
        break;
      }
      case NEW_FILE: {
        // Load File (running from Simulation)
        FilePickerFeedback output = file_picker();

        if (!output.file_path_name.empty()) {
          // if a file, create new simulation
          sim =
              std::make_unique<Simulation>(output.file_path_name, screen_size);
          currentwindow = SIMULATION;
        } else if (output.canceled) {
          // otherwise return to existing one
          currentwindow = SIMULATION;
        }

        break;
      }
    }

    ImGui::SFML::Render(window);

    // - Finish Frame -
    window.display();
    input.dt = clock.restart().asSeconds();
  }
  ImGui::SFML::Shutdown();
}