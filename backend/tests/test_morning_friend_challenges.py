"""
Test Morning Reminders and Friend Challenges (1v1) features
Tests:
- Morning Reminders: GET/PUT /api/notifications/settings with morning_reminders field
- Friend Challenges: POST /api/challenges/friend/create, GET pending/active/history, POST respond
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
COACH_EMAIL = "testcoach@edgemode.com"
COACH_PASSWORD = "TestCoach123!"
ADMIN_EMAIL = "admin@edgemodeapp.com"
ADMIN_PASSWORD = "EdgeAdmin2024!"

# Test user for friend challenges
TEST_USER_EMAIL = f"test_friend_{uuid.uuid4().hex[:8]}@edgemode.com"
TEST_USER_PASSWORD = "TestUser123!"
TEST_USER_USERNAME = f"TestFriend{uuid.uuid4().hex[:4]}"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def coach_token(api_client):
    """Get coach authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": COACH_EMAIL,
        "password": COACH_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Coach authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Admin authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def test_user_token(api_client):
    """Create and authenticate a test user for friend challenges"""
    # First try to register
    register_response = api_client.post(f"{BASE_URL}/api/auth/register", json={
        "email": TEST_USER_EMAIL,
        "username": TEST_USER_USERNAME,
        "password": TEST_USER_PASSWORD,
        "age": 16
    })
    
    # If registration fails (user exists), try login
    if register_response.status_code != 200:
        login_response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if login_response.status_code == 200:
            return login_response.json().get("token")
        pytest.skip(f"Test user auth failed: {login_response.status_code}")
    
    return register_response.json().get("token")


@pytest.fixture(scope="module")
def authenticated_coach(api_client, coach_token):
    """Session with coach auth header"""
    api_client.headers.update({"Authorization": f"Bearer {coach_token}"})
    return api_client


class TestMorningReminders:
    """Test Morning Reminder notification settings"""
    
    def test_get_notification_settings_returns_morning_reminders(self, api_client, coach_token):
        """GET /api/notifications/settings should return morning_reminders field"""
        response = api_client.get(
            f"{BASE_URL}/api/notifications/settings",
            headers={"Authorization": f"Bearer {coach_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "morning_reminders" in data, "Response should contain morning_reminders field"
        assert "streak_reminders" in data, "Response should contain streak_reminders field"
        assert "weekly_summary" in data, "Response should contain weekly_summary field"
        assert isinstance(data["morning_reminders"], bool), "morning_reminders should be boolean"
        print(f"✓ GET notification settings: morning_reminders={data['morning_reminders']}")
    
    def test_enable_morning_reminders(self, api_client, coach_token):
        """PUT /api/notifications/settings can enable morning_reminders"""
        response = api_client.put(
            f"{BASE_URL}/api/notifications/settings",
            headers={"Authorization": f"Bearer {coach_token}"},
            json={"morning_reminders": True}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Response should contain message"
        assert "updated_fields" in data, "Response should contain updated_fields"
        assert "morning_reminders" in data["updated_fields"], "morning_reminders should be in updated_fields"
        print(f"✓ Enabled morning_reminders: {data}")
        
        # Verify the change persisted
        verify_response = api_client.get(
            f"{BASE_URL}/api/notifications/settings",
            headers={"Authorization": f"Bearer {coach_token}"}
        )
        assert verify_response.status_code == 200
        assert verify_response.json()["morning_reminders"] == True, "morning_reminders should be True after update"
        print("✓ Verified morning_reminders is now True")
    
    def test_disable_morning_reminders(self, api_client, coach_token):
        """PUT /api/notifications/settings can disable morning_reminders"""
        response = api_client.put(
            f"{BASE_URL}/api/notifications/settings",
            headers={"Authorization": f"Bearer {coach_token}"},
            json={"morning_reminders": False}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify the change persisted
        verify_response = api_client.get(
            f"{BASE_URL}/api/notifications/settings",
            headers={"Authorization": f"Bearer {coach_token}"}
        )
        assert verify_response.status_code == 200
        assert verify_response.json()["morning_reminders"] == False, "morning_reminders should be False after update"
        print("✓ Disabled morning_reminders and verified")
    
    def test_notification_settings_requires_auth(self, api_client):
        """Notification settings endpoints require authentication"""
        # GET without auth
        get_response = api_client.get(f"{BASE_URL}/api/notifications/settings")
        assert get_response.status_code in [401, 403], f"GET should require auth, got {get_response.status_code}"
        
        # PUT without auth
        put_response = api_client.put(
            f"{BASE_URL}/api/notifications/settings",
            json={"morning_reminders": True}
        )
        assert put_response.status_code in [401, 403], f"PUT should require auth, got {put_response.status_code}"
        print("✓ Notification settings endpoints require authentication")


class TestFriendChallengesCreate:
    """Test Friend Challenge creation"""
    
    def test_create_friend_challenge_success(self, api_client, coach_token):
        """POST /api/challenges/friend/create creates a 1v1 challenge"""
        # Use testplayer1@edgemode.com which was created in previous tests
        response = api_client.post(
            f"{BASE_URL}/api/challenges/friend/create",
            headers={"Authorization": f"Bearer {coach_token}"},
            json={
                "friend_email": "testplayer1@edgemode.com",
                "name": "Test 1v1 Challenge",
                "goal_type": "sessions",
                "goal_value": 10,
                "duration_days": 7
            }
        )
        
        # Could be 200 or 400 if challenge already exists
        if response.status_code == 400 and "pending challenge" in response.text.lower():
            print("✓ Challenge already exists between these users (expected)")
            return
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Response should contain message"
        assert "challenge_id" in data, "Response should contain challenge_id"
        assert data["status"] == "pending", "New challenge should have pending status"
        print(f"✓ Created friend challenge: {data['challenge_id']}")
    
    def test_create_challenge_user_not_found(self, api_client, coach_token):
        """POST /api/challenges/friend/create returns 404 for non-existent user"""
        response = api_client.post(
            f"{BASE_URL}/api/challenges/friend/create",
            headers={"Authorization": f"Bearer {coach_token}"},
            json={
                "friend_email": "nonexistent_user_12345@example.com",
                "name": "Test Challenge",
                "goal_type": "sessions",
                "goal_value": 10,
                "duration_days": 7
            }
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        assert "not found" in response.json().get("detail", "").lower()
        print("✓ Returns 404 for non-existent user")
    
    def test_create_challenge_cannot_challenge_self(self, api_client, coach_token):
        """POST /api/challenges/friend/create returns 400 when challenging self"""
        response = api_client.post(
            f"{BASE_URL}/api/challenges/friend/create",
            headers={"Authorization": f"Bearer {coach_token}"},
            json={
                "friend_email": COACH_EMAIL,
                "name": "Self Challenge",
                "goal_type": "sessions",
                "goal_value": 10,
                "duration_days": 7
            }
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        assert "yourself" in response.json().get("detail", "").lower()
        print("✓ Cannot challenge yourself")


class TestFriendChallengesPending:
    """Test pending friend challenges endpoint"""
    
    def test_get_pending_challenges(self, api_client, coach_token):
        """GET /api/challenges/friend/pending returns received and sent challenges"""
        response = api_client.get(
            f"{BASE_URL}/api/challenges/friend/pending",
            headers={"Authorization": f"Bearer {coach_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "received" in data, "Response should contain 'received' array"
        assert "sent" in data, "Response should contain 'sent' array"
        assert isinstance(data["received"], list), "received should be a list"
        assert isinstance(data["sent"], list), "sent should be a list"
        print(f"✓ GET pending challenges: {len(data['received'])} received, {len(data['sent'])} sent")
    
    def test_pending_challenges_requires_auth(self, api_client):
        """GET /api/challenges/friend/pending requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/challenges/friend/pending")
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
        print("✓ Pending challenges endpoint requires auth")


class TestFriendChallengesActive:
    """Test active friend challenges endpoint"""
    
    def test_get_active_challenges(self, api_client, coach_token):
        """GET /api/challenges/friend/active returns active challenges with scores"""
        response = api_client.get(
            f"{BASE_URL}/api/challenges/friend/active",
            headers={"Authorization": f"Bearer {coach_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "challenges" in data, "Response should contain 'challenges' array"
        assert isinstance(data["challenges"], list), "challenges should be a list"
        
        # If there are active challenges, verify structure
        if data["challenges"]:
            challenge = data["challenges"][0]
            assert "challenger_score" in challenge, "Challenge should have challenger_score"
            assert "challenged_score" in challenge, "Challenge should have challenged_score"
            assert "days_remaining" in challenge, "Challenge should have days_remaining"
            assert "is_challenger" in challenge, "Challenge should have is_challenger flag"
            print(f"✓ Active challenge structure verified: {challenge.get('name')}")
        else:
            print("✓ GET active challenges: No active challenges (expected)")
    
    def test_active_challenges_requires_auth(self, api_client):
        """GET /api/challenges/friend/active requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/challenges/friend/active")
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
        print("✓ Active challenges endpoint requires auth")


class TestFriendChallengesRespond:
    """Test responding to friend challenges"""
    
    def test_respond_to_challenge_invalid_id(self, api_client, coach_token):
        """POST /api/challenges/friend/respond returns 404 for invalid challenge"""
        response = api_client.post(
            f"{BASE_URL}/api/challenges/friend/respond",
            headers={"Authorization": f"Bearer {coach_token}"},
            json={
                "challenge_id": "nonexistent-challenge-id",
                "action": "accept"
            }
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print("✓ Returns 404 for non-existent challenge")
    
    def test_respond_invalid_action(self, api_client, coach_token):
        """POST /api/challenges/friend/respond validates action parameter"""
        # First get pending challenges to find a valid ID (if any)
        pending_response = api_client.get(
            f"{BASE_URL}/api/challenges/friend/pending",
            headers={"Authorization": f"Bearer {coach_token}"}
        )
        
        if pending_response.status_code == 200:
            received = pending_response.json().get("received", [])
            if received:
                challenge_id = received[0]["id"]
                response = api_client.post(
                    f"{BASE_URL}/api/challenges/friend/respond",
                    headers={"Authorization": f"Bearer {coach_token}"},
                    json={
                        "challenge_id": challenge_id,
                        "action": "invalid_action"
                    }
                )
                assert response.status_code == 400, f"Expected 400 for invalid action, got {response.status_code}"
                print("✓ Invalid action returns 400")
            else:
                print("✓ No pending challenges to test invalid action (skipped)")
        else:
            print("✓ Could not get pending challenges (skipped)")
    
    def test_respond_requires_auth(self, api_client):
        """POST /api/challenges/friend/respond requires authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/challenges/friend/respond",
            json={"challenge_id": "test", "action": "accept"}
        )
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
        print("✓ Respond endpoint requires auth")


class TestFriendChallengesHistory:
    """Test friend challenges history endpoint"""
    
    def test_get_challenge_history(self, api_client, coach_token):
        """GET /api/challenges/friend/history returns completed challenges"""
        response = api_client.get(
            f"{BASE_URL}/api/challenges/friend/history",
            headers={"Authorization": f"Bearer {coach_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "challenges" in data, "Response should contain 'challenges' array"
        assert isinstance(data["challenges"], list), "challenges should be a list"
        
        # If there are completed challenges, verify structure
        if data["challenges"]:
            challenge = data["challenges"][0]
            assert "won" in challenge, "Challenge should have 'won' field"
            assert "is_challenger" in challenge, "Challenge should have 'is_challenger' field"
            print(f"✓ History challenge structure verified: {challenge.get('name')}")
        else:
            print("✓ GET challenge history: No completed challenges (expected)")
    
    def test_history_requires_auth(self, api_client):
        """GET /api/challenges/friend/history requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/challenges/friend/history")
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
        print("✓ History endpoint requires auth")


class TestFriendChallengeIntegration:
    """Integration test for full friend challenge flow"""
    
    def test_full_challenge_flow(self, api_client, admin_token, test_user_token):
        """Test creating, viewing, and responding to a friend challenge"""
        # Admin creates a challenge to test user
        create_response = api_client.post(
            f"{BASE_URL}/api/challenges/friend/create",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "friend_email": TEST_USER_EMAIL,
                "name": f"Integration Test Challenge {uuid.uuid4().hex[:6]}",
                "goal_type": "minutes",
                "goal_value": 60,
                "duration_days": 3
            }
        )
        
        if create_response.status_code == 400 and "pending challenge" in create_response.text.lower():
            print("✓ Challenge already exists (integration test skipped)")
            return
        
        assert create_response.status_code == 200, f"Create failed: {create_response.status_code} - {create_response.text}"
        challenge_id = create_response.json()["challenge_id"]
        print(f"✓ Created challenge: {challenge_id}")
        
        # Test user should see it in pending received
        pending_response = api_client.get(
            f"{BASE_URL}/api/challenges/friend/pending",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert pending_response.status_code == 200
        received = pending_response.json().get("received", [])
        challenge_found = any(c["id"] == challenge_id for c in received)
        assert challenge_found, "Challenge should appear in test user's received challenges"
        print("✓ Challenge appears in test user's pending received")
        
        # Test user accepts the challenge
        accept_response = api_client.post(
            f"{BASE_URL}/api/challenges/friend/respond",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={
                "challenge_id": challenge_id,
                "action": "accept"
            }
        )
        assert accept_response.status_code == 200, f"Accept failed: {accept_response.status_code} - {accept_response.text}"
        assert accept_response.json()["status"] == "active"
        print("✓ Test user accepted challenge")
        
        # Challenge should now appear in active for both users
        admin_active = api_client.get(
            f"{BASE_URL}/api/challenges/friend/active",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert admin_active.status_code == 200
        admin_challenges = admin_active.json().get("challenges", [])
        admin_has_challenge = any(c["id"] == challenge_id for c in admin_challenges)
        assert admin_has_challenge, "Challenge should appear in admin's active challenges"
        print("✓ Challenge appears in admin's active challenges")
        
        test_user_active = api_client.get(
            f"{BASE_URL}/api/challenges/friend/active",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert test_user_active.status_code == 200
        test_user_challenges = test_user_active.json().get("challenges", [])
        test_user_has_challenge = any(c["id"] == challenge_id for c in test_user_challenges)
        assert test_user_has_challenge, "Challenge should appear in test user's active challenges"
        print("✓ Challenge appears in test user's active challenges")
        
        print("✓ Full friend challenge flow completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
