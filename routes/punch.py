"""Punch in/out API endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from models.database import get_db
from models.punch import get_latest_punch, create_punch_record, get_user_punches
from models.site import get_site
from services.geo import is_within_geofence
from routes.dependencies import get_current_user

router = APIRouter(prefix="/api/punch", tags=["punch"])


class PunchRequest(BaseModel):
    latitude: float
    longitude: float
    accuracy: float


def check_gps_accuracy(accuracy: float, radius_m: int):
    """
    Check if GPS accuracy is acceptable.

    On phones at the salon: 5-15m accuracy (great).
    On desktop via WiFi: 50-100m accuracy (acceptable for testing).
    Reject only if extremely poor (> 150m or > 3x radius).
    """
    max_acceptable = max(radius_m * 3, 150)
    if accuracy > max_acceptable:
        return False, f"GPS signal weak (±{accuracy:.0f}m). Move near a window or outside for better accuracy."
    return True, None


@router.post("/in")
def punch_in(body: PunchRequest, user=Depends(get_current_user), conn=Depends(get_db)):
    """Record a punch-in. Validates geofence server-side."""
    latitude = body.latitude
    longitude = body.longitude
    accuracy = body.accuracy

    # Validate coordinate ranges
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return JSONResponse(status_code=400, content={"detail": "Invalid coordinates."})

    # Get site configuration
    site = get_site(conn)
    if site is None:
        return JSONResponse(status_code=500, content={"detail": "Site not configured."})

    # Check GPS accuracy
    ok, msg = check_gps_accuracy(accuracy, site["radius_m"])
    if not ok:
        return JSONResponse(status_code=422, content={"detail": msg})

    # Validate geofence
    within, distance = is_within_geofence(
        latitude, longitude,
        float(site["latitude"]), float(site["longitude"]),
        site["radius_m"],
    )
    if not within:
        return JSONResponse(
            status_code=422,
            content={"detail": f"You are ~{distance:.0f} metres from the salon. Move closer."},
        )

    # Check for active session (no duplicate punch-in)
    latest = get_latest_punch(conn, user["user_id"])
    if latest and latest["type"] == "in":
        return JSONResponse(status_code=409, content={"detail": "You're already punched in."})

    # Record punch-in
    record = create_punch_record(conn, user["user_id"], "in", latitude, longitude, accuracy)
    return {"message": "Punched in successfully!", "timestamp": str(record["server_timestamp"])}


@router.post("/out")
def punch_out(body: PunchRequest, user=Depends(get_current_user), conn=Depends(get_db)):
    """Record a punch-out. Validates geofence server-side."""
    latitude = body.latitude
    longitude = body.longitude
    accuracy = body.accuracy

    # Validate coordinate ranges
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return JSONResponse(status_code=400, content={"detail": "Invalid coordinates."})

    # Get site configuration
    site = get_site(conn)
    if site is None:
        return JSONResponse(status_code=500, content={"detail": "Site not configured."})

    # Check GPS accuracy
    ok, msg = check_gps_accuracy(accuracy, site["radius_m"])
    if not ok:
        return JSONResponse(status_code=422, content={"detail": msg})

    # Validate geofence
    within, distance = is_within_geofence(
        latitude, longitude,
        float(site["latitude"]), float(site["longitude"]),
        site["radius_m"],
    )
    if not within:
        return JSONResponse(
            status_code=422,
            content={"detail": f"You are ~{distance:.0f} metres from the salon. Move closer."},
        )

    # Check for active session
    latest = get_latest_punch(conn, user["user_id"])
    if not latest or latest["type"] == "out":
        return JSONResponse(status_code=409, content={"detail": "No active session. Punch in first."})

    # Record punch-out
    record = create_punch_record(conn, user["user_id"], "out", latitude, longitude, accuracy)
    return {"message": "Punched out successfully!", "timestamp": str(record["server_timestamp"])}


@router.get("/status")
def punch_status(user=Depends(get_current_user), conn=Depends(get_db)):
    """Get the user's current punch status."""
    latest = get_latest_punch(conn, user["user_id"])

    if not latest or latest["type"] == "out":
        return {"status": "off_duty", "since": None}

    return {
        "status": "on_duty",
        "since": str(latest["server_timestamp"]),
    }


@router.get("/history")
def punch_history(
    start: str = Query(...),
    end: str = Query(...),
    user=Depends(get_current_user),
    conn=Depends(get_db),
):
    """Get attendance history for the logged-in user (grouped by day)."""
    records = get_user_punches(conn, user["user_id"], start, end)

    # Group by date into sessions (pair punch-in with punch-out)
    sessions = {}
    for r in records:
        day = r["server_timestamp"].strftime("%Y-%m-%d")
        if day not in sessions:
            sessions[day] = {"date": r["server_timestamp"].strftime("%b %d"), "in": None, "out": None}

        if r["type"] == "in" and sessions[day]["in"] is None:
            sessions[day]["in"] = r["server_timestamp"]
        elif r["type"] == "out" and sessions[day]["out"] is None:
            sessions[day]["out"] = r["server_timestamp"]

    # Format for frontend
    result = []
    for day_key in sorted(sessions.keys(), reverse=True):
        s = sessions[day_key]
        punch_in = s["in"].strftime("%I:%M %p") if s["in"] else None
        punch_out = s["out"].strftime("%I:%M %p") if s["out"] else None
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
