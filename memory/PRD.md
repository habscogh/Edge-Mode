# Edge Mode - Product Requirements Document

## Overview
Mobile-first self-improvement app for teens (12-19). Core concept: "1% Better Every Day"

**Live URL:** https://edgemodeapp.com
**Preview URL:** https://daily-edge-3.preview.emergentagent.com

## Tech Stack
- **Backend:** FastAPI (Python), APScheduler, pywebpush
- **Frontend:** React, Tailwind CSS, Shadcn UI
- **Database:** MongoDB Atlas
- **Auth:** JWT tokens
- **Payments:** Stripe (LIVE mode) ✅
- **Email:** Resend
- **Push Notifications:** Web Push API with VAPID
- **PWA:** Service Worker, manifest.json, IndexedDB

## Code Architecture
```
/app/backend/
├── server.py              # Main server (~230 lines)
├── config.py              # Configuration
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
    └── scheduler_jobs.py  # Email + push jobs

/app/frontend/
├── public/
│   ├── manifest.json      # PWA manifest
│   └── sw.js              # Service worker
└── src/
    ├── utils/
    │   └── offlineStorage.js   # IndexedDB storage manager
    ├── hooks/
    │   ├── usePushNotifications.js
    │   ├── useInstallPrompt.js
    │   └── useOfflineSync.js
    └── components/
        ├── PushNotificationSettings.jsx
        ├── InstallPrompt.jsx
        └── OfflineIndicator.jsx
```

## Features (All Complete)

### Core
- User auth (signup/login)
- 14-day free trial
- Onboarding (select 3-5 pillars)
- Dashboard with metrics & graph
- Session logging with notes
- Session history
- Edit/delete sessions

### Daily Reflections & Growth Journal ✅ NEW
- **Post-Session Reflection Modal** - After logging a session, users can reflect on their progress
- **Daily Prompts** - Rotating prompts like "What did you learn today?", "What are you grateful for?"
- **Mood Tracking** - Select from 🔥 Great, 😊 Good, 😐 Okay, 💪 Tough
- **Growth Journal Page** - View all past reflections with stats
- **Reflection Streak** - Track consecutive days of reflections
- **Skip Option** - Users can skip if they don't want to reflect

### Push Notifications ✅
- Web Push API with VAPID
- Notifications for: streak reminders, badges, inactivity, trial ending
- Toggle on/off from Profile page

### PWA Install Prompt ✅
- "Add to Home Screen" functionality
- Install Banner on Dashboard
- iOS Safari manual guide

### Offline Session Logging ✅ NEW
- **IndexedDB Storage** - Sessions saved locally when offline
- **Auto-Sync** - Automatically syncs when back online
- **Offline Indicator** - Floating badge shows offline status & pending count
- **Sync Status Card** - Profile page shows sync status and manual sync button
- **Network Error Fallback** - Falls back to offline save on network errors
- **Toast Notifications** - Shows "Saved offline!" when saving locally

### Achievements/Badges
- 12 badges available
- Toast notifications for new badges

### Social
- Private groups with invite codes
- Global leaderboard (opt-in)

### Email Notifications
- Streak reminders, weekly summaries
- Parent notifications

### Challenges
- Weekly and monthly challenges
- Auto-created via scheduler

### Coach Mode
- Free coach signup
- Team dashboard

### Parent-Student Linking
- Up to 2 parents per student
- Parent dashboard

### Admin
- Admin Dashboard at `/admin`

### Other
- Stripe subscriptions - TEST MODE
- Password reset
- Profile settings

## Completed Tasks (This Session - Dec 2025)
- [x] ✅ **Fixed Achievements back button** - Added navigation back arrow
- [x] ✅ **Added consistent back navigation** - Weekly Review, History pages
- [x] ✅ **Added Quick Actions FAB** - 6 shortcuts on Dashboard
- [x] ✅ **Added Pricing Section** - Landing page with monthly/yearly toggle
- [x] ✅ **Push Notification Prompt** - Shows after first session logged
- [x] ✅ **Enhanced Onboarding Progress** - Visual step indicators with progress bar
- [x] ✅ **Confetti Celebrations** - Real canvas-confetti on milestones
- [x] ✅ **Dark/Light Mode Toggle** - Theme switcher in Profile settings
- [x] ✅ **Share Streak Cards** - Generate shareable images for Instagram/TikTok
- [x] ✅ **Referral Rewards** - Invite 3 friends → Get 30 days free
- [x] ✅ **School Leaderboard** - US schools (Grades 8-12) with weekly rankings
  - School selector with autocomplete + custom school entry
  - New `/school-leaderboard` page with 3 tabs
- [x] ✅ **Founding Ambassador Program** - Special code activation, 1 year free, referral tracking
  - Codes: EDGEFOUNDER2025, AMBASSADOR1, FOUNDINGMEMBER
- [x] ✅ **Fixed "Failed to log session" bug** - Post-session refresh errors no longer show false error
- [x] ✅ **Fixed School Search** - Users can now add ANY school name (not just from database)
- [x] ✅ **Fixed Production Sign-Up White Screen (March 2026)** - React Error #31 fix
  - Root cause: FastAPI validation errors returned as objects, React couldn't render them
  - Fixed error handling in AuthScreen.js, ForgotPassword.js, ResetPasswordScreen.js
  - Added Error Boundary in App.js to catch unhandled errors
  - Fixed AuthContext.js race condition on registration
- [x] ✅ **Daily Reflections & Growth Journal (March 2026)** - New feature
  - Backend: `/api/reflections/` endpoints for prompts, saving, and stats
  - Frontend: ReflectionModal component shown after session log
  - Frontend: JournalScreen page at `/journal` to view past reflections
  - Added to Quick Actions FAB on dashboard
  - Tracks reflection streaks and mood distribution
- [x] ✅ **Stripe Live Payments (March 2026)** - Production payments now working
  - Updated config.py to check both STRIPE_SECRET_KEY and STRIPE_API_KEY
  - Added `/api/stripe-check` debug endpoint for verifying key status
  - Added `/api/admin/stripe-debug` authenticated endpoint
  - Resolved platform-level key override by updating Secrets
- [x] ✅ **Fixed Duplicate Challenges Bug (March 2026)**
  - Added check to prevent creating duplicate challenges for same period
  - Added Admin button "Clean Duplicate Challenges" to remove existing duplicates
  - Endpoint: `/api/admin/challenges/cleanup-duplicates`
- [x] ✅ **Fixed School Leaderboard Showing 0% (March 2026)**
  - School leaderboard now calculates consistency/performance dynamically
  - Fixed `/api/schools/leaderboard` and `/api/schools/my-school-stats`
- [x] ✅ **Fixed Timezone/Date Bug (March 2026)** - "Today" showing yesterday's sessions
  - Root cause: Frontend used `toISOString()` which converts to UTC
  - Created `src/utils/dateUtils.js` with `getLocalDateString()` helper
  - Updated Dashboard.js, LogScreen.js, WeeklyReviewScreen.js, TrialExpiredScreen.js
- [x] ✅ **Streak Recovery Feature (March 2026)** - Paid option to restore broken streaks
  - Backend: `/api/streak-recovery/` endpoints for eligibility check and Stripe checkout
  - Frontend: StreakRecoveryModal component with pricing and checkout flow
  - Frontend: StreakRecoverySuccessScreen with confetti celebration
  - Price: $2.99 one-time payment
  - Rules: Streak must have been 3+ days, can recover within 7 days of breaking
  - Broken streak data now saved when streaks break for potential recovery
- [x] ✅ **Admin Challenge Management (March 2026)** - Full CRUD for challenges
  - Backend: `/api/challenges/admin/all`, `/admin/{id}` (PUT/DELETE), `/admin/{id}/participants`
  - Frontend: AdminChallengeManager component with create/edit/delete functionality
  - Features: Create weekly/monthly challenges, set metrics & pillars, change status, view participants
- [x] ✅ **Featured Challenges on Dashboard (March 2026)** - Boost challenge participation
  - Backend: `/api/challenges/featured` endpoint, added `featured` flag to challenges
  - Frontend: FeaturedChallenges component on Dashboard showing active challenges
  - Admin: Toggle "Feature" button in Challenge Management to feature/unfeature challenges
  - Shows top 3 participants preview, days left, quick join button
- [x] ✅ **Challenge Awards System (March 2026)** - Automatic badge awards for winners
  - Badges: Weekly Champion (🏅), Monthly Champion (🥇), Silver Medal (🥈), Bronze Medal (🥉), Podium Finish (🎖️)
  - Auto-awards on challenge end via scheduler
  - Admin "Finalize & Award" button for manual finalization
  - Winners displayed in challenge cards with medals
  - Challenge streak badge for 3+ wins

## Known Issues
- MongoDB may need manual restart if it times out (mongod --dbpath /data/db --fork --logpath /var/log/mongodb.log)

## Future Enhancements
- [ ] **P1:** Social Proof Section - Add testimonials/user stats to landing page
- [ ] **P2:** Admin UI for managing coach special codes
- [ ] **P3:** Integrate real NCES school database API for complete US school coverage

## Test Credentials
- **Admin:** admin@edgemodeapp.com / EdgeAdmin2024!
- **Test User:** refactortest@example.com / test123
- **Stripe Live Card:** Use real card for live payments
- **Coach Codes:** EDGE30, COACH2024, TEAMEDGE, PROMO30
