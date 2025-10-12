#pragma once
#include <imgui-SFML.h>
#include <imgui.h>

#include <SFML/Graphics.hpp>

struct InputState {
  bool left_mouse_pressed = false;
  bool left_mouse_just_pressed = false;
  bool left_mouse_just_released = false;
  bool right_mouse_just_pressed = false;
  bool escape_pressed = false;
  // on any zoom/visual change to the roads
  bool camera_settings_changed = false;
  sf::Vector2i mouse_pos;
  float dt = 0.f;
};

void handle_events(sf::RenderWindow& window, InputState& input) {
  input.left_mouse_just_pressed = false;  // reset each frame
  input.left_mouse_just_released = false;
  input.right_mouse_just_pressed = false;
  input.escape_pressed = false;

  sf::Event event;
  while (window.pollEvent(event)) {
    ImGui::SFML::ProcessEvent(window, event);
    switch (event.type) {
      case sf::Event::Closed:
        window.close();
        break;
      case sf::Event::MouseMoved:
        input.mouse_pos = {event.mouseMove.x, event.mouseMove.y};
        break;
      case sf::Event::MouseButtonPressed:
        if (event.mouseButton.button == sf::Mouse::Left) {
          input.left_mouse_pressed = true;
          input.left_mouse_just_pressed = true;  // only true for this frame
        }
        if (event.mouseButton.button == sf::Mouse::Right) {
          input.right_mouse_just_pressed = true;  // only true for this frame
        }
        break;
      case sf::Event::MouseButtonReleased:
        if (event.mouseButton.button == sf::Mouse::Left) {
          input.left_mouse_pressed = false;
          input.left_mouse_just_released = true;
        }
        break;
      case sf::Event::KeyPressed:
        if (event.key.code == sf::Keyboard::Escape) {
          input.escape_pressed = true;
        }
        break;
    }
  }
}