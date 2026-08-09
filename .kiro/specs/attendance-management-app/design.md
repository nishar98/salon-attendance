# Design Document

## Overview

A lightweight responsive web application for salon attendance management. 6 staff punch in/out via their phone browser with GPS verification. The salon owner views attendance dashboards and exports data. Everything runs on free-tier cloud services.

**Tech Stack:**
- **Backend:** Python 3.11+ with FastAPI
- **Frontend:** HTML + TailwindCSS + vanilla JavaScript (Jinja2 templates served by FastAPI)
- **Database:** Supabase (hosted PostgreSQL, free tier)
- **Hosting:** Railway or Render (free tier)
- **Charts:** Chart.js
- **GPS:** Browser Geolocation API

**Key Design Decisions:**

| Decision | Rationale |
|----------|-----------|
| Python + FastAPI | Beginner-friendly, auto-generates API docs, fast enough for 6 users |
| Single web app (no mobile app) | No app store needed, one codebase, works on any phone browser |
| Supabase (hosted Postgres) | Free tier, zero database administration, built-in auth available |
| Server-side Haversine validation | Browser GPS can't be fully trusted; server is authoritative |
| Jinja2 templates (server-rendered) | Simpler than a separate SPA; one deployment, no CORS issues |
| Chart.js | Lightweight, well-documented charting library for browser |
| No Redis | 6 users don't need rate limiting or external session cache |
| No Docker | Everything runs in cloud; local dev needs only Python + Node (for Tailwind) |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Associate's Phone (Chrome browser)             │
│  ┌───────────────────────────────────────────┐  │
│  │  Responsive Web App (HTML + JS)           │  │
│  │  - Punch In/Out button                    │  │
│  │  - Browser Geolocation API for GPS        │  │
│  │  - Attendance history view                │  │
│  └──────────────────┬────────────────────────┘  │
└─────────────────────┼───────────────────────────┘
                      │ HTTPS
                      ▼
┌─────────────────────────────────────────────────┐
│  Railway / Render (Free Tier)                   │
│  ┌───────────────────────────────────────────┐  │
│  │  Python FastAPI Server                    │  │
│  │  - Serves HTML pages (Jinja2 templates)   │  │
│  │  - REST API endpoints (/api/punch, etc.)  │  │
│  │  - Haversine geo-validation               │  │
│  │  - Auth (JWT sessions)                    │  │
│  │  - CSV export generation                  │  │
│  └──────────────────┬────────────────────────┘  │
└─────────────────────┼───────────────────────────┘
                      │ SQL (connection pooling)
                      ▼
┌─────────────────────────────────────────────────┐
│  Supabase (Free Tier)                           │
│  ┌───────────────────────────────────────────┐  │
│  │  PostgreSQL Database                      │  │
│  │  - users, punch_records, site tables      │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### No Admin Console Needed Separately

The admin and associate views are the **same web app** — the UI adapts based on the logged-in user's role:
- Associate sees: punch button + own history
- Admin sees: dashboard + user management + geofence config + reports + export

---

## Components and Interfaces

### FastAPI Application Structure

```
attendance-app/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (DB URL, JWT secret)
├── models/
│   ├── user.py            # User model + DB operations
│   ├── punch.py           # PunchRecord model + DB operations
│   └── site.py            # Site/Geofence model
├── routes/
│   ├── auth.py            # Login, logout, session management
│   ├── punch.py           # Punch in/out endpoints
│   ├── admin.py           # User management, geofence, reports
│   └── pages.py           # Serves HTML pages (Jinja2)
├── services/
│   ├── geo.py             # Haversine distance calculation
│   ├── auth.py            # Password hashing, JWT creation/validation
│   └── reports.py         # Aggregation queries, CSV generation
├── templates/
│   ├── base.html          # Base layout (TailwindCSS)
│   ├── login.html         # Login page
│   ├── home.html          # Associate home (punch button + status)
│   ├── history.html       # Attendance history
│   ├── admin/
│   │   ├── dashboard.html # Dashboard with charts
│   │   ├── users.html     # User management
│   │   ├── geofence.html  # Geofence config with map
│   │   └── reports.html   # Reports + export
│   └── components/
│       ├── navbar.html    # Navigation bar
│       └── chart.html     # Chart.js snippets
├── static/
│   ├── css/style.css      # Compiled TailwindCSS
│   └── js/
│       ├── punch.js       # GPS + punch logic
│       ├── charts.js      # Chart.js initialization
│       └── geofence.js    # Map preview logic
└── tests/
    ├── test_geo.py        # Haversine tests
    ├── test_auth.py       # Auth tests
    └── test_punch.py      # Punch flow tests
```

### Auth Service
- Password hashing with `bcrypt` (via `passlib`)
- JWT tokens (via `python-jose`) — stored in httpOnly cookie
- Session duration: 12 hours (associate), 4 hours (admin)
- Account lockout: 5 failures / 15 min (associate), 3 failures / 10 min (admin)
- No separate session store needed — JWT is stateless, validated on each request

### Punch Service
- Receives GPS coordinates from browser via `fetch()` POST request
- Server-side Haversine distance calculation
- Checks for active session (no duplicate punch-in)
- Writes to `punch_records` table
- Returns success/failure JSON to the browser

### Geofence Service
- Single salon location stored in `site` table
- Admin can update coordinates and radius
- Haversine validation on every punch request

### Report Service
- SQL aggregation queries (GROUP BY date, user)
- Returns JSON data for Chart.js to render
- CSV export via Python's `csv` module + `StreamingResponse`

### Frontend (Jinja2 + JavaScript)
- Server-rendered HTML pages (fast, no SPA complexity)
- TailwindCSS for mobile-first responsive styling
- Vanilla JavaScript for:
  - Calling browser Geolocation API
  - Sending punch requests via `fetch()`
  - Rendering charts with Chart.js
  - Map preview (Leaflet.js with OpenStreetMap — free)

---

## Data Models

### `users`

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen_random_uuid() |
| name | VARCHAR(100) | NOT NULL |
| email | VARCHAR(255) | NOT NULL, UNIQUE |
| password_hash | VARCHAR(255) | NOT NULL |
| role | VARCHAR(20) | NOT NULL, CHECK('admin','associate'), default 'associate' |
| status | VARCHAR(20) | NOT NULL, CHECK('active','locked','inactive'), default 'active' |
| failed_login_attempts | INT | default 0 |
| locked_until | TIMESTAMPTZ | nullable |
| created_at | TIMESTAMPTZ | NOT NULL, default NOW() |

### `site`

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(100) | NOT NULL, default 'Salon' |
| latitude | DECIMAL(10,7) | NOT NULL |
| longitude | DECIMAL(10,7) | NOT NULL |
| radius_m | INT | NOT NULL, default 5, CHECK(5 to 50) |
| updated_at | TIMESTAMPTZ | NOT NULL |

Only one row expected (single salon). Could support multiple sites later.

### `punch_records`

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users.id, NOT NULL |
| type | VARCHAR(3) | NOT NULL, CHECK('in','out') |
| server_timestamp | TIMESTAMPTZ | NOT NULL, default NOW() |
| latitude | DECIMAL(10,7) | NOT NULL |
| longitude | DECIMAL(10,7) | NOT NULL |
| gps_accuracy_m | DECIMAL(6,2) | NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL |

Index: `(user_id, server_timestamp DESC)` for fast history lookup.

---

## Correctness Properties

### Property 1: Punch Session Integrity

**Validates: Requirements 1.7, 2.5**

A user can never have two active punch-in records without an intervening punch-out. Before accepting a punch-in, the server queries for the user's latest punch record — if it's type='in', the new punch-in is rejected.

### Property 2: Geofence Distance Accuracy

**Validates: Requirements 1.2, 1.3, 2.2, 2.3**

The Haversine formula is used server-side:
```python
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6_371_000  # Earth radius in metres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
```

A punch is accepted if and only if `haversine(punch_coords, site_coords) ≤ site.radius_m`.

### Property 3: Server Authority

**Validates: Requirements 10.7**

The browser-side GPS check provides instant feedback, but the server re-validates the coordinates independently. If the client sends fake coordinates, the server Haversine check rejects them.

---

## Error Handling

| Scenario | Response | User Sees |
|----------|----------|-----------|
| Outside geofence | 422 | "You are ~X metres from the salon. Move closer." |
| GPS unavailable | 400 | "Enable location services in your browser settings." |
| GPS accuracy poor | 422 | "GPS signal weak. Move near a window or outside." |
| Duplicate punch-in | 409 | "You're already punched in." |
| Punch-out without punch-in | 409 | "No active session. Punch in first." |
| Invalid credentials | 401 | "Invalid email or password." |
| Account locked | 403 | "Account locked. Try again in X minutes." |
| Unauthorized access | 403 | Redirect to login |

---

## Testing Strategy

### Manual Testing (Primary — you're 6 people)
- Open the site on your phone, try punching in at the salon → should work
- Walk 20 metres away, try punching in → should fail with distance
- Try logging in with wrong password 5 times → should lock
- Check the admin dashboard → should show today's data

### Automated Tests (Run with `pytest`)
- **test_geo.py:** Haversine with known coordinates (0m, 5m, 6m boundary)
- **test_auth.py:** Password validation, lockout counter, JWT creation
- **test_punch.py:** Punch-in succeeds inside geofence, fails outside, rejects duplicates

### Running Tests
```bash
pip install pytest httpx
pytest tests/ -v
```

---

## Deployment

### Local Development
```bash
# One-time setup
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000

# Open in browser
# http://localhost:8000
```

### Production (Railway — recommended for beginners)

1. Push code to GitHub
2. Sign up at railway.app (free tier: 500 hours/month — plenty)
3. Connect your GitHub repo
4. Set environment variables (DATABASE_URL, JWT_SECRET)
5. Railway auto-deploys on every `git push`

**That's it.** No Docker, no server management, no SSH.

### Database (Supabase)

1. Sign up at supabase.com (free tier: 500MB storage, unlimited API requests)
2. Create a new project → get the connection string
3. Run your SQL schema via the Supabase SQL editor
4. Put the connection string in your Railway environment variables

### Custom Domain (Optional, ~$10/year)

Buy a domain (e.g., `salon-attendance.com`) from Namecheap or Google Domains, point it to your Railway app. Associates access `https://salon-attendance.com` on their phone.

---

## Cost Summary

| Item | Monthly Cost |
|------|-------------|
| Railway (hosting) | $0 (free tier: 500 hrs/month) |
| Supabase (database) | $0 (free tier: 500MB, 50K rows) |
| Domain name (optional) | ~$1/month ($10/year) |
| **Total** | **$0–$1/month** |
