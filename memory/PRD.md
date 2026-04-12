# Edge Mode - Product Requirements Document

## Original Problem Statement
Build a mobile-first, full-stack application named "Edge Mode" to help teens (12-19) systematically improve themselves. Core idea: "1% Better Every Day," turning self-improvement into a data-driven, game-like experience.

## Tech Stack
- Frontend: React, Tailwind CSS, html2canvas
- Backend: FastAPI, APScheduler
- Database: MongoDB
- 3rd Party: Stripe (Payments), Resend (Emails)

## Core Features (Implemented)
- User Tracking & Onboarding (pillars, weekly targets)
- Core Metrics & Dashboards (streaks, performance)
- Social Features (private groups, school/global leaderboards, friend challenges)
- Gamification (badges, challenges, XP/Leveling, Shop, Quests, Referrals)
- Virtual Pets System (evolutions, interactions, happiness, moods, companions, codex, expeditions)
- Monetization ($4.99/mo or $49.99/yr, free trial via Stripe)
- PWA & UX (installable, offline support)
- Push Notifications (VAPID web push)
- Email Schedulers (streak reminders, weekly summaries, inactive reminders, morning motivation, trial ending, parent reports, XP event notifications)
- Shareable Story Cards (html2canvas)
- Evolution Tree Visual UI
- Shop Items (7 themes, 10 badges, 5 frames, 8 effects) & Pet Accessories
- Duplicate session prevention (frontend disable + backend 2-min check)
- Email deduplication (atomic email_log collection)
- Profile Customizations

## Architecture
```
/app/
├── backend/
│   ├── server.py
│   ├── routes/ (pets, shop, sessions, challenges, engagement, quests, referrals, push, parent, auth)
│   └── utils/ (scheduler_jobs, streaks, badges, timezone, auth)
└── frontend/
    └── src/
        ├── components/ (PetDisplay, ExpeditionModal, ShareableStoryCard, etc.)
        ├── pages/ (Dashboard, LogScreen, ProfileScreen, EvolutionTreeScreen, AdminDashboard, etc.)
        └── App.js
```

## Key DB Collections
- `users`, `daily_sessions`, `user_pillars`, `user_pets`, `shop_items`, `email_log`, `challenges`, `xp_events`, `parent_links`

## Completed Work (Latest Session - Apr 12, 2026)
- Fixed weekly summary email query: normalized date format from `.isoformat()` to `.strftime('%Y-%m-%d')` for consistent MongoDB string comparison
- Fixed inactive reminders type bug: `today_eastern` was string but used in date arithmetic  
- Fixed parent weekly summary and inactivity alerts date formats
- Standardized all scheduler date queries to use explicit `strftime('%Y-%m-%d')`

## P0 Issues (Resolved)
- Weekly summary emails reporting 0 sessions: FIXED (date format normalization)
- Duplicate session logging: FIXED
- Duplicate scheduler emails: FIXED
- Profile customizations not saving: FIXED

## Upcoming Tasks
- P1: Export Data (CSV) - Allow users to download their session history
- P2: Streak Recovery - Allow users to recover a streak once per month

## Future/Backlog
- P3: "Streak Shield" subscription tier ($0.99/mo)
- P3: Refactor AdminDashboard.js (exceeds 1300 lines)
- Offline session sync delay (PWA queue logic)
