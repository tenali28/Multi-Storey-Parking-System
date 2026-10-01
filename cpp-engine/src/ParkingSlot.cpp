#include "../include/ParkingSlot.h"

ParkingSlot::ParkingSlot()
    : slotId(0),
      compatibleType(VehicleType::CAR),
      parkedVehicle(nullptr)
{
}

ParkingSlot::ParkingSlot(int slotId, VehicleType compatibleType)
    : slotId(slotId),
      compatibleType(compatibleType),
      parkedVehicle(nullptr)
{
}

bool ParkingSlot::isAvailable() const
{
    return parkedVehicle == nullptr;
}

bool ParkingSlot::canAccept(VehicleType vehicleType) const
{
    return isAvailable() && compatibleType == vehicleType;
}

void ParkingSlot::parkVehicle(Vehicle* vehicle)
{
    parkedVehicle = vehicle;
}

Vehicle* ParkingSlot::removeVehicle()
{
    Vehicle* vehicle = parkedVehicle;
    parkedVehicle = nullptr;

    return vehicle;
}

int ParkingSlot::getSlotId() const
{
    return slotId;
}

VehicleType ParkingSlot::getCompatibleType() const
{
    return compatibleType;
}

Vehicle* ParkingSlot::getParkedVehicle() const
{
    return parkedVehicle;
}