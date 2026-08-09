"""Authentication routes: login, logout."""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from models.database import get_db
from models.user import get_user_by_email, update_failed_login, reset_failed_login
from services.auth import verify_password, create_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

# In production (Railway), this should be True. For local dev (http://localhost), False.
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(body: LoginRequest, conn=Depends(get_db)):
    """
    Authenticate with email + password. Sets a JWT cookie on success.

    Lockout policy:
        - Associate: 5 failures in 15 min → locked 30 min
        - Admin: 3 failures in 10 min → locked 60 min
    """
    email = body.email.strip().lower()
    password = body.password

    # Generic error to avoid revealing whether email or password is wrong
    generic_error = {"detail": "Invalid email or password."}

    if not email or not password:
        return JSONResponse(status_code=401, content=generic_error)

    user = get_user_by_email(conn, email)
    if user is None:
        return JSONResponse(status_code=401, content=generic_error)

    # Check if account is inactive
    if user["status"] == "inactive":
        return JSONResponse(status_code=401, content=generic_error)

    # Check if account is locked
    if user["locked_until"] and user["locked_until"] > datetime.now(timezone.utc):
        remaining = (user["locked_until"] - datetime.now(timezone.utc)).seconds // 60
        return JSONResponse(
            status_code=403,
            content={"detail": f"Account locked. Try again in {remaining + 1} minutes."},
        )

    # Verify password
    if not verify_password(password, user["password_hash"]):
        attempts = user["failed_login_attempts"] + 1
        max_attempts = 3 if user["role"] == "admin" else 5
        lockout_minutes = 60 if user["role"] == "admin" else 30

        if attempts >= max_attempts:
            locked_until = datetime.now(timezone.utc) + timedelta(minutes=lockout_minutes)
            update_failed_login(conn, str(user["id"]), attempts, locked_until)
            return JSONResponse(
                status_code=403,
                content={"detail": f"Account locked. Try again in {lockout_minutes} minutes."},
            )
        else:
            update_failed_login(conn, str(user["id"]), attempts)
            return JSONResponse(status_code=401, content=generic_error)

    # Success — reset lockout counter and issue token
    reset_failed_login(conn, str(user["id"]))
    token = create_token(str(user["id"]), user["role"])

    response = JSONResponse(content={
        "message": "Login successful",
        "role": user["role"],
        "name": user["name"],
    })
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=7 * 24 * 3600 if user["role"] == "admin" else 30 * 24 * 3600,
    )
    return response


@router.post("/logout")
def logout():
    """Clear the session cookie."""
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("session_token")
    return response
