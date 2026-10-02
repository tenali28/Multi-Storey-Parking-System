from backend.cpp_engine import ParkingEngine


def test_car_fee_from_cpp_engine():
    engine = ParkingEngine()

    fee = engine.calculate_fee(
        "CAR",
        0.5
    )

    assert fee == 50.0


def test_ev_fee_from_cpp_engine():
    engine = ParkingEngine()

    fee = engine.calculate_fee(
        "EV",
        1.2
    )

    assert fee == 150.0


def test_car_two_hour_fee_from_cpp_engine():
    engine = ParkingEngine()

    fee = engine.calculate_fee(
        "CAR",
        2.0
    )

    assert fee == 100.0


def test_invalid_vehicle_type_is_rejected():
    engine = ParkingEngine()

    try:
        engine.calculate_fee(
            "BIKE",
            1.0
        )

        assert False, (
            "Invalid vehicle type should raise ValueError."
        )

    except ValueError as error:
        assert str(error) == (
            "Vehicle type must be CAR or EV."
        )