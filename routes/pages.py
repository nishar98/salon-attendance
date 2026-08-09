"""Page routes — serves HTML templates."""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Environment, FileSystemLoader

from services.auth import verify_token

router = APIRouter(tags=["pages"])

# Set up Jinja2 environment directly (avoids Starlette's cache bug on Python 3.14)
_env = Environment(loader=FileSystemLoader("templates"), autoescape=True)


def render_template(name: str, context: dict) -> HTMLResponse:
    """Render a Jinja2 template and return as HTMLResponse."""
    template = _env.get_template(name)
    html = template.render(**context)
    return HTMLResponse(content=html)


def get_optional_user(request: Request):
    """Try to get the current user, return None if not logged in."""
    token = request.cookies.get("session_token")
    if not token:
        return None
    return verify_token(token)


@router.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    """Redirect to login or home based on auth status."""
    user = get_optional_user(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=302)
    if user["role"] == "admin":
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    return render_template("home.html", {"request": request, "user": user})


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Show the login page."""
    user = get_optional_user(request)
    if user:
        return RedirectResponse(url="/", status_code=302)
    return render_template("login.html", {"request": request})


@router.get("/history", response_class=HTMLResponse)
def history_page(request: Request):
    """Show attendance history for the logged-in associate."""
    user = get_optional_user(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=302)
    return render_template("history.html", {"request": request, "user": user})


@router.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard_page(request: Request):
    """Show admin dashboard."""
    user = get_optional_user(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=302)
    if user["role"] != "admin":
        return RedirectResponse(url="/", status_code=302)
    return render_template("admin/dashboard.html", {"request": request, "user": user})


@router.get("/admin/users", response_class=HTMLResponse)
def admin_users_page(request: Request):
    """Show user management page."""
    user = get_optional_user(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=302)
    if user["role"] != "admin":
        return RedirectResponse(url="/", status_code=302)
    return render_template("admin/users.html", {"request": request, "user": user})


@router.get("/admin/geofence", response_class=HTMLResponse)
def admin_geofence_page(request: Request):
    """Show geofence configuration page."""
    user = get_optional_user(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=302)
    if user["role"] != "admin":
        return RedirectResponse(url="/", status_code=302)
    return render_template("admin/geofence.html", {"request": request, "user": user})


@router.get("/admin/attendance", response_class=HTMLResponse)
def admin_attendance_page(request: Request):
    """Show user-wise attendance page."""
    user = get_optional_user(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=302)
    if user["role"] != "admin":
        return RedirectResponse(url="/", status_code=302)
    return render_template("admin/attendance.html", {"request": request, "user": user})
