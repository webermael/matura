#include <vector>
#include <bits/stdc++.h>
#include <cmath>

class Plot
{
public:
    std::vector<int> screen_size;
    std::vector<float> screen_center;
    std::unordered_map<std::string, float> bounds;

    std::vector<float> translation;
    std::vector<float> graph_size;
    float scale;

    void reset_values()
    {
        translation = {bounds["west"], bounds["south"]};
        graph_size = {bounds["east"] - bounds["west"], bounds["north"] - bounds["south"]};
        scale = std::min(screen_size[0] / graph_size[0], screen_size[1] / graph_size[1]);
    }

    Plot(std::vector<int> screen_size, std::vector<float> screen_center, std::unordered_map<std::string, float> bounds)
        : screen_size(screen_size), screen_center(screen_center), bounds(bounds)
    {
        reset_values();
    }

    std::vector<float> to_screen_space(std::vector<float> position)
    {
        return {
            (position[0] - translation[0] - graph_size[0] / 2) * scale + screen_center[0],
            (position[1] - translation[1] - graph_size[1] / 2) * -scale + screen_center[1]};
    }

    std::vector<float> from_screen_space(std::vector<float> position)
    {
        return {
            (position[0] - screen_center[0]) / scale + translation[0] + graph_size[0] / 2,
            (position[1] - screen_center[1]) / -scale + translation[1] + graph_size[1] / 2};
    }

    void set_values(float top, float left, float bottom, float right)
    {
        std::vector<float> temp_translation;
        std::vector<float> temp_corner;
        if (std::abs(bottom - top) > 0 && std::abs(right - left) > 0)
        {
            temp_translation = from_screen_space({left, bottom});
            temp_corner = from_screen_space({right, top});
            translation = temp_translation;
            graph_size = {temp_corner[0] - temp_translation[0], temp_corner[1] - temp_translation[1]};
            scale = std::min(screen_size[0] / graph_size[0], screen_size[1] / graph_size[1]);
        }
    }
};
