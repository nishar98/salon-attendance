"""PunchRecord model and database operations."""

from typing import Optional


def get_latest_punch(conn, user_id: str) -> Optional[dict]:
    """Get the most recent punch record for a user."""
    with conn.cursor() as cur:
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
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO punch_records (user_id, type, latitude, longitude, gps_accuracy_m, created_at)
               VALUES (%s, %s, %s, %s, %s, NOW())
               RETURNING *""",
            (user_id, punch_type, latitude, longitude, gps_accuracy_m),
        )
        conn.commit()
        return cur.fetchone()


def create_auto_punch_out(conn, user_id: str, punch_out_time, original_punch_in) -> dict:
    """Insert an auto punch-out record at midnight IST using the original punch-in's location."""
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO punch_records (user_id, type, server_timestamp, latitude, longitude, gps_accuracy_m, created_at)
               VALUES (%s, 'out', %s, %s, %s, %s, NOW())
               RETURNING *""",
            (user_id, punch_out_time,
             original_punch_in["latitude"], original_punch_in["longitude"],
             original_punch_in["gps_accuracy_m"]),
        )
        conn.commit()
        return cur.fetchone()


def get_open_sessions(conn) -> list:
    """Get all users with an active punch-in (no punch-out after their last punch-in)."""
    with conn.cursor() as cur:
        cur.execute(
            """SELECT pr.* FROM punch_records pr
               INNER JOIN (
                   SELECT user_id, MAX(server_timestamp) as max_ts
                   FROM punch_records
                   GROUP BY user_id
               ) latest ON pr.user_id = latest.user_id AND pr.server_timestamp = latest.max_ts
               WHERE pr.type = 'in'"""
        )
        return cur.fetchall()


def get_user_punches(conn, user_id: str, start_date: str, end_date: str) -> list:
    """Get punch records for a user within a date range."""
    with conn.cursor() as cur:
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
    with conn.cursor() as cur:
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
