"""Report export routes."""

import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, StreamingResponse

from models.database import get_db
from models.punch import get_all_punches_in_range
from services.timezone import now_ist, format_time_ist, ist_date_str
from routes.dependencies import require_admin

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/export")
def export_csv(
    start: str = Query(..., description="Start date YYYY-MM-DD"),
    end: str = Query(..., description="End date YYYY-MM-DD"),
    user=Depends(require_admin),
    conn=Depends(get_db),
):
    """Export attendance data as CSV. All times in IST."""
    try:
        datetime.strptime(start, "%Y-%m-%d")
        datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return JSONResponse(status_code=400, content={"detail": "Invalid date format. Use YYYY-MM-DD."})

    records = get_all_punches_in_range(conn, start, end)

    if not records:
        return JSONResponse(status_code=404, content={"detail": "No records found for the selected date range."})

    sessions = {}
    for r in records:
        key = (r["user_name"], ist_date_str(r["server_timestamp"]))
        if key not in sessions:
            sessions[key] = {"name": r["user_name"], "date": key[1], "in": None, "out": None}

        if r["type"] == "in" and sessions[key]["in"] is None:
            sessions[key]["in"] = r["server_timestamp"]
        elif r["type"] == "out" and sessions[key]["out"] is None:
            sessions[key]["out"] = r["server_timestamp"]

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([f"# Generated: {now_ist().strftime('%Y-%m-%d %I:%M %p IST')}"])
    writer.writerow(["Name", "Date", "Punch In (IST)", "Punch Out (IST)", "Total Hours"])

    for key in sorted(sessions.keys(), key=lambda k: (k[1], k[0])):
        s = sessions[key]
        punch_in = format_time_ist(s["in"]) if s["in"] else ""
        punch_out = format_time_ist(s["out"]) if s["out"] else "In Progress"
        total_hours = ""
        if s["in"] and s["out"]:
            diff = (s["out"] - s["in"]).total_seconds() / 3600
            total_hours = f"{diff:.1f}"
        writer.writerow([s["name"], s["date"], punch_in, punch_out, total_hours])

    output.seek(0)
    filename = f"attendance_{start}_to_{end}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
