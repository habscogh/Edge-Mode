# Edge Mode - Product Requirements Document

## Overview
Mobile-first self-improvement app for teens (12-19). Core concept: "1% Better Every Day"

**Live URL:** https://edgemodeapp.com
**Preview URL:** https://teen-tracker-1.preview.emergentagent.com

## Tech Stack
- **Backend:** FastAPI (Python), APScheduler
- **Frontend:** React, Tailwind CSS, Shadcn UI
- **Database:** MongoDB Atlas
- **Auth:** JWT tokens
- **Payments:** Stripe (TEST mode)
- **Email:** Resend (noreply@edgemodeapp.com)

## Code Architecture (Refactored - March 2026)
```
/app/backend/
├── server.py              # Main server (~230 lines) - includes router registration & scheduler
├── config.py              # Configuration & shared dependencies (db, constants)
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
│   └── onboarding.py      # Onboarding (pillars, team info)
└── utils/
    ├── auth.py            # Authentication helpers (JWT, password hashing)
    ├── badges.py          # Badge checking & awarding logic
    ├── streaks.py         # Streak calculation utilities
    └── scheduler_jobs.py  # Scheduled email jobs (streak, weekly, parent notifications)
```

## Features (All Complete)

### Core
- User auth (signup/login)
- 14-day free trial (updated from 7 days)
- **Trial Ending Banner** - Shows on dashboard when 3 days or less remaining
- Trial Expired screen with "What You'll Lose" personalized warning
- Onboarding (select 3-5 pillars, set weekly targets)
- Dashboard with metrics & 30-day graph
- Session logging with notes
- Session history (calendar view)
- Edit/delete sessions
- Quick Log on dashboard

### Achievements/Badges System
- **12 badges available:**
  - 🏆 First Step - Log your first session
  - 🔥 Week Warrior - Maintain a 7-day streak
  - 🔥 Fortnight Fighter - Maintain a 14-day streak
  - 🔥 Monthly Master - Maintain a 30-day streak
  - 💯 Century Club - Complete 100 sessions
  - ⏱️ 50 Hour Club - Log 50+ hours total
  - ✨ Perfect Week - Log every day for a week
  - 🎯 Pillar Master - Hit target on all pillars in a week
  - 🏅 Weekly Champion - Win a weekly challenge
  - 🥇 Monthly Champion - Win a monthly challenge
  - 🎖️ Podium Finish - Finish in top 3 of a challenge
  - 🏆 Challenge Streak - Win 3 challenges
- Dedicated Achievements page at `/achievements`
- Badge summary on Profile page
- Toast notifications when new badges are earned
- Progress bars showing progress toward locked badges

### Social
- Private groups with invite codes
- Global leaderboard (opt-in)

### Ratings
- Performance Rating (Elite → Getting Started)
- Consistency Rating

### Social Sharing
- Share to Twitter/X, Facebook, or copy to clipboard
- Shareable content: badges, stats, streaks
- All shares include app link for user acquisition

### Milestone Celebrations
- Automatic popup when users hit streak milestones (7, 14, 30, 50, 100 days)
- Celebratory modal with confetti animation

### Invite Friends / Referrals
- Unique referral code for each user
- Shareable invite link: `edgemodeapp.com/auth?ref=CODE`
- Email invite functionality
- Tracks successful referrals

### Email Notifications (Automatic via Scheduler)
- **Streak reminders:** 8 PM UTC daily (3 PM Eastern) - for users with active streaks who haven't logged
- **Inactive reminders:** 6 PM UTC daily (2 PM Eastern) - for 3-7 days inactive users
- **Trial ending reminders:** 4 PM UTC daily (12 PM Eastern) - for users with 1-3 days left
- **Weekly summaries:** Sunday 2 PM UTC (10 AM Eastern)
- **Parent weekly summaries:** Sunday 3 PM UTC (11 AM Eastern) ✅ INTEGRATED
- **Parent inactivity alerts:** 7 PM UTC daily (3 PM Eastern) ✅ INTEGRATED
- **Challenges daily job:** 12:05 AM UTC daily

### Opt-In Challenges
- Weekly and monthly challenges
- Auto-created via scheduled job
- Auto-seeding on startup if no active challenges
- Real-time leaderboard rankings
- Filter by: All, My Challenges, Weekly, Monthly

### Coach Mode in Groups
- Dedicated `/coach-signup` page (FREE)
- Special codes for extended trials: EDGE30, COACH2024, TEAMEDGE, PROMO30
- Team invite system with shareable links
- Coach Dashboard (`/coach-home`) with team stats

### Parent-Student Linking
- Student invites up to 2 parents
- Parent receives email with invite code (PARENT-XXXXXX)
- Parent Dashboard with student stats view
- **Parent Notification Emails:** ✅ INTEGRATED
  - Weekly progress summaries
  - Inactivity alerts (3+ days)
  - Streak milestone notifications (7, 14, 30 days)
  - New badge notifications

### Admin
- Admin Dashboard at `/admin`
- Stats: users, sessions, subscriptions
- Access: admin@edgemodeapp.com only

### Other
- Stripe subscriptions ($4.99/mo, $49.99/yr) - TEST MODE
- Password reset
- Profile settings
- Privacy Policy & Terms of Service
- Pillar Management

## Bug Fixes (March 2026)
- **Timezone Bug Fixed**: All stats endpoints accept `local_date` parameter
- **Coach /api/users/me Fixed**: User model now handles optional username/age for coaches

## Completed Tasks (This Session)
- [x] ✅ **Refactored backend** from 4000+ line monolithic server.py into modular routers
- [x] ✅ **Integrated parent notification emails** into scheduler (weekly summaries, inactivity alerts)
- [x] ✅ **All 41 API endpoints tested** - 97.6% pass rate (40/41)

## Future Enhancements
- [ ] **P2: Admin UI for Special Codes** - Manage coach trial codes via dashboard
- [ ] **P2: Mobile PWA Optimization** - Add offline capabilities, home screen install
- [ ] **P3: Add Referral Rewards** - Free month for 3+ referrals
- [ ] **P3: Admin Challenge Management** - Manual challenge creation UI

## Test Credentials
- **Admin:** admin@edgemodeapp.com
- **Stripe Test Card:** 4242 4242 4242 4242 | Any future date | Any 3 digits
- **Coach Special Codes:** EDGE30, COACH2024, TEAMEDGE, PROMO30
