# Salon Attendance Management App — Project Document

## Overview

A geo-fenced attendance management web application for a salon with 6-10 staff members. Associates punch in/out via their phone browser with GPS verification. The salon owner (admin) manages users, views dashboards, and exports reports.

**Live URL:** Hosted on Render (free tier)
**Database:** Supabase (hosted PostgreSQL, free tier)

---

## Tech Stack

### Backend

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Framework | **FastAPI** | 0.111.0 | REST API + serves HTML templates |
| Language | **Python** | 3.11+ | Server-side logic |
| Database Driver | **psycopg** | 3.2.13 | PostgreSQL connection (async-ready) |
| Connection Pool | **psycopg-pool** | 3.2.2 | Manages DB connections efficiently |
| Auth Tokens | **python-jose** | 3.3.0 | JWT token creation/validation |
| Password Hashing | **passlib + bcrypt** | 1.7.4 / 4.2.1 | Secure password storage |
| Server | **Uvicorn** | 0.30.1 | ASGI server to run FastAPI |
| Template Engine | **Jinja2** | 3.1.4 | Server-side HTML rendering |
| Environment | **python-dotenv** | 1.0.1 | Load .env variables |

### Frontend

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Styling | **TailwindCSS** (CDN) | Utility-first responsive CSS |
| Charts | **Chart.js** (CDN) | Bar charts on admin dashboard |
| Maps | **Leaflet.js + OpenStreetMap** (CDN) | Geofence visualization |
| JavaScript | **Vanilla JS** | GPS, fetch API calls, UI interactions |
| Templates | **Jinja2** (server-rendered HTML) | Pages served by FastAPI |

### Infrastructure

| Service | Provider | Tier | Purpose |
|---------|----------|------|---------|
| Hosting | **Render.com** | Free | Runs the Python server |
| Database | **Supabase** | Free | Hosted PostgreSQL |
| DNS/HTTPS | **Render** | Included | Auto SSL certificates |

---

## Application Structure

```
salon-attendance/
├── main.py                     # FastAPI entry point, middleware, error handlers
├── requirements.txt            # Python dependencies
├── Procfile                    # Render start command
├── runtime.txt                 # Python version specification
├── schema.sql                  # Database schema (run in Supabase SQL Editor)
├── .env.example                # Environment variable template
│
├── routes/
│   ├── auth.py                 # POST /api/auth/login, /logout
│   ├── punch.py                # POST /api/punch/in, /out; GET /status, /history
│   ├── admin.py                # GET/POST /api/admin/users, /geofence, /dashboard
│   ├── reports.py              # GET /api/reports/export (CSV download)
│   ├── pages.py                # Serves HTML pages (login, home, admin/*)
│   └── dependencies.py         # Auth middleware (get_current_user, require_admin)
│
├── models/
│   ├── database.py             # Connection pool (psycopg + psycopg-pool)
│   ├── user.py                 # User CRUD operations
│   ├── punch.py                # Punch record CRUD operations
│   └── site.py                 # Geofence configuration CRUD
│
├── services/
│   ├── auth.py                 # Password hashing, JWT creation/verification
│   └── geo.py                  # Haversine distance calculation
│
├── templates/
│   ├── base.html               # Base layout (nav, toast, TailwindCSS CDN)
│   ├── login.html              # Login page
│   ├── home.html               # Associate punch in/out page
│   ├── history.html            # Associate attendance history
│   └── admin/
│       ├── dashboard.html      # Admin dashboard (charts, summary cards)
│       ├── attendance.html     # User-wise attendance viewer
│       ├── users.html          # User management (add/deactivate)
│       └── geofence.html       # Geofence config with Leaflet map
│
├── static/
│   ├── css/style.css           # Custom CSS (punch button glow, spinner, etc.)
│   └── js/
│       ├── punch.js            # GPS acquisition + punch API calls
│       ├── charts.js           # Chart.js dashboard rendering
│       └── geofence.js         # Leaflet map + geofence form logic
│
└── tests/
    ├── test_auth.py            # Password hashing + JWT tests
    └── test_geo.py             # Haversine distance tests
```

---

## Pages & Their Purpose

### Associate Pages (Staff)

| Page | URL | Description |
|------|-----|-------------|
| **Login** | `/login` | Email + password form. Minimal, centered card layout. |
| **Home (Punch)** | `/` | Large circular punch button (green=in, red=out). Shows current status ("On Duty since 9:03 AM — 3h 22m") and GPS accuracy. |
| **History** | `/history` | Monthly attendance table. Columns: date, punch-in time, punch-out time, hours worked. Month selector dropdown. |

### Admin Pages (Salon Owner)

| Page | URL | Description |
|------|-----|-------------|
| **Dashboard** | `/admin/dashboard` | Summary cards (present/absent/active). Weekly bar chart (Chart.js). Today's attendance table. CSV export section with date range. |
| **Attendance** | `/admin/attendance` | User-wise attendance viewer. Select user + date range → see their records with summary (days present, total hours, avg hours/day). |
| **Users** | `/admin/users` | List all associates. Add new user form (name, email, password). Activate/deactivate toggle. |
| **Geofence** | `/admin/geofence` | Interactive Leaflet.js map showing the geofence circle. Latitude/longitude inputs. Radius slider (5-50m). Click map to set location. |

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login with email + password → sets JWT cookie |
| POST | `/api/auth/logout` | Clears session cookie |

### Punch (requires auth)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/punch/in` | Record punch-in (validates GPS + geofence) |
| POST | `/api/punch/out` | Record punch-out (validates GPS + geofence) |
| GET | `/api/punch/status` | Current status: on_duty/off_duty + timestamp |
| GET | `/api/punch/history?start=&end=` | User's own attendance records |

### Admin (requires admin role)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/dashboard` | Today's summary + weekly chart data |
| GET | `/api/admin/users` | List all users |
| POST | `/api/admin/users` | Create new associate |
| PUT | `/api/admin/users/{id}/status` | Activate/deactivate user |
| GET | `/api/admin/users/{id}/attendance` | User-specific attendance records |
| GET | `/api/admin/geofence` | Current geofence settings |
| PUT | `/api/admin/geofence` | Update geofence coordinates + radius |
| GET | `/api/reports/export?start=&end=` | Download CSV report |

---

## Database Schema

### `users`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Auto-generated |
| name | VARCHAR(100) | Full name |
| email | VARCHAR(255) | Unique login email |
| password_hash | VARCHAR(255) | Bcrypt hash |
| role | VARCHAR(20) | 'admin' or 'associate' |
| status | VARCHAR(20) | 'active', 'locked', or 'inactive' |
| failed_login_attempts | INT | Counter for lockout |
| locked_until | TIMESTAMPTZ | Lockout expiry time |
| created_at | TIMESTAMPTZ | Account creation time |

### `site`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Auto-generated |
| name | VARCHAR(100) | Location name (default: 'Salon') |
| latitude | DECIMAL(10,7) | Center latitude |
| longitude | DECIMAL(10,7) | Center longitude |
| radius_m | INT | Geofence radius in metres (5-50) |
| updated_at | TIMESTAMPTZ | Last modified |

### `punch_records`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Auto-generated |
| user_id | UUID (FK→users) | Who punched |
| type | VARCHAR(3) | 'in' or 'out' |
| server_timestamp | TIMESTAMPTZ | When (server time, authoritative) |
| latitude | DECIMAL(10,7) | GPS lat at punch time |
| longitude | DECIMAL(10,7) | GPS lon at punch time |
| gps_accuracy_m | DECIMAL(6,2) | GPS accuracy in metres |
| created_at | TIMESTAMPTZ | Record creation time |

---

## User Roles & Access

| Role | Can Do |
|------|--------|
| **Associate** | Login, punch in/out (GPS verified), view own history |
| **Admin** | Everything associate can do + manage users, configure geofence, view all attendance, view dashboard, export CSV |

---

## Key Features

1. **GPS Geofencing** — Staff can only punch in/out when physically at the salon (Haversine formula validates server-side)
2. **Long Sessions** — Associates stay logged in for 30 days; admin for 7 days (no daily re-login needed)
3. **Account Lockout** — 5 failed attempts locks associate for 30 min; 3 attempts locks admin for 60 min
4. **Real-time Status** — Home page shows "On Duty since X:XX AM (Xh Xm)" with live timer
5. **Admin Dashboard** — Present/absent/active counts, weekly bar chart, today's table, CSV export
6. **User-wise View** — Admin can view any associate's attendance with summary stats
7. **Interactive Geofence** — Leaflet map with click-to-set, radius slider, visual circle overlay
8. **Mobile-First** — Large touch targets, responsive layout, works on phone browsers

---

## Design Requirements for Frontend Redesign

### Login Page
- Clean, centered card layout
- Email + password inputs with clear labels
- "Log In" button (primary color)
- Error message display area (red)
- Loading state on button while authenticating
- Mobile-friendly (full-width on small screens)

### Associate Home (Punch Page)
- **Hero element:** Large circular button (green for "Punch In", red for "Punch Out")
- Status text above button: "Off Duty" or "On Duty since 9:03 AM (3h 22m)"
- GPS accuracy indicator below button
- Success/error message area (green/red banner)
- Minimal distractions — this is a 2-tap action

### Associate History
- Month selector (dropdown or date picker)
- Table: Date | Punch In | Punch Out | Hours
- "In Progress" badge for active sessions
- "No records" empty state
- Mobile: stack columns or use cards instead of table

### Admin Dashboard
- 3 summary cards at top: Present (green), Absent (red), Active Now (blue)
- Weekly bar chart (present vs absent, 7 days)
- Today's attendance table: Name | Status | Punch In | Hours
- CSV Export section: date range picker + download button

### Admin Attendance (User-wise)
- User dropdown selector
- Date range filter
- 3 summary cards: Days Present, Total Hours, Avg Hours/Day
- Full attendance table for selected user

### Admin Users
- "Add New Associate" form (name, email, password)
- User list with: name, email, role, status badge, activate/deactivate button

### Admin Geofence
- Split layout: Map on left, form on right (stacked on mobile)
- Interactive map with marker + translucent circle
- Latitude/longitude number inputs
- Radius slider with live label
- "Save Configuration" button with success feedback

### Navigation
- Sticky top nav bar with app name + links
- Admin sees: Dashboard, Attendance, Users, Geofence, Logout
- Associate sees: Home, History, Logout
- Mobile: hamburger menu that slides down

### Design Preferences
- **Color scheme:** Indigo/purple primary, green for success, red for errors
- **Style:** Clean, modern, rounded corners, subtle shadows
- **Fonts:** System font stack (-apple-system, Segoe UI, Roboto)
- **Mobile-first:** All pages must work on 375px width phones
- **Touch-friendly:** Minimum 44px tap targets on mobile

---

## Environment Variables Required

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (from Supabase) |
| `JWT_SECRET` | Secret key for signing JWT tokens |
| `COOKIE_SECURE` | `true` in production (HTTPS), `false` for localhost |

---

## Current Deployment

- **Backend:** Render.com (free tier, Python 3.11, auto-sleep after 15 min inactivity)
- **Database:** Supabase (free tier, PostgreSQL 15, Mumbai region)
- **Frontend:** Server-rendered HTML (Jinja2 templates served by the same FastAPI server)

The frontend is **not a separate SPA** — it's HTML templates rendered by the backend. Any new design must be compatible with Jinja2 template syntax (`{{ variable }}`, `{% if %}`, `{% block %}`).
