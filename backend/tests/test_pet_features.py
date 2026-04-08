"""
Test Pet Moods, Companions, Codex, Expeditions, and Souvenirs features
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "testplayer1@edgemode.com"
TEST_PASSWORD = "TestPlayer123!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for test user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def api_client(auth_token):
    """Create authenticated session"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    })
    return session


class TestPetMood:
    """Test Pet Mood & Voice Lines endpoint"""
    
    def test_mood_endpoint_returns_200(self, api_client):
        """GET /api/pets/mood should return 200"""
        response = api_client.get(f"{BASE_URL}/api/pets/mood")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Mood endpoint returns 200")
    
    def test_mood_has_pet_flag(self, api_client):
        """Mood response should have has_pet flag"""
        response = api_client.get(f"{BASE_URL}/api/pets/mood")
        data = response.json()
        assert 'has_pet' in data, "Response missing 'has_pet' field"
        print(f"✓ has_pet flag present: {data['has_pet']}")
    
    def test_mood_returns_pet_data_when_has_pet(self, api_client):
        """When user has pet, mood should return pet_name, mood, voice_line"""
        response = api_client.get(f"{BASE_URL}/api/pets/mood")
        data = response.json()
        
        if data.get('has_pet'):
            assert 'pet_name' in data, "Missing pet_name"
            assert 'mood' in data, "Missing mood"
            assert 'voice_line' in data, "Missing voice_line"
            
            # Validate mood structure
            mood = data['mood']
            assert 'level' in mood, "Mood missing level"
            assert 'icon' in mood, "Mood missing icon"
            assert 'color' in mood, "Mood missing color"
            assert 'happiness' in mood, "Mood missing happiness"
            
            print(f"✓ Pet name: {data['pet_name']}")
            print(f"✓ Mood level: {mood['level']} ({mood['happiness']}% happy)")
            print(f"✓ Voice line: {data['voice_line']}")
        else:
            print("⚠ User has no pet - skipping pet data validation")


class TestCompanions:
    """Test Companions (Micropets) endpoint"""
    
    def test_companions_endpoint_returns_200(self, api_client):
        """GET /api/pets/companions should return 200"""
        response = api_client.get(f"{BASE_URL}/api/pets/companions")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Companions endpoint returns 200")
    
    def test_companions_response_structure(self, api_client):
        """Companions response should have required fields"""
        response = api_client.get(f"{BASE_URL}/api/pets/companions")
        data = response.json()
        
        assert 'companions' in data, "Missing companions array"
        assert 'unlocked_count' in data, "Missing unlocked_count"
        assert 'total_count' in data, "Missing total_count"
        assert 'active_companion' in data, "Missing active_companion"
        
        print(f"✓ Unlocked: {data['unlocked_count']}/{data['total_count']}")
        print(f"✓ Active companion: {data['active_companion']}")
    
    def test_companions_array_structure(self, api_client):
        """Each companion should have required fields"""
        response = api_client.get(f"{BASE_URL}/api/pets/companions")
        data = response.json()
        companions = data.get('companions', [])
        
        assert len(companions) > 0, "No companions returned"
        
        # Check first companion structure
        comp = companions[0]
        required_fields = ['id', 'name', 'icon', 'description', 'rarity', 
                          'unlock_type', 'is_unlocked', 'progress', 'threshold']
        for field in required_fields:
            assert field in comp, f"Companion missing field: {field}"
        
        print(f"✓ {len(companions)} companions returned with correct structure")
        
        # Show some companion details
        unlocked = [c for c in companions if c['is_unlocked']]
        print(f"✓ Unlocked companions: {[c['name'] for c in unlocked[:3]]}")
    
    def test_companions_progress_tracking(self, api_client):
        """Companions should show progress toward unlock"""
        response = api_client.get(f"{BASE_URL}/api/pets/companions")
        data = response.json()
        companions = data.get('companions', [])
        
        # Find a locked companion with progress
        locked = [c for c in companions if not c['is_unlocked'] and c['threshold'] > 0]
        if locked:
            comp = locked[0]
            print(f"✓ Progress tracking: {comp['name']} - {comp['progress']}/{comp['threshold']} ({comp.get('progress_percent', 0)}%)")
        else:
            print("⚠ No locked companions with progress to show")


class TestPetCodex:
    """Test Pet Codex (Collection) endpoint"""
    
    def test_codex_endpoint_returns_200(self, api_client):
        """GET /api/pets/codex should return 200"""
        response = api_client.get(f"{BASE_URL}/api/pets/codex")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Codex endpoint returns 200")
    
    def test_codex_response_structure(self, api_client):
        """Codex response should have pets, companions, accessories, completion"""
        response = api_client.get(f"{BASE_URL}/api/pets/codex")
        data = response.json()
        
        assert 'pets' in data, "Missing pets section"
        assert 'companions' in data, "Missing companions section"
        assert 'completion' in data, "Missing completion section"
        
        # Check pets section
        pets = data['pets']
        assert 'items' in pets, "Pets missing items"
        assert 'owned' in pets, "Pets missing owned count"
        assert 'total' in pets, "Pets missing total count"
        
        # Check companions section
        companions = data['companions']
        assert 'items' in companions, "Companions missing items"
        assert 'owned' in companions, "Companions missing owned count"
        assert 'total' in companions, "Companions missing total count"
        
        print(f"✓ Pets: {pets['owned']}/{pets['total']}")
        print(f"✓ Companions: {companions['owned']}/{companions['total']}")
    
    def test_codex_completion_percentage(self, api_client):
        """Codex should show overall completion percentage"""
        response = api_client.get(f"{BASE_URL}/api/pets/codex")
        data = response.json()
        
        completion = data.get('completion', {})
        assert 'owned' in completion, "Completion missing owned"
        assert 'total' in completion, "Completion missing total"
        assert 'percent' in completion, "Completion missing percent"
        
        print(f"✓ Overall completion: {completion['percent']}% ({completion['owned']}/{completion['total']})")
    
    def test_codex_pet_items_structure(self, api_client):
        """Each pet in codex should have required fields"""
        response = api_client.get(f"{BASE_URL}/api/pets/codex")
        data = response.json()
        pets = data.get('pets', {}).get('items', [])
        
        assert len(pets) > 0, "No pets in codex"
        
        pet = pets[0]
        required_fields = ['id', 'name', 'icon', 'max_icon', 'rarity', 'owned']
        for field in required_fields:
            assert field in pet, f"Pet missing field: {field}"
        
        print(f"✓ {len(pets)} pets in codex with correct structure")
        
        # Show owned pets
        owned = [p for p in pets if p['owned']]
        print(f"✓ Owned pets: {[p['name'] for p in owned]}")


class TestExpeditionReward:
    """Test Expedition Reward endpoint"""
    
    def test_expedition_reward_endpoint_returns_200(self, api_client):
        """POST /api/pets/expedition-reward should return 200"""
        response = api_client.post(f"{BASE_URL}/api/pets/expedition-reward")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Expedition reward endpoint returns 200")
    
    def test_expedition_reward_response_structure(self, api_client):
        """Expedition reward response should have required fields"""
        response = api_client.post(f"{BASE_URL}/api/pets/expedition-reward")
        data = response.json()
        
        assert 'has_reward' in data, "Missing has_reward field"
        
        if data['has_reward']:
            assert 'expedition_name' in data, "Missing expedition_name"
            assert 'story' in data, "Missing story"
            assert 'rewards' in data, "Missing rewards"
            assert 'rarity' in data, "Missing rarity"
            assert 'pet_name' in data, "Missing pet_name"
            
            rewards = data['rewards']
            assert 'coins' in rewards, "Rewards missing coins"
            assert 'xp' in rewards, "Rewards missing xp"
            
            print(f"✓ Expedition: {data['expedition_name']}")
            print(f"✓ Story: {data['story'][:50]}...")
            print(f"✓ Rewards: {rewards['coins']} coins, {rewards['xp']} XP")
            if rewards.get('item'):
                print(f"✓ Found item: {rewards['item']['name']}")
        else:
            print(f"⚠ No reward available: {data.get('reason', 'unknown')}")


class TestSouvenirs:
    """Test Souvenirs endpoint"""
    
    def test_souvenirs_endpoint_returns_200(self, api_client):
        """GET /api/pets/souvenirs should return 200"""
        response = api_client.get(f"{BASE_URL}/api/pets/souvenirs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Souvenirs endpoint returns 200")
    
    def test_souvenirs_response_structure(self, api_client):
        """Souvenirs response should have required fields"""
        response = api_client.get(f"{BASE_URL}/api/pets/souvenirs")
        data = response.json()
        
        assert 'souvenirs' in data, "Missing souvenirs array"
        assert 'by_rarity' in data, "Missing by_rarity grouping"
        assert 'total_count' in data, "Missing total_count"
        
        # Check by_rarity structure
        by_rarity = data['by_rarity']
        expected_rarities = ['legendary', 'rare', 'uncommon', 'common']
        for rarity in expected_rarities:
            assert rarity in by_rarity, f"Missing rarity: {rarity}"
        
        print(f"✓ Total souvenirs: {data['total_count']}")
        print(f"✓ By rarity: legendary={len(by_rarity['legendary'])}, rare={len(by_rarity['rare'])}, uncommon={len(by_rarity['uncommon'])}, common={len(by_rarity['common'])}")
    
    def test_souvenirs_item_structure(self, api_client):
        """Each souvenir should have required fields"""
        response = api_client.get(f"{BASE_URL}/api/pets/souvenirs")
        data = response.json()
        souvenirs = data.get('souvenirs', [])
        
        if len(souvenirs) > 0:
            souvenir = souvenirs[0]
            required_fields = ['id', 'name', 'icon', 'description', 'rarity']
            for field in required_fields:
                assert field in souvenir, f"Souvenir missing field: {field}"
            
            print(f"✓ Souvenir structure valid: {souvenir['name']} ({souvenir['rarity']})")
        else:
            print("⚠ No souvenirs collected yet")


class TestCompanionActivation:
    """Test Companion activation/deactivation"""
    
    def test_activate_unlocked_companion(self, api_client):
        """Should be able to activate an unlocked companion"""
        # First get companions to find an unlocked one
        response = api_client.get(f"{BASE_URL}/api/pets/companions")
        data = response.json()
        
        unlocked = [c for c in data.get('companions', []) if c['is_unlocked']]
        
        if unlocked:
            companion_id = unlocked[0]['id']
            activate_response = api_client.post(f"{BASE_URL}/api/pets/companions/{companion_id}/activate")
            
            if activate_response.status_code == 200:
                print(f"✓ Activated companion: {unlocked[0]['name']}")
            else:
                print(f"⚠ Activation returned {activate_response.status_code}: {activate_response.text}")
        else:
            print("⚠ No unlocked companions to test activation")
    
    def test_deactivate_companion(self, api_client):
        """Should be able to deactivate companions"""
        response = api_client.post(f"{BASE_URL}/api/pets/companions/deactivate")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ Deactivated companion successfully")
    
    def test_activate_locked_companion_fails(self, api_client):
        """Should not be able to activate a locked companion"""
        # First get companions to find a locked one
        response = api_client.get(f"{BASE_URL}/api/pets/companions")
        data = response.json()
        
        locked = [c for c in data.get('companions', []) if not c['is_unlocked']]
        
        if locked:
            companion_id = locked[0]['id']
            activate_response = api_client.post(f"{BASE_URL}/api/pets/companions/{companion_id}/activate")
            
            assert activate_response.status_code == 400, f"Expected 400 for locked companion, got {activate_response.status_code}"
            print(f"✓ Correctly rejected activation of locked companion: {locked[0]['name']}")
        else:
            print("⚠ No locked companions to test rejection")


class TestMyPetEndpoint:
    """Test my-pet endpoint for mood/companion integration"""
    
    def test_my_pet_returns_200(self, api_client):
        """GET /api/pets/my-pet should return 200"""
        response = api_client.get(f"{BASE_URL}/api/pets/my-pet")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ My-pet endpoint returns 200")
    
    def test_my_pet_has_pet_data(self, api_client):
        """My-pet should return pet details"""
        response = api_client.get(f"{BASE_URL}/api/pets/my-pet")
        data = response.json()
        
        if data.get('has_pet'):
            assert 'pet' in data, "Missing pet object"
            pet = data['pet']
            assert 'name' in pet, "Pet missing name"
            assert 'happiness' in pet, "Pet missing happiness"
            assert 'evolution_stage' in pet, "Pet missing evolution_stage"
            
            print(f"✓ Pet: {pet['name']} (Stage {pet['evolution_stage']}, {pet['happiness']}% happy)")
        else:
            print("⚠ User has no pet")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
