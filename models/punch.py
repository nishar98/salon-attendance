"""PunchRecord model and database operations."""

from typing import Optional
import psycopg2.extras


def get_latest_punch(conn, user_id: str) -> Optional[dict]:
    """Get the most recent punch record for a user."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """SELECT * FROM punch_records
               WHERE user_id = %s
               ORDER BY server_timestamp DESC
               LIMIT 1""",
            (user_id,),
        )
        return cur.fetchone()


def create_punch_record(
    conn,
    user_id: str,
    punch_type: str,
    latitude: float,
    longitude: float,
    gps_accuracy_m: float,
) -> dict:
    """Insert a new punch record."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """INSERT INTO punch_records (user_id, type, latitude, longitude, gps_accuracy_m, created_at)
               VALUES (%s, %s, %s, %s, %s, NOW())
               RETURNING *""",
            (user_id, punch_type, latitude, longitude, gps_accuracy_m),
        )
        conn.commit()
        return cur.fetchone()


def get_user_punches(conn, user_id: str, start_date: str, end_date: str) -> list:
    """Get punch records for a user within a date range."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """SELECT * FROM punch_records
               WHERE user_id = %s
               AND server_timestamp >= %s
               AND server_timestamp < %s
               ORDER BY server_timestamp DESC""",
            (user_id, start_date, end_date),
        )
        return cur.fetchall()


def get_all_punches_in_range(conn, start_date: str, end_date: str) -> list:
    """Get all punch records within a date range (for admin reports)."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """SELECT pr.*, u.name as user_name, u.email as user_email
               FROM punch_records pr
               JOIN users u ON pr.user_id = u.id
               WHERE pr.server_timestamp >= %s
               AND pr.server_timestamp < %s
               ORDER BY pr.server_timestamp DESC""",
            (start_date, end_date),
        )
        return cur.fetchall()
