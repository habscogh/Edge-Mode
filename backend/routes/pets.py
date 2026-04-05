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
PET_TYPES = {
    # Classic Animals (Free starters)
    "puppy": {
        "name": "Spark",
        "category": "animals",
        "description": "A loyal pup that grows stronger with your dedication",
        "rarity": "common",
        "price": 0,  # Free starter
        "is_starter": True,
        "stages": {
            1: {"icon": "🐕", "name": "Puppy"},
            2: {"icon": "🐕", "name": "Young Dog"},
            3: {"icon": "🐕", "name": "Energetic Dog"},
            4: {"icon": "🦮", "name": "Loyal Companion"},
            5: {"icon": "🐺", "name": "Alpha Dog"},
            6: {"icon": "🐺", "name": "Legendary Wolf"}
        }
    },
    "kitten": {
        "name": "Whisker",
        "category": "animals",
        "description": "A curious kitten that becomes wiser as you grow",
        "rarity": "common",
        "price": 0,
        "is_starter": True,
        "stages": {
            1: {"icon": "🐱", "name": "Kitten"},
            2: {"icon": "🐱", "name": "Young Cat"},
            3: {"icon": "🐈", "name": "Clever Cat"},
            4: {"icon": "🐈‍⬛", "name": "Shadow Cat"},
            5: {"icon": "🦁", "name": "Proud Lion"},
            6: {"icon": "🦁", "name": "Legendary Lion"}
        }
    },
    "bunny": {
        "name": "Bounce",
        "category": "animals",
        "description": "A quick bunny that hops higher with each milestone",
        "rarity": "common",
        "price": 0,
        "is_starter": True,
        "stages": {
            1: {"icon": "🐰", "name": "Baby Bunny"},
            2: {"icon": "🐰", "name": "Young Rabbit"},
            3: {"icon": "🐇", "name": "Swift Rabbit"},
            4: {"icon": "🐇", "name": "Forest Hare"},
            5: {"icon": "🐇", "name": "Moon Rabbit"},
            6: {"icon": "🐇", "name": "Legendary Hare"}
        }
    },
    
    # Activity-Based Starters (Free)
    "sports": {
        "name": "Champ",
        "category": "activity",
        "description": "A swift cheetah that races alongside your progress",
        "rarity": "common",
        "price": 0,
        "is_starter": True,
        "stages": {
            1: {"icon": "🐆", "name": "Cheetah Cub"},
            2: {"icon": "🐆", "name": "Young Cheetah"},
            3: {"icon": "🐆", "name": "Swift Runner"},
            4: {"icon": "🐆", "name": "Sprint Champion"},
            5: {"icon": "🐆", "name": "Lightning Cheetah"},
            6: {"icon": "🐆", "name": "Legendary Speedster"}
        }
    },
    "music": {
        "name": "Melody",
        "category": "activity",
        "description": "A songbird that sings sweeter as you grow",
        "rarity": "common",
        "price": 0,
        "is_starter": True,
        "stages": {
            1: {"icon": "🐦", "name": "Little Songbird"},
            2: {"icon": "🐦", "name": "Young Warbler"},
            3: {"icon": "🦜", "name": "Colorful Singer"},
            4: {"icon": "🦜", "name": "Melodic Parrot"},
            5: {"icon": "🦚", "name": "Majestic Peacock"},
            6: {"icon": "🦅", "name": "Legendary Phoenix Bird"}
        }
    },
    "study": {
        "name": "Scholar",
        "category": "activity",
        "description": "A wise owl that grows smarter with your dedication",
        "rarity": "common",
        "price": 0,
        "is_starter": True,
        "stages": {
            1: {"icon": "🦉", "name": "Owlet"},
            2: {"icon": "🦉", "name": "Young Owl"},
            3: {"icon": "🦉", "name": "Wise Owl"},
            4: {"icon": "🦉", "name": "Scholar Owl"},
            5: {"icon": "🦉", "name": "Sage Owl"},
            6: {"icon": "🦉", "name": "Grand Owl Master"}
        }
    },
    "fox": {
        "name": "Blitz",
        "category": "fantasy",
        "description": "A mystical fox that becomes more magical over time",
        "rarity": "common",
        "price": 0,
        "is_starter": True,
        "stages": {
            1: {"icon": "🦊", "name": "Fox Kit"},
            2: {"icon": "🦊", "name": "Young Fox"},
            3: {"icon": "🦊", "name": "Swift Fox"},
            4: {"icon": "🦊", "name": "Fire Fox"},
            5: {"icon": "🦊", "name": "Spirit Fox"},
            6: {"icon": "🦊", "name": "Nine-Tail Legend"}
        }
    },
    
    # Fantasy Creatures (Shop items)
    "dragon": {
        "name": "Blaze",
        "category": "fantasy",
        "description": "A baby dragon that grows into a mighty beast",
        "rarity": "rare",
        "price": 300,
        "is_starter": False,
        "stages": {
            1: {"icon": "🐣", "name": "Dragon Egg"},
            2: {"icon": "🦎", "name": "Baby Dragon"},
            3: {"icon": "🐉", "name": "Young Drake"},
            4: {"icon": "🐉", "name": "Fire Drake"},
            5: {"icon": "🐲", "name": "Ancient Dragon"},
            6: {"icon": "🐲", "name": "Legendary Dragon"}
        }
    },
    "phoenix": {
        "name": "Ember",
        "category": "fantasy",
        "description": "A firebird that rises stronger each day",
        "rarity": "epic",
        "price": 450,
        "is_starter": False,
        "stages": {
            1: {"icon": "🪺", "name": "Phoenix Egg"},
            2: {"icon": "🐦", "name": "Flame Chick"},
            3: {"icon": "🐦‍🔥", "name": "Fire Bird"},
            4: {"icon": "🐦‍🔥", "name": "Blazing Phoenix"},
            5: {"icon": "🔥", "name": "Inferno Phoenix"},
            6: {"icon": "🔥", "name": "Legendary Phoenix"}
        }
    },
    "unicorn": {
        "name": "Shimmer",
        "category": "fantasy",
        "description": "A magical unicorn that sparkles brighter with progress",
        "rarity": "epic",
        "price": 400,
        "is_starter": False,
        "stages": {
            1: {"icon": "🐴", "name": "Foal"},
            2: {"icon": "🐴", "name": "Young Horse"},
            3: {"icon": "🦄", "name": "Unicorn"},
            4: {"icon": "🦄", "name": "Shining Unicorn"},
            5: {"icon": "🦄", "name": "Celestial Unicorn"},
            6: {"icon": "🦄", "name": "Legendary Unicorn"}
        }
    },
    
    # Abstract/Cute Mascots
    "slime": {
        "name": "Goo",
        "category": "abstract",
        "description": "A friendly slime that grows and changes color",
        "rarity": "uncommon",
        "price": 150,
        "is_starter": False,
        "stages": {
            1: {"icon": "🫧", "name": "Tiny Slime"},
            2: {"icon": "🟢", "name": "Green Slime"},
            3: {"icon": "🔵", "name": "Blue Slime"},
            4: {"icon": "🟣", "name": "Purple Slime"},
            5: {"icon": "🟡", "name": "Golden Slime"},
            6: {"icon": "⭐", "name": "Star Slime"}
        }
    },
    "spirit": {
        "name": "Wisp",
        "category": "abstract",
        "description": "A gentle spirit that guides your journey",
        "rarity": "rare",
        "price": 250,
        "is_starter": False,
        "stages": {
            1: {"icon": "✨", "name": "Tiny Spark"},
            2: {"icon": "💫", "name": "Young Wisp"},
            3: {"icon": "🌟", "name": "Bright Spirit"},
            4: {"icon": "⭐", "name": "Guiding Light"},
            5: {"icon": "🌙", "name": "Moon Spirit"},
            6: {"icon": "☀️", "name": "Sun Spirit"}
        }
    },
    "crystal": {
        "name": "Gem",
        "category": "abstract",
        "description": "A living crystal that becomes more brilliant",
        "rarity": "legendary",
        "price": 600,
        "is_starter": False,
        "stages": {
            1: {"icon": "�ite", "name": "Raw Crystal"},
            2: {"icon": "💎", "name": "Cut Gem"},
            3: {"icon": "💎", "name": "Polished Gem"},
            4: {"icon": "💎", "name": "Brilliant Gem"},
            5: {"icon": "💎", "name": "Radiant Crystal"},
            6: {"icon": "💎", "name": "Legendary Crystal"}
        }
    },
    "robot": {
        "name": "Bolt",
        "category": "abstract",
        "description": "A little robot companion that upgrades over time",
        "rarity": "rare",
        "price": 350,
        "is_starter": False,
        "stages": {
            1: {"icon": "🔩", "name": "Scrap Bot"},
            2: {"icon": "🤖", "name": "Mini Bot"},
            3: {"icon": "🤖", "name": "Helper Bot"},
            4: {"icon": "🤖", "name": "Smart Bot"},
            5: {"icon": "🤖", "name": "Super Bot"},
            6: {"icon": "🤖", "name": "Legendary Mech"}
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
    """Interact with your pet (tap, pet, play)"""
    user_pet = await db.user_pets.find_one(
        {'user_id': current_user['id'], 'is_active': True},
        {'_id': 0}
    )
    
    if not user_pet:
        raise HTTPException(status_code=404, detail="No active pet found")
    
    pet_type = user_pet['pet_type']
    pet_info = PET_TYPES.get(pet_type)
    pet_name = user_pet.get('custom_name') or pet_info['name']
    
    # Update happiness and last interaction
    new_happiness = min(100, user_pet.get('happiness', 100) + 5)
    
    await db.user_pets.update_one(
        {'id': user_pet['id']},
        {
            '$set': {
                'happiness': new_happiness,
                'last_interaction': datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Get a celebration message
    message = get_random_message('celebration', pet_name)
    
    return {
        'message': message,
        'happiness': new_happiness,
        'pet_name': pet_name,
        'interaction': request.interaction_type
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
