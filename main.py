"""
Salon Attendance Management App — FastAPI Entry Point

Run locally:
    uvicorn main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from models.database import close_pool
from routes.auth import router as auth_router
from routes.punch import router as punch_router
from routes.admin import router as admin_router
from routes.reports import router as reports_router
from routes.pages import router as pages_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: nothing extra needed (pool is lazy-initialized)
    yield
    # Shutdown: close DB connections
    close_pool()


app = FastAPI(
    title="Salon Attendance",
    description="Geo-fenced punch in/out for salon staff",
    version="1.0.0",
    lifespan=lifespan,
)


# --- Error Handlers ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return user-friendly validation errors instead of raw Pydantic output."""
    errors = exc.errors()
    if errors:
        # Get first error's message
        first = errors[0]
        field = " → ".join(str(loc) for loc in first.get("loc", []) if loc != "body")
        msg = first.get("msg", "Invalid input")
        detail = f"{field}: {msg}" if field else msg
    else:
        detail = "Invalid request data."
    return JSONResponse(status_code=422, content={"detail": detail})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all handler — don't leak internal details to the client."""
    import traceback
    traceback.print_exc()  # Print to server console for debugging
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


# --- Middleware ---

# CORS middleware (allows requests from any origin in dev; Railway handles HTTPS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Reject oversized payloads (> 1 MB) to prevent abuse."""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 1_048_576:  # 1 MB
        return JSONResponse(
            status_code=413,
            content={"detail": "Request too large."},
        )
    return await call_next(request)


# Static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register route modules
app.include_router(auth_router)
app.include_router(punch_router)
app.include_router(admin_router)
app.include_router(reports_router)
app.include_router(pages_router)
