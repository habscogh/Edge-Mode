# Edge Mode - Product Requirements Document

## Original Problem Statement
Build a mobile-first, full-stack application named "Edge Mode" to help teens (12-19) systematically improve themselves. The core idea is "1% Better Every Day," turning self-improvement into a data-driven, game-like experience.

## Tech Stack
- **Backend:** FastAPI (Python)
- **Frontend:** React, JavaScript, Tailwind CSS, Shadcn UI
- **Database:** MongoDB Atlas (production)
- **Authentication:** JWT tokens
- **Payments:** Stripe (TEST mode)
- **Email:** Resend (noreply@edgemodeapp.com)
- **Scheduler:** APScheduler (automatic emails)

## What's Been Implemented (All Complete)

### Phase 1 - Core Features
- [x] Landing page with Edge Mode branding
- [x] User authentication (signup, login, logout)
- [x] 7-day app-based free trial
- [x] Multi-step onboarding (pillar/target selection)
- [x] Dashboard with performance metrics and 30-day graph
- [x] Session logging
- [x] Weekly review page
- [x] Profile with account management
- [x] Private groups with invite codes
- [x] Global leaderboard (opt-in)
- [x] Stripe subscription (monthly/yearly)
- [x] Password reset flow
- [x] Privacy Policy & Terms of Service

### Phase 2 - Engagement Features
- [x] Edit/Delete Sessions UI
- [x] Quick Log on Dashboard
- [x] Session History page (calendar view)
- [x] Notes on sessions
- [x] Performance Ratings (Elite, High Performer, On Track, Building, Getting Started)
- [x] Notification settings in Profile

### Phase 3 - Automatic Email Notifications
- [x] Streak reminders (3:00 PM Eastern daily)
- [x] Inactive user reminders (2:00 PM Eastern, 3-7 days inactive)
- [x] Weekly summaries (Sunday 10:00 AM Eastern)
- [x] APScheduler integration for automatic sending
- [x] User toggle controls in Profile

## Deployment
- **Live URL:** https://edgemodeapp.com
- **Email Domain:** Verified (noreply@edgemodeapp.com)
- **Stripe:** TEST mode (card: 4242 4242 4242 4242)

## Prioritized Backlog

### P2 - Future Enhancements
- [ ] FAQ/Help Section
- [ ] Achievements/Badges system
- [ ] Social Sharing buttons
- [ ] Mobile PWA optimization

## Test Credentials
- Create new user via signup
- Stripe Test Card: 4242 4242 4242 4242 (any future expiry, any CVC)
