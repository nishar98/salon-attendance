"""Punch in/out API endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from models.database import get_db
from models.punch import get_latest_punch, create_punch_record, get_user_punches, get_open_sessions, create_auto_punch_out
from models.site import get_site
from services.geo import is_within_geofence
from services.timezone import now_ist, to_ist, format_time_ist, format_date_ist, today_ist_range, ist_date_str, IST
from routes.dependencies import get_current_user

router = APIRouter(prefix="/api/punch", tags=["punch"])


class PunchRequest(BaseModel):
    latitude: float
    longitude: float
    accuracy: float


def check_gps_accuracy(accuracy: float, radius_m: int):
    max_acceptable = max(radius_m * 3, 150)
    if accuracy > max_acceptable:
        return False, f"GPS signal weak (±{accuracy:.0f}m). Move near a window or outside for better accuracy."
    return True, None


def auto_punch_out_stale_sessions(conn):
    """Auto punch-out any user whose last punch-in was before today (IST midnight)."""
    today_start, _ = today_ist_range()
    open_sessions = get_open_sessions(conn)
    for session in open_sessions:
        punch_in_ist = to_ist(session["server_timestamp"])
        if punch_in_ist < today_start:
            # Auto punch-out at 11:59:59 PM IST of the day they punched in
            punch_in_day_end = punch_in_ist.replace(hour=23, minute=59, second=59, microsecond=0)
            create_auto_punch_out(conn, str(session["user_id"]), punch_in_day_end, session)


@router.post("/in")
def punch_in(body: PunchRequest, user=Depends(get_current_user), conn=Depends(get_db)):
    """Record a punch-in. Validates geofence server-side."""
    # First, auto punch-out stale sessions
    auto_punch_out_stale_sessions(conn)

    latitude = body.latitude
    longitude = body.longitude
    accuracy = body.accuracy

    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return JSONResponse(status_code=400, content={"detail": "Invalid coordinates."})

    site = get_site(conn)
    if site is None:
        return JSONResponse(status_code=500, content={"detail": "Site not configured."})

    ok, msg = check_gps_accuracy(accuracy, site["radius_m"])
    if not ok:
        return JSONResponse(status_code=422, content={"detail": msg})

    within, distance = is_within_geofence(
        latitude, longitude,
        float(site["latitude"]), float(site["longitude"]),
        site["radius_m"],
    )
    if not within:
        return JSONResponse(status_code=422, content={"detail": f"You are ~{distance:.0f} metres from the salon. Move closer."})

    latest = get_latest_punch(conn, user["user_id"])
    if latest and latest["type"] == "in":
        return JSONResponse(status_code=409, content={"detail": "You're already punched in."})

    record = create_punch_record(conn, user["user_id"], "in", latitude, longitude, accuracy)
    ist_time = format_time_ist(record["server_timestamp"])
    return {"message": f"Punched in at {ist_time}!", "timestamp": str(to_ist(record["server_timestamp"]))}


@router.post("/out")
def punch_out(body: PunchRequest, user=Depends(get_current_user), conn=Depends(get_db)):
    """Record a punch-out. Validates geofence server-side."""
    latitude = body.latitude
    longitude = body.longitude
    accuracy = body.accuracy

    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return JSONResponse(status_code=400, content={"detail": "Invalid coordinates."})

    site = get_site(conn)
    if site is None:
        return JSONResponse(status_code=500, content={"detail": "Site not configured."})

    ok, msg = check_gps_accuracy(accuracy, site["radius_m"])
    if not ok:
        return JSONResponse(status_code=422, content={"detail": msg})

    within, distance = is_within_geofence(
        latitude, longitude,
        float(site["latitude"]), float(site["longitude"]),
        site["radius_m"],
    )
    if not within:
        return JSONResponse(status_code=422, content={"detail": f"You are ~{distance:.0f} metres from the salon. Move closer."})

    latest = get_latest_punch(conn, user["user_id"])
    if not latest or latest["type"] == "out":
        return JSONResponse(status_code=409, content={"detail": "No active session. Punch in first."})

    record = create_punch_record(conn, user["user_id"], "out", latitude, longitude, accuracy)
    ist_time = format_time_ist(record["server_timestamp"])
    return {"message": f"Punched out at {ist_time}!", "timestamp": str(to_ist(record["server_timestamp"]))}


@router.get("/status")
def punch_status(user=Depends(get_current_user), conn=Depends(get_db)):
    """Get the user's current punch status."""
    # Auto punch-out stale sessions first
    auto_punch_out_stale_sessions(conn)

    latest = get_latest_punch(conn, user["user_id"])

    if not latest or latest["type"] == "out":
        return {"status": "off_duty", "since": None}

    return {
        "status": "on_duty",
        "since": str(to_ist(latest["server_timestamp"])),
    }


@router.get("/history")
def punch_history(
    start: str = Query(...),
    end: str = Query(...),
    user=Depends(get_current_user),
    conn=Depends(get_db),
):
    """Get attendance history for the logged-in user (grouped by day in IST)."""
    records = get_user_punches(conn, user["user_id"], start, end)

    sessions = {}
    for r in records:
        day = ist_date_str(r["server_timestamp"])
        if day not in sessions:
            sessions[day] = {"date": format_date_ist(r["server_timestamp"]), "in": None, "out": None}

        if r["type"] == "in" and sessions[day]["in"] is None:
            sessions[day]["in"] = r["server_timestamp"]
        elif r["type"] == "out" and sessions[day]["out"] is None:
            sessions[day]["out"] = r["server_timestamp"]

    result = []
    for day_key in sorted(sessions.keys(), reverse=True):
        s = sessions[day_key]
        punch_in = format_time_ist(s["in"])
        punch_out = format_time_ist(s["out"])
        hours = None
        if s["in"] and s["out"]:
            diff = (s["out"] - s["in"]).total_seconds() / 3600
            hours = f"{diff:.1f}h"
        result.append({
            "date": s["date"],
            "punch_in": punch_in,
            "punch_out": punch_out,
            "hours": hours,
        })

    return {"records": result}
