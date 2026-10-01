#ifndef VEHICLE_H
#define VEHICLE_H

#include <string>
#include <ctime>

enum class VehicleType
{
    CAR,
    EV
};

class Vehicle
{
private:
    std::string licensePlate;
    VehicleType type;
    std::time_t entryTime;

public:
    Vehicle(const std::string& licensePlate, VehicleType type);

    virtual ~Vehicle() = default;

    const std::string& getLicensePlate() const;
    VehicleType getType() const;
    std::time_t getEntryTime() const;

    virtual double getHourlyRate() const = 0;
};

class RegularCar : public Vehicle
{
public:
    explicit RegularCar(const std::string& licensePlate);

    double getHourlyRate() const override;
};

class ElectricVehicle : public Vehicle
{
public:
    explicit ElectricVehicle(const std::string& licensePlate);

    double getHourlyRate() const override;
};

#endif