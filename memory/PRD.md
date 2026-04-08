# Edge Mode - Product Requirements Document

## Latest Update: 2025-02-08

### Profile Customization System - COMPLETED ✅
- **Profile Themes**: 5 themes (Midnight Purple, Ocean Blue, Sunset Fire, Neon Glow, Golden Legend)
- **Avatar Frames**: 4 frames (Glow, Lightning, Flame, Diamond) with animations
- **Special Effects**: 19 total effects including particles, auras, seasonal, and achievement effects
- **Display Badge**: Users can set a purchased badge to show on profile and leaderboards

### Virtual Pet Email Integration - COMPLETED ✅
- Streak reminders now feature user's pet ("Don't Break Our Streak!")
- Inactive reminders feature pet saying "I need your help to continue my growth!"
- Personalized with pet name, icon, and evolution stage

### Bug Fixes - COMPLETED ✅
- iOS Safari "Failed to load pets" error fixed
- Duplicate email prevention (atomic MongoDB operations)
- Pet Shop visibility (brightened all purchasable pets)

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
- **Friend Challenges (1v1)** - NEW (March 29, 2026)

### Gamification
- 30+ achievement badges
- Opt-in challenges
- Streak milestones and celebrations
- Shareable achievement cards
- **XP & Leveling System** - NEW (April 2, 2026)
- **Daily Login Rewards** - NEW (April 2, 2026)
- **Mutual Friend Streaks** - NEW (April 2, 2026)

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
- [x] Groups & Teams management
  - View all groups with member details
  - Copy invite codes
  - Search/filter groups
  - Edit group names
  - Remove individual members

### Coach Dashboard (March 29, 2026)
- [x] Team Analytics with player stats
- [x] Inactive player alerts
- [x] Bulk messaging to team players

### Gamification
- [x] 30+ achievement badges
- [x] Automated challenges (weekly/monthly)
- [x] **Friend Challenges (1v1)** - NEW (March 29, 2026)
  - Challenge friends via email
  - Competition types: sessions, minutes, consistency
  - Duration: 3 days to 1 month
  - Real-time score tracking
  - Accept/decline challenges
  - Challenge history with win/loss records
  - New badges: friend_challenger, friend_wins_3, friend_wins_10
- [x] Leaderboards (global, school, team)
- [x] Streak system with milestones
- [x] Shareable achievement cards

### Notifications & Engagement
- [x] Social proof section on landing page
- [x] Daily motivational quotes
- [x] Rotating habit quotes
- [x] Push notifications for awards/inactivity
- [x] Email notifications (signup, trial ending)
- [x] Streak reminders (8 PM UTC)
- [x] Weekly summaries (Sunday 2 PM UTC)
- [x] Inactive user reminders (6 PM UTC)
- [x] **Morning Motivation** - NEW (March 29, 2026)
  - Opt-in daily motivational emails at 8 AM Eastern
  - Random inspirational quotes
  - User's pillars displayed
  - Streak status included
  - Toggle in Profile settings

### Technical
- [x] PWA capabilities (ready for App Store)
- [x] US/Eastern timezone handling
- [x] Hot reload for development

---

## Completed This Session (April 8, 2026)

15. **Pet Moods, Voice Lines & Companions UI** ✅
    - **Pet Mood Display** on PetDisplay.jsx:
      - Shows mood icon with animated bounce (ecstatic/happy/content/bored/sad/lonely)
      - Displays contextual voice line based on time of day and streak milestones
      - Color-coded mood badge with happiness percentage
    - **Active Companion Display**:
      - Shows equipped companion with rarity badge
      - Displays bonus info (XP multiplier, coin bonus)
      - One-click navigation to Companions screen
    - **Quick Navigation Links**:
      - Codex, Companions, Souvenirs buttons in 3-column grid
    - All tests passing (100% backend, 100% frontend)

16. **Pet Codex Screen** ✅ (`/pet-codex`)
    - Overall completion percentage with progress bar
    - Tabs for Pets (17 total) and Companions (13 total)
    - Grid view of all pets/companions with owned/locked status
    - Rarity-colored borders and badges
    - Evolution preview (start → max icon)

17. **Companions Screen** ✅ (`/companions`)
    - Collection stats with progress percentage
    - List of all companions with unlock progress bars
    - Rarity badges (Legendary/Epic/Rare/Uncommon/Common)
    - Bonus display (XP multiplier, coin bonus)
    - Activate/Deactivate buttons for owned companions
    - Auto-unlock when milestones are reached

18. **Pet Expeditions** ✅
    - **Trigger**: After logging 59+ minute sessions
    - **Expedition Modal** with animated particles:
      - Shows expedition name based on session pillar (Library Quest, Mountain Trail, Story Forest)
      - Story narrative featuring pet's name
      - Rewards: Coins + XP based on session duration
      - Rare souvenir items with random chance (30-80%)
    - **Rarity Tiers**:
      - Common (59 min): 5-15 coins, 10-25 XP, 30% item chance
      - Uncommon (25-39 min): 15-30 coins, 25-50 XP, 45% item chance
      - Rare (40-59 min): 30-60 coins, 50-100 XP, 60% item chance
      - Legendary (60+ min): 75-150 coins, 100-200 XP, 80% item chance
    - **Souvenirs Collection**: Pebbles, Feathers, Crystals, Dragon Scales, Phoenix Feathers, etc.

19. **Souvenirs Screen** ✅ (`/souvenirs`)
    - Total collected with rarity breakdown
    - Filter buttons: All, Legendary, Rare, Uncommon, Common
    - Grid display with rarity-colored cards
    - Empty state with helpful message about expeditions
    - Shows expedition pillar source for each souvenir

20. **Expedition History / Adventure Log** ✅ (`/expedition-history`)
    - Timeline view of all pet expeditions
    - Stats overview: Total coins earned, XP earned, items found, total trips
    - Rarity filter buttons with counts
    - Each expedition card shows:
      - Pet icon and expedition name
      - Time ago, duration, and pillar
      - Story narrative in styled quote block
      - Rewards earned (coins, XP, souvenir item)
    - Rarity-colored borders and badges

---

## Completed Previous Session (April 2, 2026)

5. **Teen Engagement Features (XP/Leveling, Daily Rewards, Friend Streaks)** ✅
   - Backend: `/app/backend/routes/engagement.py` with 6 endpoints
   - XP System:
     - 10 XP for daily login
     - 25 XP for logging a session (+15 bonus for first session of day)
     - 50 XP for earning badges
     - 75-100 XP for challenges
     - Streak day bonuses (5 XP per day, capped at 100)
   - Leveling: 21 levels with exponential thresholds (100, 250, 500, 800, 1200...)
   - Level Titles: Rookie → Rising Star → Achiever → Champion → Legend → Elite
   - Daily Login Rewards: 5-50 coins based on streak day (7-day cycle)
   - Frontend: `EngagementStatus.jsx` component on Dashboard
   - Mutual Friend Streaks: `FriendStreaks.jsx` showing activity streaks with friends
   - All tests passing (17/17 backend, 100% frontend)

6. **XP Booster Events** ✅
   - Admin can create time-limited XP multiplier events
   - Quick event creators:
     - Double XP Weekend (2x, Sat-Sun)
     - Challenge Rush (custom multiplier, custom duration)
   - Event types: "all", "sessions", "daily_login", "challenges"
   - Multiplier range: 1.0x - 10.0x
   - XPEventBanner component with:
     - Animated shimmer gradient background
     - Event name, multiplier badge (e.g., "3x XP")
     - Description and countdown timer
   - XP transactions log event info (event_id, event_name, multiplier)
   - All tests passing (25/25 backend, 100% frontend)

7. **XP Event Push Notifications** ✅
   - Scheduler job runs every 30 minutes to check for events
   - Notifications when events start (email + push)
   - Notifications 1-2 hours before events end (email + push)
   - Admin manual broadcast: `POST /api/engagement/events/{id}/broadcast`
   - Beautiful HTML email templates for event started and ending soon
   - Push notification functions: send_xp_event_started_push, send_xp_event_ending_push
   - All tests passing (15/15 backend)

8. **XP Shop (Coin Shop)** ✅
   - 5 Categories: Profile Themes, Custom Badges, Streak Shields, Avatar Frames, Special Effects
   - 18 default items seeded automatically
   - Rarity system: Common, Uncommon, Rare, Epic, Legendary (with colored borders)
   - Purchase flow with coin validation
   - Inventory management with equip/unequip
   - Streak Shields are consumable items with uses_remaining
   - Admin endpoints for item CRUD and shop stats
   - Frontend: `ShopScreen.js` with Shop/Inventory tabs, category filters, Featured Items section
   - Dashboard coins display links directly to Shop
   - All tests passing (32/32 backend, 100% frontend)

9. **Daily & Weekly Quests** ✅
   - 5 Daily Quests:
     - Daily Check-In (1 login, 5 coins)
     - One Session Wonder (1 session, 10 coins + 5 XP)
     - Triple Threat (3 sessions, 25 coins + 15 XP)
     - XP Hunter (50 XP, 15 coins)
     - Streak Keeper (maintain streak, 10 coins + 5 XP)
   - 6 Weekly Quests:
     - Consistency Champion (10 sessions, 50 coins + 30 XP)
     - Dedication Master (20 sessions, 100 coins + 50 XP)
     - XP Grinder (200 XP, 40 coins)
     - Perfect Week (7-day streak, 75 coins + 50 XP)
     - Dedicated User (5 login days, 30 coins + 20 XP)
     - Challenge Accepted (2 challenges, 60 coins + 40 XP)
   - Progress tracking integrated with sessions and engagement
   - Claim individual or all rewards
   - Frontend: `Quests.jsx` component with Daily/Weekly tabs on Dashboard
   - All tests passing (24/24 backend, 100% frontend)

10. **Admin Email Announcements** ✅
    - Compose announcements with subject and message
    - Search and select specific users by email/username
    - "Send to All Users" option for bulk announcements
    - Beautiful HTML email template with Edge Mode branding
    - Announcement history with sent/failed counts
    - Frontend: Email Announcements section in Admin Dashboard
    - All tests passing (15/15 backend, 100% frontend)

11. **Economy Rebalance** ✅
    - Reduced daily quest coin rewards (~7 coins/day max)
    - Increased shop item prices (100-600 coins)
    - Pacing: Cheapest item ~2 weeks, Mid-tier ~1 month, Legendary ~3 months

12. **Referral Exclusive Shop Items** ✅ (April 4, 2026)
    - 4 exclusive items only unlockable by referring friends:
      - Recruiter Badge (1 friend)
      - Squad Leader Frame (3 friends)
      - Connector Theme (5 friends)
      - Golden Aura (10 friends)
    - Shop UI enhancements:
      - "Referral" badge (emerald green) on exclusive items
      - Shows "X friends" instead of coin price
      - "Invite" button navigates to /invite page
      - Dedicated "Referral Exclusives" section with green gradient
      - Explanation: "These items can only be unlocked by referring friends"
      - "Invite Friends" link in section header
    - **Referral Qualification System** (3 sessions minimum):
      - Referrals only count after friend logs 3 sessions
      - Flow: Apply code → Status "pending" → 3 sessions → Status "qualified" → Rewards triggered
      - Invite page shows "Qualified Referrals" + "Pending" counts separately
      - Pending referrals display in amber with status text
    - All tests passing (100% backend, 100% frontend)

13. **Virtual Pets** ✅ (April 5, 2026)
    - **MAJOR OVERHAUL (April 6, 2026)** - Based on user's 5 image recommendations
    - **17 New Pet Types:**
      - **Free Starters (9):**
        - Flame Dragon (Blaze) - fire theme, hatches from egg
        - Phoenix (Ember) - rebirth animations on milestones
        - Spirit Wolf (Fenrir) - lightning/storm effects
        - Neon Blob (Gloo) - Pou/Moy inspired, color-changing
        - Cyber Fox (Volt) - LED lights, gears, jetpack
        - Space Jelly (Nova) - bioluminescent jellyfish
        - Sports Tiger (Striker) - ball kicks with sparkly trails
        - Music Siren (Melody) - air guitar, floating notes
        - Study Owl (Scholar) - reads books, lightbulb overhead
      - **Shop Pets (8):**
        - Galaxy Dragon (Cosmos) - 500 coins, legendary
        - Ice Phoenix (Frost) - 400 coins, epic
        - Shadow Kitsune (Umbra) - 450 coins, epic, multi-tail
        - Crystal Golem (Prism) - 300 coins, rare
        - Aqua Serpent (Tide) - 350 coins, rare
        - Mecha Dragon (Titan) - 600 coins, legendary
        - Pixel Sprite (8-Bit) - 200 coins, uncommon
        - Celestial Unicorn (Starlight) - 400 coins, epic
    - **9 Interaction Types with Enhanced Animations:**
      - Pet (💕): Purring/vibrating, heart particles rising, nuzzle
      - Feed (🍖): Treat munch, belly glow, happy dance
      - Play (⚽): Ball chase, pounce, proud return
      - Train (💪): Power stretch, energy burst, power pose
      - Dance (🎵): 360° spin, air guitar, disco lights
      - High-Five (✋): Reach out, bump flash, star burst, confetti
      - Cheer (📣): Hold sign, fist pump, sparkle glow
      - Sleep (💤): Curl up, soft snore, dream bubbles
      - Adventure (🗺️): Explorer gear, walk off-screen, return with trophy
    - Growth-based evolution tied to streaks:
      - Baby (0 days), Young (7 days), Teen (14 days), Adult (30 days), Elder (60 days), Legendary (100 days)
    - Bonuses per evolution: XP bonus (2-10%) + daily coin bonus (1-3)
    - Happiness system with cooldowns on certain interactions
    - Particle effects for each interaction type (hearts, stars, music notes, etc.)
    - Dashboard integration: PetDisplay shows pet widget with all 9 interaction buttons
    - Pet Selection screen at /pets with starter/shop tabs
    - Landing page updated: "Raise a virtual pet that grows with your progress"
    - **CSS Animations:** 40+ unique keyframe animations for all interactions
    - All tests passing (96% backend, 100% frontend)

14. **Pet Accessories & Themed Gear** ✅ (April 6, 2026)
    - **30+ Accessories** across 5 categories:
      - **Hats & Headwear:** Champion Cap, DJ Headphones, Pirate Hat, Space Helmet, Wizard Hat, Party Hat, Crowns
      - **Glasses & Eyewear:** Cool Shades, Cyber Visor, Scholar Glasses, Star Glasses
      - **Collars & Necklaces:** LED Glow Collar, Musical Chain, Crystal Pendant, Friendship Collar
      - **Wings & Back Items:** Butterfly Wings, Flame Wings, Jetpack, Champion Cape, Angel Wings
      - **Auras & Effects:** Sparkle Aura, Fire/Ice/Lightning Aura, Rainbow Trail, Galaxy Swirl, Heart Bubbles, Neon Glow, Music Waves
    - **Milestone-Based Unlocks** (with achievement badges awarded):
      - 7-day streak → 🔥 Week Warrior badge + 🎉 Party Hat, ✨ Sparkle Aura
      - 21-day streak → 🔥 Three Week Titan badge + 🧙 Wizard Hat
      - 45-day streak → 🔥 Six Week Superstar badge + 👓 Scholar Glasses, 🌈 Rainbow Trail
      - 60-day streak → 🔥 Two Month Titan badge + ⭐ Star Glasses
      - 90-day streak → 🔥 Quarter Master badge + 👑 Golden Crown, 🌌 Galaxy Swirl
      - 120-day streak → 👑 Four Month Legend badge + 💎 Diamond Crown, 👼 Angel Wings
      - 5 referrals → 🤝 Friend Magnet badge + 💕 Friendship Collar
    - **Shop Purchases** - 19 items (75-450 coins)
    - **Theme Matching Bonus** - Accessories matching pet theme get visual highlight
    - **5 Equipment Slots:** Head, Face, Neck, Back, Aura
    - **Accessories Screen** at `/pets/accessories` with Shop/Inventory/Unlock tabs
    - All tests passing (100% backend, 100% frontend)

## Previous Session (March 29, 2026)

1. **Coach Tools (Team Analytics & Bulk Messaging)** ✅
   - Fixed API path mismatch in CoachDashboard.js
   - Team analytics dashboard working
   - Bulk email messaging to players
   - Inactive player alerts

2. **Morning Reminder Notifications** ✅
   - New notification setting (morning_reminders)
   - Scheduler job at 1 PM UTC (8 AM Eastern)
   - HTML email template with motivational quotes
   - User's pillars and streak displayed
   - Profile page toggle with "New" badge

3. **Friends Challenges (1v1)** ✅
   - Full CRUD for 1v1 challenges
   - Create challenge with friend's email
   - Competition types: sessions, minutes, consistency
   - Duration options: 3 days, 1 week, 2 weeks, 1 month
   - Accept/decline pending challenges
   - Real-time score tracking during active challenges
   - Challenge history with win/loss records
   - New badges for friend challenges
   - FriendChallenges.jsx component
   - Integrated into ChallengesScreen.js

4. **Simplified Parent Access Flow** ✅
   - Parents no longer need to create an account
   - Student adds parent's email directly
   - Parent immediately starts receiving:
     - Weekly progress reports (Sunday 3 PM UTC)
     - Streak milestone notifications (7, 14, 30 days)
     - Achievement/badge notifications
     - Inactivity alerts (3+ days no activity)
   - Maximum 2 parent emails per student
   - Updated FamilyScreen.js with "How it works" explanation
   - Backwards compatible with legacy /api/parent/invite endpoint

---

## Upcoming Tasks (Prioritized)

### P1
- **Export Data (CSV)** - Download session history

### P2
- **Streak Recovery** - Save a streak once per month if missed
- "Streak Shield" subscription tier ($0.99/mo)

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
- Backend: `/app/backend/routes/auth.py`, `/app/backend/routes/payments.py`, `/app/backend/routes/challenges.py`
- Backend Engagement: `/app/backend/routes/engagement.py` (XP, Levels, Daily Rewards, Friend Streaks, XP Events)
- Backend Shop: `/app/backend/routes/shop.py` (Coin Shop, Items, Inventory, Purchases)
- Backend Quests: `/app/backend/routes/quests.py` (Daily & Weekly Quests)
- Backend Referrals: `/app/backend/routes/referrals.py` (Referral milestones, exclusive items)
- Backend Pets: `/app/backend/routes/pets.py` (Virtual Pets - ownership, evolution, interactions, mood, companions, codex, expeditions)
- Frontend: `/app/frontend/src/pages/Dashboard.js`, `/app/frontend/src/pages/ChallengesScreen.js`
- Frontend Engagement: `/app/frontend/src/components/EngagementStatus.jsx`, `/app/frontend/src/components/FriendStreaks.jsx`
- Frontend Shop: `/app/frontend/src/pages/ShopScreen.js` (includes Referral Exclusives section)
- Frontend Quests: `/app/frontend/src/components/Quests.jsx`
- Frontend Invite: `/app/frontend/src/pages/InviteFriendsScreen.js` (Referral milestones, invite link)
- Frontend Pets: `/app/frontend/src/components/PetDisplay.jsx`, `/app/frontend/src/pages/PetSelectionScreen.js`
- Frontend Pet Features: `/app/frontend/src/pages/PetCodexScreen.js`, `/app/frontend/src/pages/CompanionsScreen.js`, `/app/frontend/src/pages/SouvenirsScreen.js`, `/app/frontend/src/components/ExpeditionModal.jsx`
- Coach: `/app/frontend/src/pages/CoachDashboard.js`
- Admin: `/app/frontend/src/pages/AdminDashboard.js`

## Test Credentials
- Admin: `admin@edgemodeapp.com` / `EdgeAdmin2024!`
- Coach: `testcoach@edgemode.com` / `TestCoach123!`
- Test Player: `testplayer1@edgemode.com` / `TestPlayer123!`
