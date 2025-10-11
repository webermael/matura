#include <SFML/Graphics.hpp>

#include "../simulation/simulation.h"
#include "../utils/settings.h"

void create_settings_menu(Settings& settings, sf::RenderWindow& window,
                          sf::Vector2u interface_size, Simulation& sim,
                          InputState& input) {
  ImGui::SetNextWindowPos(ImVec2(window.getSize().x - interface_size.x, 0));
  ImGui::SetNextWindowSize(ImVec2(interface_size));
  ImGui::Begin("Settings", nullptr,
               ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoMove |
                   ImGuiWindowFlags_NoCollapse);

  // --- SIMULATION SETTTINGS
  if (ImGui::CollapsingHeader("Simulation Settings")) {
    ImGui::Checkbox("Paused", &sim.paused);
    ImGui::SliderFloat("Simulation Speed", &settings.sim.game_speed, 0.f, 10.f);
    ImGui::SliderFloat("Car Spawn Time", &settings.sim.car_spawn_time, 0.01f,
                       20.f);
    ImGui::InputInt("Car Count Cap", &settings.sim.car_cap, 0, 10000);
    ImGui::Text("Car Count: %d", sim.cars.size());
    if (ImGui::Button("Clear Cars", ImVec2(100.f, 40.f))) {
      sim.clear_cars();
    }
    ImGui::SliderInt("Pathfinder Steps/Frame",
                     &settings.sim.pathfinder_step_count, 0, 50);
    ImGui::Text("Paths found: %d", sim.astar_paths.size());
  }

  // VISUAL SETTINGS
  if (ImGui::CollapsingHeader("Visual Settings")) {
    ImGui::Checkbox("Draw Cars", &settings.visual.draw_cars);
  }

  // DEBUG SETTINGS
  if (ImGui::CollapsingHeader("Debug Settings")) {
    (ImGui::Checkbox("Draw Pathfinder", &settings.debug.draw_pathfinder));

    if (ImGui::Checkbox("Draw Node Connections",
                        &settings.debug.draw_node_connections) ||
        ImGui::Checkbox("Draw Start Nodes", &settings.debug.draw_start_nodes) ||
        ImGui::Checkbox("Draw End Nodes", &settings.debug.draw_end_nodes)) {
      input.camera_settings_changed = true;
    }
  }
  ImGui::End();
}