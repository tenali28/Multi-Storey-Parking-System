#include "../include/ParkingEngineAPI.h"

#include <algorithm>
#include <cmath>

extern "C"
double calculateParkingFee(
    int vehicleType,
    double durationHours)
{
    double hourlyRate;

    if (vehicleType == 0)
    {
        hourlyRate = 50.0;
    }
    else if (vehicleType == 1)
    {
        hourlyRate = 75.0;
    }
    else
    {
        return -1.0;
    }

    double billableHours =
        std::max(1.0, std::ceil(durationHours));

    return billableHours * hourlyRate;
}