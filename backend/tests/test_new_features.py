"""
Backend API Tests for Edge Mode App - New Features
Tests: Session History, Notes on Sessions, Notification Settings
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSessionHistory:
    """Test session history endpoint"""
    
    @pytest.fixture(scope="class")
    def authenticated_user(self):
        """Create and authenticate a test user for history tests"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"history_test_{unique_id}@example.com",
            "username": f"historyuser_{unique_id}",
            "password": "TestPass123!",
            "age": 16
        }
        
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        user_data["token"] = data["token"]
        user_data["user_id"] = data["user_id"]
        user_data["headers"] = {"Authorization": f"Bearer {data['token']}"}
        
        # Complete onboarding
        pillars_data = {
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 5},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 7},
                {"pillar_name": "Reading/Learning", "weekly_target_sessions": 3}
            ]
        }
        requests.post(
            f"{BASE_URL}/api/onboarding/complete",
            json=pillars_data,
            headers=user_data["headers"]
        )
        
        print(f"Created test user: {user_data['email']}")
        return user_data
    
    def test_get_session_history_empty(self, authenticated_user):
        """Test getting session history when no sessions exist"""
        response = requests.get(
            f"{BASE_URL}/api/sessions/history?days=30",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Session history (empty): {len(data)} sessions")
    
    def test_get_session_history_with_sessions(self, authenticated_user):
        """Test getting session history after creating sessions"""
        # Create a few sessions
        for pillar in ["Fitness/Training", "Study/Academics"]:
            requests.post(
                f"{BASE_URL}/api/sessions/complete",
                json={"pillar": pillar, "minutes_spent": 30},
                headers=authenticated_user["headers"]
            )
        
        response = requests.get(
            f"{BASE_URL}/api/sessions/history?days=30",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        
        # Verify session structure
        session = data[0]
        assert "id" in session
        assert "pillar" in session
        assert "date" in session
        assert "timestamp" in session
        assert "minutes_spent" in session
        print(f"Session history: {len(data)} sessions found")
    
    def test_get_session_history_with_days_param(self, authenticated_user):
        """Test session history with different days parameter"""
        response = requests.get(
            f"{BASE_URL}/api/sessions/history?days=90",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Session history (90 days): {len(data)} sessions")


class TestSessionNotes:
    """Test session notes functionality"""
    
    @pytest.fixture(scope="class")
    def authenticated_user(self):
        """Create and authenticate a test user for notes tests"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"notes_test_{unique_id}@example.com",
            "username": f"notesuser_{unique_id}",
            "password": "TestPass123!",
            "age": 15
        }
        
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        user_data["token"] = data["token"]
        user_data["headers"] = {"Authorization": f"Bearer {data['token']}"}
        
        # Complete onboarding
        pillars_data = {
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 5},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 7},
                {"pillar_name": "Reading/Learning", "weekly_target_sessions": 3}
            ]
        }
        requests.post(
            f"{BASE_URL}/api/onboarding/complete",
            json=pillars_data,
            headers=user_data["headers"]
        )
        
        print(f"Created test user: {user_data['email']}")
        return user_data
    
    def test_create_session_with_note(self, authenticated_user):
        """Test creating a session with a note"""
        session_data = {
            "pillar": "Fitness/Training",
            "minutes_spent": 45,
            "note": "Great workout today! Focused on cardio."
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
        assert session["note"] == "Great workout today! Focused on cardio."
        
        authenticated_user["session_with_note_id"] = session["id"]
        print(f"Created session with note: {session['id']}")
    
    def test_create_session_without_note(self, authenticated_user):
        """Test creating a session without a note"""
        session_data = {
            "pillar": "Study/Academics",
            "minutes_spent": 60
        }
        
        response = requests.post(
            f"{BASE_URL}/api/sessions/complete",
            json=session_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["note"] is None
        
        authenticated_user["session_without_note_id"] = data["id"]
        print(f"Created session without note: {data['id']}")
    
    def test_verify_note_in_today_sessions(self, authenticated_user):
        """Test that notes are returned in today's sessions"""
        response = requests.get(
            f"{BASE_URL}/api/sessions/today",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Find session with note
        session_with_note = next(
            (s for s in data if s["id"] == authenticated_user["session_with_note_id"]),
            None
        )
        assert session_with_note is not None
        assert session_with_note["note"] == "Great workout today! Focused on cardio."
        print("Note verified in today's sessions")
    
    def test_edit_session_add_note(self, authenticated_user):
        """Test adding a note to an existing session"""
        edit_data = {
            "session_id": authenticated_user["session_without_note_id"],
            "minutes_spent": 60,
            "note": "Added note after the fact"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/sessions/edit",
            json=edit_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        
        # Verify the note was added
        verify_response = requests.get(
            f"{BASE_URL}/api/sessions/today",
            headers=authenticated_user["headers"]
        )
        sessions = verify_response.json()
        edited_session = next(
            (s for s in sessions if s["id"] == authenticated_user["session_without_note_id"]),
            None
        )
        assert edited_session is not None
        assert edited_session["note"] == "Added note after the fact"
        print("Note added to existing session successfully")
    
    def test_edit_session_update_note(self, authenticated_user):
        """Test updating an existing note"""
        edit_data = {
            "session_id": authenticated_user["session_with_note_id"],
            "minutes_spent": 45,
            "note": "Updated note - even better workout!"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/sessions/edit",
            json=edit_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        
        # Verify the note was updated
        verify_response = requests.get(
            f"{BASE_URL}/api/sessions/today",
            headers=authenticated_user["headers"]
        )
        sessions = verify_response.json()
        edited_session = next(
            (s for s in sessions if s["id"] == authenticated_user["session_with_note_id"]),
            None
        )
        assert edited_session is not None
        assert edited_session["note"] == "Updated note - even better workout!"
        print("Note updated successfully")
    
    def test_edit_session_remove_note(self, authenticated_user):
        """Test removing a note from a session"""
        edit_data = {
            "session_id": authenticated_user["session_with_note_id"],
            "minutes_spent": 45,
            "note": ""  # Empty string to remove note
        }
        
        response = requests.put(
            f"{BASE_URL}/api/sessions/edit",
            json=edit_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        
        # Verify the note was removed
        verify_response = requests.get(
            f"{BASE_URL}/api/sessions/today",
            headers=authenticated_user["headers"]
        )
        sessions = verify_response.json()
        edited_session = next(
            (s for s in sessions if s["id"] == authenticated_user["session_with_note_id"]),
            None
        )
        assert edited_session is not None
        assert edited_session["note"] is None
        print("Note removed successfully")
    
    def test_note_in_history(self, authenticated_user):
        """Test that notes appear in session history"""
        response = requests.get(
            f"{BASE_URL}/api/sessions/history?days=30",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check that note field exists in history
        for session in data:
            assert "note" in session
        print("Notes field present in session history")


class TestNotificationSettings:
    """Test notification settings endpoints"""
    
    @pytest.fixture(scope="class")
    def authenticated_user(self):
        """Create and authenticate a test user for notification tests"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"notif_test_{unique_id}@example.com",
            "username": f"notifuser_{unique_id}",
            "password": "TestPass123!",
            "age": 17
        }
        
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        user_data["token"] = data["token"]
        user_data["headers"] = {"Authorization": f"Bearer {data['token']}"}
        
        print(f"Created test user: {user_data['email']}")
        return user_data
    
    def test_get_notification_settings_default(self, authenticated_user):
        """Test getting default notification settings"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/settings",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Default settings should be true
        assert "streak_reminders" in data
        assert "weekly_summary" in data
        assert data["streak_reminders"] == True
        assert data["weekly_summary"] == True
        print(f"Default notification settings: {data}")
    
    def test_update_notification_settings_disable_streak(self, authenticated_user):
        """Test disabling streak reminders"""
        settings = {
            "streak_reminders": False,
            "weekly_summary": True
        }
        
        response = requests.put(
            f"{BASE_URL}/api/notifications/settings",
            json=settings,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        
        # Verify the update
        verify_response = requests.get(
            f"{BASE_URL}/api/notifications/settings",
            headers=authenticated_user["headers"]
        )
        data = verify_response.json()
        assert data["streak_reminders"] == False
        assert data["weekly_summary"] == True
        print("Streak reminders disabled successfully")
    
    def test_update_notification_settings_disable_weekly(self, authenticated_user):
        """Test disabling weekly summary"""
        settings = {
            "streak_reminders": False,
            "weekly_summary": False
        }
        
        response = requests.put(
            f"{BASE_URL}/api/notifications/settings",
            json=settings,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        
        # Verify the update
        verify_response = requests.get(
            f"{BASE_URL}/api/notifications/settings",
            headers=authenticated_user["headers"]
        )
        data = verify_response.json()
        assert data["streak_reminders"] == False
        assert data["weekly_summary"] == False
        print("Weekly summary disabled successfully")
    
    def test_update_notification_settings_enable_all(self, authenticated_user):
        """Test enabling all notifications"""
        settings = {
            "streak_reminders": True,
            "weekly_summary": True
        }
        
        response = requests.put(
            f"{BASE_URL}/api/notifications/settings",
            json=settings,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        
        # Verify the update
        verify_response = requests.get(
            f"{BASE_URL}/api/notifications/settings",
            headers=authenticated_user["headers"]
        )
        data = verify_response.json()
        assert data["streak_reminders"] == True
        assert data["weekly_summary"] == True
        print("All notifications enabled successfully")
    
    def test_send_streak_reminder_endpoint(self, authenticated_user):
        """Test streak reminder email endpoint (won't actually send without API key)"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/send-streak-reminder",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"Streak reminder endpoint response: {data['message']}")
    
    def test_send_weekly_summary_endpoint(self, authenticated_user):
        """Test weekly summary email endpoint (won't actually send without API key)"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/send-weekly-summary",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "stats" in data
        print(f"Weekly summary endpoint response: {data['message']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
