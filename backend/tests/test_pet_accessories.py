"""
Pet Accessories System Tests
Tests for shop, inventory, unlockable, equip/unequip endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_EMAIL = "testplayer1@edgemode.com"
TEST_USER_PASSWORD = "TestPlayer123!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for test user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestAccessoriesShop:
    """Tests for GET /api/pets/accessories/shop"""
    
    def test_shop_returns_200(self, auth_headers):
        """Shop endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/shop", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_shop_returns_items_array(self, auth_headers):
        """Shop returns items array"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/shop", headers=auth_headers)
        data = response.json()
        assert "items" in data, "Response should have 'items' key"
        assert isinstance(data["items"], list), "items should be a list"
    
    def test_shop_returns_user_coins(self, auth_headers):
        """Shop returns user_coins"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/shop", headers=auth_headers)
        data = response.json()
        assert "user_coins" in data, "Response should have 'user_coins' key"
        assert isinstance(data["user_coins"], int), "user_coins should be an integer"
    
    def test_shop_items_have_required_fields(self, auth_headers):
        """Shop items have all required fields"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/shop", headers=auth_headers)
        data = response.json()
        
        if len(data["items"]) > 0:
            item = data["items"][0]
            required_fields = ["id", "name", "description", "icon", "rarity", "category", "price", "can_afford", "owned"]
            for field in required_fields:
                assert field in item, f"Shop item missing '{field}' field"
    
    def test_shop_items_have_prices(self, auth_headers):
        """All shop items have prices > 0"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/shop", headers=auth_headers)
        data = response.json()
        
        for item in data["items"]:
            assert item["price"] > 0, f"Shop item {item['id']} should have price > 0"
    
    def test_shop_can_afford_status(self, auth_headers):
        """Shop items have correct can_afford status based on user coins"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/shop", headers=auth_headers)
        data = response.json()
        user_coins = data["user_coins"]
        
        for item in data["items"]:
            expected_can_afford = user_coins >= item["price"]
            assert item["can_afford"] == expected_can_afford, \
                f"Item {item['id']} can_afford should be {expected_can_afford} (coins: {user_coins}, price: {item['price']})"


class TestAccessoriesInventory:
    """Tests for GET /api/pets/accessories/inventory"""
    
    def test_inventory_returns_200(self, auth_headers):
        """Inventory endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/inventory", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_inventory_returns_inventory_array(self, auth_headers):
        """Inventory returns inventory array"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/inventory", headers=auth_headers)
        data = response.json()
        assert "inventory" in data, "Response should have 'inventory' key"
        assert isinstance(data["inventory"], list), "inventory should be a list"
    
    def test_inventory_returns_total_owned(self, auth_headers):
        """Inventory returns total_owned count"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/inventory", headers=auth_headers)
        data = response.json()
        assert "total_owned" in data, "Response should have 'total_owned' key"
        assert data["total_owned"] == len(data["inventory"]), "total_owned should match inventory length"


class TestAccessoriesUnlockable:
    """Tests for GET /api/pets/accessories/unlockable"""
    
    def test_unlockable_returns_200(self, auth_headers):
        """Unlockable endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/unlockable", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_unlockable_returns_unlockable_array(self, auth_headers):
        """Unlockable returns unlockable array"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/unlockable", headers=auth_headers)
        data = response.json()
        assert "unlockable" in data, "Response should have 'unlockable' key"
        assert isinstance(data["unlockable"], list), "unlockable should be a list"
    
    def test_unlockable_items_have_progress_info(self, auth_headers):
        """Unlockable items have unlock progress info"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/unlockable", headers=auth_headers)
        data = response.json()
        
        if len(data["unlockable"]) > 0:
            item = data["unlockable"][0]
            required_fields = ["id", "name", "unlock_type", "unlocked", "claimable", "unlock_reason"]
            for field in required_fields:
                assert field in item, f"Unlockable item missing '{field}' field"
    
    def test_unlockable_has_claimable_count(self, auth_headers):
        """Unlockable returns claimable_count"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/unlockable", headers=auth_headers)
        data = response.json()
        assert "claimable_count" in data, "Response should have 'claimable_count' key"
        
        # Verify count matches actual claimable items
        actual_claimable = len([u for u in data["unlockable"] if u["claimable"]])
        assert data["claimable_count"] == actual_claimable, "claimable_count should match actual claimable items"


class TestAccessoriesEquipped:
    """Tests for GET /api/pets/accessories/equipped"""
    
    def test_equipped_returns_200(self, auth_headers):
        """Equipped endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/equipped", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_equipped_returns_equipped_dict(self, auth_headers):
        """Equipped returns equipped dictionary"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/equipped", headers=auth_headers)
        data = response.json()
        assert "equipped" in data, "Response should have 'equipped' key"
        assert isinstance(data["equipped"], dict), "equipped should be a dictionary"
    
    def test_equipped_returns_has_pet_status(self, auth_headers):
        """Equipped returns has_pet status"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/equipped", headers=auth_headers)
        data = response.json()
        assert "has_pet" in data, "Response should have 'has_pet' key"


class TestAccessoriesPurchase:
    """Tests for POST /api/pets/accessories/purchase/{id}"""
    
    def test_purchase_invalid_accessory_returns_404(self, auth_headers):
        """Purchase invalid accessory returns 404"""
        response = requests.post(f"{BASE_URL}/api/pets/accessories/purchase/invalid_accessory_id", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_purchase_non_shop_item_returns_400(self, auth_headers):
        """Purchase non-shop item returns 400"""
        # crown_gold is a level-unlock item, not shop
        response = requests.post(f"{BASE_URL}/api/pets/accessories/purchase/crown_gold", headers=auth_headers)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "cannot be purchased" in response.json().get("detail", "").lower() or "must be unlocked" in response.json().get("detail", "").lower()
    
    def test_purchase_expensive_item_insufficient_coins(self, auth_headers):
        """Purchase expensive item with insufficient coins returns 400"""
        # space_helmet costs 350 coins, test user has only 5
        response = requests.post(f"{BASE_URL}/api/pets/accessories/purchase/space_helmet", headers=auth_headers)
        # Could be 400 (not enough coins) or 400 (already owned)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"


class TestAccessoriesClaim:
    """Tests for POST /api/pets/accessories/claim/{id}"""
    
    def test_claim_invalid_accessory_returns_404(self, auth_headers):
        """Claim invalid accessory returns 404"""
        response = requests.post(f"{BASE_URL}/api/pets/accessories/claim/invalid_accessory_id", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_claim_shop_item_returns_400(self, auth_headers):
        """Claim shop item returns 400"""
        # pirate_hat is a shop item
        response = requests.post(f"{BASE_URL}/api/pets/accessories/claim/pirate_hat", headers=auth_headers)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "must be purchased" in response.json().get("detail", "").lower()
    
    def test_claim_locked_item_returns_400(self, auth_headers):
        """Claim locked item returns 400"""
        # angel_wings requires 100-day streak
        response = requests.post(f"{BASE_URL}/api/pets/accessories/claim/angel_wings", headers=auth_headers)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"


class TestAccessoriesEquip:
    """Tests for POST /api/pets/accessories/equip"""
    
    def test_equip_invalid_accessory_returns_404(self, auth_headers):
        """Equip invalid accessory returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/pets/accessories/equip",
            headers=auth_headers,
            json={"accessory_id": "invalid_accessory_id"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_equip_unowned_accessory_returns_400(self, auth_headers):
        """Equip unowned accessory returns 400"""
        # space_helmet is a shop item user likely doesn't own
        response = requests.post(
            f"{BASE_URL}/api/pets/accessories/equip",
            headers=auth_headers,
            json={"accessory_id": "space_helmet"}
        )
        # Could be 400 (don't own) or 200 (if they do own it)
        if response.status_code == 400:
            assert "don't own" in response.json().get("detail", "").lower()


class TestAccessoriesUnequip:
    """Tests for POST /api/pets/accessories/unequip/{slot}"""
    
    def test_unequip_invalid_slot_returns_400(self, auth_headers):
        """Unequip invalid slot returns 400"""
        response = requests.post(f"{BASE_URL}/api/pets/accessories/unequip/invalid_slot", headers=auth_headers)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "invalid slot" in response.json().get("detail", "").lower()
    
    def test_unequip_empty_slot_returns_400(self, auth_headers):
        """Unequip empty slot returns 400"""
        # First check what's equipped
        equipped_res = requests.get(f"{BASE_URL}/api/pets/accessories/equipped", headers=auth_headers)
        equipped = equipped_res.json().get("equipped", {})
        
        # Find an empty slot
        valid_slots = ['head', 'face', 'neck', 'back', 'aura']
        empty_slot = None
        for slot in valid_slots:
            if slot not in equipped or equipped[slot] is None:
                empty_slot = slot
                break
        
        if empty_slot:
            response = requests.post(f"{BASE_URL}/api/pets/accessories/unequip/{empty_slot}", headers=auth_headers)
            assert response.status_code == 400, f"Expected 400, got {response.status_code}"
            assert "nothing equipped" in response.json().get("detail", "").lower()


class TestAccessoriesDataIntegrity:
    """Tests for data integrity across endpoints"""
    
    def test_shop_items_are_shop_type_only(self, auth_headers):
        """Shop only contains shop-type items"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/shop", headers=auth_headers)
        data = response.json()
        
        # All items in shop should be purchasable (have prices)
        for item in data["items"]:
            assert item["price"] > 0, f"Shop item {item['id']} should have price > 0"
    
    def test_unlockable_items_are_non_shop_type(self, auth_headers):
        """Unlockable only contains non-shop items"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/unlockable", headers=auth_headers)
        data = response.json()
        
        # All items should have unlock_type that's not 'shop'
        for item in data["unlockable"]:
            assert item["unlock_type"] != "shop", f"Unlockable item {item['id']} should not be shop type"
    
    def test_inventory_items_match_owned_status(self, auth_headers):
        """Inventory items are marked as owned in shop/unlockable"""
        inv_response = requests.get(f"{BASE_URL}/api/pets/accessories/inventory", headers=auth_headers)
        inventory = inv_response.json().get("inventory", [])
        owned_ids = {item["id"] for item in inventory}
        
        # Check shop items
        shop_response = requests.get(f"{BASE_URL}/api/pets/accessories/shop", headers=auth_headers)
        shop_items = shop_response.json().get("items", [])
        
        for item in shop_items:
            if item["id"] in owned_ids:
                assert item["owned"] == True, f"Shop item {item['id']} should be marked as owned"
        
        # Check unlockable items
        unlock_response = requests.get(f"{BASE_URL}/api/pets/accessories/unlockable", headers=auth_headers)
        unlockable_items = unlock_response.json().get("unlockable", [])
        
        for item in unlockable_items:
            if item["id"] in owned_ids:
                assert item["owned"] == True, f"Unlockable item {item['id']} should be marked as owned"


class TestAccessoriesCategories:
    """Tests for accessory categories"""
    
    def test_shop_has_multiple_categories(self, auth_headers):
        """Shop has items from multiple categories"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/shop", headers=auth_headers)
        data = response.json()
        
        categories = set(item["category"] for item in data["items"])
        assert len(categories) >= 3, f"Shop should have items from at least 3 categories, found: {categories}"
    
    def test_unlockable_has_multiple_unlock_types(self, auth_headers):
        """Unlockable has items with different unlock types"""
        response = requests.get(f"{BASE_URL}/api/pets/accessories/unlockable", headers=auth_headers)
        data = response.json()
        
        unlock_types = set(item["unlock_type"] for item in data["unlockable"])
        # Should have level, streak, achievement, referral
        assert len(unlock_types) >= 3, f"Unlockable should have at least 3 unlock types, found: {unlock_types}"


class TestAccessoriesCount:
    """Tests for accessory counts"""
    
    def test_total_accessories_count(self, auth_headers):
        """Total accessories should be 30+"""
        shop_response = requests.get(f"{BASE_URL}/api/pets/accessories/shop", headers=auth_headers)
        unlock_response = requests.get(f"{BASE_URL}/api/pets/accessories/unlockable", headers=auth_headers)
        
        shop_count = len(shop_response.json().get("items", []))
        unlock_count = len(unlock_response.json().get("unlockable", []))
        
        total = shop_count + unlock_count
        assert total >= 30, f"Total accessories should be 30+, found {total} (shop: {shop_count}, unlockable: {unlock_count})"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
