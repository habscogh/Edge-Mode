"""
Virtual Pets routes for Edge Mode - Pet ownership, evolution, interactions
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from pydantic import BaseModel
import uuid
import random

from config import db
from utils.auth import get_current_user

router = APIRouter(prefix="/pets", tags=["Pets"])


# ============ Pet Definitions ============

# Evolution stages based on streak days
EVOLUTION_STAGES = {
    1: {"name": "Baby", "streak_required": 0, "xp_bonus": 0, "coin_bonus": 0},
    2: {"name": "Young", "streak_required": 7, "xp_bonus": 0.02, "coin_bonus": 1},
    3: {"name": "Teen", "streak_required": 14, "xp_bonus": 0.03, "coin_bonus": 1},
    4: {"name": "Adult", "streak_required": 30, "xp_bonus": 0.05, "coin_bonus": 2},
    5: {"name": "Elder", "streak_required": 60, "xp_bonus": 0.07, "coin_bonus": 2},
    6: {"name": "Legendary", "streak_required": 100, "xp_bonus": 0.10, "coin_bonus": 3}
}

# Pet types with their appearances at each stage
# New Fantasy/Sci-Fi themed pets with enhanced animations

PET_TYPES = {
    # ============ FREE STARTERS ============
    # Fantasy Mythical Creatures
    "flame_dragon": {
        "name": "Blaze",
        "category": "fantasy",
        "description": "A tiny dragon hatchling that grows wings and breathes sparkles as you progress",
        "rarity": "common",
        "price": 0,
        "is_starter": True,
        "theme": "fire",
        "habit_tie": "exercise",
        "stages": {
            1: {"icon": "🥚", "name": "Dragon Egg", "aura": "warm_glow"},
            2: {"icon": "🦎", "name": "Tiny Hatchling", "aura": "small_flames"},
            3: {"icon": "🐉", "name": "Young Drake", "aura": "fire_breath"},
            4: {"icon": "🐉", "name": "Fire Drake", "aura": "flame_wings"},
            5: {"icon": "🐲", "name": "Inferno Dragon", "aura": "blazing_aura"},
            6: {"icon": "🐲", "name": "Cosmic Dragon", "aura": "galaxy_flames"}
        }
    },
    "phoenix": {
        "name": "Ember",
        "category": "fantasy",
        "description": "A mystical firebird that glows brighter and can 'rebirth' with dramatic animations on streak milestones",
        "rarity": "common",
        "price": 0,
        "is_starter": True,
        "theme": "fire",
        "habit_tie": "general",
        "stages": {
            1: {"icon": "🪺", "name": "Phoenix Egg", "aura": "warm_pulse"},
            2: {"icon": "🐦", "name": "Flame Chick", "aura": "feather_glow"},
            3: {"icon": "🐦‍🔥", "name": "Fire Fledgling", "aura": "wing_flames"},
            4: {"icon": "🐦‍🔥", "name": "Blazing Phoenix", "aura": "rebirth_ready"},
            5: {"icon": "🔥", "name": "Inferno Phoenix", "aura": "eternal_flame"},
            6: {"icon": "🔥", "name": "Neon Phoenix", "aura": "particle_trails"}
        }
    },
    "spirit_wolf": {
        "name": "Fenrir",
        "category": "fantasy",
        "description": "An elemental wolf that evolves with stronger armor and storm effects based on your habits",
        "rarity": "common",
        "price": 0,
        "is_starter": True,
        "theme": "lightning",
        "habit_tie": "sports",
        "stages": {
            1: {"icon": "🐺", "name": "Wolf Pup", "aura": "soft_glow"},
            2: {"icon": "🐺", "name": "Storm Cub", "aura": "spark_fur"},
            3: {"icon": "🐺", "name": "Thunder Wolf", "aura": "lightning_coat"},
            4: {"icon": "🐺", "name": "Storm Guardian", "aura": "electric_armor"},
            5: {"icon": "🐺", "name": "Tempest Alpha", "aura": "storm_aura"},
            6: {"icon": "🐺", "name": "Legendary Fenrir", "aura": "cosmic_storm"}
        }
    },
    
    # Sci-Fi & Alien Creatures
    "neon_blob": {
        "name": "Gloo",
        "category": "scifi",
        "description": "An adorable alien blob with glowing neon skin and eyes that change color based on your habits",
        "rarity": "common",
        "price": 0,
        "is_starter": True,
        "theme": "neon",
        "habit_tie": "study",
        "stages": {
            1: {"icon": "🫧", "name": "Tiny Blob", "aura": "soft_pulse"},
            2: {"icon": "👾", "name": "Glowing Blob", "aura": "neon_skin"},
            3: {"icon": "👾", "name": "Smart Blob", "aura": "brain_glow"},
            4: {"icon": "👽", "name": "Genius Blob", "aura": "wisdom_aura"},
            5: {"icon": "👽", "name": "Elder Blob", "aura": "multi_eye_glow"},
            6: {"icon": "👽", "name": "Cosmic Blob", "aura": "galaxy_core"}
        }
    },
    "cyber_fox": {
        "name": "Volt",
        "category": "scifi",
        "description": "A robotic cyber-fox with LED lights, gears, and upgrade animations like jetpack bursts",
        "rarity": "common",
        "price": 0,
        "is_starter": True,
        "theme": "tech",
        "habit_tie": "general",
        "stages": {
            1: {"icon": "🦊", "name": "Proto Fox", "aura": "led_eyes"},
            2: {"icon": "🦊", "name": "Cyber Kit", "aura": "gear_spin"},
            3: {"icon": "🦊", "name": "Mech Fox", "aura": "holo_shield"},
            4: {"icon": "🦊", "name": "Cyber Guardian", "aura": "jetpack_ready"},
            5: {"icon": "🦊", "name": "Neon Kitsune", "aura": "multi_tail_led"},
            6: {"icon": "🦊", "name": "Shadow Kitsune", "aura": "nine_tail_holo"}
        }
    },
    "space_jelly": {
        "name": "Nova",
        "category": "scifi",
        "description": "A floating jellyfish from another planet with customizable helmet and bioluminescent trails",
        "rarity": "common",
        "price": 0,
        "is_starter": True,
        "theme": "cosmic",
        "habit_tie": "music",
        "stages": {
            1: {"icon": "🪼", "name": "Space Polyp", "aura": "bio_glow"},
            2: {"icon": "🪼", "name": "Star Jelly", "aura": "tentacle_lights"},
            3: {"icon": "🪼", "name": "Nebula Jelly", "aura": "cosmic_pulse"},
            4: {"icon": "🪼", "name": "Galaxy Drifter", "aura": "star_trail"},
            5: {"icon": "🪼", "name": "Void Walker", "aura": "dimension_shift"},
            6: {"icon": "🪼", "name": "Cosmic Ancient", "aura": "universe_glow"}
        }
    },
    
    # Activity-Themed Starters
    "sports_tiger": {
        "name": "Striker",
        "category": "activity",
        "description": "An athletic tiger that kicks balls leaving sparkly trails and celebrates with victory dances",
        "rarity": "common",
        "price": 0,
        "is_starter": True,
        "theme": "sports",
        "habit_tie": "sports",
        "stages": {
            1: {"icon": "🐯", "name": "Tiger Cub", "aura": "energy_spark"},
            2: {"icon": "🐯", "name": "Young Striker", "aura": "ball_chase"},
            3: {"icon": "🐯", "name": "Swift Tiger", "aura": "speed_trail"},
            4: {"icon": "🐯", "name": "Champion Tiger", "aura": "medal_glow"},
            5: {"icon": "🐯", "name": "MVP Tiger", "aura": "trophy_shine"},
            6: {"icon": "🐯", "name": "Legend Striker", "aura": "hall_of_fame"}
        }
    },
    "music_siren": {
        "name": "Melody",
        "category": "activity",
        "description": "A melodic siren that plays air guitar, sways to beats, and has bouncing headphones",
        "rarity": "common",
        "price": 0,
        "is_starter": True,
        "theme": "music",
        "habit_tie": "music",
        "stages": {
            1: {"icon": "🧜", "name": "Little Siren", "aura": "note_bubble"},
            2: {"icon": "🧜", "name": "Singing Siren", "aura": "floating_notes"},
            3: {"icon": "🧜‍♀️", "name": "Melodic Siren", "aura": "music_waves"},
            4: {"icon": "🧜‍♀️", "name": "Star Singer", "aura": "concert_lights"},
            5: {"icon": "🧜‍♀️", "name": "Diva Siren", "aura": "headphone_glow"},
            6: {"icon": "🧜‍♀️", "name": "Legendary Siren", "aura": "symphony_aura"}
        }
    },
    "study_owl": {
        "name": "Scholar",
        "category": "activity",
        "description": "A wise owl with glasses that reads glowing books and shows lightbulbs overhead when you study",
        "rarity": "common",
        "price": 0,
        "is_starter": True,
        "theme": "wisdom",
        "habit_tie": "study",
        "stages": {
            1: {"icon": "🦉", "name": "Owlet", "aura": "curious_eyes"},
            2: {"icon": "🦉", "name": "Young Owl", "aura": "reading_glow"},
            3: {"icon": "🦉", "name": "Scholar Owl", "aura": "book_flip"},
            4: {"icon": "🦉", "name": "Professor Owl", "aura": "lightbulb_pop"},
            5: {"icon": "🦉", "name": "Sage Owl", "aura": "wisdom_aura"},
            6: {"icon": "🦉", "name": "Grand Master", "aura": "knowledge_burst"}
        }
    },
    
    # ============ SHOP PREMIUM PETS ============
    # Rare Variants
    "galaxy_dragon": {
        "name": "Cosmos",
        "category": "fantasy",
        "description": "A rare Galaxy Dragon with starry patterns - unlocked after 30-day streaks with vibrant cosmic effects",
        "rarity": "legendary",
        "price": 500,
        "is_starter": False,
        "theme": "cosmic",
        "habit_tie": "general",
        "stages": {
            1: {"icon": "🌌", "name": "Cosmic Egg", "aura": "star_dust"},
            2: {"icon": "🐉", "name": "Star Hatchling", "aura": "nebula_glow"},
            3: {"icon": "🐉", "name": "Nebula Drake", "aura": "galaxy_breath"},
            4: {"icon": "🐲", "name": "Void Dragon", "aura": "black_hole"},
            5: {"icon": "🐲", "name": "Universe Dragon", "aura": "supernova"},
            6: {"icon": "🐲", "name": "Dimension Lord", "aura": "multiverse"}
        }
    },
    "ice_phoenix": {
        "name": "Frost",
        "category": "fantasy",
        "description": "An elegant ice phoenix with shimmering frost feathers and crystalline rebirth animations",
        "rarity": "epic",
        "price": 400,
        "is_starter": False,
        "theme": "ice",
        "habit_tie": "general",
        "stages": {
            1: {"icon": "❄️", "name": "Frost Egg", "aura": "ice_crystal"},
            2: {"icon": "🐦", "name": "Snow Chick", "aura": "snowflake_trail"},
            3: {"icon": "🐦", "name": "Ice Fledgling", "aura": "frost_wing"},
            4: {"icon": "🕊️", "name": "Crystal Phoenix", "aura": "frozen_rebirth"},
            5: {"icon": "🕊️", "name": "Blizzard Phoenix", "aura": "ice_storm"},
            6: {"icon": "🕊️", "name": "Aurora Phoenix", "aura": "northern_lights"}
        }
    },
    "shadow_kitsune": {
        "name": "Umbra",
        "category": "fantasy",
        "description": "A mysterious shadow kitsune with multiple tails that grow as you progress - ultimate fox evolution",
        "rarity": "epic",
        "price": 450,
        "is_starter": False,
        "theme": "shadow",
        "habit_tie": "general",
        "stages": {
            1: {"icon": "🦊", "name": "Shadow Kit", "aura": "dark_mist"},
            2: {"icon": "🦊", "name": "Twilight Fox", "aura": "shadow_tail"},
            3: {"icon": "🦊", "name": "Void Fox", "aura": "three_tails"},
            4: {"icon": "🦊", "name": "Phantom Kitsune", "aura": "five_tails"},
            5: {"icon": "🦊", "name": "Eclipse Kitsune", "aura": "seven_tails"},
            6: {"icon": "🦊", "name": "Legendary Kitsune", "aura": "nine_tails_shadow"}
        }
    },
    "crystal_golem": {
        "name": "Prism",
        "category": "fantasy",
        "description": "A living crystal golem that gains stronger armor as you practice - refracts light into rainbows",
        "rarity": "rare",
        "price": 300,
        "is_starter": False,
        "theme": "crystal",
        "habit_tie": "exercise",
        "stages": {
            1: {"icon": "💎", "name": "Raw Crystal", "aura": "facet_shine"},
            2: {"icon": "💎", "name": "Cut Gem", "aura": "light_refract"},
            3: {"icon": "💎", "name": "Crystal Form", "aura": "rainbow_prism"},
            4: {"icon": "💎", "name": "Gem Guardian", "aura": "diamond_armor"},
            5: {"icon": "💎", "name": "Radiant Golem", "aura": "light_explosion"},
            6: {"icon": "💎", "name": "Legendary Prism", "aura": "infinite_refraction"}
        }
    },
    "aqua_serpent": {
        "name": "Tide",
        "category": "fantasy",
        "description": "An axolotl-inspired glowing sea serpent with bioluminescent features - great for swim logs",
        "rarity": "rare",
        "price": 350,
        "is_starter": False,
        "theme": "water",
        "habit_tie": "sports",
        "stages": {
            1: {"icon": "🦑", "name": "Sea Spawn", "aura": "bubble_trail"},
            2: {"icon": "🐙", "name": "Young Serpent", "aura": "bio_glow"},
            3: {"icon": "🐙", "name": "Ocean Dweller", "aura": "wave_dance"},
            4: {"icon": "🐲", "name": "Sea Dragon", "aura": "tidal_surge"},
            5: {"icon": "🐲", "name": "Leviathan", "aura": "whirlpool"},
            6: {"icon": "🐲", "name": "Abyss Lord", "aura": "deep_sea_glow"}
        }
    },
    "mecha_dragon": {
        "name": "Titan",
        "category": "scifi",
        "description": "A mechanical dragon with LED lights, gears, and holographic shields - jetpack bursts on victories",
        "rarity": "legendary",
        "price": 600,
        "is_starter": False,
        "theme": "tech",
        "habit_tie": "general",
        "stages": {
            1: {"icon": "🔩", "name": "Scrap Core", "aura": "power_up"},
            2: {"icon": "🤖", "name": "Proto Mech", "aura": "gear_whir"},
            3: {"icon": "🤖", "name": "Battle Mech", "aura": "holo_display"},
            4: {"icon": "🤖", "name": "War Machine", "aura": "jetpack_flame"},
            5: {"icon": "🤖", "name": "Titan Class", "aura": "energy_shield"},
            6: {"icon": "🤖", "name": "Omega Titan", "aura": "nuclear_core"}
        }
    },
    "pixel_sprite": {
        "name": "8-Bit",
        "category": "gaming",
        "description": "A pixelated retro creature that 'levels up' into 3D versions - perfect for gamers",
        "rarity": "uncommon",
        "price": 200,
        "is_starter": False,
        "theme": "retro",
        "habit_tie": "general",
        "stages": {
            1: {"icon": "👾", "name": "8-Bit Blob", "aura": "pixel_glitch"},
            2: {"icon": "👾", "name": "16-Bit Sprite", "aura": "retro_shine"},
            3: {"icon": "👾", "name": "32-Bit Form", "aura": "polygon_glow"},
            4: {"icon": "👾", "name": "HD Sprite", "aura": "render_up"},
            5: {"icon": "👾", "name": "4K Entity", "aura": "ray_trace"},
            6: {"icon": "👾", "name": "Hologram", "aura": "vr_projection"}
        }
    },
    "unicorn_celestial": {
        "name": "Starlight",
        "category": "fantasy",
        "description": "An elegant unicorn with glowing horn and feathers that shimmer - brighter animations on milestones",
        "rarity": "epic",
        "price": 400,
        "is_starter": False,
        "theme": "light",
        "habit_tie": "general",
        "stages": {
            1: {"icon": "🐴", "name": "Foal", "aura": "spark_mane"},
            2: {"icon": "🐴", "name": "Young Steed", "aura": "glow_horn"},
            3: {"icon": "🦄", "name": "Unicorn", "aura": "rainbow_trail"},
            4: {"icon": "🦄", "name": "Celestial Steed", "aura": "star_wings"},
            5: {"icon": "🦄", "name": "Divine Unicorn", "aura": "holy_aura"},
            6: {"icon": "🦄", "name": "Eternal Light", "aura": "supernova_mane"}
        }
    }
}

# Encouragement messages from pets
PET_MESSAGES = {
    "motivation": [
        "{pet_name} believes in you! Keep going!",
        "{pet_name} is cheering you on today!",
        "Your buddy {pet_name} knows you can do it!",
        "{pet_name} is proud of your progress!",
        "{pet_name} says: You're amazing!",
    ],
    "streak_reminder": [
        "{pet_name} misses you! Don't break your streak!",
        "{pet_name} is waiting for you to log today!",
        "Keep {pet_name} happy - log a session!",
        "{pet_name} wants to see you succeed today!",
    ],
    "evolution": [
        "{pet_name} evolved! Look how much you've grown together!",
        "Amazing! {pet_name} reached a new stage!",
        "{pet_name} is getting stronger with you!",
    ],
    "celebration": [
        "{pet_name} is doing a happy dance!",
        "{pet_name} earned a treat for your hard work!",
        "High five from {pet_name}!",
    ]
}

# Enhanced Interaction types with themed animations and rich responses
# Based on user recommendations for engaging, reward-feeling interactions
INTERACTION_TYPES = {
    # Quick tap - Petting Response
    "pet": {
        "animations": ["petting_purr", "heart_particles", "lean_nuzzle", "happy_wiggle"],
        "messages": [
            "{pet_name} purrs and vibrates happily! 💕",
            "{pet_name} leans into your hand for more!",
            "Little hearts float from {pet_name}'s head!",
            "{pet_name} closes eyes in pure bliss!",
            "{pet_name} nuzzles warmly against you!",
        ],
        "happiness_boost": 5,
        "cooldown_seconds": 0,
        "effect": "hearts_rising"
    },
    # Treat Munch with Happy Dance
    "feed": {
        "animations": ["treat_munch", "belly_glow", "happy_dance", "satisfied_wiggle"],
        "messages": [
            "{pet_name} grabs the glowing treat and munches! 🍖",
            "Munch munch! {pet_name}'s belly glows brighter!",
            "{pet_name} does a little wiggle dance of joy!",
            "Eyes close in bliss as {pet_name} savors the treat!",
            "{pet_name} licks lips and does a happy spin!",
        ],
        "happiness_boost": 10,
        "cooldown_seconds": 3600,
        "effect": "treat_particles"
    },
    # Ball Toss Playtime
    "play": {
        "animations": ["ball_chase", "pounce_catch", "proud_return", "wagging_tail"],
        "messages": [
            "{pet_name} chases the bouncing ball across the screen! ⚡",
            "POUNCE! {pet_name} catches it perfectly!",
            "{pet_name} brings it back with a wagging tail and proud grin!",
            "Wheee! {pet_name} does zoomies chasing the ball!",
            "{pet_name} leaps high and catches it mid-air!",
        ],
        "happiness_boost": 8,
        "cooldown_seconds": 1800,
        "effect": "ball_bounce"
    },
    # Energy Burst Training
    "train": {
        "animations": ["power_stretch", "energy_burst", "power_pose", "level_glow"],
        "messages": [
            "{pet_name}'s body lights up with pulsing energy! 💪",
            "Stretching like waking up refreshed! {pet_name} feels powerful!",
            "{pet_name} strikes a power pose with flexed muscles!",
            "A lightbulb appears! {pet_name} learned something new!",
            "Training complete! {pet_name} radiates strength!",
        ],
        "happiness_boost": 7,
        "cooldown_seconds": 7200,
        "effect": "aura_pulse"
    },
    # Cozy Sleep
    "sleep": {
        "animations": ["curl_up", "soft_snore", "dream_bubbles", "peaceful_rest"],
        "messages": [
            "{pet_name} curls up into a cozy ball... 💤",
            "Shhh... little Z's float above {pet_name}...",
            "{pet_name} dreams of adventures with you!",
            "Soft snores... {pet_name} is at peace!",
            "Sweet dreams surround {pet_name}!",
        ],
        "happiness_boost": 3,
        "cooldown_seconds": 0,
        "effect": "zzz_floating"
    },
    # Happy Jump & Spin Dance
    "dance": {
        "animations": ["jump_spin_360", "air_guitar", "disco_lights", "victory_dance"],
        "messages": [
            "{pet_name} leaps and does a 360° spin! 🎵",
            "Air guitar time! {pet_name} rocks out!",
            "Disco lights surround {pet_name}! Party mode!",
            "{pet_name} does a victory dance with floating notes!",
            "Look at those moves! {pet_name} is a star!",
        ],
        "happiness_boost": 6,
        "cooldown_seconds": 300,
        "effect": "music_notes"
    },
    # High-Five / Paw Bump
    "highfive": {
        "animations": ["reach_out", "bump_flash", "star_impact", "confetti_burst"],
        "messages": [
            "{pet_name} reaches out for a paw bump! ✋",
            "BUMP! Stars flash across the screen!",
            "High five! {pet_name} celebrates with confetti!",
            "{pet_name} jumps up for the perfect high-five!",
            "Connection! You and {pet_name} are unstoppable!",
        ],
        "happiness_boost": 8,
        "cooldown_seconds": 600,
        "effect": "star_burst"
    },
    # Encouraging Cheer
    "cheer": {
        "animations": ["hold_sign", "fist_pump", "sparkle_glow", "motivate_pose"],
        "messages": [
            "{pet_name} holds up a tiny sign: 'You got this!' 📣",
            "{pet_name} pumps fists with soft glowing sparkles!",
            "Go go go! {pet_name} cheers you on!",
            "{pet_name} does a motivational pose just for you!",
            "Your biggest fan {pet_name} believes in you!",
        ],
        "happiness_boost": 5,
        "cooldown_seconds": 0,
        "effect": "sparkle_aura"
    },
    # Mini-Adventure
    "adventure": {
        "animations": ["explorer_gear", "walk_offscreen", "return_trophy", "excited_spin"],
        "messages": [
            "{pet_name} puts on explorer gear and waves goodbye! 🗺️",
            "Off on an adventure! {pet_name} disappears with a map...",
            "{pet_name} returns with a tiny trophy! What a journey!",
            "Back from adventure! {pet_name} spins excitedly with treasures!",
            "Explorer {pet_name} found something special for you!",
        ],
        "happiness_boost": 12,
        "cooldown_seconds": 14400,  # 4 hours
        "effect": "trophy_sparkle"
    }
}


# ============ Pet Accessories System ============

# Accessory categories and items
ACCESSORY_CATEGORIES = {
    "hats": {"name": "Hats & Headwear", "icon": "🎩", "slot": "head"},
    "glasses": {"name": "Glasses & Eyewear", "icon": "👓", "slot": "face"},
    "necklaces": {"name": "Collars & Necklaces", "icon": "📿", "slot": "neck"},
    "back": {"name": "Wings & Back Items", "icon": "🦋", "slot": "back"},
    "effects": {"name": "Auras & Effects", "icon": "✨", "slot": "aura"},
}

# All available accessories
PET_ACCESSORIES = {
    # ============ HATS & HEADWEAR ============
    # Milestone Unlocks
    "crown_gold": {
        "name": "Golden Crown",
        "category": "hats",
        "description": "A majestic crown for a 90-day streak!",
        "icon": "👑",
        "rarity": "epic",
        "unlock_type": "streak",
        "unlock_value": 90,
        "price": 0,
        "theme_bonus": ["fantasy"],
    },
    "crown_diamond": {
        "name": "Diamond Crown",
        "category": "hats",
        "description": "A dazzling diamond crown for a 120-day streak!",
        "icon": "💎👑",
        "rarity": "legendary",
        "unlock_type": "streak",
        "unlock_value": 120,
        "price": 0,
        "theme_bonus": ["fantasy"],
    },
    "wizard_hat": {
        "name": "Wizard Hat",
        "category": "hats",
        "description": "A mystical wizard hat for logging in 21 days in a row!",
        "icon": "🧙",
        "rarity": "rare",
        "unlock_type": "streak",
        "unlock_value": 21,
        "price": 0,
        "theme_bonus": ["fantasy", "wisdom"],
    },
    "party_hat": {
        "name": "Party Hat",
        "category": "hats",
        "description": "Celebrate logging in 7 days in a row!",
        "icon": "🎉",
        "rarity": "uncommon",
        "unlock_type": "streak",
        "unlock_value": 7,
        "price": 0,
        "theme_bonus": [],
    },
    # Shop Items
    "pirate_hat": {
        "name": "Pirate Hat",
        "category": "hats",
        "description": "Arrr! Adventure awaits!",
        "icon": "🏴‍☠️",
        "rarity": "uncommon",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 150,
        "theme_bonus": [],
    },
    "sports_cap": {
        "name": "Champion Cap",
        "category": "hats",
        "description": "The cap of a true champion",
        "icon": "🧢",
        "rarity": "common",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 75,
        "theme_bonus": ["sports"],
    },
    "headphones": {
        "name": "DJ Headphones",
        "category": "hats",
        "description": "Feel the beat with these epic headphones",
        "icon": "🎧",
        "rarity": "rare",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 200,
        "theme_bonus": ["music"],
    },
    "space_helmet": {
        "name": "Space Helmet",
        "category": "hats",
        "description": "Ready for cosmic adventures",
        "icon": "👨‍🚀",
        "rarity": "epic",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 350,
        "theme_bonus": ["cosmic", "scifi", "tech"],
    },
    
    # ============ GLASSES & EYEWEAR ============
    "reading_glasses": {
        "name": "Scholar Glasses",
        "category": "glasses",
        "description": "The mark of a true scholar - 45-day streak!",
        "icon": "👓",
        "rarity": "rare",
        "unlock_type": "streak",
        "unlock_value": 45,
        "price": 0,
        "theme_bonus": ["wisdom"],
    },
    "cool_shades": {
        "name": "Cool Shades",
        "category": "glasses",
        "description": "Looking cool never gets old",
        "icon": "😎",
        "rarity": "uncommon",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 100,
        "theme_bonus": ["sports"],
    },
    "cyber_visor": {
        "name": "Cyber Visor",
        "category": "glasses",
        "description": "High-tech visor with LED display",
        "icon": "🥽",
        "rarity": "rare",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 250,
        "theme_bonus": ["tech", "scifi", "neon"],
    },
    "star_glasses": {
        "name": "Star Glasses",
        "category": "glasses",
        "description": "Be the star you are - 60-day streak!",
        "icon": "⭐",
        "rarity": "epic",
        "unlock_type": "streak",
        "unlock_value": 60,
        "price": 0,
        "theme_bonus": [],
    },
    
    # ============ COLLARS & NECKLACES ============
    "friendship_collar": {
        "name": "Friendship Collar",
        "category": "necklaces",
        "description": "For referring 5 friends!",
        "icon": "💕",
        "rarity": "rare",
        "unlock_type": "referral",
        "unlock_value": 5,
        "price": 0,
        "theme_bonus": [],
    },
    "led_collar": {
        "name": "LED Glow Collar",
        "category": "necklaces",
        "description": "A collar that glows with neon light",
        "icon": "💡",
        "rarity": "rare",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 175,
        "theme_bonus": ["neon", "tech", "scifi"],
    },
    "music_notes_chain": {
        "name": "Musical Chain",
        "category": "necklaces",
        "description": "A chain with floating music notes",
        "icon": "🎵",
        "rarity": "uncommon",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 125,
        "theme_bonus": ["music"],
    },
    "crystal_pendant": {
        "name": "Crystal Pendant",
        "category": "necklaces",
        "description": "A magical crystal that shimmers",
        "icon": "💎",
        "rarity": "epic",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 300,
        "theme_bonus": ["fantasy", "crystal"],
    },
    
    # ============ WINGS & BACK ITEMS ============
    "angel_wings": {
        "name": "Angel Wings",
        "category": "back",
        "description": "Majestic white wings for a 120-day streak!",
        "icon": "👼",
        "rarity": "legendary",
        "unlock_type": "streak",
        "unlock_value": 120,
        "price": 0,
        "theme_bonus": ["fantasy", "light"],
    },
    "flame_wings": {
        "name": "Flame Wings",
        "category": "back",
        "description": "Wings of pure fire",
        "icon": "🔥",
        "rarity": "epic",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 400,
        "theme_bonus": ["fire", "fantasy"],
    },
    "jetpack": {
        "name": "Jetpack",
        "category": "back",
        "description": "Blast off with this high-tech jetpack",
        "icon": "🚀",
        "rarity": "epic",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 450,
        "theme_bonus": ["tech", "scifi", "cosmic"],
    },
    "butterfly_wings": {
        "name": "Butterfly Wings",
        "category": "back",
        "description": "Delicate and beautiful wings",
        "icon": "🦋",
        "rarity": "rare",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 200,
        "theme_bonus": [],
    },
    "sports_cape": {
        "name": "Champion Cape",
        "category": "back",
        "description": "The cape of a true sports champion",
        "icon": "🦸",
        "rarity": "rare",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 225,
        "theme_bonus": ["sports"],
    },
    
    # ============ AURAS & EFFECTS ============
    "sparkle_aura": {
        "name": "Sparkle Aura",
        "category": "effects",
        "description": "Constant sparkles - log in 7 days in a row!",
        "icon": "✨",
        "rarity": "uncommon",
        "unlock_type": "streak",
        "unlock_value": 7,
        "price": 0,
        "theme_bonus": [],
    },
    "fire_aura": {
        "name": "Fire Aura",
        "category": "effects",
        "description": "Flames dance around your pet",
        "icon": "🔥",
        "rarity": "rare",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 275,
        "theme_bonus": ["fire"],
    },
    "ice_aura": {
        "name": "Ice Aura",
        "category": "effects",
        "description": "Frost crystals float around your pet",
        "icon": "❄️",
        "rarity": "rare",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 275,
        "theme_bonus": ["ice"],
    },
    "rainbow_trail": {
        "name": "Rainbow Trail",
        "category": "effects",
        "description": "Leave a rainbow wherever you go - 45-day streak!",
        "icon": "🌈",
        "rarity": "epic",
        "unlock_type": "streak",
        "unlock_value": 45,
        "price": 0,
        "theme_bonus": ["light"],
    },
    "lightning_aura": {
        "name": "Lightning Aura",
        "category": "effects",
        "description": "Electric bolts crackle around your pet",
        "icon": "⚡",
        "rarity": "epic",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 350,
        "theme_bonus": ["lightning", "tech"],
    },
    "galaxy_swirl": {
        "name": "Galaxy Swirl",
        "category": "effects",
        "description": "Stars and galaxies orbit your pet - 90-day streak!",
        "icon": "🌌",
        "rarity": "legendary",
        "unlock_type": "streak",
        "unlock_value": 90,
        "price": 0,
        "theme_bonus": ["cosmic"],
    },
    "heart_bubbles": {
        "name": "Heart Bubbles",
        "category": "effects",
        "description": "Floating hearts surround your pet",
        "icon": "💕",
        "rarity": "uncommon",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 100,
        "theme_bonus": [],
    },
    "music_waves": {
        "name": "Music Waves",
        "category": "effects",
        "description": "Musical notes float around your pet",
        "icon": "🎶",
        "rarity": "uncommon",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 125,
        "theme_bonus": ["music"],
    },
    "neon_glow": {
        "name": "Neon Glow",
        "category": "effects",
        "description": "Your pet glows with vibrant neon colors",
        "icon": "💜",
        "rarity": "rare",
        "unlock_type": "shop",
        "unlock_value": None,
        "price": 200,
        "theme_bonus": ["neon", "tech"],
    },
}

# ============ SEASONAL / LIMITED EDITION ACCESSORIES ============
# These have time-based availability windows
SEASONAL_ACCESSORIES = {
    # ============ HALLOWEEN (October 15 - November 5) ============
    "halloween_witch_hat": {
        "name": "Witch Hat",
        "category": "hats",
        "description": "A spooky witch hat for Halloween!",
        "icon": "🧙‍♀️",
        "rarity": "rare",
        "unlock_type": "seasonal",
        "price": 200,
        "theme_bonus": ["fantasy"],
        "season": "halloween",
        "available_month_start": 10,
        "available_day_start": 15,
        "available_month_end": 11,
        "available_day_end": 5,
    },
    "halloween_pumpkin_head": {
        "name": "Pumpkin Head",
        "category": "hats",
        "description": "A glowing jack-o-lantern headpiece!",
        "icon": "🎃",
        "rarity": "epic",
        "unlock_type": "seasonal",
        "price": 350,
        "theme_bonus": ["fire"],
        "season": "halloween",
        "available_month_start": 10,
        "available_day_start": 15,
        "available_month_end": 11,
        "available_day_end": 5,
    },
    "halloween_ghost_aura": {
        "name": "Ghost Aura",
        "category": "effects",
        "description": "Spooky ghosts float around your pet!",
        "icon": "👻",
        "rarity": "rare",
        "unlock_type": "seasonal",
        "price": 250,
        "theme_bonus": [],
        "season": "halloween",
        "available_month_start": 10,
        "available_day_start": 15,
        "available_month_end": 11,
        "available_day_end": 5,
    },
    "halloween_bat_wings": {
        "name": "Bat Wings",
        "category": "back",
        "description": "Dark bat wings for the spooky season!",
        "icon": "🦇",
        "rarity": "epic",
        "unlock_type": "seasonal",
        "price": 400,
        "theme_bonus": ["shadow"],
        "season": "halloween",
        "available_month_start": 10,
        "available_day_start": 15,
        "available_month_end": 11,
        "available_day_end": 5,
    },
    
    # ============ WINTER / CHRISTMAS (December 1 - January 10) ============
    "winter_santa_hat": {
        "name": "Santa Hat",
        "category": "hats",
        "description": "Ho ho ho! A festive Santa hat!",
        "icon": "🎅",
        "rarity": "rare",
        "unlock_type": "seasonal",
        "price": 200,
        "theme_bonus": [],
        "season": "winter",
        "available_month_start": 12,
        "available_day_start": 1,
        "available_month_end": 1,
        "available_day_end": 10,
    },
    "winter_snowflake_halo": {
        "name": "Snowflake Halo",
        "category": "effects",
        "description": "Magical snowflakes orbit your pet!",
        "icon": "❄️",
        "rarity": "epic",
        "unlock_type": "seasonal",
        "price": 350,
        "theme_bonus": ["ice"],
        "season": "winter",
        "available_month_start": 12,
        "available_day_start": 1,
        "available_month_end": 1,
        "available_day_end": 10,
    },
    "winter_reindeer_antlers": {
        "name": "Reindeer Antlers",
        "category": "hats",
        "description": "Festive antlers with jingle bells!",
        "icon": "🦌",
        "rarity": "rare",
        "unlock_type": "seasonal",
        "price": 225,
        "theme_bonus": [],
        "season": "winter",
        "available_month_start": 12,
        "available_day_start": 1,
        "available_month_end": 1,
        "available_day_end": 10,
    },
    "winter_candy_cane_collar": {
        "name": "Candy Cane Collar",
        "category": "necklaces",
        "description": "A sweet candy cane necklace!",
        "icon": "🍬",
        "rarity": "uncommon",
        "unlock_type": "seasonal",
        "price": 150,
        "theme_bonus": [],
        "season": "winter",
        "available_month_start": 12,
        "available_day_start": 1,
        "available_month_end": 1,
        "available_day_end": 10,
    },
    "winter_present_backpack": {
        "name": "Gift Box Backpack",
        "category": "back",
        "description": "A wrapped present on your back!",
        "icon": "🎁",
        "rarity": "rare",
        "unlock_type": "seasonal",
        "price": 275,
        "theme_bonus": [],
        "season": "winter",
        "available_month_start": 12,
        "available_day_start": 1,
        "available_month_end": 1,
        "available_day_end": 10,
    },
    
    # ============ VALENTINE'S DAY (February 1 - February 20) ============
    "valentines_heart_crown": {
        "name": "Heart Crown",
        "category": "hats",
        "description": "A crown made of hearts!",
        "icon": "💖",
        "rarity": "rare",
        "unlock_type": "seasonal",
        "price": 200,
        "theme_bonus": [],
        "season": "valentines",
        "available_month_start": 2,
        "available_day_start": 1,
        "available_month_end": 2,
        "available_day_end": 20,
    },
    "valentines_cupid_wings": {
        "name": "Cupid Wings",
        "category": "back",
        "description": "Tiny pink wings from Cupid himself!",
        "icon": "💘",
        "rarity": "epic",
        "unlock_type": "seasonal",
        "price": 400,
        "theme_bonus": ["light"],
        "season": "valentines",
        "available_month_start": 2,
        "available_day_start": 1,
        "available_month_end": 2,
        "available_day_end": 20,
    },
    "valentines_love_aura": {
        "name": "Love Aura",
        "category": "effects",
        "description": "Floating hearts surround your pet!",
        "icon": "💕",
        "rarity": "rare",
        "unlock_type": "seasonal",
        "price": 250,
        "theme_bonus": [],
        "season": "valentines",
        "available_month_start": 2,
        "available_day_start": 1,
        "available_month_end": 2,
        "available_day_end": 20,
    },
    
    # ============ SPRING / EASTER (March 15 - April 25) ============
    "spring_bunny_ears": {
        "name": "Bunny Ears",
        "category": "hats",
        "description": "Cute floppy bunny ears!",
        "icon": "🐰",
        "rarity": "rare",
        "unlock_type": "seasonal",
        "price": 200,
        "theme_bonus": [],
        "season": "spring",
        "available_month_start": 3,
        "available_day_start": 15,
        "available_month_end": 4,
        "available_day_end": 25,
    },
    "spring_flower_crown": {
        "name": "Flower Crown",
        "category": "hats",
        "description": "A beautiful crown of spring flowers!",
        "icon": "🌸",
        "rarity": "rare",
        "unlock_type": "seasonal",
        "price": 225,
        "theme_bonus": [],
        "season": "spring",
        "available_month_start": 3,
        "available_day_start": 15,
        "available_month_end": 4,
        "available_day_end": 25,
    },
    "spring_butterfly_swarm": {
        "name": "Butterfly Swarm",
        "category": "effects",
        "description": "Colorful butterflies dance around!",
        "icon": "🦋",
        "rarity": "epic",
        "unlock_type": "seasonal",
        "price": 300,
        "theme_bonus": [],
        "season": "spring",
        "available_month_start": 3,
        "available_day_start": 15,
        "available_month_end": 4,
        "available_day_end": 25,
    },
    
    # ============ SUMMER (June 1 - August 31) ============
    "summer_sunglasses": {
        "name": "Beach Shades",
        "category": "glasses",
        "description": "Cool summer sunglasses!",
        "icon": "🕶️",
        "rarity": "uncommon",
        "unlock_type": "seasonal",
        "price": 125,
        "theme_bonus": [],
        "season": "summer",
        "available_month_start": 6,
        "available_day_start": 1,
        "available_month_end": 8,
        "available_day_end": 31,
    },
    "summer_beach_hat": {
        "name": "Beach Hat",
        "category": "hats",
        "description": "A stylish sun hat for the beach!",
        "icon": "👒",
        "rarity": "rare",
        "unlock_type": "seasonal",
        "price": 175,
        "theme_bonus": [],
        "season": "summer",
        "available_month_start": 6,
        "available_day_start": 1,
        "available_month_end": 8,
        "available_day_end": 31,
    },
    "summer_surfboard": {
        "name": "Mini Surfboard",
        "category": "back",
        "description": "A tiny surfboard for riding waves!",
        "icon": "🏄",
        "rarity": "rare",
        "unlock_type": "seasonal",
        "price": 250,
        "theme_bonus": ["water"],
        "season": "summer",
        "available_month_start": 6,
        "available_day_start": 1,
        "available_month_end": 8,
        "available_day_end": 31,
    },
    "summer_sunshine_aura": {
        "name": "Sunshine Aura",
        "category": "effects",
        "description": "Warm golden rays surround your pet!",
        "icon": "☀️",
        "rarity": "epic",
        "unlock_type": "seasonal",
        "price": 300,
        "theme_bonus": ["light", "fire"],
        "season": "summer",
        "available_month_start": 6,
        "available_day_start": 1,
        "available_month_end": 8,
        "available_day_end": 31,
    },
    
    # ============ BACK TO SCHOOL (August 15 - September 30) ============
    "school_graduation_cap": {
        "name": "Graduation Cap",
        "category": "hats",
        "description": "Celebrate academic achievement!",
        "icon": "🎓",
        "rarity": "epic",
        "unlock_type": "seasonal",
        "price": 300,
        "theme_bonus": ["wisdom"],
        "season": "school",
        "available_month_start": 8,
        "available_day_start": 15,
        "available_month_end": 9,
        "available_day_end": 30,
    },
    "school_book_bag": {
        "name": "Scholar's Backpack",
        "category": "back",
        "description": "A backpack full of knowledge!",
        "icon": "📚",
        "rarity": "rare",
        "unlock_type": "seasonal",
        "price": 225,
        "theme_bonus": ["wisdom"],
        "season": "school",
        "available_month_start": 8,
        "available_day_start": 15,
        "available_month_end": 9,
        "available_day_end": 30,
    },
    "school_pencil_glasses": {
        "name": "Nerdy Glasses",
        "category": "glasses",
        "description": "Smart-looking study glasses!",
        "icon": "🤓",
        "rarity": "uncommon",
        "unlock_type": "seasonal",
        "price": 150,
        "theme_bonus": ["wisdom"],
        "season": "school",
        "available_month_start": 8,
        "available_day_start": 15,
        "available_month_end": 9,
        "available_day_end": 30,
    },
    
    # ============ NEW YEAR (December 28 - January 15) ============
    "newyear_party_hat": {
        "name": "New Year Party Hat",
        "category": "hats",
        "description": "Ring in the new year!",
        "icon": "🥳",
        "rarity": "rare",
        "unlock_type": "seasonal",
        "price": 200,
        "theme_bonus": [],
        "season": "newyear",
        "available_month_start": 12,
        "available_day_start": 28,
        "available_month_end": 1,
        "available_day_end": 15,
    },
    "newyear_fireworks_aura": {
        "name": "Fireworks Aura",
        "category": "effects",
        "description": "Celebration fireworks everywhere!",
        "icon": "🎆",
        "rarity": "epic",
        "unlock_type": "seasonal",
        "price": 350,
        "theme_bonus": ["fire"],
        "season": "newyear",
        "available_month_start": 12,
        "available_day_start": 28,
        "available_month_end": 1,
        "available_day_end": 15,
    },
    "newyear_champagne_collar": {
        "name": "Celebration Chain",
        "category": "necklaces",
        "description": "Sparkly celebration necklace!",
        "icon": "🍾",
        "rarity": "rare",
        "unlock_type": "seasonal",
        "price": 225,
        "theme_bonus": [],
        "season": "newyear",
        "available_month_start": 12,
        "available_day_start": 28,
        "available_month_end": 1,
        "available_day_end": 15,
    },
}

# ============ Pydantic Models ============

class SelectPetRequest(BaseModel):
    pet_type: str
    pet_name: Optional[str] = None  # Custom name


class InteractRequest(BaseModel):
    interaction_type: str = "pet"  # "pet", "feed", "play"


class EquipAccessoryRequest(BaseModel):
    accessory_id: str
    slot: Optional[str] = None  # Auto-detect from accessory if not provided


# ============ Helper Functions ============

def get_evolution_stage(streak_days: int) -> int:
    """Get evolution stage based on streak days"""
    stage = 1
    for s, info in EVOLUTION_STAGES.items():
        if streak_days >= info["streak_required"]:
            stage = s
    return stage


def is_seasonal_available(accessory: dict) -> dict:
    """Check if a seasonal accessory is currently available"""
    now = datetime.now(timezone.utc)
    current_month = now.month
    current_day = now.day
    
    start_month = accessory.get('available_month_start', 1)
    start_day = accessory.get('available_day_start', 1)
    end_month = accessory.get('available_month_end', 12)
    end_day = accessory.get('available_day_end', 31)
    
    # Handle year-wrap (e.g., December to January)
    if start_month > end_month:
        # Available if we're in the end-of-year portion OR start-of-year portion
        in_end_year = (current_month > start_month) or (current_month == start_month and current_day >= start_day)
        in_start_year = (current_month < end_month) or (current_month == end_month and current_day <= end_day)
        is_available = in_end_year or in_start_year
    else:
        # Normal date range within same year
        after_start = (current_month > start_month) or (current_month == start_month and current_day >= start_day)
        before_end = (current_month < end_month) or (current_month == end_month and current_day <= end_day)
        is_available = after_start and before_end
    
    # Calculate days remaining if available
    days_remaining = None
    if is_available:
        # Calculate end date for current or next occurrence
        year = now.year
        if end_month < current_month:
            year += 1
        try:
            end_date = datetime(year, end_month, end_day, tzinfo=timezone.utc)
            days_remaining = (end_date - now).days + 1
        except:
            days_remaining = 30  # Fallback
    
    return {
        'available': is_available,
        'days_remaining': days_remaining,
        'season': accessory.get('season', 'unknown'),
        'start': f"{start_month}/{start_day}",
        'end': f"{end_month}/{end_day}"
    }


def get_season_info(season_key: str) -> dict:
    """Get display info for a season"""
    season_info = {
        'halloween': {'name': 'Halloween', 'icon': '🎃', 'color': 'orange'},
        'winter': {'name': 'Winter Holidays', 'icon': '🎄', 'color': 'green'},
        'valentines': {'name': "Valentine's Day", 'icon': '💖', 'color': 'pink'},
        'spring': {'name': 'Spring', 'icon': '🌸', 'color': 'pink'},
        'summer': {'name': 'Summer', 'icon': '☀️', 'color': 'yellow'},
        'school': {'name': 'Back to School', 'icon': '📚', 'color': 'blue'},
        'newyear': {'name': 'New Year', 'icon': '🎆', 'color': 'gold'},
    }
    return season_info.get(season_key, {'name': season_key.title(), 'icon': '🎉', 'color': 'purple'})


def get_pet_appearance(pet_type: str, stage: int) -> dict:
    """Get pet appearance for current stage"""
    pet = PET_TYPES.get(pet_type)
    if not pet:
        return {"icon": "❓", "name": "Unknown"}
    return pet["stages"].get(stage, pet["stages"][1])


def get_random_message(category: str, pet_name: str) -> str:
    """Get random encouragement message"""
    messages = PET_MESSAGES.get(category, PET_MESSAGES["motivation"])
    message = random.choice(messages)
    return message.format(pet_name=pet_name)


async def check_and_evolve_pet(user_id: str, current_streak: int) -> dict:
    """Check if pet should evolve based on streak"""
    user_pet = await db.user_pets.find_one(
        {'user_id': user_id, 'is_active': True},
        {'_id': 0}
    )
    
    if not user_pet:
        return None
    
    new_stage = get_evolution_stage(current_streak)
    old_stage = user_pet.get('evolution_stage', 1)
    
    if new_stage > old_stage:
        # Pet evolved!
        await db.user_pets.update_one(
            {'id': user_pet['id']},
            {
                '$set': {
                    'evolution_stage': new_stage,
                    'evolved_at': datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        pet_type = user_pet['pet_type']
        pet_name = user_pet.get('custom_name') or PET_TYPES[pet_type]['name']
        new_appearance = get_pet_appearance(pet_type, new_stage)
        
        return {
            'evolved': True,
            'pet_name': pet_name,
            'old_stage': old_stage,
            'new_stage': new_stage,
            'new_appearance': new_appearance,
            'stage_info': EVOLUTION_STAGES[new_stage],
            'message': get_random_message('evolution', pet_name)
        }
    
    return {'evolved': False}


# ============ API Endpoints ============

@router.get("/available")
async def get_available_pets(current_user: dict = Depends(get_current_user)):
    """Get all available pets (starters + shop items)"""
    pets = []
    for pet_type, pet_info in PET_TYPES.items():
        pets.append({
            'type': pet_type,
            'name': pet_info['name'],
            'category': pet_info['category'],
            'description': pet_info['description'],
            'rarity': pet_info['rarity'],
            'price': pet_info['price'],
            'is_starter': pet_info['is_starter'],
            'preview_icon': pet_info['stages'][1]['icon'],
            'max_icon': pet_info['stages'][6]['icon']
        })
    
    return {
        'pets': pets,
        'starters': [p for p in pets if p['is_starter']],
        'shop_pets': [p for p in pets if not p['is_starter']]
    }


@router.get("/my-pet")
async def get_my_pet(current_user: dict = Depends(get_current_user)):
    """Get user's active pet"""
    user_pet = await db.user_pets.find_one(
        {'user_id': current_user['id'], 'is_active': True},
        {'_id': 0}
    )
    
    if not user_pet:
        return {'has_pet': False, 'pet': None}
    
    pet_type = user_pet['pet_type']
    pet_info = PET_TYPES.get(pet_type)
    
    # Handle case where pet type no longer exists (legacy pets)
    if not pet_info:
        # Default to flame_dragon as fallback
        pet_type = 'flame_dragon'
        pet_info = PET_TYPES['flame_dragon']
        # Update the user's pet to use the new type
        await db.user_pets.update_one(
            {'id': user_pet['id']},
            {'$set': {'pet_type': pet_type}}
        )
    
    stage = user_pet.get('evolution_stage', 1)
    appearance = get_pet_appearance(pet_type, stage)
    stage_info = EVOLUTION_STAGES.get(stage, EVOLUTION_STAGES[1])
    
    # Get user's streak for next evolution
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0, 'current_streak': 1})
    current_streak = user.get('current_streak', 0)
    
    # Find next evolution stage
    next_stage = None
    for s, info in EVOLUTION_STAGES.items():
        if s > stage:
            next_stage = {'stage': s, **info}
            break
    
    return {
        'has_pet': True,
        'pet': {
            'id': user_pet['id'],
            'type': pet_type,
            'name': user_pet.get('custom_name') or pet_info['name'],
            'category': pet_info['category'],
            'rarity': pet_info['rarity'],
            'evolution_stage': stage,
            'stage_name': stage_info['name'],
            'icon': appearance['icon'],
            'appearance_name': appearance['name'],
            'xp_bonus': stage_info['xp_bonus'],
            'coin_bonus': stage_info['coin_bonus'],
            'happiness': user_pet.get('happiness', 100),
            'last_interaction': user_pet.get('last_interaction'),
            'acquired_at': user_pet['acquired_at']
        },
        'current_streak': current_streak,
        'next_evolution': next_stage,
        'days_until_evolution': max(0, next_stage['streak_required'] - current_streak) if next_stage else 0
    }


@router.post("/select")
async def select_starter_pet(request: SelectPetRequest, current_user: dict = Depends(get_current_user)):
    """Select a starter pet (first time) or purchase a new pet"""
    pet_type = request.pet_type
    
    if pet_type not in PET_TYPES:
        raise HTTPException(status_code=400, detail="Invalid pet type")
    
    pet_info = PET_TYPES[pet_type]
    
    # Check if user already has this pet
    existing = await db.user_pets.find_one({
        'user_id': current_user['id'],
        'pet_type': pet_type
    })
    if existing:
        raise HTTPException(status_code=400, detail="You already own this pet")
    
    # Check if it's a free starter or needs purchase
    if not pet_info['is_starter']:
        # Need to purchase with coins
        user = await db.users.find_one({'id': current_user['id']}, {'_id': 0, 'coins': 1})
        current_coins = user.get('coins', 0)
        
        if current_coins < pet_info['price']:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough coins. You have {current_coins}, need {pet_info['price']}"
            )
        
        # Deduct coins
        await db.users.update_one(
            {'id': current_user['id']},
            {'$inc': {'coins': -pet_info['price']}}
        )
    else:
        # Check if user already has a starter
        has_starter = await db.user_pets.find_one({
            'user_id': current_user['id'],
            'is_starter': True
        })
        if has_starter:
            raise HTTPException(status_code=400, detail="You already have a starter pet. Purchase new pets from the shop.")
    
    # Deactivate current pet
    await db.user_pets.update_many(
        {'user_id': current_user['id'], 'is_active': True},
        {'$set': {'is_active': False}}
    )
    
    # Create new pet
    user_pet = {
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'pet_type': pet_type,
        'custom_name': request.pet_name or pet_info['name'],
        'is_starter': pet_info['is_starter'],
        'evolution_stage': 1,
        'happiness': 100,
        'is_active': True,
        'acquired_at': datetime.now(timezone.utc).isoformat(),
        'last_interaction': datetime.now(timezone.utc).isoformat()
    }
    await db.user_pets.insert_one(user_pet)
    
    appearance = get_pet_appearance(pet_type, 1)
    
    return {
        'message': f"Welcome {user_pet['custom_name']}! Your new companion is ready!",
        'pet': {
            'id': user_pet['id'],
            'type': pet_type,
            'name': user_pet['custom_name'],
            'icon': appearance['icon'],
            'stage_name': 'Baby'
        }
    }


@router.post("/set-active/{pet_id}")
async def set_active_pet(pet_id: str, current_user: dict = Depends(get_current_user)):
    """Set a pet as active companion"""
    pet = await db.user_pets.find_one({
        'id': pet_id,
        'user_id': current_user['id']
    })
    
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    # Deactivate all pets
    await db.user_pets.update_many(
        {'user_id': current_user['id']},
        {'$set': {'is_active': False}}
    )
    
    # Activate this pet
    await db.user_pets.update_one(
        {'id': pet_id},
        {'$set': {'is_active': True}}
    )
    
    pet_info = PET_TYPES.get(pet['pet_type'])
    return {
        'message': f"{pet.get('custom_name', pet_info['name'])} is now your active companion!",
        'pet_id': pet_id
    }


@router.post("/interact")
async def interact_with_pet(request: InteractRequest, current_user: dict = Depends(get_current_user)):
    """Interact with your pet with various actions"""
    user_pet = await db.user_pets.find_one(
        {'user_id': current_user['id'], 'is_active': True},
        {'_id': 0}
    )
    
    if not user_pet:
        raise HTTPException(status_code=404, detail="No active pet found")
    
    interaction_type = request.interaction_type
    
    # Validate interaction type
    if interaction_type not in INTERACTION_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid interaction type. Choose from: {', '.join(INTERACTION_TYPES.keys())}")
    
    interaction = INTERACTION_TYPES[interaction_type]
    
    # Check cooldown for this interaction
    cooldown = interaction['cooldown_seconds']
    if cooldown > 0:
        last_key = f'last_{interaction_type}'
        last_time = user_pet.get(last_key)
        if last_time:
            last_dt = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
            elapsed = (datetime.now(timezone.utc) - last_dt).total_seconds()
            if elapsed < cooldown:
                remaining = int(cooldown - elapsed)
                mins = remaining // 60
                secs = remaining % 60
                raise HTTPException(
                    status_code=400, 
                    detail=f"{interaction_type.title()} is on cooldown. Try again in {mins}m {secs}s"
                )
    
    pet_type = user_pet['pet_type']
    pet_info = PET_TYPES.get(pet_type)
    pet_name = user_pet.get('custom_name') or pet_info['name']
    
    # Update happiness and last interaction
    happiness_boost = interaction['happiness_boost']
    new_happiness = min(100, user_pet.get('happiness', 100) + happiness_boost)
    
    update_fields = {
        'happiness': new_happiness,
        'last_interaction': datetime.now(timezone.utc).isoformat(),
        f'last_{interaction_type}': datetime.now(timezone.utc).isoformat()
    }
    
    await db.user_pets.update_one(
        {'id': user_pet['id']},
        {'$set': update_fields}
    )
    
    # Get random message and animation for this interaction
    message_template = random.choice(interaction['messages'])
    message = message_template.format(pet_name=pet_name)
    animation = random.choice(interaction['animations'])
    effect = interaction.get('effect', 'sparkle_aura')
    
    # Get pet theme for themed effects
    pet_theme = pet_info.get('theme', 'general')
    
    return {
        'message': message,
        'animation': animation,
        'effect': effect,
        'theme': pet_theme,
        'happiness': new_happiness,
        'happiness_boost': happiness_boost,
        'pet_name': pet_name,
        'interaction': interaction_type,
        'cooldown_seconds': cooldown
    }


@router.get("/interactions")
async def get_available_interactions(current_user: dict = Depends(get_current_user)):
    """Get available interaction types and their cooldown status"""
    user_pet = await db.user_pets.find_one(
        {'user_id': current_user['id'], 'is_active': True},
        {'_id': 0}
    )
    
    if not user_pet:
        return {'interactions': [], 'has_pet': False}
    
    interactions = []
    now = datetime.now(timezone.utc)
    
    for int_type, info in INTERACTION_TYPES.items():
        cooldown = info['cooldown_seconds']
        available = True
        remaining_seconds = 0
        
        if cooldown > 0:
            last_key = f'last_{int_type}'
            last_time = user_pet.get(last_key)
            if last_time:
                last_dt = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
                elapsed = (now - last_dt).total_seconds()
                if elapsed < cooldown:
                    available = False
                    remaining_seconds = int(cooldown - elapsed)
        
        interactions.append({
            'type': int_type,
            'available': available,
            'cooldown_seconds': cooldown,
            'remaining_seconds': remaining_seconds,
            'happiness_boost': info['happiness_boost']
        })
    
    return {
        'interactions': interactions,
        'has_pet': True
    }


@router.get("/collection")
async def get_pet_collection(current_user: dict = Depends(get_current_user)):
    """Get all pets owned by user"""
    owned_pets = await db.user_pets.find(
        {'user_id': current_user['id']},
        {'_id': 0}
    ).to_list(50)
    
    collection = []
    for user_pet in owned_pets:
        pet_type = user_pet['pet_type']
        pet_info = PET_TYPES.get(pet_type)
        if not pet_info:
            continue
            
        stage = user_pet.get('evolution_stage', 1)
        appearance = get_pet_appearance(pet_type, stage)
        
        collection.append({
            'id': user_pet['id'],
            'type': pet_type,
            'name': user_pet.get('custom_name') or pet_info['name'],
            'category': pet_info['category'],
            'rarity': pet_info['rarity'],
            'evolution_stage': stage,
            'icon': appearance['icon'],
            'is_active': user_pet.get('is_active', False),
            'acquired_at': user_pet['acquired_at']
        })
    
    return {
        'collection': collection,
        'total_owned': len(collection)
    }


@router.get("/encouragement")
async def get_pet_encouragement(current_user: dict = Depends(get_current_user)):
    """Get an encouragement message from your pet"""
    user_pet = await db.user_pets.find_one(
        {'user_id': current_user['id'], 'is_active': True},
        {'_id': 0}
    )
    
    if not user_pet:
        return {'has_pet': False, 'message': None}
    
    pet_type = user_pet['pet_type']
    pet_info = PET_TYPES.get(pet_type)
    pet_name = user_pet.get('custom_name') or pet_info['name']
    stage = user_pet.get('evolution_stage', 1)
    appearance = get_pet_appearance(pet_type, stage)
    
    message = get_random_message('motivation', pet_name)
    
    return {
        'has_pet': True,
        'pet_name': pet_name,
        'pet_icon': appearance['icon'],
        'message': message
    }


@router.get("/shop")
async def get_pet_shop(current_user: dict = Depends(get_current_user)):
    """Get pets available in shop"""
    # Get user's owned pets
    owned = await db.user_pets.find(
        {'user_id': current_user['id']},
        {'_id': 0, 'pet_type': 1}
    ).to_list(50)
    owned_types = [p['pet_type'] for p in owned]
    
    # Get user's coins
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0, 'coins': 1})
    user_coins = user.get('coins', 0)
    
    shop_pets = []
    for pet_type, pet_info in PET_TYPES.items():
        if not pet_info['is_starter']:  # Only non-starters in shop
            shop_pets.append({
                'type': pet_type,
                'name': pet_info['name'],
                'category': pet_info['category'],
                'description': pet_info['description'],
                'rarity': pet_info['rarity'],
                'price': pet_info['price'],
                'preview_icon': pet_info['stages'][1]['icon'],
                'max_icon': pet_info['stages'][6]['icon'],
                'owned': pet_type in owned_types,
                'can_afford': user_coins >= pet_info['price']
            })
    
    # Sort by price
    shop_pets.sort(key=lambda x: x['price'])
    
    return {
        'pets': shop_pets,
        'user_coins': user_coins
    }



# ============ Accessory Helper Functions ============

async def check_accessory_unlock(user_id: str, accessory_id: str) -> dict:
    """Check if user has unlocked a specific accessory"""
    accessory = PET_ACCESSORIES.get(accessory_id)
    if not accessory:
        return {"unlocked": False, "reason": "Accessory not found"}
    
    unlock_type = accessory['unlock_type']
    unlock_value = accessory['unlock_value']
    
    # Shop items are always "unlocked" but need purchase
    if unlock_type == "shop":
        # Check if already purchased
        owned = await db.user_accessories.find_one({
            'user_id': user_id,
            'accessory_id': accessory_id
        })
        if owned:
            return {"unlocked": True, "owned": True, "reason": "Already purchased"}
        return {"unlocked": True, "owned": False, "reason": "Available for purchase", "price": accessory['price']}
    
    # Level-based unlock
    if unlock_type == "level":
        user = await db.users.find_one({'id': user_id}, {'_id': 0, 'level': 1})
        user_level = user.get('level', 1)
        if user_level >= unlock_value:
            return {"unlocked": True, "reason": f"Unlocked at Level {unlock_value}"}
        return {"unlocked": False, "reason": f"Reach Level {unlock_value} to unlock", "progress": f"{user_level}/{unlock_value}"}
    
    # Streak-based unlock
    if unlock_type == "streak":
        user = await db.users.find_one({'id': user_id}, {'_id': 0, 'longest_streak': 1, 'current_streak': 1})
        longest = user.get('longest_streak', 0)
        current = user.get('current_streak', 0)
        best = max(longest, current)
        if best >= unlock_value:
            return {"unlocked": True, "reason": f"Unlocked with {unlock_value}-day streak"}
        return {"unlocked": False, "reason": f"Reach a {unlock_value}-day streak to unlock", "progress": f"{best}/{unlock_value}"}
    
    # Achievement-based unlock
    if unlock_type == "achievement":
        badge = await db.user_badges.find_one({
            'user_id': user_id,
            'badge_id': unlock_value
        })
        if badge:
            return {"unlocked": True, "reason": f"Unlocked with '{unlock_value}' achievement"}
        return {"unlocked": False, "reason": f"Earn the '{unlock_value}' badge to unlock"}
    
    # Referral-based unlock
    if unlock_type == "referral":
        user = await db.users.find_one({'id': user_id}, {'_id': 0, 'referral_count': 1})
        referrals = user.get('referral_count', 0)
        if referrals >= unlock_value:
            return {"unlocked": True, "reason": f"Unlocked with {unlock_value} referrals"}
        return {"unlocked": False, "reason": f"Refer {unlock_value} friends to unlock", "progress": f"{referrals}/{unlock_value}"}
    
    return {"unlocked": False, "reason": "Unknown unlock type"}


def get_theme_match_bonus(accessory_id: str, pet_type: str) -> bool:
    """Check if accessory theme matches pet theme for bonus"""
    accessory = PET_ACCESSORIES.get(accessory_id)
    pet = PET_TYPES.get(pet_type)
    
    if not accessory or not pet:
        return False
    
    pet_theme = pet.get('theme', '')
    accessory_themes = accessory.get('theme_bonus', [])
    
    return pet_theme in accessory_themes


# ============ Accessory API Endpoints ============

@router.get("/accessories")
async def get_all_accessories(current_user: dict = Depends(get_current_user)):
    """Get all available accessories with unlock status"""
    user_id = current_user['id']
    
    # Get user's owned accessories
    owned_accessories = await db.user_accessories.find(
        {'user_id': user_id},
        {'_id': 0}
    ).to_list(100)
    owned_ids = {a['accessory_id'] for a in owned_accessories}
    
    # Get user's active pet for theme matching
    user_pet = await db.user_pets.find_one(
        {'user_id': user_id, 'is_active': True},
        {'_id': 0, 'pet_type': 1}
    )
    pet_type = user_pet.get('pet_type') if user_pet else None
    
    # Get user coins
    user = await db.users.find_one({'id': user_id}, {'_id': 0, 'coins': 1})
    user_coins = user.get('coins', 0)
    
    accessories_by_category = {}
    
    for acc_id, acc_info in PET_ACCESSORIES.items():
        category = acc_info['category']
        if category not in accessories_by_category:
            accessories_by_category[category] = {
                'name': ACCESSORY_CATEGORIES[category]['name'],
                'icon': ACCESSORY_CATEGORIES[category]['icon'],
                'slot': ACCESSORY_CATEGORIES[category]['slot'],
                'items': []
            }
        
        # Check unlock status
        unlock_status = await check_accessory_unlock(user_id, acc_id)
        is_owned = acc_id in owned_ids
        
        # Check theme match bonus
        theme_match = get_theme_match_bonus(acc_id, pet_type) if pet_type else False
        
        accessories_by_category[category]['items'].append({
            'id': acc_id,
            'name': acc_info['name'],
            'description': acc_info['description'],
            'icon': acc_info['icon'],
            'rarity': acc_info['rarity'],
            'unlock_type': acc_info['unlock_type'],
            'price': acc_info['price'],
            'owned': is_owned,
            'unlocked': unlock_status.get('unlocked', False),
            'unlock_reason': unlock_status.get('reason', ''),
            'unlock_progress': unlock_status.get('progress'),
            'theme_match': theme_match,
            'can_afford': user_coins >= acc_info['price'] if acc_info['unlock_type'] == 'shop' else True
        })
    
    return {
        'categories': accessories_by_category,
        'user_coins': user_coins,
        'total_accessories': len(PET_ACCESSORIES),
        'owned_count': len(owned_ids)
    }


@router.get("/accessories/equipped")
async def get_equipped_accessories(current_user: dict = Depends(get_current_user)):
    """Get currently equipped accessories for active pet"""
    user_pet = await db.user_pets.find_one(
        {'user_id': current_user['id'], 'is_active': True},
        {'_id': 0}
    )
    
    if not user_pet:
        return {'has_pet': False, 'equipped': {}}
    
    equipped = user_pet.get('equipped_accessories', {})
    
    # Enrich with accessory info
    equipped_details = {}
    for slot, acc_id in equipped.items():
        if acc_id and acc_id in PET_ACCESSORIES:
            acc_info = PET_ACCESSORIES[acc_id]
            equipped_details[slot] = {
                'id': acc_id,
                'name': acc_info['name'],
                'icon': acc_info['icon'],
                'rarity': acc_info['rarity'],
                'category': acc_info['category']
            }
    
    return {
        'has_pet': True,
        'pet_id': user_pet['id'],
        'equipped': equipped_details,
        'slots': list(ACCESSORY_CATEGORIES.keys())
    }


@router.post("/accessories/purchase/{accessory_id}")
async def purchase_accessory(accessory_id: str, current_user: dict = Depends(get_current_user)):
    """Purchase an accessory from the shop"""
    if accessory_id not in PET_ACCESSORIES:
        raise HTTPException(status_code=404, detail="Accessory not found")
    
    accessory = PET_ACCESSORIES[accessory_id]
    
    # Check if it's a shop item
    if accessory['unlock_type'] != 'shop':
        raise HTTPException(status_code=400, detail="This accessory cannot be purchased - it must be unlocked through achievements")
    
    # Check if already owned
    existing = await db.user_accessories.find_one({
        'user_id': current_user['id'],
        'accessory_id': accessory_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="You already own this accessory")
    
    # Check coins
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0, 'coins': 1})
    user_coins = user.get('coins', 0)
    
    if user_coins < accessory['price']:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough coins. You have {user_coins}, need {accessory['price']}"
        )
    
    # Deduct coins
    await db.users.update_one(
        {'id': current_user['id']},
        {'$inc': {'coins': -accessory['price']}}
    )
    
    # Add to user's accessories
    user_accessory = {
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'accessory_id': accessory_id,
        'acquired_at': datetime.now(timezone.utc).isoformat(),
        'acquired_via': 'purchase'
    }
    await db.user_accessories.insert_one(user_accessory)
    
    return {
        'message': f"You purchased {accessory['name']}!",
        'accessory': {
            'id': accessory_id,
            'name': accessory['name'],
            'icon': accessory['icon'],
            'rarity': accessory['rarity']
        },
        'coins_spent': accessory['price'],
        'coins_remaining': user_coins - accessory['price']
    }


@router.post("/accessories/claim/{accessory_id}")
async def claim_accessory(accessory_id: str, current_user: dict = Depends(get_current_user)):
    """Claim an unlocked accessory (non-shop items)"""
    if accessory_id not in PET_ACCESSORIES:
        raise HTTPException(status_code=404, detail="Accessory not found")
    
    accessory = PET_ACCESSORIES[accessory_id]
    
    # Check if it's NOT a shop item
    if accessory['unlock_type'] == 'shop':
        raise HTTPException(status_code=400, detail="This accessory must be purchased, not claimed")
    
    # Check if already owned
    existing = await db.user_accessories.find_one({
        'user_id': current_user['id'],
        'accessory_id': accessory_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="You already own this accessory")
    
    # Check unlock status
    unlock_status = await check_accessory_unlock(current_user['id'], accessory_id)
    if not unlock_status.get('unlocked'):
        raise HTTPException(status_code=400, detail=f"Cannot claim: {unlock_status.get('reason', 'Not unlocked yet')}")
    
    # Add to user's accessories
    user_accessory = {
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'accessory_id': accessory_id,
        'acquired_at': datetime.now(timezone.utc).isoformat(),
        'acquired_via': accessory['unlock_type']
    }
    await db.user_accessories.insert_one(user_accessory)
    
    return {
        'message': f"You claimed {accessory['name']}!",
        'accessory': {
            'id': accessory_id,
            'name': accessory['name'],
            'icon': accessory['icon'],
            'rarity': accessory['rarity']
        },
        'unlock_type': accessory['unlock_type']
    }


@router.post("/accessories/equip")
async def equip_accessory(request: EquipAccessoryRequest, current_user: dict = Depends(get_current_user)):
    """Equip an owned accessory to your active pet"""
    accessory_id = request.accessory_id
    
    if accessory_id not in PET_ACCESSORIES:
        raise HTTPException(status_code=404, detail="Accessory not found")
    
    # Check if user owns this accessory
    owned = await db.user_accessories.find_one({
        'user_id': current_user['id'],
        'accessory_id': accessory_id
    })
    if not owned:
        raise HTTPException(status_code=400, detail="You don't own this accessory")
    
    # Get user's active pet
    user_pet = await db.user_pets.find_one(
        {'user_id': current_user['id'], 'is_active': True},
        {'_id': 0}
    )
    if not user_pet:
        raise HTTPException(status_code=400, detail="No active pet to equip accessory on")
    
    accessory = PET_ACCESSORIES[accessory_id]
    slot = ACCESSORY_CATEGORIES[accessory['category']]['slot']
    
    # Update equipped accessories
    equipped = user_pet.get('equipped_accessories', {})
    equipped[slot] = accessory_id
    
    await db.user_pets.update_one(
        {'id': user_pet['id']},
        {'$set': {'equipped_accessories': equipped}}
    )
    
    # Check for theme bonus
    pet_type = user_pet['pet_type']
    theme_match = get_theme_match_bonus(accessory_id, pet_type)
    
    return {
        'message': f"Equipped {accessory['name']}!",
        'slot': slot,
        'accessory': {
            'id': accessory_id,
            'name': accessory['name'],
            'icon': accessory['icon']
        },
        'theme_bonus': theme_match,
        'theme_bonus_message': f"Theme match! {accessory['name']} looks great on your pet!" if theme_match else None
    }


@router.post("/accessories/unequip/{slot}")
async def unequip_accessory(slot: str, current_user: dict = Depends(get_current_user)):
    """Unequip an accessory from a slot"""
    valid_slots = ['head', 'face', 'neck', 'back', 'aura']
    if slot not in valid_slots:
        raise HTTPException(status_code=400, detail=f"Invalid slot. Choose from: {', '.join(valid_slots)}")
    
    # Get user's active pet
    user_pet = await db.user_pets.find_one(
        {'user_id': current_user['id'], 'is_active': True},
        {'_id': 0}
    )
    if not user_pet:
        raise HTTPException(status_code=400, detail="No active pet")
    
    equipped = user_pet.get('equipped_accessories', {})
    
    if slot not in equipped or not equipped[slot]:
        raise HTTPException(status_code=400, detail=f"Nothing equipped in {slot} slot")
    
    # Remove from slot
    old_accessory_id = equipped[slot]
    equipped[slot] = None
    
    await db.user_pets.update_one(
        {'id': user_pet['id']},
        {'$set': {'equipped_accessories': equipped}}
    )
    
    old_accessory = PET_ACCESSORIES.get(old_accessory_id, {})
    
    return {
        'message': f"Unequipped {old_accessory.get('name', 'accessory')} from {slot}",
        'slot': slot
    }


@router.get("/accessories/inventory")
async def get_accessory_inventory(current_user: dict = Depends(get_current_user)):
    """Get all accessories owned by the user"""
    owned = await db.user_accessories.find(
        {'user_id': current_user['id']},
        {'_id': 0}
    ).to_list(100)
    
    # Get active pet's equipped accessories
    user_pet = await db.user_pets.find_one(
        {'user_id': current_user['id'], 'is_active': True},
        {'_id': 0, 'equipped_accessories': 1, 'pet_type': 1}
    )
    equipped = user_pet.get('equipped_accessories', {}) if user_pet else {}
    pet_type = user_pet.get('pet_type') if user_pet else None
    equipped_ids = set(equipped.values())
    
    inventory = []
    for item in owned:
        acc_id = item['accessory_id']
        if acc_id in PET_ACCESSORIES:
            acc_info = PET_ACCESSORIES[acc_id]
            theme_match = get_theme_match_bonus(acc_id, pet_type) if pet_type else False
            
            inventory.append({
                'id': acc_id,
                'name': acc_info['name'],
                'description': acc_info['description'],
                'icon': acc_info['icon'],
                'rarity': acc_info['rarity'],
                'category': acc_info['category'],
                'slot': ACCESSORY_CATEGORIES[acc_info['category']]['slot'],
                'is_equipped': acc_id in equipped_ids,
                'theme_match': theme_match,
                'acquired_at': item['acquired_at'],
                'acquired_via': item.get('acquired_via', 'unknown')
            })
    
    # Group by category
    by_category = {}
    for item in inventory:
        cat = item['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)
    
    return {
        'inventory': inventory,
        'by_category': by_category,
        'total_owned': len(inventory),
        'equipped_slots': equipped
    }


@router.get("/accessories/shop")
async def get_accessory_shop(current_user: dict = Depends(get_current_user)):
    """Get accessories available for purchase in the shop"""
    user_id = current_user['id']
    
    # Get user's owned accessories
    owned = await db.user_accessories.find(
        {'user_id': user_id},
        {'_id': 0, 'accessory_id': 1}
    ).to_list(100)
    owned_ids = {a['accessory_id'] for a in owned}
    
    # Get user coins
    user = await db.users.find_one({'id': user_id}, {'_id': 0, 'coins': 1})
    user_coins = user.get('coins', 0)
    
    # Get active pet for theme matching
    user_pet = await db.user_pets.find_one(
        {'user_id': user_id, 'is_active': True},
        {'_id': 0, 'pet_type': 1}
    )
    pet_type = user_pet.get('pet_type') if user_pet else None
    
    shop_items = []
    for acc_id, acc_info in PET_ACCESSORIES.items():
        if acc_info['unlock_type'] == 'shop':
            theme_match = get_theme_match_bonus(acc_id, pet_type) if pet_type else False
            shop_items.append({
                'id': acc_id,
                'name': acc_info['name'],
                'description': acc_info['description'],
                'icon': acc_info['icon'],
                'rarity': acc_info['rarity'],
                'category': acc_info['category'],
                'slot': ACCESSORY_CATEGORIES[acc_info['category']]['slot'],
                'price': acc_info['price'],
                'owned': acc_id in owned_ids,
                'can_afford': user_coins >= acc_info['price'],
                'theme_match': theme_match,
                'theme_bonus': acc_info.get('theme_bonus', [])
            })
    
    # Sort by price
    shop_items.sort(key=lambda x: x['price'])
    
    return {
        'items': shop_items,
        'user_coins': user_coins,
        'total_available': len([i for i in shop_items if not i['owned']])
    }


@router.get("/accessories/unlockable")
async def get_unlockable_accessories(current_user: dict = Depends(get_current_user)):
    """Get accessories that can be unlocked through achievements/progress"""
    user_id = current_user['id']
    
    # Get owned accessories
    owned = await db.user_accessories.find(
        {'user_id': user_id},
        {'_id': 0, 'accessory_id': 1}
    ).to_list(100)
    owned_ids = {a['accessory_id'] for a in owned}
    
    unlockable = []
    for acc_id, acc_info in PET_ACCESSORIES.items():
        if acc_info['unlock_type'] != 'shop':
            unlock_status = await check_accessory_unlock(user_id, acc_id)
            
            unlockable.append({
                'id': acc_id,
                'name': acc_info['name'],
                'description': acc_info['description'],
                'icon': acc_info['icon'],
                'rarity': acc_info['rarity'],
                'category': acc_info['category'],
                'unlock_type': acc_info['unlock_type'],
                'unlock_value': acc_info['unlock_value'],
                'owned': acc_id in owned_ids,
                'unlocked': unlock_status.get('unlocked', False),
                'claimable': unlock_status.get('unlocked', False) and acc_id not in owned_ids,
                'unlock_reason': unlock_status.get('reason', ''),
                'progress': unlock_status.get('progress')
            })
    
    # Sort: claimable first, then by unlock type
    unlockable.sort(key=lambda x: (not x['claimable'], x['unlock_type'], x['name']))
    
    return {
        'unlockable': unlockable,
        'claimable_count': len([u for u in unlockable if u['claimable']])
    }



@router.get("/accessories/seasonal")
async def get_seasonal_accessories(current_user: dict = Depends(get_current_user)):
    """Get currently available seasonal/limited edition accessories"""
    user_id = current_user['id']
    
    # Get user's owned accessories
    owned = await db.user_accessories.find(
        {'user_id': user_id},
        {'_id': 0, 'accessory_id': 1}
    ).to_list(200)
    owned_ids = {a['accessory_id'] for a in owned}
    
    # Get user coins
    user = await db.users.find_one({'id': user_id}, {'_id': 0, 'coins': 1})
    user_coins = user.get('coins', 0)
    
    # Get active pet for theme matching
    user_pet = await db.user_pets.find_one(
        {'user_id': user_id, 'is_active': True},
        {'_id': 0, 'pet_type': 1}
    )
    pet_type = user_pet.get('pet_type') if user_pet else None
    
    available_seasonal = []
    upcoming_seasonal = []
    
    for acc_id, acc_info in SEASONAL_ACCESSORIES.items():
        availability = is_seasonal_available(acc_info)
        season_info = get_season_info(acc_info.get('season', ''))
        theme_match = get_theme_match_bonus(acc_id, pet_type) if pet_type else False
        
        item_data = {
            'id': acc_id,
            'name': acc_info['name'],
            'description': acc_info['description'],
            'icon': acc_info['icon'],
            'rarity': acc_info['rarity'],
            'category': acc_info['category'],
            'slot': ACCESSORY_CATEGORIES[acc_info['category']]['slot'],
            'price': acc_info['price'],
            'owned': acc_id in owned_ids,
            'can_afford': user_coins >= acc_info['price'],
            'theme_match': theme_match,
            'season': season_info['name'],
            'season_icon': season_info['icon'],
            'season_color': season_info['color'],
            'is_limited': True,
            'available': availability['available'],
            'days_remaining': availability['days_remaining'],
            'available_dates': f"{availability['start']} - {availability['end']}"
        }
        
        if availability['available']:
            available_seasonal.append(item_data)
        else:
            upcoming_seasonal.append(item_data)
    
    # Sort available by days remaining (urgency), upcoming by season
    available_seasonal.sort(key=lambda x: (x['owned'], x['days_remaining'] or 999))
    
    # Group by season for display
    by_season = {}
    for item in available_seasonal:
        season = item['season']
        if season not in by_season:
            by_season[season] = {
                'name': season,
                'icon': item['season_icon'],
                'items': []
            }
        by_season[season]['items'].append(item)
    
    return {
        'available': available_seasonal,
        'by_season': by_season,
        'upcoming_count': len(upcoming_seasonal),
        'user_coins': user_coins,
        'total_available': len([i for i in available_seasonal if not i['owned']]),
        'seasons': list(by_season.keys())
    }


@router.post("/accessories/purchase-seasonal/{accessory_id}")
async def purchase_seasonal_accessory(accessory_id: str, current_user: dict = Depends(get_current_user)):
    """Purchase a seasonal accessory (only available during its season)"""
    if accessory_id not in SEASONAL_ACCESSORIES:
        raise HTTPException(status_code=404, detail="Seasonal accessory not found")
    
    accessory = SEASONAL_ACCESSORIES[accessory_id]
    
    # Check if currently available
    availability = is_seasonal_available(accessory)
    if not availability['available']:
        season_info = get_season_info(accessory.get('season', ''))
        raise HTTPException(
            status_code=400, 
            detail=f"This item is only available during {season_info['name']} ({availability['start']} - {availability['end']})"
        )
    
    # Check if already owned
    existing = await db.user_accessories.find_one({
        'user_id': current_user['id'],
        'accessory_id': accessory_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="You already own this seasonal item")
    
    # Check coins
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0, 'coins': 1})
    user_coins = user.get('coins', 0)
    
    if user_coins < accessory['price']:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough coins. You have {user_coins}, need {accessory['price']}"
        )
    
    # Deduct coins
    await db.users.update_one(
        {'id': current_user['id']},
        {'$inc': {'coins': -accessory['price']}}
    )
    
    # Add to user's accessories with seasonal flag
    user_accessory = {
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'accessory_id': accessory_id,
        'acquired_at': datetime.now(timezone.utc).isoformat(),
        'acquired_via': 'seasonal_purchase',
        'season': accessory.get('season', 'unknown'),
        'is_limited_edition': True
    }
    await db.user_accessories.insert_one(user_accessory)
    
    season_info = get_season_info(accessory.get('season', ''))
    
    return {
        'message': f"You purchased the limited edition {accessory['name']}!",
        'accessory': {
            'id': accessory_id,
            'name': accessory['name'],
            'icon': accessory['icon'],
            'rarity': accessory['rarity'],
            'season': season_info['name'],
            'is_limited': True
        },
        'coins_spent': accessory['price'],
        'coins_remaining': user_coins - accessory['price']
    }


@router.get("/accessories/all-seasons")
async def get_all_seasons_info(current_user: dict = Depends(get_current_user)):
    """Get info about all seasonal events and their accessories"""
    seasons_data = {}
    
    for acc_id, acc_info in SEASONAL_ACCESSORIES.items():
        season_key = acc_info.get('season', 'unknown')
        
        if season_key not in seasons_data:
            season_info = get_season_info(season_key)
            availability = is_seasonal_available(acc_info)
            
            seasons_data[season_key] = {
                'key': season_key,
                'name': season_info['name'],
                'icon': season_info['icon'],
                'color': season_info['color'],
                'available_dates': f"{acc_info['available_month_start']}/{acc_info['available_day_start']} - {acc_info['available_month_end']}/{acc_info['available_day_end']}",
                'is_active': availability['available'],
                'days_remaining': availability['days_remaining'],
                'items_count': 0,
                'items': []
            }
        
        seasons_data[season_key]['items_count'] += 1
        seasons_data[season_key]['items'].append({
            'id': acc_id,
            'name': acc_info['name'],
            'icon': acc_info['icon'],
            'price': acc_info['price'],
            'rarity': acc_info['rarity']
        })
    
    # Sort seasons: active first, then by upcoming date
    seasons_list = sorted(
        seasons_data.values(),
        key=lambda x: (not x['is_active'], x['name'])
    )
    
    return {
        'seasons': seasons_list,
        'active_seasons': [s for s in seasons_list if s['is_active']],
        'total_seasonal_items': len(SEASONAL_ACCESSORIES)
    }
