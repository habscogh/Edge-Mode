# Edge Mode - Product Requirements Document

## Overview
Mobile-first self-improvement app for teens (12-19). Core concept: "1% Better Every Day"

**Live URL:** https://edgemodeapp.com
**Preview URL:** https://daily-improvement-1.preview.emergentagent.com

## Tech Stack
- **Backend:** FastAPI (Python), APScheduler
- **Frontend:** React, Tailwind CSS, Shadcn UI
- **Database:** MongoDB Atlas
- **Auth:** JWT tokens
- **Payments:** Stripe (TEST mode)
- **Email:** Resend (noreply@edgemodeapp.com)

## Features (All Complete)

### Core
- User auth (signup/login)
- 14-day free trial (updated from 7 days)
- Trial Expired screen with subscription prompt (auto-redirect for expired trials)
- Onboarding (select 3-5 pillars, set weekly targets)
- Dashboard with metrics & 30-day graph
- Session logging with notes
- Session history (calendar view)
- Edit/delete sessions
- Quick Log on dashboard

### Social
- Private groups with invite codes
- Global leaderboard (opt-in)

### Ratings
- Performance Rating (Elite → Getting Started)
- Consistency Rating

### Email Notifications (Automatic)
- Streak reminders: 3 PM Eastern daily
- Inactive reminders: 2 PM Eastern (3-7 days inactive)
- Weekly summaries: Sunday 10 AM Eastern

### Admin
- Admin Dashboard at `/admin`
- Stats: users, sessions, subscriptions
- Recent signups & activity
- Access: admin@edgemodeapp.com only

### Other
- Stripe subscriptions ($5.99/mo, $59.99/yr)
- Password reset
- Profile settings
- Privacy Policy & Terms of Service
- "1 session = 30 minutes" guidance

## Future Enhancements
- [ ] FAQ/Help Section
- [ ] Achievements/Badges
- [ ] Social Sharing
- [ ] Mobile PWA

## Test Credentials
- Stripe Test Card: 4242 4242 4242 4242
