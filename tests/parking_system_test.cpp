#include "../cpp-engine/include/ParkingSystem.h"

#include <cassert>
#include <iostream>

void testInitialAvailability()
{
    ParkingSystem parkingSystem(2, 3, 2);

    assert(parkingSystem.getTotalFloors() == 2);
    assert(parkingSystem.getTotalAvailableCarSlots() == 6);
    assert(parkingSystem.getTotalAvailableEVSlots() == 4);

    std::cout << "PASS: Initial availability\n";
}

void testCarAllocation()
{
    ParkingSystem parkingSystem(2, 3, 2);

    ParkingAllocation result =
        parkingSystem.parkVehicle(
            "TN01AB1234",
            VehicleType::CAR
        );

    assert(result.success);
    assert(result.floorId == 1);
    assert(result.slotId == 1);

    assert(parkingSystem.isVehicleParked("TN01AB1234"));

    std::cout << "PASS: Car allocation\n";
}

void testEVAllocation()
{
    ParkingSystem parkingSystem(2, 3, 2);

    ParkingAllocation result =
        parkingSystem.parkVehicle(
            "TN01EV5678",
            VehicleType::EV
        );

    assert(result.success);
    assert(result.floorId == 1);
    assert(result.slotId == 4);

    assert(parkingSystem.isVehicleParked("TN01EV5678"));

    std::cout << "PASS: EV allocation\n";
}

void testDuplicateVehicle()
{
    ParkingSystem parkingSystem(2, 3, 2);

    parkingSystem.parkVehicle(
        "TN01AB1234",
        VehicleType::CAR
    );

    ParkingAllocation secondAttempt =
        parkingSystem.parkVehicle(
            "TN01AB1234",
            VehicleType::CAR
        );

    assert(!secondAttempt.success);

    std::cout << "PASS: Duplicate vehicle rejection\n";
}

void testCheckout()
{
    ParkingSystem parkingSystem(2, 3, 2);

    parkingSystem.parkVehicle(
        "TN01AB1234",
        VehicleType::CAR
    );

    ParkingReceipt receipt =
        parkingSystem.checkoutVehicle("TN01AB1234");

    assert(receipt.success);
    assert(receipt.licensePlate == "TN01AB1234");
    assert(receipt.floorId == 1);
    assert(receipt.slotId == 1);
    assert(receipt.amount == 50.0);

    assert(!parkingSystem.isVehicleParked("TN01AB1234"));

    std::cout << "PASS: Vehicle checkout\n";
}

void testCheckoutUnknownVehicle()
{
    ParkingSystem parkingSystem(2, 3, 2);

    ParkingReceipt receipt =
        parkingSystem.checkoutVehicle("TN99XX9999");

    assert(!receipt.success);

    std::cout << "PASS: Unknown vehicle checkout rejection\n";
}

void testCarCapacity()
{
    ParkingSystem parkingSystem(1, 2, 1);

    ParkingAllocation first =
        parkingSystem.parkVehicle(
            "TN01AA1111",
            VehicleType::CAR
        );

    ParkingAllocation second =
        parkingSystem.parkVehicle(
            "TN01AA2222",
            VehicleType::CAR
        );

    ParkingAllocation third =
        parkingSystem.parkVehicle(
            "TN01AA3333",
            VehicleType::CAR
        );

    assert(first.success);
    assert(second.success);
    assert(!third.success);

    assert(
        parkingSystem.getTotalAvailableCarSlots() == 0
    );

    std::cout << "PASS: Car capacity limit\n";
}

void testEVCannotUseCarSlot()
{
    ParkingSystem parkingSystem(1, 1, 0);

    ParkingAllocation result =
        parkingSystem.parkVehicle(
            "TN01EV9999",
            VehicleType::EV
        );

    assert(!result.success);

    std::cout << "PASS: EV cannot use car slot\n";
}

int main()
{
    std::cout << "=====================================\n";
    std::cout << "     SMART PARKING SYSTEM TESTS\n";
    std::cout << "=====================================\n\n";

    testInitialAvailability();
    testCarAllocation();
    testEVAllocation();
    testDuplicateVehicle();
    testCheckout();
    testCheckoutUnknownVehicle();
    testCarCapacity();
    testEVCannotUseCarSlot();

    std::cout << "\n=====================================\n";
    std::cout << "       ALL TESTS PASSED\n";
    std::cout << "=====================================\n";

    return 0;
}