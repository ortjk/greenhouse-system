#include "math.h"

// data structure for window configuration
struct Setpoints
{
    bool manualEnable = false;
    bool manualOpen = false;
    float minTemperature = 20;
    float maxTemperature = 30;
};

// round a float to a binary representation of the form 0b...XXXXXXY, where:
// X is the n-bit binary whole number portion
// Y is a bit that adds one half
// e.g. 28.67 -> 111001 -> 28 + 0.5 -> 28.5
unsigned short roundWithHalf(float* num)
{
    unsigned short x = 0;
    float half = fmod(*num, 0.5f); // get the remainder of division by 0.5
    if (*num - floor(*num) >= 0.5f) // if the passed number is closer to its ceil than floor
    {
        if (half >= 0.25f) // if the remainder of division by 0.5 was greater than 0.25
        {
            // round up the number to int with no added half
            x = static_cast<int>(ceil(*num)) << 1;
        }
        else
        {
            // round down the number to int with an added half
            x = 1;
            x = x | (static_cast<int>(floor(*num))) << 1;
        }
    }
    else // else the passed number is closer to its floor than ceil
    {
        if (half >= 0.25f)
        {
            // round down the number with an added half
            x = 1;
            x = x | (static_cast<int>(floor(*num))) << 1;
        }
        else
        {
            // round down the number with no added half
            x = static_cast<int>(floor(*num)) << 1;
        }
    }

    return x;
}

// encode temperature, humidity, and status to a binary representation of the form 0bXYYY_YYYY_ZZZZ_ZZZZ, where:
// X is the error status
// Y is the binary representation of temperature (max 63.5)
// Z is the binary representation of humidity (max 127.5)
unsigned short encodeOutput(bool* status, float* temperature, float* humidity)
{
    unsigned short x = 0;
    x = x | (static_cast<int>(*status) << 15); // set MSB
    x = x | ((roundWithHalf(temperature) << 8) & 0x7F00); // set next 7 MSBs
    x = x | roundWithHalf(humidity); // set remaining 8 bits
    return x;
}

// decode setpoints from a binary representation of the form 0bXXYY_YYYY_YZZZ_ZZZZ, where:
// X is the manual control override (enable and open)
// Y is the maximum temperature setpoint (max 63.5)
// Z is the minimum temperature setpoint (max 63.5)
void decodeInput(byte* lower, byte* upper, Setpoints* setpoints)
{
    
    setpoints->manualEnable = *upper >> 7; // get MSB
    setpoints->manualOpen = (*upper >> 6) & 1;  // get second MSB

    setpoints->maxTemperature = *upper & ((1 << 6) - 1); // isolate next 6 MSB
    if (*lower >> 7) // check for half bit
    {
        setpoints->maxTemperature += 0.5f;
    }

    setpoints->minTemperature = (*lower >> 1) & ((1 << 6) - 1); // isolate next 6 MSB
    if (*lower & 1) // check for half bit
    {
        setpoints->minTemperature += 0.5f;
    }
}
