# Edge Mode - Product Requirements Document

## Original Problem Statement
Build a mobile-first, full-stack application named "Edge Mode" to help teens (12-19) systematically improve themselves. Core idea: "1% Better Every Day," turning self-improvement into a data-driven, game-like experience.

## Tech Stack
- Frontend: React, Tailwind CSS, html2canvas
- Backend: FastAPI, APScheduler
- Database: MongoDB
- 3rd Party: Stripe (Payments), Resend (Emails)

## Core Features (Implemented)
- User Tracking & Onboarding, Dashboards, Social Features
- Gamification (badges, challenges, XP/Leveling, Shop, Quests, Referrals)
- Virtual Pets System (25 total), Expeditions, Pet Codex
- Monetization via Stripe, Email Schedulers via Resend
- PWA, Push Notifications, Shareable Story Cards
- Coin Earning Info Sheet (bottom sheet on dashboard coin tap)

## Shop Items
- 7 themes, 21 badges (incl. 6 athletic), 5 frames, 8 effects, 6 sport vehicles
- 16 premium pets purchasable with coins

## Email Deduplication System (Fixed Apr 15, 2026)
All scheduler email jobs now use atomic `find_one_and_update` to claim one user at a time:
- `send_streak_reminders_job`: Converted from batch-query-then-loop to atomic claim pattern
- `send_weekly_summaries_job`: Already used atomic pattern
- `send_inactive_reminders_job`: Already used atomic per-user claim
- `send_morning_reminders_job`: Already used atomic per-user claim
- Secondary dedup via `email_log` collection with unique compound index
- Scheduler lock acquisition made atomic to prevent two instances starting

## Completed Work (Apr 15, 2026)
- Fixed double streak reminder emails: converted to atomic find_one_and_update per user
- Fixed scheduler lock race condition: atomic lock acquisition
- Fixed date format bugs in weekly summary and inactive reminders
- Added 6 athletic badges, 6 sport vehicles, 8 exotic pets
- Added "Ways to Earn Coins" bottom sheet

## Upcoming Tasks
- P1: Export Data (CSV) - download session history
- P2: Streak Recovery - recover streak once/month

## Future/Backlog
- P3: "Streak Shield" subscription tier ($0.99/mo)
- P3: Refactor AdminDashboard.js (1300+ lines)
- Offline session sync delay (PWA queue logic)
