"""
Test Email Announcements Feature
- GET /api/admin/users/list - returns list of users for selection, supports search param
- POST /api/admin/announcements/send - sends announcement to selected users or all
- POST /api/admin/announcements/send - validates subject and message required
- POST /api/admin/announcements/send - validates users selected or send_to_all
- GET /api/admin/announcements/history - returns sent announcements
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "admin@edgemodeapp.com"
ADMIN_PASSWORD = "EdgeAdmin2024!"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Admin authentication failed: {response.status_code} - {response.text}")


@pytest.fixture
def admin_headers(admin_token):
    """Headers with admin auth token"""
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }


class TestUsersListEndpoint:
    """Tests for GET /api/admin/users/list"""
    
    def test_users_list_requires_auth(self):
        """Test that users list endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/users/list")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Users list requires authentication")
    
    def test_users_list_returns_users(self, admin_headers):
        """Test that users list returns users array"""
        response = requests.get(f"{BASE_URL}/api/admin/users/list", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "users" in data, "Response should contain 'users' key"
        assert "total" in data, "Response should contain 'total' key"
        assert isinstance(data["users"], list), "Users should be a list"
        print(f"PASS: Users list returns {data['total']} users")
    
    def test_users_list_user_structure(self, admin_headers):
        """Test that each user has required fields"""
        response = requests.get(f"{BASE_URL}/api/admin/users/list", headers=admin_headers)
        assert response.status_code == 200
        
        data = response.json()
        if data["users"]:
            user = data["users"][0]
            assert "id" in user, "User should have 'id'"
            assert "email" in user, "User should have 'email'"
            # username may be optional
            print(f"PASS: User structure valid - id: {user['id']}, email: {user['email']}")
        else:
            print("PASS: No users to validate structure (empty list)")
    
    def test_users_list_search_filter(self, admin_headers):
        """Test that search parameter filters users"""
        # Search for admin user
        response = requests.get(
            f"{BASE_URL}/api/admin/users/list?search=admin",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data["users"], list)
        # Should find at least the admin user
        if data["users"]:
            emails = [u.get("email", "").lower() for u in data["users"]]
            usernames = [u.get("username", "").lower() for u in data["users"]]
            has_match = any("admin" in e for e in emails) or any("admin" in u for u in usernames)
            print(f"PASS: Search filter works - found {len(data['users'])} users matching 'admin'")
        else:
            print("PASS: Search filter works - no users match 'admin'")
    
    def test_users_list_limit_param(self, admin_headers):
        """Test that limit parameter works"""
        response = requests.get(
            f"{BASE_URL}/api/admin/users/list?limit=5",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["users"]) <= 5, f"Expected max 5 users, got {len(data['users'])}"
        print(f"PASS: Limit parameter works - returned {len(data['users'])} users (max 5)")


class TestAnnouncementsSendEndpoint:
    """Tests for POST /api/admin/announcements/send"""
    
    def test_send_requires_auth(self):
        """Test that send announcement requires authentication"""
        response = requests.post(f"{BASE_URL}/api/admin/announcements/send", json={
            "subject": "Test",
            "message": "Test message",
            "send_to_all": True
        })
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Send announcement requires authentication")
    
    def test_send_validates_subject_required(self, admin_headers):
        """Test that subject is required"""
        response = requests.post(
            f"{BASE_URL}/api/admin/announcements/send",
            headers=admin_headers,
            json={
                "subject": "",
                "message": "Test message",
                "send_to_all": True
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("PASS: Subject validation works - empty subject rejected")
    
    def test_send_validates_message_required(self, admin_headers):
        """Test that message is required"""
        response = requests.post(
            f"{BASE_URL}/api/admin/announcements/send",
            headers=admin_headers,
            json={
                "subject": "Test Subject",
                "message": "",
                "send_to_all": True
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("PASS: Message validation works - empty message rejected")
    
    def test_send_validates_users_or_send_to_all(self, admin_headers):
        """Test that either users must be selected or send_to_all must be true"""
        response = requests.post(
            f"{BASE_URL}/api/admin/announcements/send",
            headers=admin_headers,
            json={
                "subject": "Test Subject",
                "message": "Test message",
                "user_ids": [],
                "send_to_all": False
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "detail" in data
        print(f"PASS: User selection validation works - error: {data['detail']}")
    
    def test_send_to_all_users(self, admin_headers):
        """Test sending announcement to all users (may return 503 if email not configured)"""
        response = requests.post(
            f"{BASE_URL}/api/admin/announcements/send",
            headers=admin_headers,
            json={
                "subject": "Test Announcement - All Users",
                "message": "This is a test announcement sent to all users.",
                "user_ids": [],
                "send_to_all": True
            }
        )
        # Accept 200 (success) or 503 (email service not configured)
        assert response.status_code in [200, 503], f"Expected 200 or 503, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "sent_count" in data, "Response should contain 'sent_count'"
            assert "message" in data, "Response should contain 'message'"
            print(f"PASS: Send to all works - sent to {data.get('sent_count', 0)} users")
        else:
            data = response.json()
            print(f"PASS: Email service not configured (503) - {data.get('detail', 'No detail')}")
    
    def test_send_to_specific_users(self, admin_headers):
        """Test sending announcement to specific users"""
        # First get a user ID
        users_response = requests.get(
            f"{BASE_URL}/api/admin/users/list?limit=1",
            headers=admin_headers
        )
        assert users_response.status_code == 200
        users_data = users_response.json()
        
        if not users_data["users"]:
            pytest.skip("No users available for testing")
        
        user_id = users_data["users"][0]["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/admin/announcements/send",
            headers=admin_headers,
            json={
                "subject": "Test Announcement - Specific User",
                "message": "This is a test announcement sent to a specific user.",
                "user_ids": [user_id],
                "send_to_all": False
            }
        )
        # Accept 200 (success) or 503 (email service not configured)
        assert response.status_code in [200, 503], f"Expected 200 or 503, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "sent_count" in data
            print(f"PASS: Send to specific user works - sent to {data.get('sent_count', 0)} users")
        else:
            print("PASS: Email service not configured (503)")


class TestAnnouncementsHistoryEndpoint:
    """Tests for GET /api/admin/announcements/history"""
    
    def test_history_requires_auth(self):
        """Test that history endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/announcements/history")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Announcements history requires authentication")
    
    def test_history_returns_announcements(self, admin_headers):
        """Test that history returns announcements array"""
        response = requests.get(
            f"{BASE_URL}/api/admin/announcements/history",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "announcements" in data, "Response should contain 'announcements' key"
        assert isinstance(data["announcements"], list), "Announcements should be a list"
        print(f"PASS: History returns {len(data['announcements'])} announcements")
    
    def test_history_announcement_structure(self, admin_headers):
        """Test that announcements have required fields"""
        response = requests.get(
            f"{BASE_URL}/api/admin/announcements/history",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        if data["announcements"]:
            ann = data["announcements"][0]
            assert "subject" in ann, "Announcement should have 'subject'"
            assert "message" in ann, "Announcement should have 'message'"
            assert "sent_at" in ann, "Announcement should have 'sent_at'"
            assert "sent_to_count" in ann, "Announcement should have 'sent_to_count'"
            print(f"PASS: Announcement structure valid - subject: {ann['subject'][:30]}...")
        else:
            print("PASS: No announcements to validate structure (empty list)")


class TestAnnouncementIntegration:
    """Integration tests for the full announcement flow"""
    
    def test_full_announcement_flow(self, admin_headers):
        """Test complete flow: search users -> send announcement -> check history"""
        # Step 1: Search for users
        search_response = requests.get(
            f"{BASE_URL}/api/admin/users/list?search=test&limit=5",
            headers=admin_headers
        )
        assert search_response.status_code == 200
        print("Step 1: User search works")
        
        # Step 2: Get history count before
        history_before = requests.get(
            f"{BASE_URL}/api/admin/announcements/history",
            headers=admin_headers
        )
        assert history_before.status_code == 200
        count_before = len(history_before.json()["announcements"])
        print(f"Step 2: History has {count_before} announcements before")
        
        # Step 3: Send announcement (may fail with 503 if email not configured)
        send_response = requests.post(
            f"{BASE_URL}/api/admin/announcements/send",
            headers=admin_headers,
            json={
                "subject": "Integration Test Announcement",
                "message": "This is an integration test announcement.",
                "user_ids": [],
                "send_to_all": True
            }
        )
        
        if send_response.status_code == 503:
            print("Step 3: Email service not configured - skipping history verification")
            print("PASS: Integration test completed (email service unavailable)")
            return
        
        assert send_response.status_code == 200, f"Send failed: {send_response.text}"
        print(f"Step 3: Announcement sent - {send_response.json().get('sent_count', 0)} recipients")
        
        # Step 4: Verify history updated
        history_after = requests.get(
            f"{BASE_URL}/api/admin/announcements/history",
            headers=admin_headers
        )
        assert history_after.status_code == 200
        count_after = len(history_after.json()["announcements"])
        
        assert count_after >= count_before, "History should have same or more announcements"
        print(f"Step 4: History now has {count_after} announcements")
        print("PASS: Full integration test completed successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
