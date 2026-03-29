# Edge Mode - Product Requirements Document

## Original Problem Statement
Build a mobile-first, full-stack application named "Edge Mode" to help teens (12-19) systematically improve themselves. Core philosophy: "1% Better Every Day" - turning self-improvement into a data-driven, game-like experience.

## Target Audience
- Primary: Teens aged 12-19
- Secondary: Coaches, Parents (view-only roles)

## Core Features

### User Tracking & Onboarding
- Account creation with age verification (12-19)
- Select 3-5 "pillars" (e.g., Fitness, Study)
- Set weekly effort targets

### Dashboard & Metrics
- Track streaks, consistency, and performance
- Main dashboard visualizes progress
- Daily motivational quotes
- Habit-building tips

### Social Features
- Private groups with leaderboards
- Opt-in global leaderboard
- School-based leaderboard
- Coach-player team system with invite links
- **Friend Challenges (1v1)** - NEW (March 29, 2026)

### Gamification
- 30+ achievement badges
- Opt-in challenges
- Streak milestones and celebrations
- Shareable achievement cards

### Monetization
- Subscription: $4.99/mo or $49.99/yr
- 14-day free trial (no card required)
- 30-day extended trial for coach teams
- Parent gift subscription flow

### User Roles
- Standard users (players)
- Coaches (free accounts, manage teams)
- Parents (view-only)
- Admins

---

## What's Been Implemented ✅

### Authentication & Users
- [x] JWT-based authentication
- [x] User registration with referral codes
- [x] Coach registration with team creation
- [x] Player join via team invite links
- [x] Password reset via email
- [x] Admin user role

### Payments (Stripe)
- [x] Credit/debit card payments
- [x] Apple Pay / Google Pay
- [x] Parent gift subscription flow
- [x] Trial management (14-day, 30-day extended)

### Admin Dashboard
- [x] User search and management
- [x] Challenge management
- [x] Coach code management
- [x] Fix user subscription status tool
- [x] Extend user access tool
- [x] System maintenance tools
- [x] Groups & Teams management
  - View all groups with member details
  - Copy invite codes
  - Search/filter groups
  - Edit group names
  - Remove individual members

### Coach Dashboard (March 29, 2026)
- [x] Team Analytics with player stats
- [x] Inactive player alerts
- [x] Bulk messaging to team players

### Gamification
- [x] 30+ achievement badges
- [x] Automated challenges (weekly/monthly)
- [x] **Friend Challenges (1v1)** - NEW (March 29, 2026)
  - Challenge friends via email
  - Competition types: sessions, minutes, consistency
  - Duration: 3 days to 1 month
  - Real-time score tracking
  - Accept/decline challenges
  - Challenge history with win/loss records
  - New badges: friend_challenger, friend_wins_3, friend_wins_10
- [x] Leaderboards (global, school, team)
- [x] Streak system with milestones
- [x] Shareable achievement cards

### Notifications & Engagement
- [x] Social proof section on landing page
- [x] Daily motivational quotes
- [x] Rotating habit quotes
- [x] Push notifications for awards/inactivity
- [x] Email notifications (signup, trial ending)
- [x] Streak reminders (8 PM UTC)
- [x] Weekly summaries (Sunday 2 PM UTC)
- [x] Inactive user reminders (6 PM UTC)
- [x] **Morning Motivation** - NEW (March 29, 2026)
  - Opt-in daily motivational emails at 8 AM Eastern
  - Random inspirational quotes
  - User's pillars displayed
  - Streak status included
  - Toggle in Profile settings

### Technical
- [x] PWA capabilities (ready for App Store)
- [x] US/Eastern timezone handling
- [x] Hot reload for development

---

## Completed This Session (March 29, 2026)

1. **Coach Tools (Team Analytics & Bulk Messaging)** ✅
   - Fixed API path mismatch in CoachDashboard.js
   - Team analytics dashboard working
   - Bulk email messaging to players
   - Inactive player alerts

2. **Morning Reminder Notifications** ✅
   - New notification setting (morning_reminders)
   - Scheduler job at 1 PM UTC (8 AM Eastern)
   - HTML email template with motivational quotes
   - User's pillars and streak displayed
   - Profile page toggle with "New" badge

3. **Friends Challenges (1v1)** ✅
   - Full CRUD for 1v1 challenges
   - Create challenge with friend's email
   - Competition types: sessions, minutes, consistency
   - Duration options: 3 days, 1 week, 2 weeks, 1 month
   - Accept/decline pending challenges
   - Real-time score tracking during active challenges
   - Challenge history with win/loss records
   - New badges for friend challenges
   - FriendChallenges.jsx component
   - Integrated into ChallengesScreen.js

4. **Simplified Parent Access Flow** ✅
   - Parents no longer need to create an account
   - Student adds parent's email directly
   - Parent immediately starts receiving:
     - Weekly progress reports (Sunday 3 PM UTC)
     - Streak milestone notifications (7, 14, 30 days)
     - Achievement/badge notifications
     - Inactivity alerts (3+ days no activity)
   - Maximum 2 parent emails per student
   - Updated FamilyScreen.js with "How it works" explanation
   - Backwards compatible with legacy /api/parent/invite endpoint

---

## Upcoming Tasks (Prioritized)

### P1
- **Export Data (CSV)** - Download session history

### P2
- **Streak Recovery** - Save a streak once per month if missed
- "Streak Shield" subscription tier ($0.99/mo)

### P3
- NCES school database integration

### Technical Debt
- Refactor AdminDashboard.js (1100+ lines) into smaller components
- Add automated tests for critical flows

---

## Tech Stack
- **Frontend:** React, Tailwind CSS, Shadcn UI
- **Backend:** FastAPI, Python, Pydantic
- **Database:** MongoDB
- **Payments:** Stripe (via emergentintegrations)
- **Email:** Resend
- **Auth:** JWT

## Key Files
- Backend: `/app/backend/routes/auth.py`, `/app/backend/routes/payments.py`, `/app/backend/routes/challenges.py`
- Frontend: `/app/frontend/src/pages/Dashboard.js`, `/app/frontend/src/pages/ChallengesScreen.js`
- Coach: `/app/frontend/src/pages/CoachDashboard.js`
- Admin: `/app/frontend/src/pages/AdminDashboard.js`

## Test Credentials
- Admin: `admin@edgemodeapp.com` / `EdgeAdmin2024!`
- Coach: `testcoach@edgemode.com` / `TestCoach123!`
