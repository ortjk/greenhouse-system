#include "math.h"

struct Setpoints
{
    bool manualEnable = false;
    bool manualOpen = false;
    float minTemperature = 20;
    float maxTemperature = 30;
};

unsigned short roundWithHalf(float* num)
{
    unsigned short x = 0;
    float half = fmod(*num, 0.5f);
    if (*num - floor(*num) >= 0.5f)
    {
        if (half >= 0.25f)
        {
            x = static_cast<int>(ceil(*num)) << 1;
        }
        else
        {
            x = 1;
            x = x | (static_cast<int>(floor(*num))) << 1;
        }
    }
    else
    {
        if (half >= 0.25f)
        {
            x = 1;
            x = x | (static_cast<int>(floor(*num))) << 1;
        }
        else
        {
            x = static_cast<int>(floor(*num)) << 1;
        }
    }

    return x;
}

unsigned short encodeOutput(bool* status, float* temperature, float* humidity)
{
    unsigned short x = 0;
    x = x | (static_cast<int>(*status) << 15); // set MSB
    x = x | ((roundWithHalf(temperature) << 8) & 0x7F00); // set next 7 MSBs
    x = x | roundWithHalf(humidity); // set remaining 8 bits
    return x;
}

void decodeInput(Setpoints* setpoints)
{
    
}
