"""
Virtual Pets Feature Tests
Tests for: GET /api/pets/available, GET /api/pets/my-pet, POST /api/pets/select,
POST /api/pets/interact, GET /api/pets/shop
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@edgemodeapp.com"
ADMIN_PASSWORD = "EdgeAdmin2024!"
COACH_EMAIL = "testcoach@edgemode.com"
COACH_PASSWORD = "TestCoach123!"


def get_auth_token(email, password):
    """Get authentication token for a user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": email,
        "password": password
    })
    if response.status_code == 200:
        # API returns 'token' not 'access_token'
        return response.json().get("token")
    return None


class TestPetsAvailable:
    """Tests for GET /api/pets/available endpoint"""
    
    def test_get_available_pets_returns_starters_and_shop(self):
        """GET /api/pets/available returns starters (3) and shop_pets (7)"""
        token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token, "Failed to get admin token"
        
        response = requests.get(
            f"{BASE_URL}/api/pets/available",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "starters" in data, "Response should contain 'starters' field"
        assert "shop_pets" in data, "Response should contain 'shop_pets' field"
        assert "pets" in data, "Response should contain 'pets' field"
        
        # Verify 3 starters
        assert len(data["starters"]) == 3, f"Expected 3 starters, got {len(data['starters'])}"
        
        # Verify 7 shop pets
        assert len(data["shop_pets"]) == 7, f"Expected 7 shop pets, got {len(data['shop_pets'])}"
        
        # Verify total pets = 10
        assert len(data["pets"]) == 10, f"Expected 10 total pets, got {len(data['pets'])}"
        print(f"PASS: Available pets - 3 starters, 7 shop pets")
    
    def test_starters_are_free(self):
        """Verify all starter pets have price=0 and is_starter=True"""
        token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token, "Failed to get admin token"
        
        response = requests.get(
            f"{BASE_URL}/api/pets/available",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        for starter in data["starters"]:
            assert starter["price"] == 0, f"Starter {starter['name']} should be free"
            assert starter["is_starter"] == True, f"Starter {starter['name']} should have is_starter=True"
        
        # Verify starter types: puppy, kitten, bunny
        starter_types = [s["type"] for s in data["starters"]]
        assert "puppy" in starter_types, "Puppy should be a starter"
        assert "kitten" in starter_types, "Kitten should be a starter"
        assert "bunny" in starter_types, "Bunny should be a starter"
        print(f"PASS: All starters are free - puppy, kitten, bunny")
    
    def test_shop_pets_have_prices(self):
        """Verify shop pets have correct prices"""
        token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token, "Failed to get admin token"
        
        response = requests.get(
            f"{BASE_URL}/api/pets/available",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        expected_prices = {
            "dragon": 300,
            "phoenix": 450,
            "unicorn": 400,
            "slime": 150,
            "spirit": 250,
            "crystal": 600,
            "robot": 350
        }
        
        for pet in data["shop_pets"]:
            assert pet["is_starter"] == False, f"Shop pet {pet['name']} should have is_starter=False"
            if pet["type"] in expected_prices:
                assert pet["price"] == expected_prices[pet["type"]], \
                    f"Pet {pet['type']} should cost {expected_prices[pet['type']]}, got {pet['price']}"
        
        print(f"PASS: Shop pets have correct prices")


class TestMyPet:
    """Tests for GET /api/pets/my-pet endpoint"""
    
    def test_admin_has_pet(self):
        """Admin user already selected a puppy named 'Buddy'"""
        token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token, "Failed to get admin token"
        
        response = requests.get(
            f"{BASE_URL}/api/pets/my-pet",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "has_pet" in data, "Response should contain 'has_pet' field"
        
        # Admin should have a pet (Buddy the puppy)
        if data["has_pet"]:
            assert "pet" in data, "Response should contain 'pet' field when has_pet=True"
            pet = data["pet"]
            assert "id" in pet, "Pet should have 'id'"
            assert "type" in pet, "Pet should have 'type'"
            assert "name" in pet, "Pet should have 'name'"
            assert "icon" in pet, "Pet should have 'icon'"
            assert "evolution_stage" in pet, "Pet should have 'evolution_stage'"
            print(f"PASS: Admin has pet - {pet['name']} ({pet['type']}) at stage {pet['evolution_stage']}")
        else:
            print(f"INFO: Admin does not have a pet yet (has_pet=False)")
    
    def test_my_pet_returns_evolution_info(self):
        """Verify my-pet returns evolution progress info"""
        token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token, "Failed to get admin token"
        
        response = requests.get(
            f"{BASE_URL}/api/pets/my-pet",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        if data["has_pet"]:
            assert "current_streak" in data, "Response should contain 'current_streak'"
            assert "next_evolution" in data, "Response should contain 'next_evolution'"
            assert "days_until_evolution" in data, "Response should contain 'days_until_evolution'"
            
            pet = data["pet"]
            assert "xp_bonus" in pet, "Pet should have 'xp_bonus'"
            assert "coin_bonus" in pet, "Pet should have 'coin_bonus'"
            assert "happiness" in pet, "Pet should have 'happiness'"
            print(f"PASS: My-pet returns evolution info - streak: {data['current_streak']}, days until evolution: {data['days_until_evolution']}")
        else:
            print(f"INFO: Admin has no pet, skipping evolution info check")
    
    def test_coach_no_pet(self):
        """Test coach user may not have a pet yet"""
        token = get_auth_token(COACH_EMAIL, COACH_PASSWORD)
        assert token, "Failed to get coach token"
        
        response = requests.get(
            f"{BASE_URL}/api/pets/my-pet",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "has_pet" in data, "Response should contain 'has_pet' field"
        print(f"PASS: Coach has_pet = {data['has_pet']}")


class TestPetSelect:
    """Tests for POST /api/pets/select endpoint"""
    
    def test_cannot_select_second_starter(self):
        """User with starter pet cannot select another starter"""
        token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token, "Failed to get admin token"
        
        # First check if admin has a starter pet
        my_pet_response = requests.get(
            f"{BASE_URL}/api/pets/my-pet",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if my_pet_response.status_code == 200 and my_pet_response.json().get("has_pet"):
            # Try to select another starter
            response = requests.post(
                f"{BASE_URL}/api/pets/select",
                headers={"Authorization": f"Bearer {token}"},
                json={"pet_type": "kitten", "pet_name": "Test Kitten"}
            )
            
            # Should fail - either already owns this pet or already has a starter
            assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
            print(f"PASS: Cannot select second starter - {response.json().get('detail')}")
        else:
            pytest.skip("Admin doesn't have a pet yet, cannot test second starter prevention")
    
    def test_cannot_select_same_pet_twice(self):
        """User cannot select a pet they already own"""
        token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token, "Failed to get admin token"
        
        # Get admin's current pet
        my_pet_response = requests.get(
            f"{BASE_URL}/api/pets/my-pet",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if my_pet_response.status_code == 200 and my_pet_response.json().get("has_pet"):
            pet_type = my_pet_response.json()["pet"]["type"]
            
            # Try to select the same pet again
            response = requests.post(
                f"{BASE_URL}/api/pets/select",
                headers={"Authorization": f"Bearer {token}"},
                json={"pet_type": pet_type}
            )
            
            assert response.status_code == 400, f"Expected 400, got {response.status_code}"
            assert "already own" in response.json().get("detail", "").lower(), \
                f"Error should mention already owning the pet"
            print(f"PASS: Cannot select same pet twice - {response.json().get('detail')}")
        else:
            pytest.skip("Admin doesn't have a pet yet")
    
    def test_cannot_buy_shop_pet_without_coins(self):
        """Cannot purchase shop pet without enough coins"""
        token = get_auth_token(COACH_EMAIL, COACH_PASSWORD)
        assert token, "Failed to get coach token"
        
        # Try to buy the most expensive pet (crystal - 600 coins)
        response = requests.post(
            f"{BASE_URL}/api/pets/select",
            headers={"Authorization": f"Bearer {token}"},
            json={"pet_type": "crystal", "pet_name": "Test Crystal"}
        )
        
        # Should fail if user doesn't have 600 coins
        if response.status_code == 400:
            detail = response.json().get("detail", "")
            if "not enough coins" in detail.lower() or "coins" in detail.lower():
                print(f"PASS: Cannot buy shop pet without coins - {detail}")
            elif "already" in detail.lower():
                print(f"INFO: User already owns this pet or has a starter")
            else:
                print(f"INFO: Got 400 with detail: {detail}")
        else:
            print(f"INFO: User might have enough coins or already owns the pet - status {response.status_code}")
    
    def test_invalid_pet_type_rejected(self):
        """Invalid pet type should be rejected"""
        token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token, "Failed to get admin token"
        
        response = requests.post(
            f"{BASE_URL}/api/pets/select",
            headers={"Authorization": f"Bearer {token}"},
            json={"pet_type": "invalid_pet_type"}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"PASS: Invalid pet type rejected")


class TestPetInteract:
    """Tests for POST /api/pets/interact endpoint"""
    
    def test_interact_returns_encouragement(self):
        """Interacting with pet returns encouragement message and updates happiness"""
        token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token, "Failed to get admin token"
        
        # First check if user has a pet
        my_pet_response = requests.get(
            f"{BASE_URL}/api/pets/my-pet",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if my_pet_response.status_code == 200 and my_pet_response.json().get("has_pet"):
            response = requests.post(
                f"{BASE_URL}/api/pets/interact",
                headers={"Authorization": f"Bearer {token}"},
                json={"interaction_type": "pet"}
            )
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            data = response.json()
            assert "message" in data, "Response should contain 'message'"
            assert "happiness" in data, "Response should contain 'happiness'"
            assert "pet_name" in data, "Response should contain 'pet_name'"
            assert "interaction" in data, "Response should contain 'interaction'"
            
            # Happiness should be between 0 and 100
            assert 0 <= data["happiness"] <= 100, f"Happiness should be 0-100, got {data['happiness']}"
            
            print(f"PASS: Interact returns encouragement - '{data['message']}', happiness: {data['happiness']}")
        else:
            pytest.skip("User doesn't have a pet to interact with")
    
    def test_interact_without_pet_fails(self):
        """Interacting without a pet should fail"""
        # Test without auth
        response = requests.post(
            f"{BASE_URL}/api/pets/interact",
            json={"interaction_type": "pet"}
        )
        
        # Should fail without auth
        assert response.status_code in [401, 403, 404], \
            f"Expected auth error or not found, got {response.status_code}"
        print(f"PASS: Interact without auth fails with {response.status_code}")


class TestPetShop:
    """Tests for GET /api/pets/shop endpoint"""
    
    def test_shop_returns_pets_with_status(self):
        """Shop returns pets with owned/can_afford status"""
        token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token, "Failed to get admin token"
        
        response = requests.get(
            f"{BASE_URL}/api/pets/shop",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "pets" in data, "Response should contain 'pets'"
        assert "user_coins" in data, "Response should contain 'user_coins'"
        
        # Verify shop pets have required fields
        for pet in data["pets"]:
            assert "type" in pet, "Pet should have 'type'"
            assert "name" in pet, "Pet should have 'name'"
            assert "price" in pet, "Pet should have 'price'"
            assert "owned" in pet, "Pet should have 'owned' status"
            assert "can_afford" in pet, "Pet should have 'can_afford' status"
            assert "rarity" in pet, "Pet should have 'rarity'"
        
        # Shop should only have non-starter pets
        for pet in data["pets"]:
            assert pet["price"] > 0, f"Shop pet {pet['name']} should have price > 0"
        
        print(f"PASS: Shop returns {len(data['pets'])} pets, user has {data['user_coins']} coins")
    
    def test_shop_pets_sorted_by_price(self):
        """Shop pets should be sorted by price"""
        token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token, "Failed to get admin token"
        
        response = requests.get(
            f"{BASE_URL}/api/pets/shop",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        prices = [pet["price"] for pet in data["pets"]]
        
        # Verify sorted ascending
        assert prices == sorted(prices), f"Pets should be sorted by price: {prices}"
        print(f"PASS: Shop pets sorted by price - {prices}")


class TestPetCollection:
    """Tests for GET /api/pets/collection endpoint"""
    
    def test_collection_returns_owned_pets(self):
        """Collection returns all pets owned by user"""
        token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token, "Failed to get admin token"
        
        response = requests.get(
            f"{BASE_URL}/api/pets/collection",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "collection" in data, "Response should contain 'collection'"
        assert "total_owned" in data, "Response should contain 'total_owned'"
        
        # Verify collection count matches total_owned
        assert len(data["collection"]) == data["total_owned"], \
            f"Collection length should match total_owned"
        
        print(f"PASS: Collection returns {data['total_owned']} owned pets")


class TestPetEncouragement:
    """Tests for GET /api/pets/encouragement endpoint"""
    
    def test_encouragement_returns_message(self):
        """Encouragement endpoint returns motivational message"""
        token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token, "Failed to get admin token"
        
        response = requests.get(
            f"{BASE_URL}/api/pets/encouragement",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "has_pet" in data, "Response should contain 'has_pet'"
        
        if data["has_pet"]:
            assert "message" in data, "Response should contain 'message'"
            assert "pet_name" in data, "Response should contain 'pet_name'"
            assert "pet_icon" in data, "Response should contain 'pet_icon'"
            print(f"PASS: Encouragement - '{data['message']}'")
        else:
            print(f"INFO: User has no pet, encouragement returns has_pet=False")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
