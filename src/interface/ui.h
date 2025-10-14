#include <SFML/Graphics.hpp>

#include "../simulation/node.h"
#include "../simulation/simulation.h"
#include "../utils/settings.h"
// Window statemachine, used to run correct window
enum CurrentWindow { START, FROM_FILE, NEW_FILE, SIMULATION, EXPORT };
// Outputs of file picking
struct FilePickerFeedback {
  std::string file_path = "";
  std::string file_path_name = "";
  bool canceled = false;
};
// outputs from the Main Menu
struct StartButton {
  bool pick_file = false;
  bool quit = false;
};

// Load File and Quit buttons
StartButton start_window() {
  StartButton output;

  ImVec2 windowSize = ImGui::GetWindowSize();
  ImVec2 displaySize = ImGui::GetIO().DisplaySize;

  ImGui::SetNextWindowPos(ImVec2((displaySize.x - windowSize.x) * 0.5f,
                                 (displaySize.y - windowSize.y) * 0.5f));
  ImGui::SetNextWindowSize(ImVec2(400, 200), ImGuiCond_FirstUseEver);
  ImGui::Begin("Traffix", nullptr,
               ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoCollapse);

  float buttonWidth = 200;

  // Load button
  ImGui::SetCursorPosX((windowSize.x - buttonWidth) * 0.5f);  // center button
  if (ImGui::Button("Load From File", ImVec2(buttonWidth, 50))) {
    output.pick_file = true;
  }
  // Quit button
  ImGui::SetCursorPosX((windowSize.x - buttonWidth) * 0.5f);
  if (ImGui::Button("Quit", ImVec2(buttonWidth, 50))) {
    output.quit = true;
  }

  ImGui::End();
  return output;
}

// Runs until a file is chosen or canceled, if canceled returns to previous menu
FilePickerFeedback file_picker() {
  FilePickerFeedback output;
  ImGuiFileDialog::Instance()->OpenDialog("ChooseJSONDlgKey",
                                          "Choose JSON File", ".json", ".");

  if (ImGuiFileDialog::Instance()->Display("ChooseJSONDlgKey")) {
    if (ImGuiFileDialog::Instance()->IsOk()) {
      output.file_path_name = ImGuiFileDialog::Instance()->GetFilePathName();
      output.file_path = ImGuiFileDialog::Instance()->GetCurrentPath();
    } else {
      output.canceled = true;
    }
    ImGuiFileDialog::Instance()->Close();  // close once an action was taken
  }
  return output;
}

// helper functions
void pathfinding(Settings& settings, Simulation& sim) {
  const char* pathfinding_names[] = {"A*", "Dijkstra"};
  int current = static_cast<int>(settings.sim.pathfinding);

  if (ImGui::Combo("Pathfinding Algorithm", &current, pathfinding_names,
                   IM_ARRAYSIZE(pathfinding_names))) {
    sim.change_pathfinder_mode(static_cast<PathFinding>(current));
  }
  ImGui::InputInt("Pathfinder Steps/Frame", &settings.sim.pathfinder_step_count,
                  10, 50);
  settings.sim.pathfinder_step_count =
      std::max(0, settings.sim.pathfinder_step_count);

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
void ColorEditor(const char* label, sf::Color& color, InputState& input,
                 bool camera_changed = true) {
  // ImGui uses floats [0,1] for color components
  float col[3] = {color.r / 255.f, color.g / 255.f, color.b / 255.f};

  if (ImGui::ColorEdit3(label, col)) {  // returns true if value changed
    color.r = static_cast<sf::Uint8>(col[0] * 255.f);
    color.g = static_cast<sf::Uint8>(col[1] * 255.f);
    color.b = static_cast<sf::Uint8>(col[2] * 255.f);
    input.camera_settings_changed = camera_changed;
  }
}

// Runs during the simulation, allows changes in Simulation variables
void create_settings_menu(Settings& settings, sf::RenderWindow& window,
                          sf::Vector2u interface_size, Simulation& sim,
                          InputState& input, CurrentWindow& currentwindow) {
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
    settings.sim.car_cap = std::max(0, settings.sim.car_cap);
    ImGui::Text("Car Count: %d", sim.cars.size());
    if (ImGui::Button("Clear Cars", ImVec2(120.f, 25.f))) {
      sim.clear_cars();
    }
    ImGui::SameLine();
    if (ImGui::Button("Clear Blockades", ImVec2(120.f, 25.f))) {
      sim.clear_blockades();
      input.camera_settings_changed = true;
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
    ColorEditor("Blocked Road Color", settings.visual.blocked_road_color,
                input);
    ColorEditor("Car Color", settings.visual.car_color, input, false);
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

  // SELECTION SETTINGS
  if (ImGui::CollapsingHeader("Selection Settings")) {
    ImGui::Checkbox("Selection Mode", &settings.selection.active);
    if (settings.selection.start_node) {
      ImGui::Text("Start Node %s:", settings.selection.start_node->id.c_str());
      ImGui::Text("  Pos: (%.2f, %.2f)", settings.selection.start_node->pos.x,
                  settings.selection.start_node->pos.y);
    }
    if (settings.selection.end_node) {
      ImGui::Text("End Node %s:", settings.selection.end_node->id.c_str());
      ImGui::Text("  Pos: (%.2f, %.2f)", settings.selection.end_node->pos.x,
                  settings.selection.end_node->pos.y);
    }

    if (settings.selection.selected_way) {
      bool clear_selection = false;

      ImGui::Text("Way %s:", settings.selection.selected_way->id.c_str());
      ImGui::Text("  Index in Osm Way: %d",
                  settings.selection.selected_way->index);
      ImGui::Text("  Speed Limit: %d", settings.selection.selected_way->speed);
      ImGui::Text("  Lane Count: %d", settings.selection.selected_way->lanes);
      ImGui::Text("  Oneway: %s",
                  settings.selection.selected_way->oneway ? "True" : "False");
      if (ImGui::Button("Deselect Way", ImVec2(120, 25))) {
        clear_selection = true;
      }
      ImGui::SameLine();
      std::string label;
      if (settings.selection.selected_way->blocked) {
        label = "Unblock Way";
      } else {
        label = "Block Way";
      }
      if (ImGui::Button(label.c_str(), ImVec2(120, 25))) {
        sim.block_way(settings.selection.selected_way);
        clear_selection = true;
        input.camera_settings_changed = true;
      }
      // clear afterwards to avoid nullptr referencing
      if (clear_selection) {
        settings.selection = SelectionSettings{};
        settings.selection.active = true;
      }
    }
  }

  // FILE STUFF
  if (ImGui::CollapsingHeader("Menu")) {
    if (ImGui::Button("Main Menu", ImVec2(120, 25))) {
      currentwindow = START;
    }
    ImGui::SameLine();
    if (ImGui::Button("Load New File", ImVec2(120, 25))) {
      currentwindow = NEW_FILE;
    }
    ImGui::SameLine();
    if (ImGui::Button("Quit", ImVec2(120, 25))) {
      window.close();
    }
  }
  ImGui::End();
}
