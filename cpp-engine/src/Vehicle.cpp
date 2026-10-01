#include "../include/Vehicle.h"

Vehicle::Vehicle(const std::string& licensePlate, VehicleType type)
    : licensePlate(licensePlate),
      type(type),
      entryTime(std::time(nullptr))
{
}

const std::string& Vehicle::getLicensePlate() const
{
    return licensePlate;
}

VehicleType Vehicle::getType() const
{
    return type;
}

std::time_t Vehicle::getEntryTime() const
{
    return entryTime;
}

RegularCar::RegularCar(const std::string& licensePlate)
    : Vehicle(licensePlate, VehicleType::CAR)
{
}

double RegularCar::getHourlyRate() const
{
    return 50.0;
}

ElectricVehicle::ElectricVehicle(const std::string& licensePlate)
    : Vehicle(licensePlate, VehicleType::EV)
{
}

double ElectricVehicle::getHourlyRate() const
{
    return 75.0;
}