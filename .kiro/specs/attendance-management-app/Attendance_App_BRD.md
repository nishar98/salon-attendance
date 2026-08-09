# Attendance Management Application

### Business Requirements Document

*Geo-Fenced Punch In / Punch Out • Role-Based Access • Analytics & Reporting*

- **Prepared for:** Small Business Deployment
- **Document Type:** Requirements & Solution Blueprint
- **Version:** 1.0
- **Date:** July 30, 2026
- **Status:** CONFIDENTIAL — INTERNAL USE

---

## Document Control

| **Field**      | **Detail**                                                          |
|----------------|---------------------------------------------------------------------|
| Document Title | Attendance Management Application — Business Requirements Document  |
| Version        | 1.0 (Draft for Review)                                              |
| Prepared Date  | July 30, 2026                                                       |
| Target Users   | Small business (assumed 15–150 employees, single or multi-location) |
| Platforms      | Android & iOS mobile app (employee) + Web-based Admin Console       |
| Status         | Draft — pending stakeholder sign-off                                |

## Revision History

| **Version** | **Date**    | **Author** | **Description**                                            |
|-------------|-------------|------------|------------------------------------------------------------|
| 0.1         | 30-Jul-2026 | Product/BA | Initial draft based on market research and stakeholder ask |
| 1.0         | 30-Jul-2026 | Product/BA | First complete version circulated for review               |

---

## 1. Executive Summary

This document defines the business and functional requirements for a mobile-first Attendance Management Application built for a small business. The system replaces manual registers, physical biometric machines, or unverified self-reported attendance with a geo-verified digital punch in / punch out mechanism, role-based access for associates and administrators, and a reporting module with visual analytics.

**Core problem being solved:** Small businesses with field staff, retail outlets, or distributed teams struggle to confirm that employees are physically present at the assigned worksite when they clock in. Manual and biometric-only systems are prone to “buddy punching,” proxy attendance, and reconciliation errors at payroll time.

**Proposed solution:** A mobile app where each associate logs in with an individual account, and can only punch in or punch out when their device-reported GPS location is within a 5-metre radius of a pre-configured worksite geofence. All punches are timestamped, geo-tagged, and synced to a central system. Admins get a separate web console for configuring locations, managing associates, and viewing attendance analytics.

### 1.1 Market Context (Research Summary)

Competitor and category research (Buddy Punch, Jibble, Truein, Connecteam, QuickBooks Time, Timeero, and India-focused platforms such as greytHR/Truein-style HRMS tools) confirms the following as now-standard expectations for this category:

- Geofencing is drawn around one or more worksites; punches outside the boundary are **blocked**, not just flagged.

- Anti-“buddy punching” controls are common: selfie-on-punch, face match, device binding, or PIN/kiosk mode for shared devices.

- Consumer GPS accuracy is realistically **5–20 metres outdoors and worse indoors/urban canyons** — leading vendors combine GPS with Wi-Fi/cell-tower assist and allow admins to set a per-site radius rather than promising pinpoint precision. This is a critical technical constraint addressed in Section 9.

- Reporting is expected to include dashboards/graphs (attendance %, late arrivals, overtime, absenteeism trends) not just flat exportable tables.

- Small businesses prefer low/no per-seat pricing at low headcounts and simple self-serve setup over enterprise HRMS complexity.

- Data privacy expectations have risen: location and biometric data are treated as sensitive personal data requiring explicit consent, minimal retention, and encryption — governed in India by the Digital Personal Data Protection (DPDP) Act, 2023, and by GDPR-equivalent principles if any EU-based staff/clients are involved.

### 1.2 Objectives

1.  Eliminate proxy/buddy-punching attendance fraud through mandatory location verification.

2.  Give every associate a personal, secure login separate from the admin console.

3.  Give admins/HR a real-time, graphical view of attendance, lateness, and absenteeism per user and per team.

4.  Meet baseline cybersecurity and data-privacy expectations for an app handling location and personal employment data.

5.  Be deployable and usable by a small business without a dedicated IT department.

## 2. Scope

### 2.1 In Scope

- Associate (employee) mobile app: registration/login, punch in/out with geo-verification, view own attendance history, request corrections, receive notifications.

- Admin web console: associate management, worksite/geofence configuration, live attendance dashboard, reporting & graphs, approvals, exports, security/audit settings.

- Geofencing engine with configurable radius (default 5 metres, adjustable per site — see Section 9 for why this must be admin-tunable).

- Reporting module with per-user and aggregate graphs, filters, and export (PDF/Excel).

- Authentication, authorization, and core cybersecurity controls (Section 10).

- Push/SMS/email notifications for punch confirmation, missed punch, late arrival, and admin alerts.

### 2.2 Out of Scope (Phase 1)

- Full payroll processing and salary disbursement (integration hooks only).

- Biometric hardware integration (fingerprint/face scanners) — selfie-based liveness check is optional Phase 2.

- Leave management, shift scheduling, and expense management as full modules (data model will reserve space for these; UI comes later, noted in the roadmap).

- Offline-first multi-day punch queuing beyond basic short-duration offline buffering.

### 2.3 Assumptions

- Business has one or more fixed worksites with known GPS coordinates (office, store, warehouse, client site).

- Associates carry a personal or company Android/iOS smartphone with GPS and mobile data/Wi-Fi.

- Business is comfortable with employees granting location permission during work hours; this will be governed by a consent and privacy policy (Section 11).

- Initial headcount is in the small-business range (~15–150 users); architecture should not block later scaling.

## 3. Stakeholders & User Roles

### 3.1 Stakeholders

| **Stakeholder**                              | **Interest**                                                                 |
|----------------------------------------------|------------------------------------------------------------------------------|
| Business Owner / Management                  | Accurate attendance data, cost control, compliance, low overhead to run      |
| HR / Admin                                   | Day-to-day configuration, approvals, report generation, associate onboarding |
| Associates (Employees)                       | Simple, fast, fair way to mark attendance; transparency on their own records |
| IT / App Support (internal or vendor)        | Security, uptime, data protection, ease of maintenance                       |
| Payroll processor (person or 3rd-party tool) | Clean, exportable attendance data mapped to pay periods                      |

### 3.2 User Roles

The system requires strict separation between the Associate role and the Admin role — different logins, different apps/interfaces, and different permission sets. A third role, Manager/Supervisor, is recommended so mid-sized teams don’t bottleneck everything through one Admin account.

| **Role**                           | **Access**                                                                                                                              |
|------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| Super Admin                        | Full control: create/edit worksites & geofences, manage all users, security settings, all reports, billing/subscription (if applicable) |
| Manager / Supervisor (recommended) | View & approve attendance for their assigned team only, request corrections on behalf of team, team-level reports                       |
| Associate (Employee)               | Punch in/out for self only, view own history, raise correction requests, receive personal notifications                                 |

## 4. Functional Requirements

### 4.1 Authentication & Account Management

| **ID** | **Requirement**                                                                                                                                                                        |
|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| FR-1.1 | Every associate has an individual account (mobile number/employee ID/email + password, or OTP-based login) — no shared credentials.                                                    |
| FR-1.2 | Admin/Manager access is a fully separate login flow (recommended: separate web console + separate role token), not just a toggle inside the same app.                                  |
| FR-1.3 | Passwords/OTPs meet minimum complexity; support optional biometric app-unlock (device-level fingerprint/Face ID) as a convenience layer, not a replacement for account authentication. |
| FR-1.4 | Multi-Factor Authentication (MFA) mandatory for Admin/Super Admin accounts; optional but encouraged for Associates.                                                                    |
| FR-1.5 | Forgot-password / account recovery flow with rate limiting and audit logging.                                                                                                          |
| FR-1.6 | Session auto-logout after configurable inactivity period; forced re-login after password change.                                                                                       |
| FR-1.7 | Admin can deactivate/offboard an associate instantly, revoking all active sessions and app access.                                                                                     |

### 4.2 Punch In / Punch Out with Geo-Verification

| **ID** | **Requirement**                                                                                                                                                                                                                |
|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| FR-2.1 | Associate can punch IN only when device GPS location is within the configured radius (default 5 m, admin-adjustable per site — see Section 9) of that site's registered coordinates.                                           |
| FR-2.2 | Same location check applies to punch OUT; punch-out location is recorded independently (may differ slightly from punch-in point but must still be within the geofence).                                                        |
| FR-2.3 | If outside the geofence, the app blocks the action, shows the distance the user is from the boundary, and logs the failed attempt (for admin visibility into repeated failed attempts).                                        |
| FR-2.4 | Each punch record stores: user ID, timestamp (server time, not device time), latitude/longitude, GPS accuracy radius reported by the device, site ID, and device ID.                                                           |
| FR-2.5 | Support multiple registered worksites; associate can be assigned to one or more sites and the app checks against all assigned sites.                                                                                           |
| FR-2.6 | Optional Phase-1.5 add-on: selfie capture at punch (liveness check) to further curb proxy punching — flagged as a strong option given market practice (Section 1.1).                                                           |
| FR-2.7 | Mock-location / GPS-spoofing detection: app detects and blocks punches from devices with developer “mock location” enabled or known spoofing apps, and flags such attempts to admin.                                           |
| FR-2.8 | Graceful short offline handling: if connectivity drops at the exact moment of punch but GPS lock was already acquired within range, the app queues the punch locally and syncs when connectivity returns, clearly timestamped. |
| FR-2.9 | Admin can manually correct/approve a punch (e.g., GPS drift edge case) with a mandatory reason logged in the audit trail — manual overrides are never silent.                                                                  |

### 4.3 Associate (Employee) App Features

- Home screen with one-tap Punch In / Punch Out button and live status (on-duty/off-duty, elapsed time).

- Personal attendance calendar/history with punch times, hours worked per day, and status tags (Present, Late, Half-day, Absent, On Leave, Holiday).

- Push notification reminders for punch-in/out and missed punch alerts.

- Self-service correction request (e.g., “forgot to punch out”) routed to Manager/Admin for approval, with justification field.

- Profile screen: view assigned site(s), shift timing, and download/view own monthly report.

- In-app notice/consent screen explaining what location data is collected, when, and why (see Section 11).

### 4.4 Admin / Manager Web Console

- Dashboard: today’s attendance snapshot — present/absent/late counts, live map view of who has punched in and where.

- Associate management: add/edit/deactivate users, assign to site(s) and shift(s), bulk import via CSV/Excel.

- Worksite/Geofence management: add a site by address search or drop-a-pin, set radius (default 5 m, override per site), preview geofence on map before saving.

- Approval queue: correction requests, manual punch overrides, leave/absence marking.

- Reporting module (detailed in Section 5).

- Security & audit settings: view login history, failed punch attempts, spoofing flags, and full audit log (Section 10).

- Role & permission management for Manager-level accounts.

- Notification/broadcast: send announcements to all or selected associates.

## 5. Reporting & Analytics Module

This module is a first-class requirement, not an afterthought — it is the primary reason Admin/Management will use the system day-to-day beyond initial setup.

### 5.1 Report Types

| **Report**                               | **Description**                                                                                                 |
|------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| Individual (user-wise) attendance report | Per associate: daily punch log, hours worked, late/early counts, absences, trend graph over selected date range |
| Team / Site-wise summary                 | Aggregate attendance % , headcount present vs assigned, by site or by manager’s team                            |
| Late arrival & early departure report    | Ranked list with frequency and average delay, graphed over time                                                 |
| Absenteeism trend report                 | Absences over weeks/months, with day-of-week pattern chart                                                      |
| Overtime / extra-hours report            | Hours beyond shift threshold, per user and aggregate                                                            |
| Geo-exception report                     | Failed punch attempts outside geofence, spoofing flags, manual overrides — for governance/audit                 |
| Payroll-ready export                     | Attendance mapped to configurable pay period, exportable to Excel/CSV/PDF for payroll processing                |

### 5.2 Graphs & Visualizations (User-wise and Aggregate)

- Per-user attendance calendar heatmap (present/late/absent by day).

- Per-user trend line: hours worked per day/week over a selected period.

- Bar chart: on-time vs late vs absent count, selectable per user, per team, or company-wide.

- Pie/donut chart: attendance status breakdown for a selected period.

- Comparative bar chart: team/site-wise attendance % ranking.

- Drill-down: click a bar/user in an aggregate graph to open that user’s detailed report.

### 5.3 Reporting Requirements

- Filters: date range, associate, team, site, status, shift.

- Export to PDF and Excel; scheduled email reports (e.g., weekly summary to Admin every Monday).

- Role-based visibility: Managers see only their team’s data; Associates see only their own.

- Report generation must not expose raw GPS coordinates to Managers/Associates — only site name and status (data-minimization principle, Section 11).

## 6. Non-Functional Requirements

| **Category**         | **Requirement**                                                                                                                                 |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| Performance          | Punch action (GPS lock + validation + server ack) completes in ≤ 5 seconds under normal network conditions                                      |
| Availability         | Target 99.5% uptime for backend/API; graceful offline punch queuing on the mobile app                                                           |
| Scalability          | Architecture supports growth from ~15 to 500+ users without redesign (multi-tenant-ready data model)                                            |
| Usability            | Punch flow completable in ≤ 2 taps; no training required for associate app                                                                      |
| Compatibility        | Android 9+ and iOS 14+ (adjust to current OS baselines at build time); responsive admin web console                                             |
| Battery/Resource use | Location is read on-demand at punch time, not via continuous background tracking, to limit battery drain and privacy exposure (see Section 9.3) |
| Localization         | Support for regional language(s) and date/time formats used by the business                                                                     |
| Auditability         | Every state-changing action (punch, override, user edit, permission change) is logged, immutable, and attributable to a user and timestamp      |
| Maintainability      | Modular architecture so leave/payroll/shift modules can be added in later phases without re-architecture                                        |

## 7. High-Level Data Model

Illustrative core entities (final schema to be defined at design stage):

- **User** — id, name, employee code, role (Associate/Manager/Admin), contact, credential reference, assigned site(s), shift, status (active/inactive)

- **Site (Geofence)** — id, name, address, latitude, longitude, radius (metres), active hours, assigned manager

- **PunchRecord** — id, user id, site id, type (IN/OUT), server timestamp, device timestamp, lat/long, GPS accuracy, device id, status (valid/blocked/overridden), override reason (if any)

- **CorrectionRequest** — id, punch record ref, user id, reason, status (pending/approved/rejected), approver id

- **AuditLog** — id, actor, action, entity affected, before/after values, timestamp, IP/device

- **Notification** — id, recipient, type, channel (push/SMS/email), status

## 8. Suggested System Architecture & Technology Stack

A conventional 3-tier architecture is sufficient for a small-business deployment; below is an illustrative, not prescriptive, stack — final choice should match the team’s existing skills and budget.

### 8.1 Architecture Overview

- Mobile app (Associate) — native or cross-platform (e.g., Flutter/React Native) communicating over HTTPS/TLS with backend APIs.

- Admin web console — responsive web app for Admin/Manager roles, separate authentication flow from the associate app.

- Backend API layer — REST/GraphQL services handling auth, punch validation, geofence calculation, reporting queries.

- Database — relational database (e.g., PostgreSQL/MySQL) for transactional data; encrypted at rest.

- Geofencing/geo-validation service — server-side distance calculation (Haversine/Vincenty formula) as the source of truth; the app-side check is a UX convenience, never trusted alone.

- Notification service — push (FCM/APNs), SMS, and email gateway integration.

- Analytics/reporting layer — aggregated read-store or reporting queries with caching for dashboard performance.

- Cloud hosting — managed cloud (AWS/Azure/GCP/local Indian cloud provider per data-residency needs) with automated backups.

### 8.2 Why Server-Side Validation Matters

A client-reported GPS coordinate can be spoofed. The authoritative punch decision must be made server-side, re-validating the coordinate, timestamp, and device signal against the registered geofence — the mobile app's on-device check is only there to give the associate instant feedback.

## 9. Geofencing Specification — The 5-Metre Requirement

The requirement that punches only succeed within 5 metres of the worksite is achievable as a configured target, but it needs a few technical caveats captured up front so expectations are set correctly during build and rollout.

### 9.1 Why 5 Metres Is Aggressive

Consumer smartphone GPS typically reports an accuracy radius of 5–20 metres outdoors under clear sky, and considerably worse indoors, near tall buildings, or in dense urban areas — a well-established limitation across all vendors researched (Section 1.1). A hard 5 m cutoff risks false rejections for legitimately on-site staff, especially indoors.

### 9.2 Recommended Approach

6.  Treat 5 metres as the configurable default, not a hard-coded constant — Admin can tighten or relax it per site based on real-world testing (e.g., open outdoor yard vs. indoor multi-floor office).

7.  Use the device’s reported GPS accuracy value alongside the raw coordinate: if accuracy itself is worse than the radius (e.g., device reports ±15 m accuracy against a 5 m geofence), show the associate a “move to an open area / near a window” prompt rather than a flat rejection.

8.  Blend GPS with Wi-Fi/cell-tower positioning where available (standard on both Android/iOS location APIs) to improve indoor accuracy.

9.  Pilot-test each registered site’s real-world accuracy before go-live and adjust that site’s radius accordingly; document the tested radius per site in the Admin console.

10. Log GPS accuracy on every punch record so repeated borderline failures can be diagnosed (bad site radius vs. genuine off-site attempt) rather than guessed at.

### 9.3 Privacy-Respecting Location Handling

- Location is captured only at the moment of a punch action — not via continuous background tracking — unless the business explicitly opts into field-staff live tracking as a separate, clearly consented feature.

- Raw coordinates are visible only to Super Admin/System; Managers see status (“On-site ✓”) not exact coordinates, per the data-minimization principle.

- Location permission is requested with a clear in-app explanation before first use, and associates must explicitly consent (see Section 11).

## 10. Cybersecurity Requirements

These requirements are grounded in the OWASP Mobile Application Security Verification Standard (MASVS), the OWASP Mobile Top 10, and standard SaaS security practice, adapted for an app that handles location and employment data.

### 10.1 Authentication & Access Control

- Strong password policy + MFA for Admin/Manager accounts; rate-limited login attempts with account lockout/backoff.

- Role-based access control (RBAC) enforced server-side on every API call, not just hidden in the UI.

- Principle of least privilege: Managers cannot see or edit data outside their assigned team; Associates cannot access any admin function even via direct API calls.

- Session tokens (e.g., short-lived JWT + refresh token) with server-side revocation on logout/offboarding.

### 10.2 Data Protection

- Encryption in transit: TLS 1.2+ for all client-server communication; certificate pinning recommended for the mobile app.

- Encryption at rest: database-level encryption for personal data, GPS coordinates, and credentials (hashed + salted, e.g., bcrypt/Argon2 — never stored in plaintext).

- No sensitive data (tokens, coordinates, credentials) stored in plaintext in mobile app local storage/shared preferences; use platform secure storage (Android Keystore / iOS Keychain).

- Secrets/API keys never hard-coded in the mobile app binary.

### 10.3 Application-Level Controls (OWASP Mobile Top 10 alignment)

| **Risk Area**               | **Control Applied**                                                                             |
|-----------------------------|-------------------------------------------------------------------------------------------------|
| Improper credential usage   | No hardcoded secrets; secure credential storage; forced rotation on suspected compromise        |
| Supply-chain security       | Vet and regularly update third-party SDKs/libraries; dependency vulnerability scanning in CI/CD |
| Insecure auth/session mgmt  | Server-side session validation, short token lifetimes, secure logout                            |
| Input/output validation     | Server-side validation on all inputs; parameterized queries to prevent SQL injection            |
| Insecure communication      | TLS everywhere; reject cleartext traffic; certificate pinning                                   |
| Inadequate privacy controls | Data minimization, purpose-limited location capture, role-based data visibility                 |
| GPS/location spoofing       | Mock-location detection, server-side distance re-validation, anomaly flags for admin review     |

### 10.4 Operational Security

- Full audit trail of admin actions, punch overrides, and permission changes — tamper-evident and retained per policy.

- Regular automated backups with tested restore procedure; disaster recovery plan documented.

- Static (SAST) and dynamic (DAST) security testing before release; periodic penetration testing (annually or on major release).

- Vulnerability/dependency scanning integrated into the build pipeline.

- Incident response plan: defined process to detect, contain, and notify affected users/regulator within statutory timelines in case of a data breach.

- Device management: ability for Admin to remotely revoke a lost/stolen device’s session.

## 11. Data Privacy & Regulatory Compliance

Location data and employment records are sensitive personal data. The application must be designed compliance-first rather than retrofitted later.

### 11.1 Applicable Framework (India context)

Under India’s Digital Personal Data Protection (DPDP) Act, 2023, personal data processed by an employer for employment purposes (including attendance) is a recognized processing ground, but the Act still expects baseline safeguards: purpose limitation, data security, and honoring data-principal (employee) rights. If the business has any EU-resident staff, clients, or data processing touchpoints, GDPR-equivalent principles (consent, right to access/erasure, data minimization) should also be applied.

### 11.2 Requirements

- Explicit, informed consent captured at onboarding for location and attendance data collection, with a plain-language privacy notice (not just a legal document).

- Purpose limitation: location data used only for attendance verification, not repurposed for continuous employee surveillance without separate, explicit consent.

- Data minimization: collect only what is needed (coordinates at punch time; not continuous tracking by default).

- Defined retention policy: attendance/location records retained only as long as legally/operationally necessary, then archived or purged per policy.

- Associate right to view their own data; process for correction requests already covered functionally in Section 4.3.

- Data Processing Agreement with any third-party vendor (cloud host, SMS/push gateway) handling personal data on the business’s behalf.

- Clear internal policy on who (which roles) can view raw GPS coordinates vs. status-only views.

## 12. Notifications

| **Trigger**                              | **Recipient**                | **Channel**          |
|------------------------------------------|------------------------------|----------------------|
| Successful punch in/out                  | Associate                    | In-app / push        |
| Missed punch (no punch-out by shift end) | Associate + Manager          | Push + email         |
| Repeated failed geo-validation attempts  | Manager/Admin                | In-app alert         |
| Possible GPS spoofing detected           | Admin                        | In-app alert + email |
| Correction request submitted / decided   | Relevant Associate & Manager | Push + email         |
| Weekly/Monthly summary report            | Admin/Manager                | Email (scheduled)    |

## 13. Risks & Mitigations

| **Risk**                                                     | **Mitigation**                                                                                              |
|--------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| GPS inaccuracy causes false rejections at legitimate punches | Configurable per-site radius, blended positioning, pilot-testing each site (Section 9)                      |
| GPS spoofing / mock-location apps used to fake presence      | Mock-location detection, server-side validation, anomaly flagging (Section 10.3)                            |
| Associates resist location tracking on personal devices      | Punch-time-only capture (not continuous), transparent consent flow, clear policy communication (Section 11) |
| Data breach exposing location/employment data                | Encryption, RBAC, audit logs, incident response plan (Section 10)                                           |
| Low user adoption due to complex UX                          | ≤ 2-tap punch flow, minimal onboarding, in-app guidance (Section 6)                                         |
| Scope creep into full payroll/HRMS in phase 1                | Explicit out-of-scope list (Section 2.2) with a phased roadmap (Section 14)                                 |

## 14. Phased Implementation Roadmap

### Phase 1 — Core MVP

- Associate login, Admin login, worksite/geofence setup

- Geo-verified punch in/out with server-side validation

- Core reporting module with per-user and aggregate graphs

- Baseline security controls (Section 10), consent flow (Section 11)

### Phase 2 — Enhancements

- Selfie/liveness check on punch

- Manager role with team-scoped access

- Scheduled/automated report emails

- Leave request module (basic)

### Phase 3 — Extended HR Suite

- Shift scheduling

- Payroll integration/export automation

- Advanced analytics (predictive absenteeism trends)

## 15. Success Metrics (KPIs)

| **Metric**                                             | **Target**                                 |
|--------------------------------------------------------|--------------------------------------------|
| Reduction in disputed/incorrect attendance entries     | ≥ 90% reduction vs. prior manual process   |
| Punch action completion time                           | ≤ 5 seconds end-to-end                     |
| False geo-rejection rate at legitimate on-site punches | \< 2% after site radius calibration        |
| Admin time spent generating monthly attendance report  | ≤ 5 minutes (down from manual compilation) |
| Security incidents (breaches, unauthorized access)     | Zero tolerance — tracked and reported      |

## 16. Glossary

| **Term**            | **Meaning**                                                                               |
|---------------------|-------------------------------------------------------------------------------------------|
| Geofence            | A virtual boundary (defined by a centre coordinate and radius) around a physical worksite |
| GPS accuracy radius | The margin of error a device reports alongside its location fix                           |
| Buddy punching      | One employee clocking in/out on behalf of another                                         |
| RBAC                | Role-Based Access Control — permissions tied to a user’s role                             |
| MFA                 | Multi-Factor Authentication                                                               |
| DPDP Act            | Digital Personal Data Protection Act, 2023 (India)                                        |
| MASVS               | OWASP Mobile Application Security Verification Standard                                   |

## Next Steps

11. Stakeholder review and sign-off on this document.

12. Finalize worksite list and pilot-test GPS accuracy at each site to confirm workable geofence radii.

13. Vendor/tech-stack selection and detailed technical design (API spec, DB schema, wireframes).

14. Phase 1 development, security testing, and a pilot rollout with one team before company-wide launch.
