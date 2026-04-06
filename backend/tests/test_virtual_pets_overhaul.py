"""
Test Virtual Pets Overhaul - 17 Pet Types (9 Free Starters + 8 Shop) and 9 Interaction Types
Tests the new Fantasy/Sci-Fi themed pets and enhanced animations
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_PLAYER_EMAIL = "testplayer1@edgemode.com"
TEST_PLAYER_PASSWORD = "TestPlayer123!"

# Expected pet types from the overhaul
FREE_STARTER_PETS = [
    "flame_dragon", "phoenix", "spirit_wolf",  # Fantasy
    "neon_blob", "cyber_fox", "space_jelly",   # Sci-Fi
    "sports_tiger", "music_siren", "study_owl"  # Activity
]

SHOP_PETS = [
    "galaxy_dragon", "ice_phoenix", "shadow_kitsune", "crystal_golem",
    "aqua_serpent", "mecha_dragon", "pixel_sprite", "unicorn_celestial"
]

# Expected interaction types
INTERACTION_TYPES = [
    "pet", "feed", "play", "train", "sleep", "dance", "highfive", "cheer", "adventure"
]

# Expected categories
CATEGORIES = ["fantasy", "scifi", "activity", "gaming"]


class TestVirtualPetsOverhaul:
    """Test the new Virtual Pets system with 17 pet types and 9 interactions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as test player
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_PLAYER_EMAIL,
            "password": TEST_PLAYER_PASSWORD
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            self.authenticated = True
        else:
            self.authenticated = False
            pytest.skip("Authentication failed - skipping authenticated tests")
    
    # ============ GET /api/pets/available Tests ============
    
    def test_get_available_pets_returns_all_17_pets(self):
        """GET /api/pets/available should return all 17 pets (9 starters + 8 shop)"""
        response = self.session.get(f"{BASE_URL}/api/pets/available")
        assert response.status_code == 200
        
        data = response.json()
        assert "pets" in data
        assert "starters" in data
        assert "shop_pets" in data
        
        # Total should be 17 pets
        assert len(data["pets"]) == 17, f"Expected 17 total pets, got {len(data['pets'])}"
    
    def test_get_available_pets_has_9_free_starters(self):
        """GET /api/pets/available should return exactly 9 free starter pets"""
        response = self.session.get(f"{BASE_URL}/api/pets/available")
        assert response.status_code == 200
        
        data = response.json()
        starters = data["starters"]
        
        assert len(starters) == 9, f"Expected 9 starters, got {len(starters)}"
        
        # Verify all expected starters are present
        starter_types = [p["type"] for p in starters]
        for expected in FREE_STARTER_PETS:
            assert expected in starter_types, f"Missing starter pet: {expected}"
    
    def test_get_available_pets_has_8_shop_pets(self):
        """GET /api/pets/available should return exactly 8 shop pets"""
        response = self.session.get(f"{BASE_URL}/api/pets/available")
        assert response.status_code == 200
        
        data = response.json()
        shop_pets = data["shop_pets"]
        
        assert len(shop_pets) == 8, f"Expected 8 shop pets, got {len(shop_pets)}"
        
        # Verify all expected shop pets are present
        shop_types = [p["type"] for p in shop_pets]
        for expected in SHOP_PETS:
            assert expected in shop_types, f"Missing shop pet: {expected}"
    
    def test_get_available_pets_starters_are_free(self):
        """All starter pets should have price=0 and is_starter=True"""
        response = self.session.get(f"{BASE_URL}/api/pets/available")
        assert response.status_code == 200
        
        starters = response.json()["starters"]
        for pet in starters:
            assert pet["price"] == 0, f"Starter {pet['type']} should be free, has price {pet['price']}"
            assert pet["is_starter"] == True, f"Starter {pet['type']} should have is_starter=True"
    
    def test_get_available_pets_shop_pets_have_prices(self):
        """All shop pets should have price > 0 and is_starter=False"""
        response = self.session.get(f"{BASE_URL}/api/pets/available")
        assert response.status_code == 200
        
        shop_pets = response.json()["shop_pets"]
        for pet in shop_pets:
            assert pet["price"] > 0, f"Shop pet {pet['type']} should have price > 0"
            assert pet["is_starter"] == False, f"Shop pet {pet['type']} should have is_starter=False"
    
    def test_get_available_pets_has_correct_categories(self):
        """Pets should have correct categories: fantasy, scifi, activity, gaming"""
        response = self.session.get(f"{BASE_URL}/api/pets/available")
        assert response.status_code == 200
        
        pets = response.json()["pets"]
        categories_found = set()
        
        for pet in pets:
            assert "category" in pet, f"Pet {pet['type']} missing category"
            categories_found.add(pet["category"])
        
        # Verify expected categories exist
        for cat in ["fantasy", "scifi", "activity"]:
            assert cat in categories_found, f"Missing category: {cat}"
    
    def test_get_available_pets_has_preview_and_max_icons(self):
        """Each pet should have preview_icon and max_icon"""
        response = self.session.get(f"{BASE_URL}/api/pets/available")
        assert response.status_code == 200
        
        pets = response.json()["pets"]
        for pet in pets:
            assert "preview_icon" in pet, f"Pet {pet['type']} missing preview_icon"
            assert "max_icon" in pet, f"Pet {pet['type']} missing max_icon"
            assert len(pet["preview_icon"]) > 0, f"Pet {pet['type']} has empty preview_icon"
            assert len(pet["max_icon"]) > 0, f"Pet {pet['type']} has empty max_icon"
    
    # ============ POST /api/pets/select Tests ============
    
    def test_select_starter_pet_works(self):
        """POST /api/pets/select should allow selecting a free starter pet"""
        # First check if user already has a pet
        my_pet = self.session.get(f"{BASE_URL}/api/pets/my-pet")
        if my_pet.status_code == 200 and my_pet.json().get("has_pet"):
            pytest.skip("User already has a pet - cannot test starter selection")
        
        response = self.session.post(f"{BASE_URL}/api/pets/select", json={
            "pet_type": "flame_dragon",
            "pet_name": "TestDragon"
        })
        
        # Either 200 (success) or 400 (already has starter)
        assert response.status_code in [200, 400]
    
    def test_select_invalid_pet_type_fails(self):
        """POST /api/pets/select with invalid pet type should return 400"""
        response = self.session.post(f"{BASE_URL}/api/pets/select", json={
            "pet_type": "invalid_pet_type",
            "pet_name": "Test"
        })
        
        assert response.status_code == 400
        assert "Invalid pet type" in response.json().get("detail", "")
    
    # ============ GET /api/pets/interactions Tests ============
    
    def test_get_interactions_returns_9_types(self):
        """GET /api/pets/interactions should return all 9 interaction types"""
        response = self.session.get(f"{BASE_URL}/api/pets/interactions")
        assert response.status_code == 200
        
        data = response.json()
        
        # If user has no pet, interactions may be empty
        if not data.get("has_pet", True):
            pytest.skip("User has no pet - cannot test interactions")
        
        interactions = data.get("interactions", [])
        assert len(interactions) == 9, f"Expected 9 interaction types, got {len(interactions)}"
        
        # Verify all expected interaction types
        interaction_types = [i["type"] for i in interactions]
        for expected in INTERACTION_TYPES:
            assert expected in interaction_types, f"Missing interaction type: {expected}"
    
    def test_get_interactions_has_cooldown_info(self):
        """Each interaction should have cooldown_seconds and available status"""
        response = self.session.get(f"{BASE_URL}/api/pets/interactions")
        assert response.status_code == 200
        
        data = response.json()
        if not data.get("has_pet", True):
            pytest.skip("User has no pet")
        
        for interaction in data.get("interactions", []):
            assert "cooldown_seconds" in interaction
            assert "available" in interaction
            assert "happiness_boost" in interaction
    
    # ============ POST /api/pets/interact Tests ============
    
    def test_interact_pet_returns_petting_animations(self):
        """POST /api/pets/interact with type='pet' should return petting animations"""
        response = self.session.post(f"{BASE_URL}/api/pets/interact", json={
            "interaction_type": "pet"
        })
        
        if response.status_code == 404:
            pytest.skip("User has no active pet")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "animation" in data
        assert "effect" in data
        assert data["effect"] == "hearts_rising"
        
        # Petting animations should be one of these
        petting_animations = ["petting_purr", "heart_particles", "lean_nuzzle", "happy_wiggle"]
        assert data["animation"] in petting_animations, f"Unexpected animation: {data['animation']}"
    
    def test_interact_feed_returns_feeding_animations(self):
        """POST /api/pets/interact with type='feed' should return feeding animations"""
        response = self.session.post(f"{BASE_URL}/api/pets/interact", json={
            "interaction_type": "feed"
        })
        
        if response.status_code == 404:
            pytest.skip("User has no active pet")
        
        # May be on cooldown
        if response.status_code == 400 and "cooldown" in response.json().get("detail", "").lower():
            pytest.skip("Feed is on cooldown")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["effect"] == "treat_particles"
        feeding_animations = ["treat_munch", "belly_glow", "happy_dance", "satisfied_wiggle"]
        assert data["animation"] in feeding_animations
    
    def test_interact_play_returns_play_animations(self):
        """POST /api/pets/interact with type='play' should return play animations"""
        response = self.session.post(f"{BASE_URL}/api/pets/interact", json={
            "interaction_type": "play"
        })
        
        if response.status_code == 404:
            pytest.skip("User has no active pet")
        
        if response.status_code == 400 and "cooldown" in response.json().get("detail", "").lower():
            pytest.skip("Play is on cooldown")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["effect"] == "ball_bounce"
        play_animations = ["ball_chase", "pounce_catch", "proud_return", "wagging_tail"]
        assert data["animation"] in play_animations
    
    def test_interact_highfive_returns_highfive_animations(self):
        """POST /api/pets/interact with type='highfive' should return high-five animations"""
        response = self.session.post(f"{BASE_URL}/api/pets/interact", json={
            "interaction_type": "highfive"
        })
        
        if response.status_code == 404:
            pytest.skip("User has no active pet")
        
        if response.status_code == 400 and "cooldown" in response.json().get("detail", "").lower():
            pytest.skip("Highfive is on cooldown")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["effect"] == "star_burst"
        highfive_animations = ["reach_out", "bump_flash", "star_impact", "confetti_burst"]
        assert data["animation"] in highfive_animations
    
    def test_interact_cheer_returns_cheer_animations(self):
        """POST /api/pets/interact with type='cheer' should return cheer animations"""
        response = self.session.post(f"{BASE_URL}/api/pets/interact", json={
            "interaction_type": "cheer"
        })
        
        if response.status_code == 404:
            pytest.skip("User has no active pet")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["effect"] == "sparkle_aura"
        cheer_animations = ["hold_sign", "fist_pump", "sparkle_glow", "motivate_pose"]
        assert data["animation"] in cheer_animations
    
    def test_interact_adventure_returns_adventure_animations(self):
        """POST /api/pets/interact with type='adventure' should return adventure animations"""
        response = self.session.post(f"{BASE_URL}/api/pets/interact", json={
            "interaction_type": "adventure"
        })
        
        if response.status_code == 404:
            pytest.skip("User has no active pet")
        
        if response.status_code == 400 and "cooldown" in response.json().get("detail", "").lower():
            pytest.skip("Adventure is on cooldown")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["effect"] == "trophy_sparkle"
        adventure_animations = ["explorer_gear", "walk_offscreen", "return_trophy", "excited_spin"]
        assert data["animation"] in adventure_animations
    
    def test_interact_invalid_type_fails(self):
        """POST /api/pets/interact with invalid type should return 400"""
        response = self.session.post(f"{BASE_URL}/api/pets/interact", json={
            "interaction_type": "invalid_type"
        })
        
        if response.status_code == 404:
            pytest.skip("User has no active pet")
        
        assert response.status_code == 400
        assert "Invalid interaction type" in response.json().get("detail", "")
    
    def test_interact_returns_happiness_boost(self):
        """Interactions should return happiness_boost value"""
        response = self.session.post(f"{BASE_URL}/api/pets/interact", json={
            "interaction_type": "pet"
        })
        
        if response.status_code == 404:
            pytest.skip("User has no active pet")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "happiness_boost" in data
        assert "happiness" in data
        assert isinstance(data["happiness_boost"], int)
        assert isinstance(data["happiness"], int)
    
    # ============ GET /api/pets/my-pet Tests ============
    
    def test_get_my_pet_returns_pet_details(self):
        """GET /api/pets/my-pet should return pet details if user has a pet"""
        response = self.session.get(f"{BASE_URL}/api/pets/my-pet")
        assert response.status_code == 200
        
        data = response.json()
        assert "has_pet" in data
        
        if data["has_pet"]:
            pet = data["pet"]
            assert "type" in pet
            assert "name" in pet
            assert "category" in pet
            assert "rarity" in pet
            assert "evolution_stage" in pet
            assert "icon" in pet
            assert "happiness" in pet
    
    # ============ Specific Pet Type Tests ============
    
    def test_flame_dragon_exists_with_correct_properties(self):
        """flame_dragon should exist with correct category and theme"""
        response = self.session.get(f"{BASE_URL}/api/pets/available")
        assert response.status_code == 200
        
        pets = {p["type"]: p for p in response.json()["pets"]}
        assert "flame_dragon" in pets
        
        dragon = pets["flame_dragon"]
        assert dragon["category"] == "fantasy"
        assert dragon["is_starter"] == True
        assert dragon["price"] == 0
    
    def test_cyber_fox_exists_with_correct_properties(self):
        """cyber_fox should exist with scifi category"""
        response = self.session.get(f"{BASE_URL}/api/pets/available")
        assert response.status_code == 200
        
        pets = {p["type"]: p for p in response.json()["pets"]}
        assert "cyber_fox" in pets
        
        fox = pets["cyber_fox"]
        assert fox["category"] == "scifi"
        assert fox["is_starter"] == True
    
    def test_galaxy_dragon_is_shop_pet(self):
        """galaxy_dragon should be a shop pet with price > 0"""
        response = self.session.get(f"{BASE_URL}/api/pets/available")
        assert response.status_code == 200
        
        pets = {p["type"]: p for p in response.json()["pets"]}
        assert "galaxy_dragon" in pets
        
        galaxy = pets["galaxy_dragon"]
        assert galaxy["is_starter"] == False
        assert galaxy["price"] > 0
        assert galaxy["rarity"] == "legendary"
    
    def test_pixel_sprite_has_gaming_category(self):
        """pixel_sprite should have gaming category"""
        response = self.session.get(f"{BASE_URL}/api/pets/available")
        assert response.status_code == 200
        
        pets = {p["type"]: p for p in response.json()["pets"]}
        assert "pixel_sprite" in pets
        
        sprite = pets["pixel_sprite"]
        assert sprite["category"] == "gaming"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
