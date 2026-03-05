# Edge Mode - Product Requirements Document

## Overview
Mobile-first self-improvement app for teens (12-19). Core concept: "1% Better Every Day"

**Live URL:** https://edgemodeapp.com
**Preview URL:** https://daily-progress-96.preview.emergentagent.com

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

### Milestone Celebrations
- Automatic popup when users hit streak milestones (7, 14, 30, 50, 100 days)
- Celebratory modal with confetti animation
- Shows streak count and motivational message
- Built-in share buttons (Twitter, Facebook, Copy)
- "Keep Going!" button to continue

### Invite Friends / Referrals
- Unique referral code for each user (auto-generated)
- Shareable invite link: `edgemodeapp.com/auth?ref=CODE`
- Copy link/code to clipboard
- Email invite: sends branded email to friend with invite link
- Tracks successful referrals (friend signups)
- Referral code input field on signup form
- Accessible from Profile page at `/invite`
- No limits on referrals

### FAQ / Help Center
- Comprehensive FAQ page at `/faq`
- 6 categories: Getting Started, Streaks & Progress, Badges & Achievements, Subscription & Pricing, Groups & Social, Account & Privacy
- Accordion-style expandable questions
- Contact support link (support@edgemodeapp.com)
- Links to Privacy Policy and Terms of Service
- Accessible from:
  - Landing page footer
  - Profile page

### Email Notifications (Automatic)
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
- Stripe subscriptions ($4.99/mo, $49.99/yr) - TEST MODE
- Password reset
- Profile settings
- Privacy Policy & Terms of Service
- "1 session = 30 minutes" guidance
- **Pillar Management** - Users can add/remove/edit pillars from Profile page

### Opt-In Challenges (NEW - March 2026)
- **Challenge Types:**
  - Weekly challenges (Monday-Sunday)
  - Monthly challenges (1st of month to end of month)
- **Competition Categories:**
  - Pillar-specific: Most sessions in a specific pillar (e.g., Fitness, Study)
  - General: Highest consistency %, most total minutes, most total sessions
- **Features:**
  - Browse all available challenges at `/challenges`
  - Join/leave challenges freely
  - Real-time leaderboard rankings
  - View participants and their scores
  - Filter by: All, My Challenges, Weekly, Monthly
- **Rewards/Badges:**
  - 🏅 Weekly Champion - Win a weekly challenge
  - 🥇 Monthly Champion - Win a monthly challenge
  - 🎖️ Podium Finish - Finish in top 3
  - 🏆 Challenge Streak - Win 3 challenges
- **Automation:**
  - Challenges auto-created via scheduled job (12:05 AM UTC daily)
  - **Auto-seeding on startup**: If no active challenges exist, 6 initial challenges are seeded automatically
  - Badges auto-awarded when challenges complete
- **Visibility:** Everyone can view, only participants compete

### Coach Mode in Groups (NEW - March 2026)
- **Coach Role:**
  - Enable "Coach Mode" when creating a group
  - Coach can view all players' detailed stats (view-only)
  - Coach Dashboard shows team overview and individual player details
- **Team Stats:**
  - Total players, average consistency, average performance
  - Total sessions this week across team
- **Player Details (Coach View):**
  - Current streak, consistency %, performance index
  - Pillar breakdown with sessions vs targets
  - Last active date
  - Detailed player modal with weekly stats, pillars, badges
- **Access:**
  - Only coach can access coach dashboard (403 for others)
  - Players see regular group leaderboard

### Parent-Student Linking (NEW - March 2026)
- **Student Actions:**
  - Invite parents from Profile > Family Access
  - Enter parent's email address
  - Maximum 2 parents per student
  - View pending/active parent links
  - Unlink parents at any time
- **Parent Actions:**
  - Receive email invitation with code (PARENT-XXXXXX format)
  - Create account and accept invite with code
  - View linked students' dashboards
- **Parent Dashboard:**
  - View student's current streak, weekly stats, monthly stats
  - See pillar breakdown with progress bars
  - View badges earned count
  - See recent activity (last 5 sessions)
- **Notifications:**
  - Parents receive progress notifications (via email)

## Bug Fixes (March 2026)
- **Timezone Bug Fixed**: All stats endpoints (`/api/stats/comparison`, `/api/stats/weekly`, `/api/stats/weekly-review`, `/api/stats/history`) now accept `local_date` parameter from frontend to ensure dashboard shows correct "today" and "yesterday" counts based on user's local timezone
- **Variable Shadowing Bug Fixed**: Fixed issue in `/api/stats/history` where loop variable `date` shadowed the `date` class, causing errors when `local_date` parameter was provided

## Future Enhancements
- [ ] **P1: Refactor server.py** into separate routers (auth, sessions, badges, groups, admin, challenges) - File is now 2900+ lines
- [ ] Mobile PWA optimization
- [ ] Add referral rewards (e.g., free month for 3+ referrals)
- [ ] Admin challenge management UI (manual challenge creation)

## Test Credentials
- Stripe Test Card: 4242 4242 4242 4242
