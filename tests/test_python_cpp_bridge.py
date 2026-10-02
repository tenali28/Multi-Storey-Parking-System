from backend.cpp_engine import parking_engine


def main():
    print("=====================================")
    print("     PYTHON-C++ BRIDGE TESTS")
    print("=====================================\n")

    car_fee = parking_engine.calculate_fee(
        "CAR",
        0.5
    )

    assert car_fee == 50.0

    print(
        "PASS: Python -> C++ CAR fee = Rs.",
        car_fee
    )

    car_fee_two_hours = parking_engine.calculate_fee(
        "CAR",
        2.0
    )

    assert car_fee_two_hours == 100.0

    print(
        "PASS: Python -> C++ CAR 2-hour fee = Rs.",
        car_fee_two_hours
    )

    ev_fee = parking_engine.calculate_fee(
        "EV",
        1.2
    )

    assert ev_fee == 150.0

    print(
        "PASS: Python -> C++ EV fee = Rs.",
        ev_fee
    )

    print("\n=====================================")
    print("     PYTHON-C++ BRIDGE WORKING")
    print("=====================================")


if __name__ == "__main__":
    main()