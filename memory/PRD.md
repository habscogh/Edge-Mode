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
- Coin Earning Info Sheet (bottom sheet on dashboard)
- Vehicle Garage: equip vehicles on profile + dashboard flex

## Shop Items
- 7 themes, 21 badges (incl. 6 athletic), 5 frames, 8 effects, 6 sport vehicles
- 16 premium pets purchasable with coins

## Vehicle System (New)
- Vehicles purchasable in shop, equippable via Profile > Customize > Garage tab
- Equipped vehicle shows on Profile header (visible to others)
- Equipped vehicle shows as "My Ride" flex on Dashboard stats row
- Backend: `POST /api/shop/set-vehicle`, `GET /api/shop/available-vehicles`
- Stored as `active_vehicle` on user document

## Admin Debug Endpoints
- `GET /api/admin/debug-weekly-summary` — diagnose session queries
- `POST /api/admin/reset-weekly-summary-flags` — clear sent markers
- `POST /api/admin/trigger-weekly-summary` — manually re-trigger

## Upcoming Tasks
- P1: Export Data (CSV) - download session history
- P2: Streak Recovery - recover streak once/month

## Future/Backlog
- P3: "Streak Shield" subscription tier ($0.99/mo)
- P3: Refactor AdminDashboard.js (1300+ lines)
- Offline session sync delay (PWA queue logic)
