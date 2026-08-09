# Implementation Plan: Salon Attendance Web App

## Overview

A lightweight responsive web app for a 6-person salon. Python (FastAPI) backend with Jinja2 templates, hosted on Railway + Supabase for $0/month.

**Total estimated build time:** 2–3 weeks for a beginner working part-time.

## Tasks

- [x] 1. Project setup
  - [x] 1.1 Initialize Python project and dependencies
    - Create project directory with `main.py`, `requirements.txt`, `.env.example`
    - Install: fastapi, uvicorn, python-jose, passlib[bcrypt], psycopg2-binary, python-dotenv, jinja2, python-multipart
    - Create folder structure: `routes/`, `models/`, `services/`, `templates/`, `static/`, `tests/`
    - Create `.gitignore` (exclude `.env`, `venv/`, `__pycache__/`)
    - _Requirements: Non-functional (Tech Stack)_

  - [x] 1.2 Set up Supabase database and create schema
    - Create Supabase project (free tier)
    - Create `users` table with email, password_hash, role, status, lockout fields
    - Create `site` table with latitude, longitude, radius_m
    - Create `punch_records` table with user_id FK, type, timestamp, coordinates, accuracy
    - Add index on `punch_records(user_id, server_timestamp DESC)`
    - Insert the salon's GPS coordinates into `site` table
    - Create initial Admin account (salon owner)
    - _Requirements: Data Model_

  - [x] 1.3 Create FastAPI app entry point with basic configuration
    - Set up FastAPI app with CORS middleware
    - Configure Jinja2 template rendering
    - Configure static file serving (CSS, JS)
    - Set up database connection pool (psycopg2 or asyncpg)
    - Load environment variables (DATABASE_URL, JWT_SECRET)
    - _Requirements: 10.1 (HTTPS handled by Railway)_

- [x] 2. Authentication
  - [x] 2.1 Implement password hashing and JWT utilities
    - `hash_password(plain)` → bcrypt hash
    - `verify_password(plain, hash)` → bool
    - `create_token(user_id, role)` → JWT string (12hr/4hr expiry based on role)
    - `verify_token(token)` → user payload or raise error
    - _Requirements: 4.2, 5.2, 10.2_

  - [x] 2.2 Implement login and logout routes
    - `POST /api/auth/login` — validate credentials, check lockout, issue JWT cookie
    - `POST /api/auth/logout` — clear JWT cookie
    - Account lockout: 5 failures/15min (associate), 3/10min (admin)
    - Generic error messages (don't reveal if email or password wrong)
    - _Requirements: 4.1–4.6, 5.1–5.4_

  - [x] 2.3 Implement auth middleware (dependency injection)
    - `get_current_user` dependency that reads JWT from cookie, validates, returns user
    - `require_admin` dependency that additionally checks role == 'admin'
    - Return 403 for unauthorized access
    - _Requirements: 6.1–6.4_

  - [x] 2.4 Create login page template
    - `templates/login.html` — email + password form, error message display
    - Mobile-first responsive styling with TailwindCSS
    - POST to `/api/auth/login`, redirect to home on success
    - _Requirements: 4.1, 5.1_

- [x] 3. Punch In / Punch Out
  - [x] 3.1 Implement Haversine distance calculation
    - `services/geo.py` — `haversine(lat1, lon1, lat2, lon2)` returns distance in metres
    - Pure Python using `math` module
    - _Requirements: 1.2, 2.2_

  - [x] 3.2 Implement punch API endpoints
    - `POST /api/punch/in` — receive {latitude, longitude, accuracy}, validate geofence, check no active session, insert record
    - `POST /api/punch/out` — receive {latitude, longitude, accuracy}, validate geofence, check active session exists, insert record
    - `GET /api/punch/status` — return current state (punched in or not, elapsed time)
    - Server-side Haversine validation is authoritative
    - Return clear error messages for each rejection scenario
    - _Requirements: 1.1–1.7, 2.1–2.6, 10.7_

  - [x] 3.3 Create Associate home page template
    - `templates/home.html` — large Punch In / Punch Out button
    - Show current status: "On duty since 9:03 AM (3h 22m)" or "Off duty"
    - JavaScript: call `navigator.geolocation.getCurrentPosition()`, send to API via `fetch()`
    - Display success/error messages inline
    - Mobile-first: big buttons, clear text, works on small screens
    - _Requirements: 9.4, Non-functional (Usability: ≤ 2 taps)_

  - [x] 3.4 Create attendance history page
    - `templates/history.html` — table/list of own punch records
    - Show: date, punch-in time, punch-out time, total hours
    - Default to current month; allow month selector
    - Active sessions show "In Progress"
    - "No records" message for empty months
    - _Requirements: 9.1–9.3, 9.5 (implied)_

  - [x]* 3.5 Write tests for Haversine and punch logic
    - Test Haversine with known coordinates (e.g., 5m apart, 100m apart)
    - Test punch-in accepted inside geofence
    - Test punch-in rejected outside geofence
    - Test duplicate punch-in rejected
    - Test punch-out without punch-in rejected
    - _Requirements: 1.2, 1.3, 1.7, 2.5_

- [x] 4. Admin Dashboard
  - [x] 4.1 Implement report aggregation queries
    - Today's attendance: who punched in, who didn't, who was late
    - Weekly summary: per-day counts (present/absent)
    - Per-user hours worked this week/month
    - Date range queries for historical data (up to 90 days)
    - _Requirements: 7.1–7.4_

  - [x] 4.2 Create admin dashboard page
    - `templates/admin/dashboard.html` — today's status cards + charts
    - Include Chart.js via CDN
    - Bar chart: daily attendance this week
    - Table: each associate's status today (present/absent, punch time, hours)
    - Calendar heatmap or simple grid for monthly overview
    - _Requirements: 7.1–7.5_

  - [x] 4.3 Create user management page
    - `templates/admin/users.html` — list of associates with status
    - Add new associate form (name, email, password)
    - Deactivate/reactivate toggle
    - _Requirements: 6.6 (implied admin user CRUD)_

  - [x] 4.4 Create geofence configuration page
    - `templates/admin/geofence.html` — current coordinates + radius display
    - Map preview using Leaflet.js + OpenStreetMap (free, no API key needed)
    - Edit form: latitude, longitude, radius slider (5–50m)
    - Show circle on map to visualize the geofence
    - _Requirements: 3.1–3.4_

  - [x] 4.5 Implement CSV export endpoint
    - `GET /api/reports/export?start=YYYY-MM-DD&end=YYYY-MM-DD`
    - Generate CSV with columns: name, date, punch-in, punch-out, total hours
    - Include generation timestamp as first row comment
    - Return as file download (`Content-Disposition: attachment`)
    - Return "No records" message if filter matches nothing
    - _Requirements: 8.1–8.4_

- [x] 5. Styling and polish
  - [x] 5.1 Apply TailwindCSS responsive styling to all pages
    - Install TailwindCSS (via CDN for simplicity, or build step)
    - Mobile-first: large touch targets, readable fonts, proper spacing
    - Desktop: side navigation for admin, wider tables
    - Consistent color scheme and branding
    - _Requirements: Non-functional (Usability, Compatibility)_

  - [x] 5.2 Add error handling and loading states
    - Loading spinner while GPS is being acquired
    - Clear error messages for all failure scenarios
    - Success confirmations (green toast/banner)
    - Handle network errors gracefully
    - _Requirements: 1.5, 1.6, 2.3, 2.6_

- [x] 6. Security and validation
  - [x] 6.1 Implement input validation on all endpoints
    - Validate email format, password length, coordinate ranges
    - Reject empty/whitespace-only required fields
    - Parameterized SQL queries (psycopg2 handles this)
    - Encode user text before rendering in templates (Jinja2 auto-escapes)
    - _Requirements: 10.3–10.5_

  - [x] 6.2 Implement server-side geofence validation
    - ALWAYS validate coordinates on the server even if client already checked
    - Compare GPS accuracy against radius — reject if accuracy is too poor
    - This prevents anyone from sending fake coordinates via browser dev tools
    - _Requirements: 10.7, 1.6, 2.6_

- [ ] 7. Deployment
  - [ ] 7.1 Deploy to Railway
    - Push code to GitHub
    - Connect repo to Railway
    - Set environment variables: DATABASE_URL, JWT_SECRET
    - Verify app starts and responds
    - _Requirements: Non-functional (Hosting Cost: $0)_

  - [ ] 7.2 Configure Supabase production database
    - Run schema SQL in Supabase SQL editor
    - Create initial admin account
    - Insert salon GPS coordinates
    - Test connection from Railway app
    - _Requirements: Data Model_

  - [ ] 7.3 Final testing on real phones
    - Have each salon associate open the URL on their phone
    - Test punch-in at the salon (should succeed)
    - Test punch-in away from salon (should fail)
    - Test admin dashboard on laptop
    - Test CSV export
    - _Requirements: All_

## Notes

- Tasks marked with `*` are optional tests — recommended but not blocking
- No Docker, no Redis, no Android Studio, no app store needed
- Total deployment cost: $0/month on free tiers
- The entire app can be built in Kiro without any external tooling besides Python and a browser
- For ongoing use: Railway free tier gives 500 hours/month — enough for a salon's working hours

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["1.3"] },
    { "id": 2, "tasks": ["2.1"] },
    { "id": 3, "tasks": ["2.2", "2.3"] },
    { "id": 4, "tasks": ["2.4", "3.1"] },
    { "id": 5, "tasks": ["3.2"] },
    { "id": 6, "tasks": ["3.3", "3.4", "3.5"] },
    { "id": 7, "tasks": ["4.1"] },
    { "id": 8, "tasks": ["4.2", "4.3", "4.4"] },
    { "id": 9, "tasks": ["4.5"] },
    { "id": 10, "tasks": ["5.1", "5.2"] },
    { "id": 11, "tasks": ["6.1", "6.2"] },
    { "id": 12, "tasks": ["7.1", "7.2"] },
    { "id": 13, "tasks": ["7.3"] }
  ]
}
```
