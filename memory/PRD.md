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
- **PWA:** Service Worker, manifest.json

## Code Architecture (Refactored - March 2026)
```
/app/backend/
├── server.py              # Main server (~230 lines)
├── config.py              # Configuration (db, VAPID keys, constants)
├── routes/
│   ├── auth.py            # Authentication
│   ├── users.py           # User management
│   ├── sessions.py        # Session logging
│   ├── stats.py           # Statistics
│   ├── badges.py          # Badges system
│   ├── groups.py          # Groups
│   ├── leaderboard.py     # Global leaderboard
│   ├── coach.py           # Coach dashboard
│   ├── parent.py          # Parent-student linking
│   ├── challenges.py      # Challenges system
│   ├── payments.py        # Stripe integration
│   ├── admin.py           # Admin dashboard
│   ├── notifications.py   # Email notifications
│   ├── referral.py        # Referral system
│   ├── onboarding.py      # Onboarding
│   └── push.py            # Push notifications
└── utils/
    ├── auth.py            # JWT, password hashing
    ├── badges.py          # Badge logic
    ├── streaks.py         # Streak calculation
    └── scheduler_jobs.py  # Email + push scheduled jobs

/app/frontend/
├── public/
│   ├── manifest.json      # PWA manifest
│   └── sw.js              # Service worker (push + caching)
└── src/
    ├── hooks/
    │   ├── usePushNotifications.js
    │   └── useInstallPrompt.js
    └── components/
        ├── PushNotificationSettings.jsx
        └── InstallPrompt.jsx
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

### Push Notifications ✅
- Web Push API with VAPID authentication
- Service Worker at `/sw.js`
- Notifications for: streak reminders, badges, inactivity, trial ending
- Toggle on/off from Profile page
- Test notification button

### PWA Install Prompt ✅ NEW
- **manifest.json** with app name, icons, theme colors
- **"Add to Home Screen"** functionality
- **Install Banner** on Dashboard (dismissible)
- **Install Settings** on Profile page
- **iOS Safari Guide** - 3-step manual instructions
- **Offline Support** - Basic caching via Service Worker
- Benefits shown: Quick access, Push notifications, Full screen mode, Works offline

### Achievements/Badges System
- 12 badges available
- Toast notifications when new badges earned
- Progress bars for locked badges

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

## Completed Tasks (This Session)
- [x] ✅ **Refactored backend** - 4000+ line monolithic → modular routers
- [x] ✅ **Integrated parent notification emails** into scheduler
- [x] ✅ **Added push notifications** with Web Push API
- [x] ✅ **Added PWA install prompt** with "Add to Home Screen"
- [x] ✅ **All features tested** - 100% pass rate

## Future Enhancements
- [ ] **P2: Admin UI for Special Codes** - Manage coach trial codes
- [ ] **P3: Add Referral Rewards** - Free month for 3+ referrals
- [ ] **P3: Admin Challenge Management** - Manual challenge creation UI
- [ ] **P3: Offline Session Logging** - Queue sessions when offline

## Test Credentials
- **Admin:** admin@edgemodeapp.com
- **Test User:** refactortest@example.com / test123
- **Stripe Test Card:** 4242 4242 4242 4242
- **Coach Special Codes:** EDGE30, COACH2024, TEAMEDGE, PROMO30
