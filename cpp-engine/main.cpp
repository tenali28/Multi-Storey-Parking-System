#include "include/ParkingSystem.h"

#include <iostream>
#include <string>

int main()
{
    ParkingSystem parkingSystem(3, 3, 2);

    std::cout << "=====================================\n";
    std::cout << "   SMART PARKING SYSTEM - C++ ENGINE\n";
    std::cout << "=====================================\n\n";

    std::cout << "Parking floors: "
              << parkingSystem.getTotalFloors()
              << "\n";

    std::cout << "Available car slots: "
              << parkingSystem.getTotalAvailableCarSlots()
              << "\n";

    std::cout << "Available EV slots: "
              << parkingSystem.getTotalAvailableEVSlots()
              << "\n\n";

    std::cout << "Parking a regular car...\n";

    ParkingAllocation carResult =
        parkingSystem.parkVehicle(
            "TN01AB1234",
            VehicleType::CAR
        );

    std::cout << "Result: "
              << carResult.message
              << "\n";

    if (carResult.success)
    {
        std::cout << "Floor: "
                  << carResult.floorId
                  << "\n";

        std::cout << "Slot: "
                  << carResult.slotId
                  << "\n";
    }

    std::cout << "\n";

    std::cout << "Parking an electric vehicle...\n";

    ParkingAllocation evResult =
        parkingSystem.parkVehicle(
            "TN01EV5678",
            VehicleType::EV
        );

    std::cout << "Result: "
              << evResult.message
              << "\n";

    if (evResult.success)
    {
        std::cout << "Floor: "
                  << evResult.floorId
                  << "\n";

        std::cout << "Slot: "
                  << evResult.slotId
                  << "\n";
    }

    std::cout << "\n";

    std::cout << "Available car slots after parking: "
              << parkingSystem.getTotalAvailableCarSlots()
              << "\n";

    std::cout << "Available EV slots after parking: "
              << parkingSystem.getTotalAvailableEVSlots()
              << "\n\n";

    std::cout << "Checking out TN01AB1234...\n";

    ParkingReceipt receipt =
        parkingSystem.checkoutVehicle("TN01AB1234");

    std::cout << "Result: "
              << receipt.message
              << "\n";

    if (receipt.success)
    {
        std::cout << "License plate: "
                  << receipt.licensePlate
                  << "\n";

        std::cout << "Floor: "
                  << receipt.floorId
                  << "\n";

        std::cout << "Slot: "
                  << receipt.slotId
                  << "\n";

        std::cout << "Parking duration: "
                  << receipt.durationHours
                  << " hours\n";

        std::cout << "Amount: Rs. "
                  << receipt.amount
                  << "\n";
    }

    std::cout << "\n=====================================\n";
    std::cout << "          TEST COMPLETED\n";
    std::cout << "=====================================\n";

    return 0;
}