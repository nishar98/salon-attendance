"""User model and database operations."""

from datetime import datetime
from typing import Optional
import psycopg2.extras


def get_user_by_email(conn, email: str) -> Optional[dict]:
    """Fetch a user by email address."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cur.fetchone()


def get_user_by_id(conn, user_id: str) -> Optional[dict]:
    """Fetch a user by ID."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cur.fetchone()


def get_all_users(conn) -> list:
    """Fetch all users (for admin)."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT id, name, email, role, status, created_at FROM users ORDER BY name")
        return cur.fetchall()


def create_user(conn, name: str, email: str, password_hash: str, role: str = "associate") -> dict:
    """Create a new user."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """INSERT INTO users (name, email, password_hash, role)
               VALUES (%s, %s, %s, %s)
               RETURNING id, name, email, role, status, created_at""",
            (name, email, password_hash, role),
        )
        conn.commit()
        return cur.fetchone()


def update_failed_login(conn, user_id: str, attempts: int, locked_until: Optional[datetime] = None):
    """Update failed login attempts and optional lockout."""
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE users
               SET failed_login_attempts = %s, locked_until = %s
               WHERE id = %s""",
            (attempts, locked_until, user_id),
        )
        conn.commit()


def reset_failed_login(conn, user_id: str):
    """Reset failed login counter after successful login."""
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE users
               SET failed_login_attempts = 0, locked_until = NULL
               WHERE id = %s""",
            (user_id,),
        )
        conn.commit()


def update_user_status(conn, user_id: str, status: str):
    """Activate or deactivate a user."""
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE users SET status = %s WHERE id = %s",
            (status, user_id),
        )
        conn.commit()
