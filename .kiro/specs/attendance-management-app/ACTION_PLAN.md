# Salon Attendance App — Beginner's Action Plan

## What You're Building

A **website** that your 6 salon staff open on their phone browser to punch in/out. You (the owner) open the same website on your laptop to see who's present, view charts, and export salary data.

```
Associate's Phone (Chrome)  ──►  Your Python Server (Railway, free)  ──►  Database (Supabase, free)
Admin's Laptop (any browser) ──►         ↑ same server ↑
```

---

## What You Need Installed

| Tool | Why | Install |
|------|-----|---------|
| **Python 3.11+** | Runs the backend | https://www.python.org/downloads/ (check "Add to PATH" during install) |
| **Git** | Version control + deployment | https://git-scm.com |
| **VS Code or Kiro** | Code editor | Already have Kiro ✓ |
| **A browser** | Testing | Chrome ✓ |

**That's it.** No Docker, no Android Studio, no Redis, no PostgreSQL installation.

### Verify setup (open a terminal):
```bash
python --version    # Should show 3.11+
git --version       # Should show 2.x
```

---

## Execution Order

### Week 1: Backend + Auth + Punch Logic

**Day 1–2: Project setup**
1. Create project folder and Python virtual environment
2. Install FastAPI + dependencies
3. Set up Supabase (sign up → create project → get connection string)
4. Create database tables via Supabase SQL editor
5. Get your basic FastAPI server running at `localhost:8000`

**Day 3–4: Authentication**
6. Build login endpoint (email + password → JWT cookie)
7. Build logout endpoint
8. Build the login HTML page
9. Test: can you log in and see a "Welcome" page?

**Day 5–7: Punch in/out**
10. Write the Haversine function (10 lines of Python)
11. Build `POST /api/punch/in` endpoint
12. Build `POST /api/punch/out` endpoint
13. Build the home page with the punch button
14. Add JavaScript to get GPS from browser and send to server
15. Test: open on phone → punch in at salon → success; walk away → fails

### Week 2: Admin + Reports + Styling

**Day 8–9: Admin dashboard**
16. Build aggregation queries (who's present today, hours this week)
17. Create dashboard page with Chart.js charts
18. Test: log in as admin → see today's attendance

**Day 10–11: User management + Geofence**
19. Build "add/remove user" page
20. Build geofence config page with map (Leaflet.js)
21. Test: change geofence radius → punch validation uses new radius

**Day 12–13: Export + Polish**
22. Build CSV export endpoint
23. Apply consistent styling (TailwindCSS)
24. Add error messages and loading states
25. Test everything end-to-end

### Week 3: Deploy + Go Live

**Day 14: Deploy**
26. Push code to GitHub
27. Connect to Railway (free) → set environment variables → it's live
28. Open the URL on your phone → confirm it works

**Day 15: Pilot with staff**
29. Share the URL with your 6 salon staff
30. Have everyone punch in/out for a day
31. Fix any issues
32. You're done! 🎉

---

## How to Test

### As you build (daily):
- Open `http://localhost:8000` in your browser
- Test each feature immediately after building it
- Use Chrome DevTools (F12) → Network tab to see API requests/responses
- Use Supabase dashboard to verify data is being written to the database

### Before going live:
1. ✅ Log in as associate → see punch button
2. ✅ Punch in at salon location → success
3. ✅ Punch in from far away → shows "too far" message
4. ✅ Punch in twice → shows "already punched in"
5. ✅ Punch out → success, hours calculated
6. ✅ View attendance history → shows today's records
7. ✅ Log in as admin → see dashboard with charts
8. ✅ Export CSV → file downloads with correct data
9. ✅ Try wrong password 5 times → account locks
10. ✅ Try accessing admin page as associate → denied

### Automated tests (optional but recommended):
```bash
# In your project folder
pip install pytest httpx
pytest tests/ -v
```

---

## How to Deploy (Free)

### Step 1: Create a Supabase database (5 minutes)
1. Go to https://supabase.com → sign up (free)
2. Click "New Project" → pick a name and password
3. Go to SQL Editor → paste your table creation SQL → run
4. Go to Settings → Database → copy the "Connection string (URI)"

### Step 2: Push to GitHub (2 minutes)
```bash
git init
git add .
git commit -m "initial commit"
# Create a repo on github.com, then:
git remote add origin https://github.com/yourusername/salon-attendance.git
git push -u origin main
```

### Step 3: Deploy on Railway (5 minutes)
1. Go to https://railway.app → sign up with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repo
4. Add environment variables:
   - `DATABASE_URL` = (paste from Supabase)
   - `JWT_SECRET` = (any long random string)
5. Railway auto-detects Python, installs deps, starts the server
6. Click "Generate Domain" → you get a URL like `salon-attendance-production.up.railway.app`

### Step 4: Share with your team
- Send the URL to your 6 staff via WhatsApp
- Tell them: "Open this link, log in with the email and password I gave you, and tap Punch In when you arrive"
- They can bookmark it to their home screen (looks like an app)

---

## Monthly Costs

| Item | Cost |
|------|------|
| Railway hosting | $0 (free: 500 hrs/month) |
| Supabase database | $0 (free: 500MB, unlimited API) |
| Domain name (optional) | $1/month if you want a custom URL |
| **Total** | **$0/month** |

---

## Monetization Path

Once it works for your salon, you can sell it to other salons:

1. **Multi-tenant:** Add a `salon_id` column to each table → one deployment serves multiple salons
2. **Pricing:** ₹499–₹999/month per salon (typical for Indian SMB SaaS)
3. **Upgrade hosting:** When you have 10+ salons paying, upgrade Railway ($5/mo) and Supabase ($25/mo)
4. **Custom domain:** `salonattendance.in` or similar

---

## Key Files You'll Create

```
salon-attendance/
├── main.py                  ← FastAPI app (the core)
├── requirements.txt         ← Python packages list
├── .env                     ← Secrets (never commit this)
├── routes/
│   ├── auth.py             ← Login/logout
│   ├── punch.py            ← Punch in/out API
│   └── admin.py            ← Dashboard, users, reports, export
├── services/
│   ├── geo.py              ← Haversine function (10 lines)
│   └── auth.py             ← Password hashing, JWT
├── templates/
│   ├── login.html          ← Login page
│   ├── home.html           ← Punch button (associate view)
│   ├── history.html        ← Attendance history
│   └── admin/
│       ├── dashboard.html  ← Charts + today's summary
│       ├── users.html      ← Manage staff
│       └── geofence.html   ← Set salon location
├── static/
│   ├── css/style.css       ← TailwindCSS
│   └── js/punch.js         ← GPS + fetch() logic
└── tests/
    └── test_geo.py         ← Test the Haversine math
```

---

## Tips

1. **Build the punch-in feature first.** It's the core of the app. Everything else is secondary.
2. **Test on your actual phone at the salon.** GPS accuracy indoors varies — you might need to increase the radius to 10–15m.
3. **Don't over-engineer.** You have 6 users. Simple is better than perfect.
4. **Use Kiro to generate code.** Each task in `tasks.md` is designed to be small enough for one Kiro session.
5. **Deploy early.** Push to Railway in Week 1 so you can test on real phones instead of only localhost.
