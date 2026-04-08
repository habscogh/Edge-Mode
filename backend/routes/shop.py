"""
Shop routes for Edge Mode - Coin Shop, Items, Inventory, Purchases
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel
import uuid

from config import db
from utils.auth import get_current_user, require_admin as get_current_admin

router = APIRouter(prefix="/shop", tags=["Shop"])


# ============ Shop Item Categories ============

SHOP_CATEGORIES = {
    "themes": {
        "name": "Profile Themes",
        "description": "Customize your profile appearance",
        "icon": "🎨"
    },
    "badges": {
        "name": "Custom Badges",
        "description": "Show off exclusive badges",
        "icon": "🏅"
    },
    "streak_shields": {
        "name": "Streak Shields",
        "description": "Protect your streaks from breaking",
        "icon": "🛡️"
    },
    "avatars": {
        "name": "Avatar Frames",
        "description": "Stand out with unique avatar frames",
        "icon": "👤"
    },
    "effects": {
        "name": "Special Effects",
        "description": "Add flair to your achievements",
        "icon": "✨"
    }
}


# ============ Default Shop Items (Seeded on first run) ============
# Pricing: Common ~100 coins (2 weeks), Mid-tier ~200 (1 month), Legendary ~600 (3 months)

DEFAULT_SHOP_ITEMS = [
    # Themes - each has gradient colors for profile customization
    {
        "id": "theme-midnight",
        "name": "Midnight Purple",
        "description": "Deep purple gradient theme",
        "category": "themes",
        "price": 100,
        "rarity": "common",
        "preview_color": "#7c3aed",
        "icon": "🌙",
        "theme_data": {
            "gradient": "linear-gradient(135deg, #1e1b4b 0%, #4c1d95 50%, #7c3aed 100%)",
            "border_color": "#7c3aed",
            "accent_color": "#a78bfa",
            "glow_color": "rgba(124, 58, 237, 0.3)"
        }
    },
    {
        "id": "theme-ocean",
        "name": "Ocean Blue",
        "description": "Calming ocean-inspired theme",
        "category": "themes",
        "price": 100,
        "rarity": "common",
        "preview_color": "#0ea5e9",
        "icon": "🌊",
        "theme_data": {
            "gradient": "linear-gradient(135deg, #0c4a6e 0%, #0369a1 50%, #0ea5e9 100%)",
            "border_color": "#0ea5e9",
            "accent_color": "#38bdf8",
            "glow_color": "rgba(14, 165, 233, 0.3)"
        }
    },
    {
        "id": "theme-sunset",
        "name": "Sunset Fire",
        "description": "Warm orange and red gradient",
        "category": "themes",
        "price": 150,
        "rarity": "uncommon",
        "preview_color": "#f97316",
        "icon": "🌅",
        "theme_data": {
            "gradient": "linear-gradient(135deg, #7c2d12 0%, #c2410c 50%, #f97316 100%)",
            "border_color": "#f97316",
            "accent_color": "#fb923c",
            "glow_color": "rgba(249, 115, 22, 0.3)"
        }
    },
    {
        "id": "theme-neon",
        "name": "Neon Glow",
        "description": "Cyberpunk neon aesthetic",
        "category": "themes",
        "price": 250,
        "rarity": "rare",
        "preview_color": "#ec4899",
        "icon": "💜",
        "theme_data": {
            "gradient": "linear-gradient(135deg, #500724 0%, #9d174d 50%, #ec4899 100%)",
            "border_color": "#ec4899",
            "accent_color": "#f472b6",
            "glow_color": "rgba(236, 72, 153, 0.4)"
        }
    },
    {
        "id": "theme-gold",
        "name": "Golden Legend",
        "description": "Prestigious gold theme for champions",
        "category": "themes",
        "price": 600,
        "rarity": "legendary",
        "preview_color": "#fbbf24",
        "icon": "👑",
        "theme_data": {
            "gradient": "linear-gradient(135deg, #78350f 0%, #b45309 50%, #fbbf24 100%)",
            "border_color": "#fbbf24",
            "accent_color": "#fcd34d",
            "glow_color": "rgba(251, 191, 36, 0.4)"
        }
    },
    
    # Custom Badges
    {
        "id": "badge-fire",
        "name": "Fire Starter",
        "description": "Show you're on fire!",
        "category": "badges",
        "price": 100,
        "rarity": "common",
        "icon": "🔥"
    },
    {
        "id": "badge-diamond",
        "name": "Diamond Mind",
        "description": "Unbreakable focus badge",
        "category": "badges",
        "price": 175,
        "rarity": "uncommon",
        "icon": "💎"
    },
    {
        "id": "badge-rocket",
        "name": "Rocket Riser",
        "description": "Always climbing higher",
        "category": "badges",
        "price": 250,
        "rarity": "rare",
        "icon": "🚀"
    },
    {
        "id": "badge-crown",
        "name": "Crown Achiever",
        "description": "Royal excellence badge",
        "category": "badges",
        "price": 400,
        "rarity": "epic",
        "icon": "👑"
    },
    
    # Streak Shields
    {
        "id": "shield-bronze",
        "name": "Bronze Shield",
        "description": "Protects your streak once",
        "category": "streak_shields",
        "price": 100,
        "rarity": "common",
        "uses": 1,
        "icon": "🛡️"
    },
    {
        "id": "shield-silver",
        "name": "Silver Shield",
        "description": "Protects your streak 3 times",
        "category": "streak_shields",
        "price": 200,
        "rarity": "uncommon",
        "uses": 3,
        "icon": "🛡️"
    },
    {
        "id": "shield-gold",
        "name": "Gold Shield",
        "description": "Protects your streak 7 times",
        "category": "streak_shields",
        "price": 350,
        "rarity": "rare",
        "uses": 7,
        "icon": "🛡️"
    },
    
    # Avatar Frames - each has frame styling data
    {
        "id": "frame-basic",
        "name": "Glow Frame",
        "description": "Subtle glowing border",
        "category": "avatars",
        "price": 100,
        "rarity": "common",
        "icon": "⭕",
        "frame_data": {
            "border_width": "3px",
            "border_style": "solid",
            "border_color": "#10b981",
            "box_shadow": "0 0 15px rgba(16, 185, 129, 0.5), inset 0 0 10px rgba(16, 185, 129, 0.2)",
            "animation": "none"
        }
    },
    {
        "id": "frame-lightning",
        "name": "Lightning Frame",
        "description": "Electric energy border",
        "category": "avatars",
        "price": 175,
        "rarity": "uncommon",
        "icon": "⚡",
        "frame_data": {
            "border_width": "3px",
            "border_style": "solid",
            "border_color": "#facc15",
            "box_shadow": "0 0 20px rgba(250, 204, 21, 0.6), 0 0 40px rgba(250, 204, 21, 0.3)",
            "animation": "pulse-lightning"
        }
    },
    {
        "id": "frame-flame",
        "name": "Flame Frame",
        "description": "Burning fire border",
        "category": "avatars",
        "price": 250,
        "rarity": "rare",
        "icon": "🔥",
        "frame_data": {
            "border_width": "4px",
            "border_style": "solid",
            "border_color": "#f97316",
            "box_shadow": "0 0 25px rgba(249, 115, 22, 0.7), 0 0 50px rgba(239, 68, 68, 0.4)",
            "animation": "pulse-flame"
        }
    },
    {
        "id": "frame-diamond",
        "name": "Diamond Frame",
        "description": "Prestigious diamond border",
        "category": "avatars",
        "price": 500,
        "rarity": "legendary",
        "icon": "💎",
        "frame_data": {
            "border_width": "4px",
            "border_style": "double",
            "border_color": "#60a5fa",
            "box_shadow": "0 0 30px rgba(96, 165, 250, 0.6), 0 0 60px rgba(147, 197, 253, 0.3), inset 0 0 20px rgba(96, 165, 250, 0.2)",
            "animation": "shimmer"
        }
    },
    
    # Special Effects - particles and animations
    {
        "id": "effect-sparkle",
        "name": "Sparkle Trail",
        "description": "Sparkles on your achievements",
        "category": "effects",
        "price": 125,
        "rarity": "common",
        "icon": "✨",
        "effect_data": {
            "type": "sparkle",
            "particle_color": "#fbbf24",
            "animation_class": "effect-sparkle"
        }
    },
    {
        "id": "effect-confetti",
        "name": "Confetti Burst",
        "description": "Celebrate with confetti!",
        "category": "effects",
        "price": 200,
        "rarity": "uncommon",
        "icon": "🎉",
        "effect_data": {
            "type": "confetti",
            "particle_colors": ["#f87171", "#fbbf24", "#34d399", "#60a5fa", "#a78bfa"],
            "animation_class": "effect-confetti"
        }
    },
    {
        "id": "effect-rainbow",
        "name": "Rainbow Aura",
        "description": "Colorful rainbow effects",
        "category": "effects",
        "price": 450,
        "rarity": "epic",
        "icon": "🌈",
        "effect_data": {
            "type": "rainbow",
            "animation_class": "effect-rainbow"
        }
    },
    {
        "id": "effect-stars",
        "name": "Starfall",
        "description": "Shooting stars animation",
        "category": "effects",
        "price": 350,
        "rarity": "rare",
        "icon": "⭐",
        "effect_data": {
            "type": "stars",
            "particle_color": "#fbbf24",
            "animation_class": "effect-stars"
        }
    }
]


# ============ Pydantic Models ============

class CreateShopItem(BaseModel):
    name: str
    description: str
    category: str
    price: int
    rarity: str = "common"  # common, uncommon, rare, epic, legendary
    icon: str = "🎁"
    preview_color: Optional[str] = None
    uses: Optional[int] = None  # For consumables like streak shields
    is_limited: bool = False
    stock: Optional[int] = None


class UpdateShopItem(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    is_active: Optional[bool] = None
    stock: Optional[int] = None


# ============ Helper Functions ============

async def seed_shop_items():
    """Seed default shop items if they don't exist, or update prices if they do"""
    for item in DEFAULT_SHOP_ITEMS:
        existing = await db.shop_items.find_one({'id': item['id']})
        if not existing:
            item_doc = {
                **item,
                'is_active': True,
                'is_limited': False,
                'stock': None,
                'total_sold': 0,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            await db.shop_items.insert_one(item_doc)
        else:
            # Update price if it changed
            if existing.get('price') != item['price']:
                await db.shop_items.update_one(
                    {'id': item['id']},
                    {'$set': {'price': item['price']}}
                )
    
    # Also seed/update referral exclusive items from referrals module
    from routes.referrals import REFERRAL_EXCLUSIVE_ITEMS
    for item in REFERRAL_EXCLUSIVE_ITEMS:
        existing = await db.shop_items.find_one({'id': item['id']})
        if not existing:
            item_doc = {
                **item,
                'is_active': True,
                'is_limited': False,
                'stock': None,
                'total_sold': 0,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            await db.shop_items.insert_one(item_doc)
        else:
            # Update price and other fields if changed
            await db.shop_items.update_one(
                {'id': item['id']},
                {'$set': {
                    'price': item['price'],
                    'referrals_required': item.get('referrals_required'),
                    'is_referral_exclusive': item.get('is_referral_exclusive', True)
                }}
            )


def get_rarity_color(rarity: str) -> str:
    """Get color for rarity level"""
    colors = {
        "common": "#9ca3af",      # Gray
        "uncommon": "#22c55e",    # Green
        "rare": "#3b82f6",        # Blue
        "epic": "#a855f7",        # Purple
        "legendary": "#fbbf24"    # Gold
    }
    return colors.get(rarity, "#9ca3af")


# ============ Public Shop Endpoints ============

@router.get("/categories")
async def get_shop_categories():
    """Get all shop categories"""
    return {"categories": SHOP_CATEGORIES}


@router.get("/items")
async def get_shop_items(category: Optional[str] = None):
    """Get all available shop items"""
    # Seed items on first access
    await seed_shop_items()
    
    query = {'is_active': True}
    if category:
        query['category'] = category
    
    items = await db.shop_items.find(query, {'_id': 0}).to_list(100)
    
    # Add rarity color to each item
    for item in items:
        item['rarity_color'] = get_rarity_color(item.get('rarity', 'common'))
    
    return {'items': items}


@router.get("/items/{item_id}")
async def get_shop_item(item_id: str):
    """Get a specific shop item"""
    item = await db.shop_items.find_one({'id': item_id, 'is_active': True}, {'_id': 0})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item['rarity_color'] = get_rarity_color(item.get('rarity', 'common'))
    return {'item': item}


@router.get("/featured")
async def get_featured_items():
    """Get featured/popular shop items"""
    await seed_shop_items()
    
    # Get top selling items
    items = await db.shop_items.find(
        {'is_active': True},
        {'_id': 0}
    ).sort('total_sold', -1).to_list(6)
    
    for item in items:
        item['rarity_color'] = get_rarity_color(item.get('rarity', 'common'))
    
    return {'featured': items}


# ============ User Inventory & Purchase Endpoints ============

@router.get("/inventory")
async def get_user_inventory(current_user: dict = Depends(get_current_user)):
    """Get user's purchased items"""
    inventory = await db.user_inventory.find(
        {'user_id': current_user['id']},
        {'_id': 0}
    ).to_list(100)
    
    # Get item details for each inventory item
    for inv_item in inventory:
        item = await db.shop_items.find_one({'id': inv_item['item_id']}, {'_id': 0})
        if item:
            inv_item['item'] = item
            inv_item['item']['rarity_color'] = get_rarity_color(item.get('rarity', 'common'))
    
    return {'inventory': inventory}


@router.get("/equipped")
async def get_equipped_items(current_user: dict = Depends(get_current_user)):
    """Get user's currently equipped items"""
    equipped = await db.user_inventory.find(
        {'user_id': current_user['id'], 'is_equipped': True},
        {'_id': 0}
    ).to_list(10)
    
    # Get item details
    for inv_item in equipped:
        item = await db.shop_items.find_one({'id': inv_item['item_id']}, {'_id': 0})
        if item:
            inv_item['item'] = item
    
    return {'equipped': equipped}


@router.post("/purchase/{item_id}")
async def purchase_item(item_id: str, current_user: dict = Depends(get_current_user)):
    """Purchase a shop item with coins"""
    # Get item
    item = await db.shop_items.find_one({'id': item_id, 'is_active': True}, {'_id': 0})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check if item is referral exclusive
    if item.get('is_referral_exclusive'):
        # User must have unlocked this item via referrals first
        user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
        referral_count = user.get('referral_count', 0)
        required_referrals = item.get('referrals_required', 999)
        
        if referral_count < required_referrals:
            raise HTTPException(
                status_code=400, 
                detail=f"This item requires {required_referrals} referrals to unlock. You have {referral_count}."
            )
    
    # Check stock for limited items
    if item.get('is_limited') and item.get('stock', 0) <= 0:
        raise HTTPException(status_code=400, detail="Item is out of stock")
    
    # Get user's coin balance
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0})
    current_coins = user.get('coins', 0)
    
    if current_coins < item['price']:
        raise HTTPException(
            status_code=400, 
            detail=f"Not enough coins. You have {current_coins}, need {item['price']}"
        )
    
    # Check if user already owns this item (for non-consumables)
    if item['category'] != 'streak_shields':
        existing = await db.user_inventory.find_one({
            'user_id': current_user['id'],
            'item_id': item_id
        })
        if existing:
            raise HTTPException(status_code=400, detail="You already own this item")
    
    # Deduct coins
    new_balance = current_coins - item['price']
    await db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'coins': new_balance}}
    )
    
    # Add to inventory
    inventory_item = {
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'item_id': item_id,
        'category': item['category'],
        'is_equipped': False,
        'uses_remaining': item.get('uses'),  # For consumables
        'purchased_at': datetime.now(timezone.utc).isoformat()
    }
    await db.user_inventory.insert_one(inventory_item)
    
    # Update stock and sales count
    update_ops = {'$inc': {'total_sold': 1}}
    if item.get('is_limited'):
        update_ops['$inc']['stock'] = -1
    await db.shop_items.update_one({'id': item_id}, update_ops)
    
    # Log transaction
    await db.coin_transactions.insert_one({
        'user_id': current_user['id'],
        'amount': -item['price'],
        'reason': f"Purchased {item['name']}",
        'item_id': item_id,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'new_balance': new_balance
    })
    
    return {
        'message': f"🎉 Purchased {item['name']}!",
        'item': item,
        'coins_spent': item['price'],
        'new_balance': new_balance,
        'inventory_id': inventory_item['id']
    }


@router.post("/equip/{inventory_id}")
async def equip_item(inventory_id: str, current_user: dict = Depends(get_current_user)):
    """Equip an item from inventory"""
    # Get inventory item
    inv_item = await db.user_inventory.find_one({
        'id': inventory_id,
        'user_id': current_user['id']
    })
    if not inv_item:
        raise HTTPException(status_code=404, detail="Item not found in your inventory")
    
    # Get item details
    item = await db.shop_items.find_one({'id': inv_item['item_id']}, {'_id': 0})
    if not item:
        raise HTTPException(status_code=404, detail="Item no longer exists")
    
    # Unequip other items in the same category
    await db.user_inventory.update_many(
        {
            'user_id': current_user['id'],
            'category': item['category'],
            'is_equipped': True
        },
        {'$set': {'is_equipped': False}}
    )
    
    # Equip this item
    await db.user_inventory.update_one(
        {'id': inventory_id},
        {'$set': {'is_equipped': True, 'equipped_at': datetime.now(timezone.utc).isoformat()}}
    )
    
    return {
        'message': f"Equipped {item['name']}!",
        'item': item
    }


@router.post("/unequip/{inventory_id}")
async def unequip_item(inventory_id: str, current_user: dict = Depends(get_current_user)):
    """Unequip an item"""
    result = await db.user_inventory.update_one(
        {'id': inventory_id, 'user_id': current_user['id']},
        {'$set': {'is_equipped': False}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found in your inventory")
    
    return {'message': 'Item unequipped'}


# ============ Display Badge Feature ============

class SetDisplayBadgeRequest(BaseModel):
    badge_id: Optional[str] = None  # None to clear display badge


@router.get("/display-badge")
async def get_display_badge(current_user: dict = Depends(get_current_user)):
    """Get user's currently set display badge"""
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0, 'display_badge': 1})
    display_badge = user.get('display_badge') if user else None
    
    if display_badge:
        # Get the badge details from inventory
        inventory_item = await db.user_inventory.find_one({
            'user_id': current_user['id'],
            'id': display_badge
        }, {'_id': 0})
        
        if inventory_item:
            # Get item details
            item = await db.shop_items.find_one({'id': inventory_item['item_id']}, {'_id': 0})
            if item:
                return {
                    'has_display_badge': True,
                    'badge': {
                        'inventory_id': inventory_item['id'],
                        'item_id': item['id'],
                        'name': item['name'],
                        'icon': item['icon'],
                        'rarity': item.get('rarity', 'common')
                    }
                }
    
    return {'has_display_badge': False, 'badge': None}


@router.get("/available-display-badges")
async def get_available_display_badges(current_user: dict = Depends(get_current_user)):
    """Get all badges user can set as display badge (owned badges from shop)"""
    # Get user's badge inventory items
    inventory_items = await db.user_inventory.find({
        'user_id': current_user['id'],
        'category': 'badges'
    }, {'_id': 0}).to_list(100)
    
    badges = []
    for inv_item in inventory_items:
        item = await db.shop_items.find_one({'id': inv_item['item_id']}, {'_id': 0})
        if item:
            badges.append({
                'inventory_id': inv_item['id'],
                'item_id': item['id'],
                'name': item['name'],
                'icon': item['icon'],
                'description': item.get('description', ''),
                'rarity': item.get('rarity', 'common')
            })
    
    # Get current display badge
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0, 'display_badge': 1})
    current_display = user.get('display_badge') if user else None
    
    return {
        'badges': badges,
        'current_display_badge': current_display
    }


@router.post("/set-display-badge")
async def set_display_badge(request: SetDisplayBadgeRequest, current_user: dict = Depends(get_current_user)):
    """Set or clear the user's display badge"""
    if request.badge_id:
        # Verify user owns this badge
        inventory_item = await db.user_inventory.find_one({
            'user_id': current_user['id'],
            'id': request.badge_id,
            'category': 'badges'
        })
        
        if not inventory_item:
            raise HTTPException(status_code=400, detail="You don't own this badge")
        
        # Set the display badge
        await db.users.update_one(
            {'id': current_user['id']},
            {'$set': {'display_badge': request.badge_id}}
        )
        
        # Get badge details for response
        item = await db.shop_items.find_one({'id': inventory_item['item_id']}, {'_id': 0})
        
        return {
            'message': f"Display badge set to {item['name']}!",
            'badge': {
                'inventory_id': inventory_item['id'],
                'name': item['name'],
                'icon': item['icon']
            }
        }
    else:
        # Clear display badge
        await db.users.update_one(
            {'id': current_user['id']},
            {'$unset': {'display_badge': ''}}
        )
        
        return {'message': 'Display badge cleared', 'badge': None}


# ============ Profile Customization (Themes, Frames, Effects) ============

class SetProfileCustomizationRequest(BaseModel):
    inventory_id: Optional[str] = None  # None to clear


@router.get("/profile-customization")
async def get_profile_customization(current_user: dict = Depends(get_current_user)):
    """Get user's active profile customizations (theme, frame, effect)"""
    user = await db.users.find_one(
        {'id': current_user['id']}, 
        {'_id': 0, 'active_theme': 1, 'active_frame': 1, 'active_effect': 1}
    )
    
    result = {
        'theme': None,
        'frame': None,
        'effect': None
    }
    
    # Get active theme
    if user and user.get('active_theme'):
        inv_item = await db.user_inventory.find_one({
            'user_id': current_user['id'],
            'id': user['active_theme']
        }, {'_id': 0, 'item_id': 1})
        if inv_item:
            item = await db.shop_items.find_one({'id': inv_item['item_id']}, {'_id': 0})
            if item:
                result['theme'] = {
                    'inventory_id': user['active_theme'],
                    'item_id': item['id'],
                    'name': item['name'],
                    'icon': item['icon'],
                    'theme_data': item.get('theme_data', {})
                }
    
    # Get active frame
    if user and user.get('active_frame'):
        inv_item = await db.user_inventory.find_one({
            'user_id': current_user['id'],
            'id': user['active_frame']
        }, {'_id': 0, 'item_id': 1})
        if inv_item:
            item = await db.shop_items.find_one({'id': inv_item['item_id']}, {'_id': 0})
            if item:
                result['frame'] = {
                    'inventory_id': user['active_frame'],
                    'item_id': item['id'],
                    'name': item['name'],
                    'icon': item['icon'],
                    'frame_data': item.get('frame_data', {})
                }
    
    # Get active effect
    if user and user.get('active_effect'):
        inv_item = await db.user_inventory.find_one({
            'user_id': current_user['id'],
            'id': user['active_effect']
        }, {'_id': 0, 'item_id': 1})
        if inv_item:
            item = await db.shop_items.find_one({'id': inv_item['item_id']}, {'_id': 0})
            if item:
                result['effect'] = {
                    'inventory_id': user['active_effect'],
                    'item_id': item['id'],
                    'name': item['name'],
                    'icon': item['icon'],
                    'effect_data': item.get('effect_data', {})
                }
    
    return result


@router.get("/available-customizations/{category}")
async def get_available_customizations(category: str, current_user: dict = Depends(get_current_user)):
    """Get all items user owns in a category (themes, avatars, effects)"""
    valid_categories = {'themes': 'active_theme', 'avatars': 'active_frame', 'effects': 'active_effect'}
    
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Choose from: {list(valid_categories.keys())}")
    
    # Get user's inventory items in this category
    inventory_items = await db.user_inventory.find({
        'user_id': current_user['id'],
        'category': category
    }, {'_id': 0}).to_list(100)
    
    items = []
    for inv_item in inventory_items:
        item = await db.shop_items.find_one({'id': inv_item['item_id']}, {'_id': 0})
        if item:
            item_data = {
                'inventory_id': inv_item['id'],
                'item_id': item['id'],
                'name': item['name'],
                'icon': item['icon'],
                'description': item.get('description', ''),
                'rarity': item.get('rarity', 'common')
            }
            # Add category-specific data
            if category == 'themes' and item.get('theme_data'):
                item_data['theme_data'] = item['theme_data']
            elif category == 'avatars' and item.get('frame_data'):
                item_data['frame_data'] = item['frame_data']
            elif category == 'effects' and item.get('effect_data'):
                item_data['effect_data'] = item['effect_data']
            
            items.append(item_data)
    
    # Get current active item
    user = await db.users.find_one({'id': current_user['id']}, {'_id': 0, valid_categories[category]: 1})
    current_active = user.get(valid_categories[category]) if user else None
    
    return {
        'items': items,
        'current_active': current_active
    }


@router.post("/set-theme")
async def set_active_theme(request: SetProfileCustomizationRequest, current_user: dict = Depends(get_current_user)):
    """Set or clear the user's active profile theme"""
    if request.inventory_id:
        # Verify user owns this theme
        inventory_item = await db.user_inventory.find_one({
            'user_id': current_user['id'],
            'id': request.inventory_id,
            'category': 'themes'
        })
        
        if not inventory_item:
            raise HTTPException(status_code=400, detail="You don't own this theme")
        
        await db.users.update_one(
            {'id': current_user['id']},
            {'$set': {'active_theme': request.inventory_id}}
        )
        
        item = await db.shop_items.find_one({'id': inventory_item['item_id']}, {'_id': 0})
        
        return {
            'message': f"Theme set to {item['name']}!",
            'theme': {
                'inventory_id': inventory_item['id'],
                'name': item['name'],
                'icon': item['icon'],
                'theme_data': item.get('theme_data', {})
            }
        }
    else:
        await db.users.update_one(
            {'id': current_user['id']},
            {'$unset': {'active_theme': ''}}
        )
        return {'message': 'Theme cleared', 'theme': None}


@router.post("/set-frame")
async def set_active_frame(request: SetProfileCustomizationRequest, current_user: dict = Depends(get_current_user)):
    """Set or clear the user's active avatar frame"""
    if request.inventory_id:
        # Verify user owns this frame
        inventory_item = await db.user_inventory.find_one({
            'user_id': current_user['id'],
            'id': request.inventory_id,
            'category': 'avatars'
        })
        
        if not inventory_item:
            raise HTTPException(status_code=400, detail="You don't own this frame")
        
        await db.users.update_one(
            {'id': current_user['id']},
            {'$set': {'active_frame': request.inventory_id}}
        )
        
        item = await db.shop_items.find_one({'id': inventory_item['item_id']}, {'_id': 0})
        
        return {
            'message': f"Frame set to {item['name']}!",
            'frame': {
                'inventory_id': inventory_item['id'],
                'name': item['name'],
                'icon': item['icon'],
                'frame_data': item.get('frame_data', {})
            }
        }
    else:
        await db.users.update_one(
            {'id': current_user['id']},
            {'$unset': {'active_frame': ''}}
        )
        return {'message': 'Frame cleared', 'frame': None}


@router.post("/set-effect")
async def set_active_effect(request: SetProfileCustomizationRequest, current_user: dict = Depends(get_current_user)):
    """Set or clear the user's active special effect"""
    if request.inventory_id:
        # Verify user owns this effect
        inventory_item = await db.user_inventory.find_one({
            'user_id': current_user['id'],
            'id': request.inventory_id,
            'category': 'effects'
        })
        
        if not inventory_item:
            raise HTTPException(status_code=400, detail="You don't own this effect")
        
        await db.users.update_one(
            {'id': current_user['id']},
            {'$set': {'active_effect': request.inventory_id}}
        )
        
        item = await db.shop_items.find_one({'id': inventory_item['item_id']}, {'_id': 0})
        
        return {
            'message': f"Effect set to {item['name']}!",
            'effect': {
                'inventory_id': inventory_item['id'],
                'name': item['name'],
                'icon': item['icon'],
                'effect_data': item.get('effect_data', {})
            }
        }
    else:
        await db.users.update_one(
            {'id': current_user['id']},
            {'$unset': {'active_effect': ''}}
        )
        return {'message': 'Effect cleared', 'effect': None}


@router.post("/use-shield")
async def use_streak_shield(current_user: dict = Depends(get_current_user)):
    """Use a streak shield to protect streak"""
    # Find an available streak shield
    shield = await db.user_inventory.find_one({
        'user_id': current_user['id'],
        'category': 'streak_shields',
        'uses_remaining': {'$gt': 0}
    })
    
    if not shield:
        raise HTTPException(status_code=400, detail="No streak shields available")
    
    # Decrement uses
    new_uses = shield['uses_remaining'] - 1
    if new_uses <= 0:
        # Remove from inventory if used up
        await db.user_inventory.delete_one({'id': shield['id']})
    else:
        await db.user_inventory.update_one(
            {'id': shield['id']},
            {'$set': {'uses_remaining': new_uses}}
        )
    
    return {
        'message': '🛡️ Streak shield activated! Your streak is protected.',
        'shields_remaining': new_uses
    }


@router.get("/coin-history")
async def get_coin_history(current_user: dict = Depends(get_current_user), limit: int = 20):
    """Get user's coin transaction history"""
    transactions = await db.coin_transactions.find(
        {'user_id': current_user['id']},
        {'_id': 0}
    ).sort('timestamp', -1).to_list(limit)
    
    return {'transactions': transactions}


# ============ Admin Shop Management ============

@router.post("/admin/items")
async def create_shop_item(item_data: CreateShopItem, current_user: dict = Depends(get_current_admin)):
    """Admin: Create a new shop item"""
    if item_data.category not in SHOP_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category. Choose from: {list(SHOP_CATEGORIES.keys())}")
    
    item_doc = {
        'id': str(uuid.uuid4()),
        'name': item_data.name,
        'description': item_data.description,
        'category': item_data.category,
        'price': item_data.price,
        'rarity': item_data.rarity,
        'icon': item_data.icon,
        'preview_color': item_data.preview_color,
        'uses': item_data.uses,
        'is_limited': item_data.is_limited,
        'stock': item_data.stock,
        'is_active': True,
        'total_sold': 0,
        'created_by': current_user['id'],
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.shop_items.insert_one(item_doc)
    
    return {
        'message': f"Shop item '{item_data.name}' created!",
        'item': {k: v for k, v in item_doc.items() if k != '_id'}
    }


@router.put("/admin/items/{item_id}")
async def update_shop_item(item_id: str, update_data: UpdateShopItem, current_user: dict = Depends(get_current_admin)):
    """Admin: Update a shop item"""
    item = await db.shop_items.find_one({'id': item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    updates = {}
    if update_data.name is not None:
        updates['name'] = update_data.name
    if update_data.description is not None:
        updates['description'] = update_data.description
    if update_data.price is not None:
        updates['price'] = update_data.price
    if update_data.is_active is not None:
        updates['is_active'] = update_data.is_active
    if update_data.stock is not None:
        updates['stock'] = update_data.stock
    
    if updates:
        updates['updated_at'] = datetime.now(timezone.utc).isoformat()
        await db.shop_items.update_one({'id': item_id}, {'$set': updates})
    
    return {'message': 'Item updated', 'updates': updates}


@router.delete("/admin/items/{item_id}")
async def delete_shop_item(item_id: str, current_user: dict = Depends(get_current_admin)):
    """Admin: Delete a shop item"""
    result = await db.shop_items.delete_one({'id': item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {'message': 'Item deleted'}


@router.get("/admin/stats")
async def get_shop_stats(current_user: dict = Depends(get_current_admin)):
    """Admin: Get shop statistics"""
    # Total items
    total_items = await db.shop_items.count_documents({'is_active': True})
    
    # Total sales
    pipeline = [
        {'$group': {'_id': None, 'total_sold': {'$sum': '$total_sold'}}}
    ]
    sales_result = await db.shop_items.aggregate(pipeline).to_list(1)
    total_sales = sales_result[0]['total_sold'] if sales_result else 0
    
    # Total coins spent
    pipeline = [
        {'$match': {'amount': {'$lt': 0}}},
        {'$group': {'_id': None, 'total': {'$sum': {'$abs': '$amount'}}}}
    ]
    coins_result = await db.coin_transactions.aggregate(pipeline).to_list(1)
    total_coins_spent = coins_result[0]['total'] if coins_result else 0
    
    # Top selling items
    top_items = await db.shop_items.find(
        {'is_active': True},
        {'_id': 0, 'id': 1, 'name': 1, 'total_sold': 1, 'category': 1}
    ).sort('total_sold', -1).to_list(5)
    
    return {
        'total_items': total_items,
        'total_sales': total_sales,
        'total_coins_spent': total_coins_spent,
        'top_selling_items': top_items
    }
