"""Admin routes: user management, geofence, dashboard data."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from models.database import get_db
from models.user import get_all_users, create_user, update_user_status, get_user_by_email
from models.site import get_site, update_site
from models.punch import get_all_punches_in_range, get_user_punches, get_open_sessions, get_latest_punch
from services.auth import hash_password
from services.timezone import now_ist, to_ist, format_time_ist, format_date_ist, today_ist_range, ist_date_str, IST
from routes.dependencies import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


class CreateUserRequest(BaseModel):
    name: str
    email: str
    password: str


class UpdateStatusRequest(BaseModel):
    status: str


class UpdateGeofenceRequest(BaseModel):
    latitude: float
    longitude: float
    radius_m: int


@router.get("/users")
def list_users(user=Depends(require_admin), conn=Depends(get_db)):
    users = get_all_users(conn)
    return {"users": [dict(u) for u in users]}


@router.post("/users")
def add_user(body: CreateUserRequest, user=Depends(require_admin), conn=Depends(get_db)):
    name = body.name.strip()
    email = body.email.strip().lower()
    password = body.password

    if not name or not email or not password:
        return JSONResponse(status_code=400, content={"detail": "All fields are required."})
    if len(password) < 8:
        return JSONResponse(status_code=400, content={"detail": "Password must be at least 8 characters."})

    existing = get_user_by_email(conn, email)
    if existing:
        return JSONResponse(status_code=409, content={"detail": "A user with this email already exists."})

    hashed = hash_password(password)
    new_user = create_user(conn, name, email, hashed, "associate")
    return dict(new_user)


@router.put("/users/{user_id}/status")
def change_user_status(user_id: str, body: UpdateStatusRequest, user=Depends(require_admin), conn=Depends(get_db)):
    if body.status not in ("active", "inactive"):
        return JSONResponse(status_code=400, content={"detail": "Status must be 'active' or 'inactive'."})
    update_user_status(conn, user_id, body.status)
    return {"message": f"User status set to {body.status}."}


@router.get("/geofence")
def get_geofence(user=Depends(require_admin), conn=Depends(get_db)):
    site = get_site(conn)
    if not site:
        return JSONResponse(status_code=404, content={"detail": "Site not configured."})
    return {"latitude": float(site["latitude"]), "longitude": float(site["longitude"]), "radius_m": site["radius_m"], "name": site["name"]}


@router.put("/geofence")
def update_geofence(body: UpdateGeofenceRequest, user=Depends(require_admin), conn=Depends(get_db)):
    if not (-90 <= body.latitude <= 90) or not (-180 <= body.longitude <= 180):
        return JSONResponse(status_code=400, content={"detail": "Invalid coordinates."})
    if not (5 <= body.radius_m <= 50):
        return JSONResponse(status_code=400, content={"detail": "Radius must be between 5 and 50 metres."})
    updated = update_site(conn, body.latitude, body.longitude, body.radius_m)
    return {"latitude": float(updated["latitude"]), "longitude": float(updated["longitude"]), "radius_m": updated["radius_m"]}


@router.get("/dashboard")
def dashboard_data(user=Depends(require_admin), conn=Depends(get_db)):
    """Get dashboard summary data. All times in IST."""
    today_start, today_end = today_ist_range()

    users = get_all_users(conn)
    active_users = [u for u in users if u["status"] == "active" and u["role"] == "associate"]

    today_punches = get_all_punches_in_range(conn, today_start.isoformat(), today_end.isoformat())

    users_who_punched_in = set()
    user_first_punch = {}

    for p in today_punches:
        uid = str(p["user_id"])
        if p["type"] == "in":
            users_who_punched_in.add(uid)
            if uid not in user_first_punch:
                user_first_punch[uid] = p["server_timestamp"]

    # Determine who's CURRENTLY active (check latest punch globally, not just today)
    active_sessions = set()
    for u in active_users:
        uid = str(u["id"])
        latest = get_latest_punch(conn, uid)
        if latest and latest["type"] == "in":
            # Check it's from today (IST)
            punch_ist = to_ist(latest["server_timestamp"])
            if punch_ist >= today_start:
                active_sessions.add(uid)

    present_today = len(users_who_punched_in)
    absent_today = len(active_users) - present_today
    active_now = len(active_sessions)

    today_details = []
    for u in active_users:
        uid = str(u["id"])
        status = "Present" if uid in users_who_punched_in else "Absent"
        punch_in_time = user_first_punch.get(uid)
        is_active = uid in active_sessions
        today_details.append({
            "name": u["name"],
            "status": "Active" if is_active else status,
            "punch_in": format_time_ist(punch_in_time),
            "hours": None,
        })

    # Weekly data (last 7 days in IST)
    weekly = []
    for i in range(6, -1, -1):
        day_start = today_start - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        day_punches = get_all_punches_in_range(conn, day_start.isoformat(), day_end.isoformat())
        day_users = set(str(p["user_id"]) for p in day_punches if p["type"] == "in")
        weekly.append({
            "day": day_start.strftime("%a"),
            "present": len(day_users),
            "absent": len(active_users) - len(day_users),
        })

    return {
        "present_today": present_today,
        "absent_today": absent_today,
        "active_now": active_now,
        "today_details": today_details,
        "weekly": weekly,
    }


@router.get("/users/{user_id}/attendance")
def user_attendance(user_id: str, start: str = None, end: str = None, user=Depends(require_admin), conn=Depends(get_db)):
    """Get attendance records for a specific user. All times in IST."""
    from models.user import get_user_by_id

    if not start or not end:
        now = now_ist()
        start = now.replace(day=1).strftime("%Y-%m-%d")
        if now.month == 12:
            end = f"{now.year + 1}-01-01"
        else:
            end = f"{now.year}-{now.month + 1:02d}-01"

    target_user = get_user_by_id(conn, user_id)
    if not target_user:
        return JSONResponse(status_code=404, content={"detail": "User not found."})

    records = get_user_punches(conn, user_id, start, end)

    sessions = {}
    for r in records:
        day = ist_date_str(r["server_timestamp"])
        if day not in sessions:
            sessions[day] = {"date": format_date_ist(r["server_timestamp"], include_year=True), "in": None, "out": None}

        if r["type"] == "in" and sessions[day]["in"] is None:
            sessions[day]["in"] = r["server_timestamp"]
        elif r["type"] == "out" and sessions[day]["out"] is None:
            sessions[day]["out"] = r["server_timestamp"]

    result = []
    total_hours = 0
    for day_key in sorted(sessions.keys(), reverse=True):
        s = sessions[day_key]
        punch_in = format_time_ist(s["in"])
        punch_out = format_time_ist(s["out"])
        hours = None
        if s["in"] and s["out"]:
            diff = (s["out"] - s["in"]).total_seconds() / 3600
            hours = round(diff, 1)
            total_hours += diff
        result.append({
            "date": s["date"],
            "punch_in": punch_in,
            "punch_out": punch_out,
            "hours": f"{hours}h" if hours else ("In Progress" if s["in"] and not s["out"] else None),
        })

    return {
        "user_name": target_user["name"],
        "user_email": target_user["email"],
        "records": result,
        "total_hours": round(total_hours, 1),
        "days_present": len(result),
    }
