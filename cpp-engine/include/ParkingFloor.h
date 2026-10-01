#ifndef PARKING_FLOOR_H
#define PARKING_FLOOR_H

#include "ParkingSlot.h"
#include <vector>

class ParkingFloor
{
private:
    int floorId;
    std::vector<ParkingSlot> slots;

public:
    ParkingFloor(int floorId, int carSlotCount, int evSlotCount);

    ParkingSlot* findAvailableSlot(VehicleType vehicleType);

    int getFloorId() const;
std::vector<ParkingSlot>& getSlots();
const std::vector<ParkingSlot>& getSlots() const;
    int getAvailableCarSlots() const;
    int getAvailableEVSlots() const;
};

#endif