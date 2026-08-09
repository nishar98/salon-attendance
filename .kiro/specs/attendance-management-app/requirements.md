# Requirements Document

*Geo-Fenced Punch In / Punch Out • Role-Based Access • Analytics & Reporting*

- **Prepared for:** Salon Business (6 active members)
- **Version:** 2.0
- **Date:** August 3, 2026
- **Platform:** Responsive Web Application (PWA-ready, mobile-first)
- **Target Users:** Small salon business with 6 employees, single location

---

## Introduction

This document defines the requirements for a lightweight Attendance Management Web Application for a salon with 6 active members. The system replaces manual attendance tracking with a geo-verified digital punch-in/punch-out mechanism accessible via any mobile browser, with a role-based admin dashboard for reporting and analytics.

**Core problem:** The salon owner needs to verify that staff are physically at the salon when they mark attendance. Manual registers are unreliable and don't provide analytics.

**Proposed solution:** A responsive website where each associate logs in via their phone browser and can only punch in/out when their GPS location is within a configurable radius (default 5 metres) of the salon. The owner/admin accesses the same website on a laptop or phone to view attendance data, charts, and exports. No app store needed — associates simply bookmark the URL.

### Market Context

- Geo-fencing via the browser Geolocation API is supported on all modern mobile browsers (Chrome, Firefox, Samsung Internet).
- A Progressive Web App (PWA) can be "installed" to the home screen and feels native.
- For 6 users, a cloud-hosted free tier (Supabase + Railway/Render) provides more than enough capacity.
- Push notifications work on Android browsers via the Web Push API.

### Objectives

1. Verify salon staff are physically present when marking attendance (GPS geo-fence).
2. Provide each associate a personal, secure login.
3. Give the salon owner a visual dashboard showing attendance patterns.
4. Keep the application lightweight, cheap to run ($0/month on free tiers), and easy to maintain.
5. Build as a responsive web app — no app store, no Android Studio needed.

---

## Glossary

- **App**: The Attendance Management Web Application
- **Associate**: A salon employee who uses the App to record attendance
- **Admin**: The salon owner/manager with elevated privileges
- **Punch_In / Punch_Out**: Recording the start/end of a work session
- **Geo_Fence**: A virtual boundary (center coordinate + radius) around the salon
- **Geo_Tag**: GPS coordinates + timestamp captured at the moment of a punch action
- **Auth_Service**: Authentication and authorization subsystem (Supabase Auth)
- **Session_Token**: JWT token granting time-limited access

## Scope

### In Scope (MVP)

- Responsive web app accessible on mobile (Chrome/Android) and desktop browsers.
- Associate view: login, geo-verified punch in/out, view own attendance history.
- Admin view: user management, geofence configuration, attendance dashboard with charts, CSV export.
- Geo-fencing via browser Geolocation API with server-side Haversine validation.
- Role-based access (Admin + Associate).
- Basic security: HTTPS, password hashing, session management.

### Out of Scope (MVP)

- Native mobile app / Play Store distribution.
- Push notifications (use WhatsApp/SMS reminders manually for now).
- Biometric/selfie liveness check.
- Leave management, shift scheduling.
- Offline punch queuing (requires internet connection).
- Multi-tenant / multiple salon support (build for one salon first).

### Assumptions

- Salon has one fixed location with a known GPS coordinate.
- All 6 associates have Android smartphones with Chrome browser and data connectivity.
- Salon has stable Wi-Fi (assists with GPS accuracy indoors).
- The admin (salon owner) is comfortable using a web browser.

---

## User Roles

| **Role** | **Access** |
|----------|-----------|
| Admin (Salon Owner) | Full control: manage geofence, manage users, view all attendance, reports, exports |
| Associate (Staff) | Punch in/out for self only, view own attendance history |

---

## Requirements

### Requirement 1: Geo-Fenced Punch-In

**User Story:** As an Associate, I want to punch in via my phone browser, so that my attendance is recorded and verified by my location at the salon.

#### Acceptance Criteria

1. WHEN an Associate taps the Punch In button, THE App SHALL request GPS coordinates from the browser Geolocation API.
2. WHEN the browser returns coordinates within the configured Geo_Fence (≤ radius from the salon center), THE App SHALL record the Punch_In with the Geo_Tag.
3. WHEN the browser returns coordinates outside the Geo_Fence, THE App SHALL reject the Punch_In and display a message showing approximate distance from the salon.
4. THE App SHALL store latitude, longitude, server timestamp, and GPS accuracy for every successful Punch_In.
5. IF the browser denies location permission or the Geolocation API fails, THEN THE App SHALL reject the Punch_In and instruct the Associate to enable location services.
6. IF the GPS accuracy reported is worse than the Geo_Fence radius, THEN THE App SHALL prompt the Associate to move near a window or outside for better signal.
7. IF the Associate already has an active Punch_In with no Punch_Out, THEN THE App SHALL reject the new Punch_In.

### Requirement 2: Geo-Fenced Punch-Out

**User Story:** As an Associate, I want to punch out via my phone browser to end my work session.

#### Acceptance Criteria

1. WHEN an Associate taps Punch Out, THE App SHALL request GPS coordinates from the browser.
2. WHEN coordinates are within the Geo_Fence, THE App SHALL record the Punch_Out.
3. WHEN coordinates are outside the Geo_Fence, THE App SHALL reject the Punch_Out with a distance message.
4. THE App SHALL store the Geo_Tag for every successful Punch_Out.
5. IF no active Punch_In exists, THEN THE App SHALL reject the Punch_Out.
6. IF GPS accuracy is worse than the Geo_Fence radius, THE App SHALL prompt the Associate to improve signal.

### Requirement 3: Geo-Fence Configuration

**User Story:** As the Admin, I want to set the salon's GPS coordinates and radius so that punch validation works correctly.

#### Acceptance Criteria

1. THE App SHALL allow the Admin to set the salon's center latitude, longitude, and radius (default 5 metres, adjustable between 5 and 50 metres).
2. THE App SHALL validate that coordinates are within valid ranges.
3. THE App SHALL display a map preview showing the geofence circle before saving.
4. Changes SHALL apply immediately to subsequent punch validations.

### Requirement 4: Associate Authentication

**User Story:** As an Associate, I want to log in with my own credentials so that only I can record my attendance.

#### Acceptance Criteria

1. Each Associate SHALL have a unique email and password.
2. WHEN valid credentials are submitted, a session SHALL be created (valid for up to 12 hours).
3. WHEN invalid credentials are submitted, THE App SHALL display a generic error.
4. IF 5 consecutive failed logins occur within 15 minutes, THE account SHALL be locked for 30 minutes.
5. Passwords SHALL be minimum 8 characters.
6. THE App SHALL use HTTPS for all communication.

### Requirement 5: Admin Authentication

**User Story:** As the Admin, I want a separate elevated login to manage the salon's attendance system.

#### Acceptance Criteria

1. THE Admin SHALL log in with email and password (minimum 10 characters).
2. Admin session SHALL expire after 4 hours.
3. Admin login uses the same web interface but reveals admin-only navigation after authentication.
4. IF 3 consecutive failed logins occur, THE account SHALL be locked for 60 minutes.

### Requirement 6: Role-Based Access Control

**User Story:** As the salon owner, I want associates to only see their own data while I can see everything.

#### Acceptance Criteria

1. Associates can ONLY: punch in/out, view own history.
2. Admin can: manage users, configure geofence, view all attendance, view reports, export data.
3. IF an Associate attempts to access admin functions, THE App SHALL deny with a 403 error.
4. RBAC SHALL be enforced on the server side (API level), not just hidden in the UI.

### Requirement 7: Attendance Dashboard

**User Story:** As the Admin, I want a visual dashboard showing today's attendance and trends.

#### Acceptance Criteria

1. THE dashboard SHALL show today's summary: who is present, who is absent, who arrived late.
2. THE dashboard SHALL show a weekly attendance chart (bar chart: present vs absent per day).
3. THE dashboard SHALL show each associate's hours worked this week.
4. THE Admin SHALL be able to select a date range (up to 90 days) to view historical data.
5. THE dashboard SHALL display a per-user calendar view (present/absent/late color coding).

### Requirement 8: Report Export

**User Story:** As the Admin, I want to export attendance data to CSV for salary calculations.

#### Acceptance Criteria

1. THE App SHALL allow CSV export with columns: name, date, punch-in time, punch-out time, total hours.
2. THE export SHALL include a date range filter.
3. THE export SHALL include a generation timestamp.
4. IF no records match the filter, THE App SHALL inform the Admin rather than generating an empty file.

### Requirement 9: Associate Attendance View

**User Story:** As an Associate, I want to see my own attendance history.

#### Acceptance Criteria

1. THE App SHALL display the Associate's attendance for the current month by default.
2. Each record SHALL show: date, punch-in time, punch-out time, total hours.
3. Active sessions SHALL show "In Progress."
4. The home screen SHALL show current status (on-duty / off-duty) with elapsed time.

### Requirement 10: Security

**User Story:** As the salon owner, I want the system to be secure and data protected.

#### Acceptance Criteria

1. All communication SHALL use HTTPS (TLS).
2. Passwords SHALL be hashed (bcrypt) — never stored in plaintext.
3. API endpoints SHALL validate all inputs: reject empty fields, invalid formats, oversized payloads.
4. THE App SHALL use parameterized queries to prevent SQL injection.
5. THE App SHALL encode user-provided text before rendering (XSS prevention).
6. Session tokens SHALL expire (12 hours for associates, 4 hours for admin).
7. Server-side geofence validation is authoritative — client-side check is UX only.

### Requirement 11: Data Privacy

**User Story:** As the salon owner, I want to handle employee location data responsibly.

#### Acceptance Criteria

1. GPS coordinates SHALL be captured ONLY at punch time — no background tracking.
2. Location permission SHALL be requested with a clear explanation.
3. Only the Admin can see GPS coordinates; Associates see only "Location verified ✓."
4. Attendance records SHALL be retained for 12 months, then auto-deleted.

---

## Non-Functional Requirements

| **Category** | **Requirement** |
|---|---|
| Performance | Punch action ≤ 5 seconds (including GPS lock) |
| Usability | Punch flow completable in ≤ 2 taps; mobile-first responsive design |
| Compatibility | Chrome (Android), Firefox, Edge; responsive on mobile + desktop |
| Hosting Cost | $0/month using free tiers (Supabase + Railway/Render/Vercel) |
| Scalability | Supports up to 50 users without changes (room to sell to other salons) |
| Availability | Cloud-hosted, no self-managed infrastructure |

---

## High-Level Data Model

| **Entity** | **Key Fields** |
|---|---|
| User | id, name, email, password_hash, role (admin/associate), status (active/inactive) |
| Site (Geo_Fence) | id, name, latitude, longitude, radius_m |
| PunchRecord | id, user_id, type (in/out), server_timestamp, latitude, longitude, gps_accuracy |

---

## Technical Stack

| Layer | Technology | Cost |
|---|---|---|
| Backend API | **Python + FastAPI** | Free |
| Frontend | **HTML + TailwindCSS + JavaScript** (served by FastAPI or as static files) | Free |
| Database | **Supabase** (hosted PostgreSQL + Auth) | Free tier |
| Hosting | **Railway** or **Render** | Free tier |
| GPS | Browser **Geolocation API** | Free |
| Charts | **Chart.js** (JavaScript library) | Free |
| **Total** | | **$0/month** |

---

## Success Metrics

| **Metric** | **Target** |
|---|---|
| Punch action time | ≤ 5 seconds |
| False geo-rejection rate | < 5% (after radius calibration) |
| Monthly hosting cost | $0 |
| Time to generate monthly report | ≤ 1 minute |
