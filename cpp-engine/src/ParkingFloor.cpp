#include "../include/ParkingFloor.h"

ParkingFloor::ParkingFloor(int floorId, int carSlotCount, int evSlotCount)
    : floorId(floorId)
{
    int slotId = 1;

    for (int i = 0; i < carSlotCount; ++i)
    {
        slots.emplace_back(slotId++, VehicleType::CAR);
    }

    for (int i = 0; i < evSlotCount; ++i)
    {
        slots.emplace_back(slotId++, VehicleType::EV);
    }
}

ParkingSlot* ParkingFloor::findAvailableSlot(VehicleType vehicleType)
{
    for (auto& slot : slots)
    {
        if (slot.canAccept(vehicleType))
        {
            return &slot;
        }
    }

    return nullptr;
}

int ParkingFloor::getFloorId() const
{
    return floorId;
}

std::vector<ParkingSlot>& ParkingFloor::getSlots()
{
    return slots;
}

const std::vector<ParkingSlot>& ParkingFloor::getSlots() const
{
    return slots;
}

int ParkingFloor::getAvailableCarSlots() const
{
    int count = 0;

    for (const auto& slot : slots)
    {
        if (slot.getCompatibleType() == VehicleType::CAR &&
            slot.isAvailable())
        {
            ++count;
        }
    }

    return count;
}

int ParkingFloor::getAvailableEVSlots() const
{
    int count = 0;

    for (const auto& slot : slots)
    {
        if (slot.getCompatibleType() == VehicleType::EV &&
            slot.isAvailable())
        {
            ++count;
        }
    }

    return count;
}