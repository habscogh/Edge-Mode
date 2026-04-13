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

## Shop Items
- 7 themes, 21 badges (incl. 6 athletic), 5 frames, 8 effects, 6 sport vehicles
- 16 premium pets purchasable with coins

## Virtual Pets (25 total)
### Free Starters (9)
- Blaze (flame_dragon), Ember (phoenix), Fenrir (spirit_wolf)
- Gloo (neon_blob), Volt (cyber_fox), Nova (space_jelly)
- Striker (sports_tiger), Melody (music_siren), Scholar (study_owl)

### Premium Pets (8 original)
- Cosmos (galaxy_dragon) 500, Frost (ice_phoenix) 400, Umbra (shadow_kitsune) 450
- Prism (crystal_golem) 300, Tide (aqua_serpent) 350, Titan (mecha_dragon) 600
- 8-Bit (pixel_sprite) 200, Starlight (unicorn_celestial) 400

### Exotic Premium Pets (8 new - Apr 12, 2026)
- Abyssal (kraken) 550, Zephyr (thunderbird) 425, Havoc (chimera) 650
- Dune (sand_wyrm) 300, Cipher (neon_tiger) 450, Zodiac (astral_serpent) 325
- Phantom (shadow_panther) 400, Magmus (lava_golem) 500

## Completed Work (Apr 12, 2026)
- Fixed weekly summary email date format bug
- Fixed inactive reminders type bug
- Added 6 athletic badges + 6 sport vehicles to shop
- Added 8 exotic premium pets (kraken, thunderbird, chimera, sand_wyrm, neon_tiger, astral_serpent, shadow_panther, lava_golem)

## Upcoming Tasks
- P1: Export Data (CSV) - download session history
- P2: Streak Recovery - recover streak once/month

## Future/Backlog
- P3: "Streak Shield" subscription tier ($0.99/mo)
- P3: Refactor AdminDashboard.js (1300+ lines)
- Offline session sync delay (PWA queue logic)
