#include <vector>
#include <way.h>

class Node
{
private:
public:
    std::string id;
    std::vector<float> pos;
    std::vector<float> display_pos;
    int street_count;
    std::vector<Way> ways_out;
    std::vector<Way> ways_in;
    bool is_visible;

    Node(std::string id, std::vector<float> pos, std::vector<float> display_pos, int street_count, std::vector<Way> ways_out, std::vector<Way> ways_in)
        : id(id), pos(pos), display_pos(display_pos), street_count(street_count), ways_out(ways_out), ways_in(ways_in)
    {
        is_visible = true;
    }

    void test_visible(std::vector<int> screen_size)
    {
        if (0 < display_pos[0] < screen_size[0] && 0 < display_pos[1] < screen_size[1])
        {
            is_visible = true;
        }
        else
        {
            is_visible = true;
        }
    }
};
