# Edge Mode - Product Requirements Document

## Overview
Mobile-first self-improvement app for teens (12-19). Core concept: "1% Better Every Day"

**Live URL:** https://edgemodeapp.com
**Preview URL:** https://teen-tracker-1.preview.emergentagent.com

## Tech Stack
- **Backend:** FastAPI (Python), APScheduler, pywebpush
- **Frontend:** React, Tailwind CSS, Shadcn UI
- **Database:** MongoDB Atlas
- **Auth:** JWT tokens
- **Payments:** Stripe (TEST mode)
- **Email:** Resend (noreply@edgemodeapp.com)
- **Push Notifications:** Web Push API with VAPID

## Code Architecture (Refactored - March 2026)
```
/app/backend/
├── server.py              # Main server (~230 lines) - includes router registration & scheduler
├── config.py              # Configuration & shared dependencies (db, VAPID keys, constants)
├── models/
│   └── schemas.py         # Pydantic models for all endpoints
├── routes/
│   ├── auth.py            # Authentication (register, login, coach signup, password reset)
│   ├── users.py           # User management (profile, pillars, settings)
│   ├── sessions.py        # Session logging (complete, edit, delete, history)
│   ├── stats.py           # Statistics (weekly, comparison, history, review)
│   ├── badges.py          # Badges system (all, user, progress)
│   ├── groups.py          # Groups (create, join, leaderboard)
│   ├── leaderboard.py     # Global leaderboard
│   ├── coach.py           # Coach dashboard & player details
│   ├── parent.py          # Parent-student linking & notifications
│   ├── challenges.py      # Challenges system (CRUD, leaderboard, automation)
│   ├── payments.py        # Stripe integration (checkout, webhook)
│   ├── admin.py           # Admin dashboard (stats, users)
│   ├── notifications.py   # Email notification routes & settings
│   ├── referral.py        # Referral system (invite, track)
│   ├── onboarding.py      # Onboarding (pillars, team info)
│   └── push.py            # Push notifications (subscribe, unsubscribe, send) ✅ NEW
└── utils/
    ├── auth.py            # Authentication helpers (JWT, password hashing)
    ├── badges.py          # Badge checking & awarding logic
    ├── streaks.py         # Streak calculation utilities
    └── scheduler_jobs.py  # Scheduled email + push notification jobs
```

## Features (All Complete)

### Core
- User auth (signup/login)
- 14-day free trial
- Onboarding (select 3-5 pillars, set weekly targets)
- Dashboard with metrics & 30-day graph
- Session logging with notes
- Session history (calendar view)
- Edit/delete sessions

### Achievements/Badges System
- 12 badges available
- Toast notifications when new badges earned
- Progress bars for locked badges

### Push Notifications ✅ NEW (March 2026)
- **Web Push API** with VAPID authentication
- **Service Worker** at `/sw.js` for handling push events
- **Notification Types:**
  - 🔥 Streak reminders (daily)
  - 🏅 New badge earned (on session complete)
  - 👋 Inactivity alerts (3+ days)
  - ⏰ Trial ending reminders
- **Frontend Integration:**
  - Toggle on/off from Profile page
  - Browser permission handling
  - Test notification button
  - Pro tips for mobile users
- **Backend Endpoints:**
  - `GET /api/push/vapid-key` - Get VAPID public key
  - `POST /api/push/subscribe` - Subscribe to push
  - `DELETE /api/push/unsubscribe` - Unsubscribe
  - `GET /api/push/status` - Check subscription status
  - `POST /api/push/test` - Send test notification

### Social
- Private groups with invite codes
- Global leaderboard (opt-in)

### Email Notifications (via Scheduler)
- Streak reminders: 8 PM UTC daily
- Inactive reminders: 6 PM UTC daily
- Trial ending reminders: 4 PM UTC daily
- Weekly summaries: Sunday 2 PM UTC
- Parent weekly summaries: Sunday 3 PM UTC
- Parent inactivity alerts: 7 PM UTC daily

### Opt-In Challenges
- Weekly and monthly challenges
- Auto-created via scheduled job
- Real-time leaderboard rankings

### Coach Mode
- Dedicated coach signup (FREE)
- Special codes for extended trials
- Team dashboard with player stats

### Parent-Student Linking
- Student invites up to 2 parents
- Parent Dashboard with student stats
- Parent notification emails

### Admin
- Admin Dashboard at `/admin`
- Access: admin@edgemodeapp.com only

### Other
- Stripe subscriptions ($4.99/mo, $49.99/yr) - TEST MODE
- Password reset
- Profile settings
- Privacy Policy & Terms of Service
- Pillar Management

## Completed Tasks (This Session)
- [x] ✅ **Refactored backend** from 4000+ line monolithic server.py into modular routers
- [x] ✅ **Integrated parent notification emails** into scheduler
- [x] ✅ **Added push notifications** with Web Push API and VAPID
- [x] ✅ **All backend API endpoints tested** - 100% pass rate

## Future Enhancements
- [ ] **P2: Admin UI for Special Codes** - Manage coach trial codes via dashboard
- [ ] **P2: Mobile PWA Optimization** - Add offline capabilities, home screen install prompt
- [ ] **P3: Add Referral Rewards** - Free month for 3+ referrals
- [ ] **P3: Admin Challenge Management** - Manual challenge creation UI

## Test Credentials
- **Admin:** admin@edgemodeapp.com
- **Test User:** refactortest@example.com / test123
- **Stripe Test Card:** 4242 4242 4242 4242 | Any future date | Any 3 digits
- **Coach Special Codes:** EDGE30, COACH2024, TEAMEDGE, PROMO30
