import uuid

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import (
    DATABASE_DIR,
    DATABASE_PATH,
    get_connection,
    initialize_database,
    seed_admin_user,
    seed_parking_data
)


TEST_DATABASE_PATH = (
    DATABASE_DIR / "test_parking.db"
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():

    import backend.database as database

    original_database_path = database.DATABASE_PATH

    database.DATABASE_PATH = TEST_DATABASE_PATH

    if TEST_DATABASE_PATH.exists():
        TEST_DATABASE_PATH.unlink()

    initialize_database()
    seed_parking_data()
    seed_admin_user()

    yield

    if TEST_DATABASE_PATH.exists():
        TEST_DATABASE_PATH.unlink()

    database.DATABASE_PATH = original_database_path


@pytest.fixture
def client():

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_token(client):

    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):

    return {
        "Authorization": f"Bearer {auth_token}"
    }


def generate_license_plate():

    unique_id = uuid.uuid4().hex[:6].upper()

    return f"TEST{unique_id}"


def test_health_endpoint(client):

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy"
    }


def test_successful_login(client):

    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Login successful."

    assert data["token_type"] == "bearer"

    assert "access_token" in data

    assert data["user"]["username"] == "admin"

    assert data["user"]["role"] == "ADMIN"


def test_invalid_login(client):

    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "wrong-password"
        }
    )

    assert response.status_code == 401

    assert (
        response.json()["detail"]
        == "Invalid username or password."
    )


def test_protected_endpoint_requires_authentication(
    client
):

    response = client.get(
        "/parking-slots"
    )

    assert response.status_code == 401


def test_authenticated_user_profile(
    client,
    auth_headers
):

    response = client.get(
        "/auth/me",
        headers=auth_headers
    )

    assert response.status_code == 200

    user = response.json()["user"]

    assert user["username"] == "admin"

    assert user["role"] == "ADMIN"


def test_parking_slots_endpoint(
    client,
    auth_headers
):

    response = client.get(
        "/parking-slots",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_slots"] == 15

    assert len(data["slots"]) == 15


def test_vehicle_registration(
    client,
    auth_headers
):

    license_plate = generate_license_plate()

    response = client.post(
        "/vehicles",
        headers=auth_headers,
        json={
            "license_plate": license_plate,
            "vehicle_type": "CAR"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["message"]
        == "Vehicle registered successfully."
    )

    vehicle = data["vehicle"]

    assert vehicle["license_plate"] == license_plate

    assert vehicle["vehicle_type"] == "CAR"


def test_complete_parking_flow(
    client,
    auth_headers
):

    license_plate = generate_license_plate()

    register_response = client.post(
        "/vehicles",
        headers=auth_headers,
        json={
            "license_plate": license_plate,
            "vehicle_type": "CAR"
        }
    )

    assert register_response.status_code == 200

    parking_response = client.post(
        "/parking",
        headers=auth_headers,
        json={
            "license_plate": license_plate
        }
    )

    assert parking_response.status_code == 200

    parking_data = parking_response.json()

    assert (
        parking_data["message"]
        == "Vehicle parked successfully."
    )

    parking_session = (
        parking_data["parking_session"]
    )

    assert (
        parking_session["license_plate"]
        == license_plate
    )

    assert parking_session["vehicle_type"] == "CAR"

    assert parking_session["status"] == "ACTIVE"

    active_response = client.get(
        "/active-parking",
        headers=auth_headers
    )

    assert active_response.status_code == 200

    active_vehicles = (
        active_response.json()["vehicles"]
    )

    matching_vehicle = [
        vehicle
        for vehicle in active_vehicles
        if vehicle["license_plate"] == license_plate
    ]

    assert len(matching_vehicle) == 1

    checkout_response = client.post(
        "/checkout",
        headers=auth_headers,
        json={
            "license_plate": license_plate
        }
    )

    assert checkout_response.status_code == 200

    receipt = checkout_response.json()["receipt"]

    assert receipt["license_plate"] == license_plate

    assert receipt["vehicle_type"] == "CAR"

    assert receipt["payment_status"] == "PAID"

    assert receipt["amount"] >= 50.0

    history_response = client.get(
        "/parking-history",
        headers=auth_headers
    )

    assert history_response.status_code == 200

    history = history_response.json()["history"]

    matching_history = [
        record
        for record in history
        if record["license_plate"] == license_plate
    ]

    assert len(matching_history) == 1

    assert (
        matching_history[0]["payment_status"]
        == "PAID"
    )


def test_duplicate_vehicle_registration(
    client,
    auth_headers
):

    license_plate = generate_license_plate()

    first_response = client.post(
        "/vehicles",
        headers=auth_headers,
        json={
            "license_plate": license_plate,
            "vehicle_type": "EV"
        }
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/vehicles",
        headers=auth_headers,
        json={
            "license_plate": license_plate,
            "vehicle_type": "EV"
        }
    )

    assert second_response.status_code == 409


def test_invalid_vehicle_type(
    client,
    auth_headers
):

    license_plate = generate_license_plate()

    response = client.post(
        "/vehicles",
        headers=auth_headers,
        json={
            "license_plate": license_plate,
            "vehicle_type": "BIKE"
        }
    )

    assert response.status_code == 422


def test_checkout_nonexistent_vehicle(
    client,
    auth_headers
):

    response = client.post(
        "/checkout",
        headers=auth_headers,
        json={
            "license_plate": "DOESNOTEXIST"
        }
    )

    assert response.status_code == 404