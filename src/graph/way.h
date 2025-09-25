#include <iostream>
#include <vector>
#include <node.h>
#include <../traffic/car.h>

class Way
{
private:
public:
    std::string id;
    int index; /*new*/
    bool oneway;
    int lanes;
    std::vector<std::string> turns;
    int speed;
    std::vector<Node>;
    float length;
    std::vector<Car> cars; 
    bool is_visible;

    Way(std::string id, int index /*new*/, bool oneway, int lanes, std::vector<std::string> turns, int speed, std::vector<Node>, float length)
        : id(id), index(index), oneway(oneway), lanes(lanes), turns(turns), speed(speed), nodes(nodes), length(length) 
    {
        is_visible = true;
    }

    void test_visible(std::vector<int> screen_size)
    {
        for (auto node: nodes)
        {
            if (node.is_visible)
            {
                is_visible = true;
                return;
            }
        }
        is_visible = false;
    }
};
