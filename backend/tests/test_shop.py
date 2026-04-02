"""
Test Shop API Endpoints - XP Shop Feature
Tests: categories, items, featured, inventory, purchase, equip/unequip, streak shields, coin history
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@edgemodeapp.com"
ADMIN_PASSWORD = "EdgeAdmin2024!"
TEST_PLAYER_EMAIL = "testplayer1@edgemode.com"
TEST_PLAYER_PASSWORD = "TestPlayer123!"


class TestShopPublicEndpoints:
    """Test public shop endpoints (categories, items, featured)"""
    
    def test_get_shop_categories(self):
        """GET /api/shop/categories - returns shop categories"""
        response = requests.get(f"{BASE_URL}/api/shop/categories")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "categories" in data
        categories = data["categories"]
        
        # Verify expected categories exist
        expected_categories = ["themes", "badges", "streak_shields", "avatars", "effects"]
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"
            assert "name" in categories[cat]
            assert "description" in categories[cat]
            assert "icon" in categories[cat]
        
        print(f"✓ GET /api/shop/categories - Found {len(categories)} categories")
    
    def test_get_shop_items(self):
        """GET /api/shop/items - returns all shop items (should seed 18 default items)"""
        response = requests.get(f"{BASE_URL}/api/shop/items")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "items" in data
        items = data["items"]
        
        # Should have at least 18 default items
        assert len(items) >= 18, f"Expected at least 18 items, got {len(items)}"
        
        # Verify item structure
        for item in items[:3]:  # Check first 3 items
            assert "id" in item
            assert "name" in item
            assert "description" in item
            assert "category" in item
            assert "price" in item
            assert "rarity" in item
            assert "rarity_color" in item  # Added by API
            assert "icon" in item
        
        print(f"✓ GET /api/shop/items - Found {len(items)} items")
    
    def test_get_shop_items_filter_by_category(self):
        """GET /api/shop/items?category=themes - filter by category"""
        response = requests.get(f"{BASE_URL}/api/shop/items?category=themes")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        items = data["items"]
        
        # All items should be themes
        for item in items:
            assert item["category"] == "themes", f"Expected themes category, got {item['category']}"
        
        # Should have at least 5 theme items
        assert len(items) >= 5, f"Expected at least 5 theme items, got {len(items)}"
        
        print(f"✓ GET /api/shop/items?category=themes - Found {len(items)} theme items")
    
    def test_get_shop_items_filter_badges(self):
        """GET /api/shop/items?category=badges - filter by badges"""
        response = requests.get(f"{BASE_URL}/api/shop/items?category=badges")
        assert response.status_code == 200
        
        data = response.json()
        items = data["items"]
        
        for item in items:
            assert item["category"] == "badges"
        
        print(f"✓ GET /api/shop/items?category=badges - Found {len(items)} badge items")
    
    def test_get_shop_items_filter_streak_shields(self):
        """GET /api/shop/items?category=streak_shields - filter by streak shields"""
        response = requests.get(f"{BASE_URL}/api/shop/items?category=streak_shields")
        assert response.status_code == 200
        
        data = response.json()
        items = data["items"]
        
        for item in items:
            assert item["category"] == "streak_shields"
            assert "uses" in item  # Streak shields have uses
        
        print(f"✓ GET /api/shop/items?category=streak_shields - Found {len(items)} shield items")
    
    def test_get_featured_items(self):
        """GET /api/shop/featured - returns popular/featured items"""
        response = requests.get(f"{BASE_URL}/api/shop/featured")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "featured" in data
        featured = data["featured"]
        
        # Should return up to 6 featured items
        assert len(featured) <= 6, f"Expected max 6 featured items, got {len(featured)}"
        
        # Verify item structure
        for item in featured:
            assert "id" in item
            assert "name" in item
            assert "rarity_color" in item
        
        print(f"✓ GET /api/shop/featured - Found {len(featured)} featured items")
    
    def test_get_single_shop_item(self):
        """GET /api/shop/items/{item_id} - get specific item"""
        # First get all items to find a valid ID
        response = requests.get(f"{BASE_URL}/api/shop/items")
        items = response.json()["items"]
        
        if items:
            item_id = items[0]["id"]
            response = requests.get(f"{BASE_URL}/api/shop/items/{item_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert "item" in data
            assert data["item"]["id"] == item_id
            
            print(f"✓ GET /api/shop/items/{item_id} - Retrieved item details")
    
    def test_get_nonexistent_item(self):
        """GET /api/shop/items/{item_id} - returns 404 for non-existent item"""
        response = requests.get(f"{BASE_URL}/api/shop/items/nonexistent-item-id")
        assert response.status_code == 404
        
        print("✓ GET /api/shop/items/nonexistent - Returns 404")


class TestShopAuthenticatedEndpoints:
    """Test authenticated shop endpoints (inventory, purchase, equip)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        # Login as admin (has coins from daily login)
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        self.admin_token = response.json()["token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Login as test player
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_PLAYER_EMAIL,
            "password": TEST_PLAYER_PASSWORD
        })
        if response.status_code == 200:
            self.player_token = response.json()["token"]
            self.player_headers = {"Authorization": f"Bearer {self.player_token}"}
        else:
            self.player_token = None
            self.player_headers = None
    
    def test_get_user_inventory(self):
        """GET /api/shop/inventory - returns user's purchased items"""
        response = requests.get(f"{BASE_URL}/api/shop/inventory", headers=self.admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "inventory" in data
        
        print(f"✓ GET /api/shop/inventory - Found {len(data['inventory'])} items in inventory")
    
    def test_get_inventory_requires_auth(self):
        """GET /api/shop/inventory - requires authentication"""
        response = requests.get(f"{BASE_URL}/api/shop/inventory")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        
        print("✓ GET /api/shop/inventory - Requires auth")
    
    def test_get_equipped_items(self):
        """GET /api/shop/equipped - returns user's equipped items"""
        response = requests.get(f"{BASE_URL}/api/shop/equipped", headers=self.admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "equipped" in data
        
        print(f"✓ GET /api/shop/equipped - Found {len(data['equipped'])} equipped items")
    
    def test_get_coin_history(self):
        """GET /api/shop/coin-history - user's coin transaction history"""
        response = requests.get(f"{BASE_URL}/api/shop/coin-history", headers=self.admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "transactions" in data
        
        print(f"✓ GET /api/shop/coin-history - Found {len(data['transactions'])} transactions")
    
    def test_coin_history_requires_auth(self):
        """GET /api/shop/coin-history - requires authentication"""
        response = requests.get(f"{BASE_URL}/api/shop/coin-history")
        assert response.status_code in [401, 403]
        
        print("✓ GET /api/shop/coin-history - Requires auth")
    
    def test_purchase_not_enough_coins(self):
        """POST /api/shop/purchase/{item_id} - fails with not enough coins"""
        # Get an expensive item (legendary theme costs 200)
        response = requests.get(f"{BASE_URL}/api/shop/items")
        items = response.json()["items"]
        
        # Find an expensive item
        expensive_item = None
        for item in items:
            if item["price"] >= 200:
                expensive_item = item
                break
        
        if expensive_item:
            # Try to purchase (admin has only 5 coins)
            response = requests.post(
                f"{BASE_URL}/api/shop/purchase/{expensive_item['id']}", 
                headers=self.admin_headers
            )
            
            # Should fail with 400 (not enough coins)
            assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
            assert "Not enough coins" in response.json().get("detail", "")
            
            print(f"✓ POST /api/shop/purchase - Not enough coins validation works")
    
    def test_purchase_nonexistent_item(self):
        """POST /api/shop/purchase/{item_id} - fails for non-existent item"""
        response = requests.post(
            f"{BASE_URL}/api/shop/purchase/nonexistent-item", 
            headers=self.admin_headers
        )
        assert response.status_code == 404
        
        print("✓ POST /api/shop/purchase - Returns 404 for non-existent item")
    
    def test_purchase_requires_auth(self):
        """POST /api/shop/purchase/{item_id} - requires authentication"""
        response = requests.post(f"{BASE_URL}/api/shop/purchase/theme-midnight")
        assert response.status_code in [401, 403]
        
        print("✓ POST /api/shop/purchase - Requires auth")
    
    def test_equip_requires_auth(self):
        """POST /api/shop/equip/{inventory_id} - requires authentication"""
        response = requests.post(f"{BASE_URL}/api/shop/equip/some-id")
        assert response.status_code in [401, 403]
        
        print("✓ POST /api/shop/equip - Requires auth")
    
    def test_unequip_requires_auth(self):
        """POST /api/shop/unequip/{inventory_id} - requires authentication"""
        response = requests.post(f"{BASE_URL}/api/shop/unequip/some-id")
        assert response.status_code in [401, 403]
        
        print("✓ POST /api/shop/unequip - Requires auth")
    
    def test_equip_nonexistent_item(self):
        """POST /api/shop/equip/{inventory_id} - fails for non-existent inventory item"""
        response = requests.post(
            f"{BASE_URL}/api/shop/equip/nonexistent-inventory-id", 
            headers=self.admin_headers
        )
        assert response.status_code == 404
        
        print("✓ POST /api/shop/equip - Returns 404 for non-existent inventory item")
    
    def test_unequip_nonexistent_item(self):
        """POST /api/shop/unequip/{inventory_id} - fails for non-existent inventory item"""
        response = requests.post(
            f"{BASE_URL}/api/shop/unequip/nonexistent-inventory-id", 
            headers=self.admin_headers
        )
        assert response.status_code == 404
        
        print("✓ POST /api/shop/unequip - Returns 404 for non-existent inventory item")
    
    def test_use_shield_no_shields(self):
        """POST /api/shop/use-shield - fails when no shields available"""
        response = requests.post(
            f"{BASE_URL}/api/shop/use-shield", 
            headers=self.admin_headers
        )
        # Should fail with 400 if no shields
        assert response.status_code in [200, 400], f"Expected 200 or 400, got {response.status_code}"
        
        if response.status_code == 400:
            assert "No streak shields" in response.json().get("detail", "")
            print("✓ POST /api/shop/use-shield - No shields available validation works")
        else:
            print("✓ POST /api/shop/use-shield - Shield used successfully")
    
    def test_use_shield_requires_auth(self):
        """POST /api/shop/use-shield - requires authentication"""
        response = requests.post(f"{BASE_URL}/api/shop/use-shield")
        assert response.status_code in [401, 403]
        
        print("✓ POST /api/shop/use-shield - Requires auth")


class TestShopAdminEndpoints:
    """Test admin shop management endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        self.admin_token = response.json()["token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Login as test player (non-admin)
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_PLAYER_EMAIL,
            "password": TEST_PLAYER_PASSWORD
        })
        if response.status_code == 200:
            self.player_token = response.json()["token"]
            self.player_headers = {"Authorization": f"Bearer {self.player_token}"}
        else:
            self.player_token = None
            self.player_headers = None
    
    def test_admin_create_shop_item(self):
        """POST /api/shop/admin/items - admin can create shop item"""
        test_item = {
            "name": f"TEST_Item_{uuid.uuid4().hex[:8]}",
            "description": "Test item for testing",
            "category": "badges",
            "price": 100,
            "rarity": "rare",
            "icon": "🧪"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/shop/admin/items",
            json=test_item,
            headers=self.admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "item" in data
        assert data["item"]["name"] == test_item["name"]
        
        # Store item ID for cleanup
        self.created_item_id = data["item"]["id"]
        
        print(f"✓ POST /api/shop/admin/items - Created item: {test_item['name']}")
        
        # Cleanup - delete the test item
        requests.delete(
            f"{BASE_URL}/api/shop/admin/items/{self.created_item_id}",
            headers=self.admin_headers
        )
    
    def test_admin_create_item_invalid_category(self):
        """POST /api/shop/admin/items - fails with invalid category"""
        test_item = {
            "name": "Invalid Category Item",
            "description": "Test",
            "category": "invalid_category",
            "price": 50
        }
        
        response = requests.post(
            f"{BASE_URL}/api/shop/admin/items",
            json=test_item,
            headers=self.admin_headers
        )
        assert response.status_code == 400
        
        print("✓ POST /api/shop/admin/items - Invalid category validation works")
    
    def test_admin_create_item_requires_admin(self):
        """POST /api/shop/admin/items - requires admin role"""
        if not self.player_headers:
            pytest.skip("Test player not available")
        
        test_item = {
            "name": "Unauthorized Item",
            "description": "Test",
            "category": "badges",
            "price": 50
        }
        
        response = requests.post(
            f"{BASE_URL}/api/shop/admin/items",
            json=test_item,
            headers=self.player_headers
        )
        assert response.status_code in [401, 403]
        
        print("✓ POST /api/shop/admin/items - Requires admin role")
    
    def test_admin_update_shop_item(self):
        """PUT /api/shop/admin/items/{item_id} - admin can update shop item"""
        # First create an item
        test_item = {
            "name": f"TEST_Update_{uuid.uuid4().hex[:8]}",
            "description": "Test item",
            "category": "badges",
            "price": 50
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/shop/admin/items",
            json=test_item,
            headers=self.admin_headers
        )
        
        if create_response.status_code == 200:
            item_id = create_response.json()["item"]["id"]
            
            # Update the item
            update_data = {"price": 75, "name": "Updated Name"}
            response = requests.put(
                f"{BASE_URL}/api/shop/admin/items/{item_id}",
                json=update_data,
                headers=self.admin_headers
            )
            assert response.status_code == 200
            
            print("✓ PUT /api/shop/admin/items - Updated item successfully")
            
            # Cleanup
            requests.delete(
                f"{BASE_URL}/api/shop/admin/items/{item_id}",
                headers=self.admin_headers
            )
    
    def test_admin_delete_shop_item(self):
        """DELETE /api/shop/admin/items/{item_id} - admin can delete shop item"""
        # First create an item
        test_item = {
            "name": f"TEST_Delete_{uuid.uuid4().hex[:8]}",
            "description": "Test item to delete",
            "category": "badges",
            "price": 50
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/shop/admin/items",
            json=test_item,
            headers=self.admin_headers
        )
        
        if create_response.status_code == 200:
            item_id = create_response.json()["item"]["id"]
            
            # Delete the item
            response = requests.delete(
                f"{BASE_URL}/api/shop/admin/items/{item_id}",
                headers=self.admin_headers
            )
            assert response.status_code == 200
            
            # Verify deletion
            get_response = requests.get(f"{BASE_URL}/api/shop/items/{item_id}")
            assert get_response.status_code == 404
            
            print("✓ DELETE /api/shop/admin/items - Deleted item successfully")
    
    def test_admin_delete_nonexistent_item(self):
        """DELETE /api/shop/admin/items/{item_id} - returns 404 for non-existent item"""
        response = requests.delete(
            f"{BASE_URL}/api/shop/admin/items/nonexistent-item-id",
            headers=self.admin_headers
        )
        assert response.status_code == 404
        
        print("✓ DELETE /api/shop/admin/items - Returns 404 for non-existent item")
    
    def test_admin_get_shop_stats(self):
        """GET /api/shop/admin/stats - admin can get shop statistics"""
        response = requests.get(
            f"{BASE_URL}/api/shop/admin/stats",
            headers=self.admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_items" in data
        assert "total_sales" in data
        assert "total_coins_spent" in data
        assert "top_selling_items" in data
        
        print(f"✓ GET /api/shop/admin/stats - Total items: {data['total_items']}, Total sales: {data['total_sales']}")
    
    def test_admin_stats_requires_admin(self):
        """GET /api/shop/admin/stats - requires admin role"""
        if not self.player_headers:
            pytest.skip("Test player not available")
        
        response = requests.get(
            f"{BASE_URL}/api/shop/admin/stats",
            headers=self.player_headers
        )
        assert response.status_code in [401, 403]
        
        print("✓ GET /api/shop/admin/stats - Requires admin role")


class TestShopPurchaseFlow:
    """Test complete purchase flow with coins"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin and check coin balance"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.admin_token = response.json()["token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get current engagement status to check coins
        status_response = requests.get(
            f"{BASE_URL}/api/engagement/status",
            headers=self.admin_headers
        )
        if status_response.status_code == 200:
            self.current_coins = status_response.json().get("coins", 0)
        else:
            self.current_coins = 0
    
    def test_purchase_flow_with_sufficient_coins(self):
        """Test full purchase flow when user has enough coins"""
        # Get cheapest item
        response = requests.get(f"{BASE_URL}/api/shop/items")
        items = response.json()["items"]
        
        # Find cheapest item user doesn't own
        inventory_response = requests.get(
            f"{BASE_URL}/api/shop/inventory",
            headers=self.admin_headers
        )
        owned_ids = [inv["item_id"] for inv in inventory_response.json().get("inventory", [])]
        
        affordable_items = [
            item for item in items 
            if item["price"] <= self.current_coins and item["id"] not in owned_ids
        ]
        
        if affordable_items:
            item = min(affordable_items, key=lambda x: x["price"])
            
            # Purchase the item
            purchase_response = requests.post(
                f"{BASE_URL}/api/shop/purchase/{item['id']}",
                headers=self.admin_headers
            )
            
            if purchase_response.status_code == 200:
                data = purchase_response.json()
                assert "message" in data
                assert "new_balance" in data
                assert "coins_spent" in data
                assert data["coins_spent"] == item["price"]
                
                # Verify item in inventory
                inv_response = requests.get(
                    f"{BASE_URL}/api/shop/inventory",
                    headers=self.admin_headers
                )
                inventory = inv_response.json()["inventory"]
                assert any(inv["item_id"] == item["id"] for inv in inventory)
                
                print(f"✓ Purchase flow - Bought {item['name']} for {item['price']} coins")
            else:
                print(f"✓ Purchase flow - Could not purchase (status: {purchase_response.status_code})")
        else:
            print(f"✓ Purchase flow - No affordable items (coins: {self.current_coins})")
    
    def test_cannot_purchase_same_item_twice(self):
        """Test that non-consumable items cannot be purchased twice"""
        # Get inventory
        inventory_response = requests.get(
            f"{BASE_URL}/api/shop/inventory",
            headers=self.admin_headers
        )
        inventory = inventory_response.json().get("inventory", [])
        
        # Find a non-consumable item user owns
        owned_non_consumable = None
        for inv in inventory:
            if inv.get("category") != "streak_shields":
                owned_non_consumable = inv
                break
        
        if owned_non_consumable:
            # Try to purchase again
            response = requests.post(
                f"{BASE_URL}/api/shop/purchase/{owned_non_consumable['item_id']}",
                headers=self.admin_headers
            )
            assert response.status_code == 400
            assert "already own" in response.json().get("detail", "").lower()
            
            print("✓ Cannot purchase same non-consumable item twice")
        else:
            print("✓ No owned non-consumable items to test duplicate purchase")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
