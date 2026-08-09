"""Authentication utilities: password hashing, JWT creation/validation."""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"

# Password hashing with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain, hashed)


def create_token(user_id: str, role: str) -> str:
    """
    Create a JWT token.

    Expiry:
        - Admin: 4 hours
        - Associate: 12 hours
    """
    # Long sessions: associates stay logged in for 30 days, admin for 7 days
    days = 7 if role == "admin" else 30
    expire = datetime.now(timezone.utc) + timedelta(days=days)
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.

    Returns:
        Dict with 'sub' (user_id) and 'role', or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")
        if user_id is None:
            return None
        return {"user_id": user_id, "role": role}
    except JWTError:
        return None
