"""
Test Referral Exclusive Shop Items - Backend API Tests
Tests for exclusive referral items in shop, referral milestones, and invite page functionality
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@edgemodeapp.com"
ADMIN_PASSWORD = "EdgeAdmin2024!"
TEST_PLAYER_EMAIL = "testplayer1@edgemode.com"
TEST_PLAYER_PASSWORD = "TestPlayer123!"


class TestShopItemsAPI:
    """Test shop items API returns referral exclusive items correctly"""
    
    def test_shop_items_returns_referral_exclusive_items(self):
        """Shop items endpoint returns items with is_referral_exclusive field"""
        response = requests.get(f"{BASE_URL}/api/shop/items")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'items' in data, "Response should have 'items' key"
        
        items = data['items']
        assert len(items) > 0, "Should have shop items"
        
        # Check for referral exclusive items
        referral_items = [i for i in items if i.get('is_referral_exclusive') == True]
        assert len(referral_items) >= 4, f"Expected at least 4 referral exclusive items, got {len(referral_items)}"
        
        print(f"✓ Found {len(referral_items)} referral exclusive items")
    
    def test_referral_items_have_referrals_required_field(self):
        """Referral exclusive items have referrals_required field"""
        response = requests.get(f"{BASE_URL}/api/shop/items")
        assert response.status_code == 200
        
        data = response.json()
        referral_items = [i for i in data['items'] if i.get('is_referral_exclusive') == True]
        
        for item in referral_items:
            assert 'referrals_required' in item, f"Item {item['name']} missing referrals_required"
            assert isinstance(item['referrals_required'], int), f"referrals_required should be int"
            assert item['referrals_required'] > 0, f"referrals_required should be positive"
            print(f"  ✓ {item['name']}: {item['referrals_required']} friends required")
    
    def test_referral_items_have_exclusive_rarity(self):
        """Referral exclusive items have exclusive or legendary rarity"""
        response = requests.get(f"{BASE_URL}/api/shop/items")
        assert response.status_code == 200
        
        data = response.json()
        referral_items = [i for i in data['items'] if i.get('is_referral_exclusive') == True]
        
        for item in referral_items:
            assert item.get('rarity') in ['exclusive', 'legendary'], \
                f"Item {item['name']} has rarity {item.get('rarity')}, expected exclusive or legendary"
        
        print(f"✓ All referral items have correct rarity")
    
    def test_regular_items_have_price(self):
        """Regular (non-referral) items have price field"""
        response = requests.get(f"{BASE_URL}/api/shop/items")
        assert response.status_code == 200
        
        data = response.json()
        regular_items = [i for i in data['items'] if not i.get('is_referral_exclusive')]
        
        assert len(regular_items) > 0, "Should have regular shop items"
        
        for item in regular_items:
            assert 'price' in item, f"Item {item['name']} missing price"
            assert isinstance(item['price'], int), f"price should be int"
            assert item['price'] > 0, f"price should be positive"
        
        print(f"✓ All {len(regular_items)} regular items have valid prices")
    
    def test_referral_items_have_zero_price(self):
        """Referral exclusive items have price=0 (not purchasable with coins)"""
        response = requests.get(f"{BASE_URL}/api/shop/items")
        assert response.status_code == 200
        
        data = response.json()
        referral_items = [i for i in data['items'] if i.get('is_referral_exclusive') == True]
        
        for item in referral_items:
            assert item.get('price') == 0, f"Referral item {item['name']} should have price=0, got {item.get('price')}"
        
        print(f"✓ All referral items have price=0")


class TestReferralMilestonesAPI:
    """Test referral milestones and exclusive rewards API"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for test player"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_PLAYER_EMAIL,
            "password": TEST_PLAYER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_referral_my_code_endpoint(self, auth_token):
        """GET /api/referrals/my-code returns referral code and milestones"""
        response = requests.get(
            f"{BASE_URL}/api/referrals/my-code",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'referral_code' in data, "Response should have referral_code"
        assert 'referral_link' in data, "Response should have referral_link"
        assert 'milestones' in data, "Response should have milestones"
        assert 'referral_count' in data, "Response should have referral_count"
        
        print(f"✓ Referral code: {data['referral_code']}")
        print(f"✓ Referral link: {data['referral_link']}")
        print(f"✓ Milestones count: {len(data['milestones'])}")
    
    def test_milestones_have_required_fields(self, auth_token):
        """Milestones have all required fields for UI display"""
        response = requests.get(
            f"{BASE_URL}/api/referrals/my-code",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        milestones = data.get('milestones', [])
        assert len(milestones) >= 4, f"Expected at least 4 milestones, got {len(milestones)}"
        
        required_fields = ['id', 'referrals_required', 'reward_name', 'reward_description', 
                          'reward_icon', 'coins_bonus', 'is_claimed', 'is_unlocked', 'progress_pct']
        
        for milestone in milestones:
            for field in required_fields:
                assert field in milestone, f"Milestone missing field: {field}"
            print(f"  ✓ Milestone: {milestone['reward_name']} ({milestone['referrals_required']} friends)")
    
    def test_exclusive_items_endpoint(self, auth_token):
        """GET /api/referrals/exclusive-items returns exclusive items with unlock status"""
        response = requests.get(
            f"{BASE_URL}/api/referrals/exclusive-items",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'items' in data, "Response should have items"
        
        items = data['items']
        assert len(items) >= 4, f"Expected at least 4 exclusive items, got {len(items)}"
        
        for item in items:
            assert 'is_unlocked' in item, f"Item {item['name']} missing is_unlocked"
            assert 'is_owned' in item, f"Item {item['name']} missing is_owned"
            assert 'referrals_needed' in item, f"Item {item['name']} missing referrals_needed"
            print(f"  ✓ {item['name']}: unlocked={item['is_unlocked']}, owned={item['is_owned']}")


class TestReferralInfoAPI:
    """Test referral info endpoint for invite page"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for test player"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_PLAYER_EMAIL,
            "password": TEST_PLAYER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_referral_info_endpoint(self, auth_token):
        """GET /api/referral/info returns referral info for invite page"""
        response = requests.get(
            f"{BASE_URL}/api/referral/info",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'referral_code' in data, "Response should have referral_code"
        assert 'referral_link' in data, "Response should have referral_link"
        assert 'total_referrals' in data, "Response should have total_referrals"
        
        print(f"✓ Referral info endpoint working")
        print(f"  - Code: {data.get('referral_code')}")
        print(f"  - Total referrals: {data.get('total_referrals')}")


class TestShopCategories:
    """Test shop categories endpoint"""
    
    def test_shop_categories_endpoint(self):
        """GET /api/shop/categories returns categories"""
        response = requests.get(f"{BASE_URL}/api/shop/categories")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'categories' in data, "Response should have categories"
        
        categories = data['categories']
        expected_categories = ['themes', 'badges', 'streak_shields', 'avatars', 'effects']
        
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"
        
        print(f"✓ All {len(categories)} categories present")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
