"""Site (Geofence) model and database operations."""

from typing import Optional
import psycopg2.extras


def get_site(conn) -> Optional[dict]:
    """Get the salon site configuration (single row)."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM site LIMIT 1")
        return cur.fetchone()


def update_site(conn, latitude: float, longitude: float, radius_m: int) -> dict:
    """Update the salon geofence coordinates and radius."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        # Update the existing row (there's only one)
        cur.execute(
            """UPDATE site
               SET latitude = %s, longitude = %s, radius_m = %s, updated_at = NOW()
               RETURNING *""",
            (latitude, longitude, radius_m),
        )
        conn.commit()
        return cur.fetchone()
