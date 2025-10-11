#include <SFML/Graphics.hpp>

#include "../simulation/simulation.h"
#include "../utils/settings.h"

void pathfinding(Settings& settings, Simulation& sim) {
  const char* pathfinding_names[] = {"A*", "Dijkstra"};
  int current = static_cast<int>(settings.sim.pathfinding);

  if (ImGui::Combo("Pathfinding Algorithm", &current, pathfinding_names,
                   IM_ARRAYSIZE(pathfinding_names))) {
    sim.change_pathfinder_mode(static_cast<PathFinding>(current));
  }
  ImGui::SliderInt("Pathfinder Steps/Frame",
                   &settings.sim.pathfinder_step_count, 0, 50);

  ImGui::Text("Path count: %zu", sim.paths.size());
}

void highlight_selector(Settings& settings) {
  const char* highlight_names[] = {"Acceleration", "Speed", "Off"};
  int current = static_cast<int>(settings.visual.highlight_mode);

  if (ImGui::Combo("Car Highlight Mode", &current, highlight_names,
                   IM_ARRAYSIZE(highlight_names))) {
    settings.visual.highlight_mode = static_cast<Highlight>(current);
  }
}

void ColorEditor(const char* label, sf::Color& color, InputState& input) {
  // ImGui uses floats [0,1] for color components
  float col[3] = {color.r / 255.f, color.g / 255.f, color.b / 255.f};

  if (ImGui::ColorEdit3(label, col)) {  // returns true if value changed
    color.r = static_cast<sf::Uint8>(col[0] * 255.f);
    color.g = static_cast<sf::Uint8>(col[1] * 255.f);
    color.b = static_cast<sf::Uint8>(col[2] * 255.f);
    input.camera_settings_changed = true;
  }
}

void create_settings_menu(Settings& settings, sf::RenderWindow& window,
                          sf::Vector2u interface_size, Simulation& sim,
                          InputState& input) {
  ImGui::SetNextWindowPos(ImVec2(window.getSize().x - interface_size.x, 0));
  ImGui::SetNextWindowSize(ImVec2(interface_size));
  ImGui::Begin("Settings", nullptr,
               ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoMove |
                   ImGuiWindowFlags_NoCollapse);
  ImGui::PushItemWidth(200);

  // --- DRIVING ---
  if (ImGui::CollapsingHeader("Driving Settings")) {
    ImGui::InputFloat("Car Gap", &settings.driving.car_gap_target, 0.1f, 1.f,
                      "%.2f");
    settings.driving.car_gap_target =
        std::max(settings.driving.car_gap_target, 0.f);
    ImGui::Checkbox("Gap Speed Dependency",
                    &settings.driving.multiply_by_speed);
    ImGui::InputFloat("Curvature Slowdown",
                      &settings.driving.curvature_slowdown, 0.1f, 1.f, "%.2f");
    settings.driving.curvature_slowdown =
        std::max(settings.driving.curvature_slowdown, 0.f);
    ImGui::InputInt("Global Speedcap (km/h)", &settings.driving.speed_cap, 5,
                    10);
    settings.driving.speed_cap = std::max(settings.driving.speed_cap, 0);
    ImGui::Checkbox("Use Road Speed Limit",
                    &settings.driving.use_road_maxspeed);
  }

  // --- SIMULATION SETTTINGS
  if (ImGui::CollapsingHeader("Simulation Settings")) {
    ImGui::Checkbox("Paused", &sim.paused);
    ImGui::InputFloat("Simulation Speed", &settings.sim.game_speed, 0.1f, 1.f,
                      "%.2f");
    settings.sim.game_speed = std::max(settings.sim.game_speed, 0.f);
    ImGui::Checkbox("Car Spawning", &sim.car_spawning);
    if (ImGui::SliderFloat("Car Spawn Time (s)", &settings.sim.car_spawn_time,
                           0.01f, 1.f, "%.2f")) {
      sim.car_timer = settings.sim.car_spawn_time;
    }
    ImGui::InputInt("Car Count Cap", &settings.sim.car_cap, 25, 100);
    ImGui::Text("Car Count: %d", sim.cars.size());
    if (ImGui::Button("Clear Cars", ImVec2(100.f, 40.f))) {
      sim.clear_cars();
    }
    pathfinding(settings, sim);
  }

  // VISUAL SETTINGS
  if (ImGui::CollapsingHeader("Visual Settings")) {
    highlight_selector(settings);
    ImGui::Checkbox("Weight Speed Highlight by Speed Cap",
                    &settings.visual.highlight_speedcap_weight);
    ImGui::Checkbox("Draw Cars", &settings.visual.draw_cars);
    ColorEditor("Background Color", settings.visual.bg_color, input);
    ColorEditor("Road Color", settings.visual.road_color, input);
    ColorEditor("Car Color", settings.visual.car_color, input);
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
