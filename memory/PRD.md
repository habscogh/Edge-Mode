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

### Gamification
- [x] 30+ achievement badges
- [x] Automated challenges
- [x] Leaderboards (global, school, team)
- [x] Streak system with milestones
- [x] Shareable achievement cards

### Engagement
- [x] Social proof section on landing page
- [x] Daily motivational quotes
- [x] Rotating habit quotes
- [x] Push notifications for awards/inactivity
- [x] Email notifications (signup, trial ending)

### Technical
- [x] PWA capabilities
- [x] US/Eastern timezone handling
- [x] Hot reload for development

---

## Verified Working (March 19, 2026)

### Coach Invite Flow ✅
- Coach registration creates team with invite code
- `/api/team/{code}` returns team info (public)
- Player registration via invite adds to team
- Frontend join page renders correctly

---

## Upcoming Tasks (Prioritized)

### P1 - Progress Insights
Add motivational messages to dashboard:
- "You logged 20% more than last week"
- "3rd consecutive week hitting targets"
- Compare current vs previous week metrics

### P1 - Quick Log Buttons
Add one-tap presets on logging screen:
- 15 min / 30 min / 60 min buttons
- Reduce friction for common log durations

### P2 - Export Data (CSV)
Allow users to download their session history:
- Date, pillar, duration, notes
- Downloadable CSV format

---

## Future/Backlog

### P2
- "Streak Shield" subscription tier ($0.99/mo)
- Daily login reminder push notifications

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
- Backend: `/app/backend/routes/auth.py`, `/app/backend/routes/payments.py`
- Frontend: `/app/frontend/src/pages/Dashboard.js`, `/app/frontend/src/pages/JoinTeam.js`
- Admin: `/app/frontend/src/pages/AdminDashboard.js`

## Test Credentials
- Admin: `admin@edgemodeapp.com` / `EdgeAdmin2024!`
