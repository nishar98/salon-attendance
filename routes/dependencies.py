"""Auth middleware / dependency injection for FastAPI routes."""

from fastapi import Request, HTTPException

from services.auth import verify_token


def get_current_user(request: Request) -> dict:
    """
    Extract and validate JWT from the session cookie.

    Returns:
        Dict with 'user_id' and 'role'.

    Raises:
        HTTPException 401 if no valid token is found.
    """
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")

    return payload


def require_admin(request: Request) -> dict:
    """
    Ensure the current user has admin role.

    Returns:
        Dict with 'user_id' and 'role'.

    Raises:
        HTTPException 403 if user is not an admin.
    """
    user = get_current_user(request)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return user
