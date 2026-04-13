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
- Virtual Pets System (25 total: 9 starters + 16 premium/exotic)
- Monetization ($4.99/mo or $49.99/yr, free trial via Stripe)
- PWA & UX (installable, offline support)
- Push Notifications, Email Schedulers
- Shareable Story Cards, Evolution Tree, Pet Codex, Expeditions
- Coin Earning Info Sheet (bottom sheet on dashboard coin tap)

## Shop Items
- 7 themes, 21 badges (incl. 6 athletic), 5 frames, 8 effects, 6 sport vehicles
- 16 premium pets purchasable with coins

## Virtual Pets (25 total)
### Free Starters (9)
- Blaze, Ember, Fenrir, Gloo, Volt, Nova, Striker, Melody, Scholar

### Premium Pets (16)
- Original 8: Cosmos, Frost, Umbra, Prism, Tide, Titan, 8-Bit, Starlight
- Exotic 8: Abyssal, Zephyr, Havoc, Dune, Cipher, Zodiac, Phantom, Magmus

## Coin Earning Methods (displayed in bottom sheet)
- Daily Login: 1-5 coins/day
- Quests: 1-10 coins each
- Pet Expeditions: 2-25 coins (59+ min sessions)
- Pet Evolution Bonus: +1-3 coins/session
- Referrals: 25-300 coins per milestone
- Companions: +1-5 coins/session

## Completed Work (Apr 13, 2026)
- Fixed weekly summary email date format bug
- Added 6 athletic badges + 6 sport vehicles to shop
- Added 8 exotic premium pets
- Added "Ways to Earn Coins" bottom sheet on dashboard coin tap

## Upcoming Tasks
- P1: Export Data (CSV) - download session history
- P2: Streak Recovery - recover streak once/month

## Future/Backlog
- P3: "Streak Shield" subscription tier ($0.99/mo)
- P3: Refactor AdminDashboard.js (1300+ lines)
- Offline session sync delay (PWA queue logic)
