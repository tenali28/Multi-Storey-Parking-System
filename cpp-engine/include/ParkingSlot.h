#ifndef PARKING_SLOT_H
#define PARKING_SLOT_H

#include "Vehicle.h"

class ParkingSlot
{
private:
    int slotId;
    VehicleType compatibleType;
    Vehicle* parkedVehicle;

public:
    ParkingSlot();

    ParkingSlot(int slotId, VehicleType compatibleType);

    bool isAvailable() const;
    bool canAccept(VehicleType vehicleType) const;

    void parkVehicle(Vehicle* vehicle);
    Vehicle* removeVehicle();

    int getSlotId() const;
    VehicleType getCompatibleType() const;
    Vehicle* getParkedVehicle() const;
};

#endif