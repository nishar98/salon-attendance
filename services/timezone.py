"""IST timezone utilities. All times in the app should use these helpers."""

from datetime import datetime, timedelta, timezone

# Indian Standard Time = UTC + 5:30
IST = timezone(timedelta(hours=5, minutes=30))


def now_ist() -> datetime:
    """Get current time in IST."""
    return datetime.now(IST)


def to_ist(dt: datetime) -> datetime:
    """Convert any datetime to IST."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Assume UTC if naive
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST)


def format_time_ist(dt: datetime) -> str:
    """Format a datetime as 12-hour IST time string (e.g., '09:03 AM')."""
    if dt is None:
        return None
    ist_dt = to_ist(dt)
    return ist_dt.strftime("%I:%M %p")


def format_date_ist(dt: datetime, include_year: bool = False) -> str:
    """Format a datetime as date string in IST (e.g., 'Aug 09' or 'Aug 09, 2026')."""
    if dt is None:
        return None
    ist_dt = to_ist(dt)
    if include_year:
        return ist_dt.strftime("%b %d, %Y")
    return ist_dt.strftime("%b %d")


def today_ist_range() -> tuple[datetime, datetime]:
    """Get start and end of today in IST (as UTC datetimes for DB queries)."""
    now = now_ist()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return start, end


def ist_date_str(dt: datetime) -> str:
    """Get YYYY-MM-DD date string in IST."""
    if dt is None:
        return None
    return to_ist(dt).strftime("%Y-%m-%d")
