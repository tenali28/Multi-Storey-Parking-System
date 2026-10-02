import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

from backend.auth import hash_password


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "parking.db"


def get_connection():

    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS floors (
            floor_id INTEGER PRIMARY KEY,
            floor_number INTEGER NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS slots (
            slot_id INTEGER PRIMARY KEY,
            floor_id INTEGER NOT NULL,
            slot_number INTEGER NOT NULL,
            slot_type TEXT NOT NULL CHECK (
                slot_type IN ('CAR', 'EV')
            ),
            status TEXT NOT NULL DEFAULT 'AVAILABLE' CHECK (
                status IN ('AVAILABLE', 'OCCUPIED')
            ),
            FOREIGN KEY (floor_id)
                REFERENCES floors(floor_id)
                ON DELETE CASCADE,
            UNIQUE (floor_id, slot_number)
        );

        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_plate TEXT NOT NULL UNIQUE,
            vehicle_type TEXT NOT NULL CHECK (
                vehicle_type IN ('CAR', 'EV')
            ),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS parking_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            slot_id INTEGER NOT NULL,
            entry_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            exit_time TEXT,
            duration_hours REAL,
            amount REAL,
            status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (
                status IN ('ACTIVE', 'COMPLETED')
            ),
            FOREIGN KEY (vehicle_id)
                REFERENCES vehicles(vehicle_id),
            FOREIGN KEY (slot_id)
                REFERENCES slots(slot_id)
        );

        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL UNIQUE,
            amount REAL NOT NULL,
            payment_status TEXT NOT NULL DEFAULT 'PAID' CHECK (
                payment_status IN ('PAID', 'PENDING')
            ),
            paid_at TEXT,
            FOREIGN KEY (session_id)
                REFERENCES parking_sessions(session_id)
        );

        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'ADMIN' CHECK (
                role IN ('ADMIN')
            ),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_slots_floor
            ON slots(floor_id);

        CREATE INDEX IF NOT EXISTS idx_slots_status
            ON slots(status);

        CREATE INDEX IF NOT EXISTS idx_sessions_vehicle
            ON parking_sessions(vehicle_id);

        CREATE INDEX IF NOT EXISTS idx_sessions_status
            ON parking_sessions(status);

        CREATE INDEX IF NOT EXISTS idx_users_username
            ON users(username);
        """
    )

    connection.commit()
    connection.close()


def seed_parking_data():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM floors"
    )

    floor_count = cursor.fetchone()[0]

    if floor_count == 0:

        for floor_number in range(1, 4):

            cursor.execute(
                """
                INSERT INTO floors (
                    floor_id,
                    floor_number
                )
                VALUES (?, ?)
                """,
                (
                    floor_number,
                    floor_number
                )
            )

    cursor.execute(
        "SELECT COUNT(*) FROM slots"
    )

    slot_count = cursor.fetchone()[0]

    if slot_count == 0:

        slot_id = 1

        for floor_id in range(1, 4):

            for slot_number in range(1, 4):

                cursor.execute(
                    """
                    INSERT INTO slots
                    (
                        slot_id,
                        floor_id,
                        slot_number,
                        slot_type,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        slot_id,
                        floor_id,
                        slot_number,
                        "CAR",
                        "AVAILABLE"
                    )
                )

                slot_id += 1

            for slot_number in range(4, 6):

                cursor.execute(
                    """
                    INSERT INTO slots
                    (
                        slot_id,
                        floor_id,
                        slot_number,
                        slot_type,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        slot_id,
                        floor_id,
                        slot_number,
                        "EV",
                        "AVAILABLE"
                    )
                )

                slot_id += 1

    connection.commit()
    connection.close()


def seed_admin_user():

    connection = get_connection()

    existing_user = connection.execute(
        """
        SELECT user_id
        FROM users
        WHERE username = ?
        """,
        ("admin",)
    ).fetchone()

    if existing_user is None:

        admin_password = os.getenv(
            "ADMIN_PASSWORD",
            "admin123"
        )

        salt, password_hash = hash_password(
            admin_password
        )

        connection.execute(
            """
            INSERT INTO users
            (
                username,
                password_hash,
                password_salt,
                role
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                "admin",
                password_hash,
                salt,
                "ADMIN"
            )
        )

        connection.commit()

    connection.close()