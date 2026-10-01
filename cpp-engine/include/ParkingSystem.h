#ifndef PARKING_SYSTEM_H
#define PARKING_SYSTEM_H

#include "ParkingFloor.h"
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

struct ParkingAllocation
{
    bool success;
    int floorId;
    int slotId;
    std::string message;
};

struct ParkingReceipt
{
    bool success;
    std::string licensePlate;
    int floorId;
    int slotId;
    double durationHours;
    double amount;
    std::string message;
};

class ParkingSystem
{
private:
    std::vector<ParkingFloor> floors;

    std::unordered_map<std::string, std::unique_ptr<Vehicle>> activeVehicles;

public:
    ParkingSystem(int floorCount, int carSlotsPerFloor, int evSlotsPerFloor);

    ParkingAllocation parkVehicle(
        const std::string& licensePlate,
        VehicleType vehicleType
    );

    ParkingReceipt checkoutVehicle(
        const std::string& licensePlate
    );

    bool isVehicleParked(const std::string& licensePlate) const;

    int getTotalFloors() const;

    int getTotalAvailableCarSlots() const;

    int getTotalAvailableEVSlots() const;
};

#endif