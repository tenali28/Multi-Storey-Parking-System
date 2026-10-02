import os

from contextlib import asynccontextmanager
from math import ceil

from dotenv import load_dotenv

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    status
)

from fastapi.middleware.cors import CORSMiddleware

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from backend.auth import (
    create_access_token,
    decode_access_token,
    verify_password
)

from backend.database import (
    get_connection,
    initialize_database,
    seed_admin_user,
    seed_parking_data
)

from backend.models import (
    CheckoutRequest,
    LoginRequest,
    ParkingRequest,
    VehicleCreate
)

from backend.cpp_engine import parking_engine


load_dotenv()


security = HTTPBearer()


FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    initialize_database()

    seed_parking_data()

    seed_admin_user()

    yield


app = FastAPI(
    title="Smart Parking System API",
    description="Backend API for the Smart Parking System",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )
):

    username = decode_access_token(
        credentials.credentials
    )

    if username is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    connection = get_connection()

    user = connection.execute(
        """
        SELECT
            user_id,
            username,
            role
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    connection.close()

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    return dict(user)


@app.get("/")
def root():

    return {
        "message": "Smart Parking System API is running",
        "status": "success"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


@app.post("/auth/login")
def login(request: LoginRequest):

    connection = get_connection()

    user = connection.execute(
        """
        SELECT
            user_id,
            username,
            password_hash,
            password_salt,
            role
        FROM users
        WHERE username = ?
        """,
        (request.username,)
    ).fetchone()

    connection.close()

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )

    password_valid = verify_password(
        request.password,
        user["password_salt"],
        user["password_hash"]
    )

    if not password_valid:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )

    access_token = create_access_token(
        user["username"]
    )

    return {
        "message": "Login successful.",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["role"]
        }
    }


@app.get("/auth/me")
def get_current_user_info(
    current_user: dict = Depends(
        get_current_user
    )
):

    return {
        "user": current_user
    }


@app.get("/database-status")
def database_status(
    current_user: dict = Depends(
        get_current_user
    )
):

    return {
        "database": "SQLite",
        "status": "connected"
    }


@app.get("/parking-slots")
def get_parking_slots(
    current_user: dict = Depends(
        get_current_user
    )
):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            slot_id,
            floor_id,
            slot_number,
            slot_type,
            status
        FROM slots
        ORDER BY floor_id, slot_id
        """
    ).fetchall()

    connection.close()

    return {
        "total_slots": len(rows),
        "slots": [dict(row) for row in rows]
    }


@app.post("/vehicles")
def create_vehicle(
    vehicle: VehicleCreate,
    current_user: dict = Depends(
        get_current_user
    )
):

    connection = get_connection()

    existing_vehicle = connection.execute(
        """
        SELECT
            vehicle_id,
            license_plate,
            vehicle_type
        FROM vehicles
        WHERE license_plate = ?
        """,
        (vehicle.license_plate,)
    ).fetchone()

    if existing_vehicle:

        connection.close()

        raise HTTPException(
            status_code=409,
            detail="Vehicle with this license plate already exists."
        )

    cursor = connection.execute(
        """
        INSERT INTO vehicles (
            license_plate,
            vehicle_type
        )
        VALUES (?, ?)
        """,
        (
            vehicle.license_plate,
            vehicle.vehicle_type
        )
    )

    connection.commit()

    vehicle_id = cursor.lastrowid

    created_vehicle = connection.execute(
        """
        SELECT
            vehicle_id,
            license_plate,
            vehicle_type,
            created_at
        FROM vehicles
        WHERE vehicle_id = ?
        """,
        (vehicle_id,)
    ).fetchone()

    connection.close()

    return {
        "message": "Vehicle registered successfully.",
        "vehicle": dict(created_vehicle)
    }


@app.get("/vehicles")
def get_vehicles(
    current_user: dict = Depends(
        get_current_user
    )
):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            vehicle_id,
            license_plate,
            vehicle_type,
            created_at
        FROM vehicles
        ORDER BY vehicle_id
        """
    ).fetchall()

    connection.close()

    return {
        "total_vehicles": len(rows),
        "vehicles": [dict(row) for row in rows]
    }


@app.post("/parking")
def park_vehicle(
    request: ParkingRequest,
    current_user: dict = Depends(
        get_current_user
    )
):

    connection = get_connection()

    try:

        vehicle = connection.execute(
            """
            SELECT
                vehicle_id,
                license_plate,
                vehicle_type
            FROM vehicles
            WHERE license_plate = ?
            """,
            (request.license_plate,)
        ).fetchone()

        if vehicle is None:

            raise HTTPException(
                status_code=404,
                detail="Vehicle is not registered."
            )

        active_session = connection.execute(
            """
            SELECT session_id
            FROM parking_sessions
            WHERE vehicle_id = ?
              AND status = 'ACTIVE'
            """,
            (vehicle["vehicle_id"],)
        ).fetchone()

        if active_session:

            raise HTTPException(
                status_code=409,
                detail="Vehicle is already parked."
            )

        available_slot = connection.execute(
            """
            SELECT
                slot_id,
                floor_id,
                slot_number,
                slot_type
            FROM slots
            WHERE slot_type = ?
              AND status = 'AVAILABLE'
            ORDER BY floor_id, slot_id
            LIMIT 1
            """,
            (vehicle["vehicle_type"],)
        ).fetchone()

        if available_slot is None:

            raise HTTPException(
                status_code=409,
                detail="No compatible parking slot is available."
            )

        connection.execute(
            """
            UPDATE slots
            SET status = 'OCCUPIED'
            WHERE slot_id = ?
            """,
            (available_slot["slot_id"],)
        )

        cursor = connection.execute(
            """
            INSERT INTO parking_sessions (
                vehicle_id,
                slot_id,
                status
            )
            VALUES (?, ?, 'ACTIVE')
            """,
            (
                vehicle["vehicle_id"],
                available_slot["slot_id"]
            )
        )

        connection.commit()

        session_id = cursor.lastrowid

        return {
            "message": "Vehicle parked successfully.",
            "parking_session": {
                "session_id": session_id,
                "license_plate": vehicle["license_plate"],
                "vehicle_type": vehicle["vehicle_type"],
                "floor_id": available_slot["floor_id"],
                "slot_id": available_slot["slot_id"],
                "slot_number": available_slot["slot_number"],
                "status": "ACTIVE"
            }
        }

    except HTTPException:

        connection.rollback()

        raise

    except Exception:

        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail="An error occurred while parking the vehicle."
        )

    finally:

        connection.close()


@app.post("/checkout")
def checkout_vehicle(
    request: CheckoutRequest,
    current_user: dict = Depends(
        get_current_user
    )
):

    connection = get_connection()

    try:

        parking_record = connection.execute(
            """
            SELECT
                ps.session_id,
                ps.vehicle_id,
                ps.slot_id,
                ps.entry_time,
                v.license_plate,
                v.vehicle_type,
                s.floor_id,
                s.slot_number
            FROM parking_sessions ps
            JOIN vehicles v
                ON ps.vehicle_id = v.vehicle_id
            JOIN slots s
                ON ps.slot_id = s.slot_id
            WHERE v.license_plate = ?
              AND ps.status = 'ACTIVE'
            """,
            (request.license_plate,)
        ).fetchone()

        if parking_record is None:

            raise HTTPException(
                status_code=404,
                detail="Vehicle is not currently parked."
            )

        duration_result = connection.execute(
            """
            SELECT
                (
                    julianday('now') -
                    julianday(?)
                ) * 24.0 AS duration_hours
            """,
            (parking_record["entry_time"],)
        ).fetchone()

        actual_duration_hours = max(
            0.0,
            duration_result["duration_hours"]
        )

        amount = parking_engine.calculate_fee(
            parking_record["vehicle_type"],
            actual_duration_hours
        )

        billable_hours = max(
            1,
            ceil(actual_duration_hours)
        )

        hourly_rate = amount / billable_hours

        connection.execute(
            """
            UPDATE parking_sessions
            SET
                exit_time = CURRENT_TIMESTAMP,
                duration_hours = ?,
                amount = ?,
                status = 'COMPLETED'
            WHERE session_id = ?
            """,
            (
                actual_duration_hours,
                amount,
                parking_record["session_id"]
            )
        )

        connection.execute(
            """
            UPDATE slots
            SET status = 'AVAILABLE'
            WHERE slot_id = ?
            """,
            (parking_record["slot_id"],)
        )

        connection.execute(
            """
            INSERT INTO payments (
                session_id,
                amount,
                payment_status,
                paid_at
            )
            VALUES (?, ?, 'PAID', CURRENT_TIMESTAMP)
            """,
            (
                parking_record["session_id"],
                amount
            )
        )

        connection.commit()

        return {
            "message": "Vehicle checked out successfully.",
            "receipt": {
                "session_id": parking_record["session_id"],
                "license_plate": parking_record["license_plate"],
                "vehicle_type": parking_record["vehicle_type"],
                "floor_id": parking_record["floor_id"],
                "slot_number": parking_record["slot_number"],
                "duration_hours": round(
                    actual_duration_hours,
                    2
                ),
                "billable_hours": billable_hours,
                "hourly_rate": hourly_rate,
                "amount": amount,
                "payment_status": "PAID"
            }
        }

    except HTTPException:

        connection.rollback()

        raise

    except Exception:

        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail="An error occurred during checkout."
        )

    finally:

        connection.close()


@app.get("/active-parking")
def get_active_parking(
    current_user: dict = Depends(
        get_current_user
    )
):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            ps.session_id,
            v.license_plate,
            v.vehicle_type,
            ps.entry_time,
            s.floor_id,
            s.slot_id,
            s.slot_number,
            s.slot_type,
            ps.status
        FROM parking_sessions ps
        JOIN vehicles v
            ON ps.vehicle_id = v.vehicle_id
        JOIN slots s
            ON ps.slot_id = s.slot_id
        WHERE ps.status = 'ACTIVE'
        ORDER BY ps.entry_time
        """
    ).fetchall()

    connection.close()

    return {
        "total_active_vehicles": len(rows),
        "vehicles": [dict(row) for row in rows]
    }


@app.get("/parking-history")
def get_parking_history(
    current_user: dict = Depends(
        get_current_user
    )
):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            ps.session_id,
            v.license_plate,
            v.vehicle_type,
            ps.entry_time,
            ps.exit_time,
            ps.duration_hours,
            ps.amount,
            s.floor_id,
            s.slot_number,
            p.payment_status,
            p.paid_at
        FROM parking_sessions ps
        JOIN vehicles v
            ON ps.vehicle_id = v.vehicle_id
        JOIN slots s
            ON ps.slot_id = s.slot_id
        LEFT JOIN payments p
            ON ps.session_id = p.session_id
        WHERE ps.status = 'COMPLETED'
        ORDER BY ps.session_id DESC
        """
    ).fetchall()

    connection.close()

    return {
        "total_completed_sessions": len(rows),
        "history": [dict(row) for row in rows]
    }