#include "../include/ParkingSystem.h"

#include <cmath>
#include <ctime>

ParkingSystem::ParkingSystem(
    int floorCount,
    int carSlotsPerFloor,
    int evSlotsPerFloor)
{
    for (int i = 1; i <= floorCount; ++i)
    {
        floors.emplace_back(
            i,
            carSlotsPerFloor,
            evSlotsPerFloor
        );
    }
}

ParkingAllocation ParkingSystem::parkVehicle(
    const std::string& licensePlate,
    VehicleType vehicleType)
{
    if (licensePlate.empty())
    {
        return {
            false,
            -1,
            -1,
            "License plate cannot be empty."
        };
    }

    if (activeVehicles.find(licensePlate) != activeVehicles.end())
    {
        return {
            false,
            -1,
            -1,
            "Vehicle is already parked."
        };
    }

    ParkingSlot* selectedSlot = nullptr;
    int selectedFloorId = -1;

    for (auto& floor : floors)
    {
        ParkingSlot* availableSlot =
            floor.findAvailableSlot(vehicleType);

        if (availableSlot != nullptr)
        {
            selectedSlot = availableSlot;
            selectedFloorId = floor.getFloorId();
            break;
        }
    }

    if (selectedSlot == nullptr)
    {
        return {
            false,
            -1,
            -1,
            "No compatible parking slot is available."
        };
    }

    std::unique_ptr<Vehicle> vehicle;

    if (vehicleType == VehicleType::CAR)
    {
        vehicle = std::make_unique<RegularCar>(licensePlate);
    }
    else
    {
        vehicle = std::make_unique<ElectricVehicle>(licensePlate);
    }

    Vehicle* vehiclePointer = vehicle.get();

    activeVehicles[licensePlate] = std::move(vehicle);

    selectedSlot->parkVehicle(vehiclePointer);

    return {
        true,
        selectedFloorId,
        selectedSlot->getSlotId(),
        "Vehicle parked successfully."
    };
}

ParkingReceipt ParkingSystem::checkoutVehicle(
    const std::string& licensePlate)
{
    auto vehicleIterator = activeVehicles.find(licensePlate);

    if (vehicleIterator == activeVehicles.end())
    {
        return {
            false,
            licensePlate,
            -1,
            -1,
            0.0,
            0.0,
            "Vehicle is not currently parked."
        };
    }

    Vehicle* vehicle = vehicleIterator->second.get();

    int parkedFloorId = -1;
    int parkedSlotId = -1;

    for (auto& floor : floors)
    {
        for (const auto& slot : floor.getSlots())
        {
            if (slot.getParkedVehicle() == vehicle)
            {
                parkedFloorId = floor.getFloorId();
                parkedSlotId = slot.getSlotId();
                break;
            }
        }

        if (parkedFloorId != -1)
        {
            break;
        }
    }

    if (parkedFloorId == -1)
    {
        return {
            false,
            licensePlate,
            -1,
            -1,
            0.0,
            0.0,
            "Parking record could not be found."
        };
    }

    std::time_t exitTime = std::time(nullptr);

    double durationSeconds =
        std::difftime(exitTime, vehicle->getEntryTime());

    double durationHours = durationSeconds / 3600.0;

    /*
        Minimum billable duration is 1 hour.
        Additional time is rounded up to the next hour.
    */
    double billableHours = std::ceil(durationHours);

    if (billableHours < 1.0)
    {
        billableHours = 1.0;
    }

    double amount =
        billableHours * vehicle->getHourlyRate();

    for (auto& floor : floors)
{
    if (floor.getFloorId() == parkedFloorId)
    {
        for (auto& slot : floor.getSlots())
        {
            if (slot.getSlotId() == parkedSlotId)
            {
                slot.removeVehicle();
                break;
            }
        }

        break;
    }
}

    activeVehicles.erase(vehicleIterator);

    return {
        true,
        licensePlate,
        parkedFloorId,
        parkedSlotId,
        durationHours,
        amount,
        "Vehicle checked out successfully."
    };
}

bool ParkingSystem::isVehicleParked(
    const std::string& licensePlate) const
{
    return activeVehicles.find(licensePlate)
        != activeVehicles.end();
}

int ParkingSystem::getTotalFloors() const
{
    return static_cast<int>(floors.size());
}

int ParkingSystem::getTotalAvailableCarSlots() const
{
    int total = 0;

    for (const auto& floor : floors)
    {
        total += floor.getAvailableCarSlots();
    }

    return total;
}

int ParkingSystem::getTotalAvailableEVSlots() const
{
    int total = 0;

    for (const auto& floor : floors)
    {
        total += floor.getAvailableEVSlots();
    }

    return total;
}