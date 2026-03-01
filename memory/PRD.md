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
- **Trial Ending Banner** - Shows on dashboard when 3 days or less remaining
- Trial Expired screen with "What You'll Lose" personalized warning
- Onboarding (select 3-5 pillars, set weekly targets)
- Dashboard with metrics & 30-day graph
- Session logging with notes
- Session history (calendar view)
- Edit/delete sessions
- Quick Log on dashboard

### Achievements/Badges System
- **8 badges available:**
  - 🏆 First Step - Log your first session
  - 🔥 Week Warrior - Maintain a 7-day streak
  - 🔥 Fortnight Fighter - Maintain a 14-day streak
  - 🔥 Monthly Master - Maintain a 30-day streak
  - 💯 Century Club - Complete 100 sessions
  - ⏱️ 50 Hour Club - Log 50+ hours total
  - ✨ Perfect Week - Log every day for a week
  - 🎯 Pillar Master - Hit target on all pillars in a week
- Dedicated Achievements page at `/achievements`
- Badge summary on Profile page (links to full achievements)
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
- Shareable content:
  - Individual badges (from Achievements page)
  - Badge collection summary
  - Weekly stats (from Weekly Review page)
  - Streak milestones
- All shares include app link (edgemodeapp.com) for user acquisition
- Native Web Share API support for mobile devices
- Streak reminders: 3 PM Eastern daily (for users with active streaks who haven't logged)
- Inactive reminders: 2 PM Eastern (for 3-7 days inactive users)
- **Trial ending reminders: 12 PM Eastern daily (for users with 1-3 days left on trial)**
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
- [ ] Social Sharing (share achievements on social media)
- [ ] Mobile PWA
- [ ] Refactor server.py into separate routers

## Test Credentials
- Stripe Test Card: 4242 4242 4242 4242
