#include "../cpp-engine/include/ParkingEngineAPI.h"

#include <cassert>
#include <cmath>
#include <iostream>

int main()
{
    std::cout << "=====================================\n";
    std::cout << "      C++ ENGINE API TESTS\n";
    std::cout << "=====================================\n\n";

    double carFee = calculateParkingFee(0, 0.5);

    assert(carFee == 50.0);

    std::cout << "PASS: CAR fee for 0.5 hours = Rs. "
              << carFee
              << "\n";

    double carFeeTwoHours =
        calculateParkingFee(0, 2.0);

    assert(carFeeTwoHours == 100.0);

    std::cout << "PASS: CAR fee for 2 hours = Rs. "
              << carFeeTwoHours
              << "\n";

    double evFee =
        calculateParkingFee(1, 1.2);

    assert(evFee == 150.0);

    std::cout << "PASS: EV fee for 1.2 hours = Rs. "
              << evFee
              << "\n";

    double invalidType =
        calculateParkingFee(99, 1.0);

    assert(invalidType == -1.0);

    std::cout << "PASS: Invalid vehicle type rejected\n";

    std::cout << "\n=====================================\n";
    std::cout << "       ALL API TESTS PASSED\n";
    std::cout << "=====================================\n";

    return 0;
}