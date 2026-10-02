#ifndef PARKING_ENGINE_API_H
#define PARKING_ENGINE_API_H

#ifdef _WIN32
#define PARKING_API __declspec(dllexport)
#else
#define PARKING_API
#endif

extern "C"
{
    PARKING_API double calculateParkingFee(
        int vehicleType,
        double durationHours
    );
}

#endif