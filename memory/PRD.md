# Edge Mode - Product Requirements Document

## Original Problem Statement
Build a mobile-first, full-stack application named "Edge Mode" to help teens (12-19) systematically improve themselves. The core idea is "1% Better Every Day," turning self-improvement into a data-driven, game-like experience.

## Core Requirements
- **User Tracking:** Users track daily effort in minutes across 3-5 chosen "pillars"
- **Pillars:** Fitness/Training, Sports Practice, Study/Academics, Skill Development, Reading/Learning, Personal Project, Discipline Habits
- **Onboarding:** 4-step flow: Create account -> Select 3-5 pillars -> Set weekly session targets -> Complete
- **Core Metrics:**
  - Current Streak: Increments daily with any log, resets after 48 hours of inactivity
  - Weekly Consistency %: (Days logged / 7)
  - Performance Index: A weighted score of consistency and target completion
- **Dashboard:** Shows current streak, weekly consistency %, 30-day improvement graph, "Yesterday vs Today" comparison
- **Groups:** Private groups with invite codes and leaderboards
- **Global Leaderboard:** Opt-in global leaderboard filterable by age
- **Subscription:** $5.99/month or $59.99/year with 7-day free trial (Stripe - TEST mode)
- **Account Management:** Password reset, change password/email, delete account
- **Legal Pages:** Privacy Policy and Terms of Service

## Tech Stack
- **Backend:** FastAPI (Python)
- **Frontend:** React, JavaScript, Tailwind CSS, Shadcn UI
- **Database:** MongoDB
- **Authentication:** JWT tokens
- **Payments:** Stripe (TEST mode)
- **Email:** Resend (domain verified: edgemodeapp.com)

## What's Been Implemented

### Phase 1 - Core Features (COMPLETE)
- [x] Landing page with Edge Mode branding
- [x] User authentication (signup, login, logout)
- [x] 7-day app-based free trial for new users
- [x] Multi-step onboarding flow for pillar/target selection
- [x] Dashboard with performance metrics and 30-day graph
- [x] Session logging functionality
- [x] Weekly review page
- [x] Profile page with account management
- [x] Private groups with invite codes, member counts, ownership transfer
- [x] Global leaderboard (opt-in)
- [x] Stripe subscription integration (monthly/yearly)
- [x] Password reset flow (backend + frontend)
- [x] Change password/email functionality
- [x] Delete account functionality
- [x] Privacy Policy & Terms of Service pages
- [x] Edit/Delete Sessions UI (Feb 26, 2026)
- [x] Quick Log Feature - Log sessions from dashboard (Feb 26, 2026)

### Phase 2 - Completed (Feb 26-27, 2026)
- [x] Session History Page - Full calendar view of past sessions
- [x] Notes on Sessions - Add text notes to any session
- [x] Email Notifications - Resend integration (domain verified)
  - Streak reminder emails
  - Weekly summary emails
  - Sender: noreply@edgemodeapp.com
- [x] Notification Settings - Toggle in Profile page
- [x] Performance Ratings - 5-tier system (Elite, High Performer, On Track, Building, Getting Started)

### Backend Endpoints
- `/api/auth/register`, `/api/auth/login`
- `/api/auth/forgot-password`, `/api/auth/reset-password`
- `/api/onboarding/complete`
- `/api/sessions/complete`, `/api/sessions/today`, `/api/sessions/history`
- `/api/sessions/edit` (PUT), `/api/sessions/{session_id}` (DELETE)
- `/api/stats/weekly`, `/api/stats/comparison`, `/api/stats/history`
- `/api/groups`, `/api/groups/join`, `/api/groups/{group_id}/leave`, `/api/groups/{group_id}/transfer`
- `/api/leaderboard/global`
- `/api/payments/create-checkout`, `/api/payments/status/{session_id}`
- `/api/users/change-password`, `/api/users/change-email`, `/api/users/account` (DELETE)
- `/api/notifications/settings` (GET/PUT)
- `/api/notifications/send-streak-reminder` (POST)
- `/api/notifications/send-weekly-summary` (POST)

## Key Files
- `/app/backend/server.py` - All backend logic
- `/app/frontend/src/App.js` - Main router
- `/app/frontend/src/pages/LogScreen.js` - Session logging + Edit/Delete + Notes
- `/app/frontend/src/pages/Dashboard.js` - Main dashboard + Quick Log
- `/app/frontend/src/pages/HistoryScreen.js` - Session history with calendar
- `/app/frontend/src/pages/ProfileScreen.js` - Profile + Notification settings
- `/app/frontend/src/components/PerformanceRating.js` - Performance rating component
- `/app/frontend/src/components/ConsistencyRating.js` - Consistency rating component
- `/app/frontend/src/context/AuthContext.js` - Auth state management

## Database Schema
- **users:** `{id, email, username, age, password_hash, join_date, current_streak, longest_streak, subscription_active, trial_ends_at, leaderboard_opt_in, streak_reminders, weekly_summary}`
- **user_pillars:** `{user_id, pillar_name, weekly_target_sessions}`
- **daily_sessions:** `{id, user_id, pillar, date, timestamp, minutes_spent, note}`
- **groups:** `{id, name, type, created_by, members[], invite_code, created_at}`
- **payment_transactions:** `{id, session_id, user_id, amount, plan, payment_status}`

## Deployment Status
- App deployed to `edgemodeapp.com` (DNS configured)
- Stripe in TEST mode (card: 4242 4242 4242 4242)

## Configuration Required
- **RESEND_API_KEY** - Add to `/app/backend/.env` for email notifications to work
- **SENDER_EMAIL** - Optional, defaults to `onboarding@resend.dev`

## Prioritized Backlog

### P0 - Critical (None remaining)
All critical features are complete.

### P1 - High Priority
- [ ] Automated email scheduling (cron job for streak reminders)
- [ ] Mobile PWA optimization

### P2 - Medium Priority (Phase 3)
- [ ] FAQ/Help Section
- [ ] Achievements/Badges system
- [ ] Social Sharing buttons

## Test Credentials
- Create new user via signup
- Stripe Test Card: 4242 4242 4242 4242 (any future expiry, any CVC)
