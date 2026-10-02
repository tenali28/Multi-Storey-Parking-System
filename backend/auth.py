import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import JWTError, jwt


load_dotenv()


SECRET_KEY = os.getenv(
    "JWT_SECRET",
    "development-secret-change-before-production"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(
    password: str,
    salt: str | None = None
):
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000
    )

    return (
        salt,
        password_hash.hex()
    )


def verify_password(
    password: str,
    salt: str,
    stored_hash: str
) -> bool:

    _, password_hash = hash_password(
        password,
        salt
    )

    return hmac.compare_digest(
        password_hash,
        stored_hash
    )


def create_access_token(username: str) -> str:

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": username,
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if not username:
            return None

        return username

    except JWTError:

        return None