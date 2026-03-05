"""
Backend API Tests for Edge Mode App
Tests: Auth, Onboarding, Sessions CRUD (Create, Edit, Delete)
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndAuth:
    """Test authentication endpoints"""
    
    @pytest.fixture(scope="class")
    def test_user_data(self):
        """Generate unique test user data"""
        unique_id = str(uuid.uuid4())[:8]
        return {
            "email": f"test_{unique_id}@example.com",
            "username": f"testuser_{unique_id}",
            "password": "TestPass123!",
            "age": 16
        }
    
    def test_pillars_endpoint(self):
        """Test that pillars endpoint returns available pillars"""
        response = requests.get(f"{BASE_URL}/api/pillars")
        assert response.status_code == 200
        data = response.json()
        assert "pillars" in data
        assert len(data["pillars"]) > 0
        print(f"Available pillars: {data['pillars']}")
    
    def test_register_new_user(self, test_user_data):
        """Test user registration"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user_data)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user_id" in data
        print(f"Registered user: {test_user_data['email']}")
        # Store for later tests
        test_user_data["token"] = data["token"]
        test_user_data["user_id"] = data["user_id"]
    
    def test_login_user(self, test_user_data):
        """Test user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        print(f"Login successful for: {test_user_data['email']}")
    
    def test_get_current_user(self, test_user_data):
        """Test getting current user info"""
        headers = {"Authorization": f"Bearer {test_user_data['token']}"}
        response = requests.get(f"{BASE_URL}/api/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        print(f"User info retrieved: {data['username']}")


class TestOnboardingAndSessions:
    """Test onboarding and session CRUD operations"""
    
    @pytest.fixture(scope="class")
    def authenticated_user(self):
        """Create and authenticate a test user for session tests"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"session_test_{unique_id}@example.com",
            "username": f"sessionuser_{unique_id}",
            "password": "TestPass123!",
            "age": 15
        }
        
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        user_data["token"] = data["token"]
        user_data["user_id"] = data["user_id"]
        user_data["headers"] = {"Authorization": f"Bearer {data['token']}"}
        
        print(f"Created test user: {user_data['email']}")
        return user_data
    
    def test_complete_onboarding(self, authenticated_user):
        """Test completing onboarding with pillar selection"""
        pillars_data = {
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 5},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 7},
                {"pillar_name": "Reading/Learning", "weekly_target_sessions": 3}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/onboarding/complete",
            json=pillars_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Onboarding complete"
        print("Onboarding completed successfully")
    
    def test_get_user_pillars(self, authenticated_user):
        """Test getting user's selected pillars"""
        response = requests.get(
            f"{BASE_URL}/api/users/pillars",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        pillar_names = [p["pillar_name"] for p in data]
        assert "Fitness/Training" in pillar_names
        print(f"User pillars: {pillar_names}")
    
    def test_create_session(self, authenticated_user):
        """Test creating a new session"""
        session_data = {
            "pillar": "Fitness/Training",
            "minutes_spent": 45
        }
        
        response = requests.post(
            f"{BASE_URL}/api/sessions/complete",
            json=session_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        # API returns {"session": {...}, "new_badges": [...]}
        assert "session" in data
        session = data["session"]
        assert "id" in session
        assert session["pillar"] == "Fitness/Training"
        assert session["minutes_spent"] == 45
        
        # Store session ID for edit/delete tests
        authenticated_user["session_id"] = session["id"]
        print(f"Created session: {session['id']}")
    
    def test_get_today_sessions(self, authenticated_user):
        """Test getting today's sessions"""
        response = requests.get(
            f"{BASE_URL}/api/sessions/today",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        # Verify our session is in the list
        session_ids = [s["id"] for s in data]
        assert authenticated_user["session_id"] in session_ids
        print(f"Today's sessions count: {len(data)}")
    
    def test_edit_session(self, authenticated_user):
        """Test editing an existing session"""
        edit_data = {
            "session_id": authenticated_user["session_id"],
            "minutes_spent": 60,
            "pillar": "Study/Academics"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/sessions/edit",
            json=edit_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Session updated successfully"
        print(f"Session edited successfully")
        
        # Verify the edit by fetching today's sessions
        verify_response = requests.get(
            f"{BASE_URL}/api/sessions/today",
            headers=authenticated_user["headers"]
        )
        assert verify_response.status_code == 200
        sessions = verify_response.json()
        edited_session = next((s for s in sessions if s["id"] == authenticated_user["session_id"]), None)
        assert edited_session is not None
        assert edited_session["minutes_spent"] == 60
        assert edited_session["pillar"] == "Study/Academics"
        print(f"Edit verified - minutes: {edited_session['minutes_spent']}, pillar: {edited_session['pillar']}")
    
    def test_edit_session_minutes_only(self, authenticated_user):
        """Test editing only minutes without changing pillar"""
        edit_data = {
            "session_id": authenticated_user["session_id"],
            "minutes_spent": 90
        }
        
        response = requests.put(
            f"{BASE_URL}/api/sessions/edit",
            json=edit_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        
        # Verify the edit
        verify_response = requests.get(
            f"{BASE_URL}/api/sessions/today",
            headers=authenticated_user["headers"]
        )
        sessions = verify_response.json()
        edited_session = next((s for s in sessions if s["id"] == authenticated_user["session_id"]), None)
        assert edited_session["minutes_spent"] == 90
        # Pillar should remain unchanged
        assert edited_session["pillar"] == "Study/Academics"
        print(f"Minutes-only edit verified: {edited_session['minutes_spent']} min")
    
    def test_edit_nonexistent_session(self, authenticated_user):
        """Test editing a session that doesn't exist"""
        edit_data = {
            "session_id": "nonexistent-session-id",
            "minutes_spent": 30
        }
        
        response = requests.put(
            f"{BASE_URL}/api/sessions/edit",
            json=edit_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 404
        print("Correctly returned 404 for nonexistent session edit")
    
    def test_delete_session(self, authenticated_user):
        """Test deleting a session"""
        # First create a new session to delete
        session_data = {
            "pillar": "Reading/Learning",
            "minutes_spent": 30
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/sessions/complete",
            json=session_data,
            headers=authenticated_user["headers"]
        )
        assert create_response.status_code == 200
        # API returns {"session": {...}, "new_badges": [...]}
        session_to_delete = create_response.json()["session"]["id"]
        print(f"Created session to delete: {session_to_delete}")
        
        # Delete the session
        delete_response = requests.delete(
            f"{BASE_URL}/api/sessions/{session_to_delete}",
            headers=authenticated_user["headers"]
        )
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert data["message"] == "Session deleted successfully"
        print("Session deleted successfully")
        
        # Verify deletion by checking today's sessions
        verify_response = requests.get(
            f"{BASE_URL}/api/sessions/today",
            headers=authenticated_user["headers"]
        )
        sessions = verify_response.json()
        session_ids = [s["id"] for s in sessions]
        assert session_to_delete not in session_ids
        print("Deletion verified - session no longer in list")
    
    def test_delete_nonexistent_session(self, authenticated_user):
        """Test deleting a session that doesn't exist"""
        response = requests.delete(
            f"{BASE_URL}/api/sessions/nonexistent-session-id",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 404
        print("Correctly returned 404 for nonexistent session delete")


class TestWeeklyStats:
    """Test weekly stats endpoints"""
    
    @pytest.fixture(scope="class")
    def stats_user(self):
        """Create user with sessions for stats testing"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"stats_test_{unique_id}@example.com",
            "username": f"statsuser_{unique_id}",
            "password": "TestPass123!",
            "age": 17
        }
        
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        data = response.json()
        user_data["token"] = data["token"]
        user_data["headers"] = {"Authorization": f"Bearer {data['token']}"}
        
        # Complete onboarding
        pillars_data = {
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 5},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 5},
                {"pillar_name": "Skill Development", "weekly_target_sessions": 3}
            ]
        }
        requests.post(
            f"{BASE_URL}/api/onboarding/complete",
            json=pillars_data,
            headers=user_data["headers"]
        )
        
        # Create some sessions
        for pillar in ["Fitness/Training", "Study/Academics"]:
            requests.post(
                f"{BASE_URL}/api/sessions/complete",
                json={"pillar": pillar, "minutes_spent": 30},
                headers=user_data["headers"]
            )
        
        return user_data
    
    def test_get_weekly_stats(self, stats_user):
        """Test getting weekly statistics"""
        response = requests.get(
            f"{BASE_URL}/api/stats/weekly",
            headers=stats_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert "consistency_pct" in data
        assert "total_sessions" in data
        assert "pillars_data" in data
        print(f"Weekly stats: {data['total_sessions']} sessions, {data['consistency_pct']}% consistency")
    
    def test_get_daily_comparison(self, stats_user):
        """Test getting daily comparison stats"""
        response = requests.get(
            f"{BASE_URL}/api/stats/comparison",
            headers=stats_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert "today_sessions" in data
        assert "yesterday_sessions" in data
        print(f"Daily comparison: today={data['today_sessions']}, yesterday={data['yesterday_sessions']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
