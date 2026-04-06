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


# ============ Pydantic Models ============

class SelectPetRequest(BaseModel):
    pet_type: str
    pet_name: Optional[str] = None  # Custom name


class InteractRequest(BaseModel):
    interaction_type: str = "pet"  # "pet", "feed", "play"


# ============ Helper Functions ============

def get_evolution_stage(streak_days: int) -> int:
    """Get evolution stage based on streak days"""
    stage = 1
    for s, info in EVOLUTION_STAGES.items():
        if streak_days >= info["streak_required"]:
            stage = s
    return stage


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
