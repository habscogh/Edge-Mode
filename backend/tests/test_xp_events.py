"""
Test suite for XP Booster Events Feature
Tests the XP events system including:
- GET /api/engagement/events/active - returns active XP events with time remaining
- GET /api/engagement/events/upcoming - returns upcoming events
- POST /api/engagement/events - admin creates custom event
- POST /api/engagement/events/quick/double-xp-weekend - admin quick creates weekend event
- POST /api/engagement/events/quick/challenge-rush - admin quick creates rush event
- PUT /api/engagement/events/{id} - admin updates event
- DELETE /api/engagement/events/{id} - admin deletes event
- GET /api/engagement/status - includes active_event in response
- XP multiplier applied when logging sessions during active event
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timezone, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://xp-leveling-lab.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@edgemodeapp.com"
ADMIN_PASSWORD = "EdgeAdmin2024!"
TEST_PLAYER_EMAIL = "testplayer1@edgemode.com"
TEST_PLAYER_PASSWORD = "TestPlayer123!"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get('token')
    pytest.skip(f"Admin login failed: {response.status_code}")


@pytest.fixture(scope="module")
def player_token():
    """Get test player authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_PLAYER_EMAIL,
        "password": TEST_PLAYER_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get('token')
    pytest.skip(f"Test player login failed: {response.status_code}")


@pytest.fixture
def admin_headers(admin_token):
    """Headers with admin auth token"""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


@pytest.fixture
def player_headers(player_token):
    """Headers with player auth token"""
    return {"Authorization": f"Bearer {player_token}", "Content-Type": "application/json"}


class TestActiveEvents:
    """Tests for GET /api/engagement/events/active endpoint"""
    
    def test_get_active_events_success(self):
        """Test getting active events returns correct structure (public endpoint)"""
        response = requests.get(f"{BASE_URL}/api/engagement/events/active")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert 'events' in data
        assert isinstance(data['events'], list)
        
        # If there are active events, verify structure
        if data['events']:
            event = data['events'][0]
            assert 'id' in event
            assert 'name' in event
            assert 'description' in event
            assert 'multiplier' in event
            assert 'starts_at' in event
            assert 'ends_at' in event
            assert 'hours_remaining' in event
            assert 'minutes_remaining' in event
            
            # Verify multiplier is a valid number
            assert isinstance(event['multiplier'], (int, float))
            assert event['multiplier'] >= 1.0
    
    def test_active_events_have_time_remaining(self):
        """Test that active events include time remaining calculations"""
        response = requests.get(f"{BASE_URL}/api/engagement/events/active")
        
        assert response.status_code == 200
        data = response.json()
        
        if data['events']:
            event = data['events'][0]
            # Time remaining should be non-negative
            assert event['hours_remaining'] >= 0
            assert event['minutes_remaining'] >= 0


class TestUpcomingEvents:
    """Tests for GET /api/engagement/events/upcoming endpoint"""
    
    def test_get_upcoming_events_success(self):
        """Test getting upcoming events returns correct structure (public endpoint)"""
        response = requests.get(f"{BASE_URL}/api/engagement/events/upcoming")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert 'events' in data
        assert isinstance(data['events'], list)


class TestAdminEventsList:
    """Tests for GET /api/engagement/events (admin only)"""
    
    def test_list_all_events_admin_success(self, admin_headers):
        """Test admin can list all events"""
        response = requests.get(f"{BASE_URL}/api/engagement/events", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'events' in data
        assert isinstance(data['events'], list)
    
    def test_list_all_events_requires_admin(self, player_headers):
        """Test that listing all events requires admin role"""
        response = requests.get(f"{BASE_URL}/api/engagement/events", headers=player_headers)
        
        # Should be forbidden for non-admin
        assert response.status_code in [401, 403]
    
    def test_list_all_events_requires_auth(self):
        """Test that listing all events requires authentication"""
        response = requests.get(f"{BASE_URL}/api/engagement/events")
        
        assert response.status_code in [401, 403]


class TestCreateEvent:
    """Tests for POST /api/engagement/events (admin creates custom event)"""
    
    def test_create_event_success(self, admin_headers):
        """Test admin can create a custom XP event"""
        now = datetime.now(timezone.utc)
        starts_at = now.isoformat()
        ends_at = (now + timedelta(hours=2)).isoformat()
        
        event_data = {
            "name": "TEST_Custom Event",
            "description": "Test event for automated testing",
            "multiplier": 2.5,
            "event_type": "all",
            "starts_at": starts_at,
            "ends_at": ends_at,
            "icon": "🧪"
        }
        
        response = requests.post(f"{BASE_URL}/api/engagement/events", headers=admin_headers, json=event_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'message' in data
        assert 'event' in data
        assert data['event']['name'] == "TEST_Custom Event"
        assert data['event']['multiplier'] == 2.5
        assert data['event']['icon'] == "🧪"
        assert 'id' in data['event']
        
        # Store event ID for cleanup
        return data['event']['id']
    
    def test_create_event_invalid_dates(self, admin_headers):
        """Test that end date must be after start date"""
        now = datetime.now(timezone.utc)
        starts_at = now.isoformat()
        ends_at = (now - timedelta(hours=1)).isoformat()  # End before start
        
        event_data = {
            "name": "TEST_Invalid Event",
            "description": "Should fail",
            "multiplier": 2.0,
            "event_type": "all",
            "starts_at": starts_at,
            "ends_at": ends_at
        }
        
        response = requests.post(f"{BASE_URL}/api/engagement/events", headers=admin_headers, json=event_data)
        
        assert response.status_code == 400
        assert 'End date must be after start date' in response.json().get('detail', '')
    
    def test_create_event_invalid_multiplier(self, admin_headers):
        """Test that multiplier must be between 1.0 and 10.0"""
        now = datetime.now(timezone.utc)
        starts_at = now.isoformat()
        ends_at = (now + timedelta(hours=2)).isoformat()
        
        event_data = {
            "name": "TEST_Invalid Multiplier",
            "description": "Should fail",
            "multiplier": 15.0,  # Too high
            "event_type": "all",
            "starts_at": starts_at,
            "ends_at": ends_at
        }
        
        response = requests.post(f"{BASE_URL}/api/engagement/events", headers=admin_headers, json=event_data)
        
        assert response.status_code == 400
        assert 'Multiplier must be between' in response.json().get('detail', '')
    
    def test_create_event_requires_admin(self, player_headers):
        """Test that creating events requires admin role"""
        now = datetime.now(timezone.utc)
        event_data = {
            "name": "TEST_Unauthorized Event",
            "description": "Should fail",
            "multiplier": 2.0,
            "event_type": "all",
            "starts_at": now.isoformat(),
            "ends_at": (now + timedelta(hours=2)).isoformat()
        }
        
        response = requests.post(f"{BASE_URL}/api/engagement/events", headers=player_headers, json=event_data)
        
        assert response.status_code in [401, 403]


class TestQuickDoubleXPWeekend:
    """Tests for POST /api/engagement/events/quick/double-xp-weekend"""
    
    def test_quick_double_xp_weekend_success(self, admin_headers):
        """Test admin can quick create a Double XP Weekend event"""
        response = requests.post(f"{BASE_URL}/api/engagement/events/quick/double-xp-weekend", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'message' in data
        assert 'event' in data
        assert 'Double XP Weekend' in data['event']['name']
        assert data['event']['multiplier'] == 2.0
        assert data['event']['event_type'] == 'all'
    
    def test_quick_double_xp_weekend_requires_admin(self, player_headers):
        """Test that quick creating Double XP Weekend requires admin"""
        response = requests.post(f"{BASE_URL}/api/engagement/events/quick/double-xp-weekend", headers=player_headers)
        
        assert response.status_code in [401, 403]


class TestQuickChallengeRush:
    """Tests for POST /api/engagement/events/quick/challenge-rush"""
    
    def test_quick_challenge_rush_default_success(self, admin_headers):
        """Test admin can quick create a Challenge Rush event with defaults"""
        response = requests.post(f"{BASE_URL}/api/engagement/events/quick/challenge-rush", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'message' in data
        assert 'event' in data
        assert 'Challenge Rush' in data['event']['name']
        assert data['event']['multiplier'] == 3.0  # Default multiplier
    
    def test_quick_challenge_rush_custom_params(self, admin_headers):
        """Test admin can quick create a Challenge Rush with custom hours and multiplier"""
        response = requests.post(
            f"{BASE_URL}/api/engagement/events/quick/challenge-rush?hours=12&multiplier=5.0", 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['event']['multiplier'] == 5.0
        assert '5x' in data['event']['name']
    
    def test_quick_challenge_rush_requires_admin(self, player_headers):
        """Test that quick creating Challenge Rush requires admin"""
        response = requests.post(f"{BASE_URL}/api/engagement/events/quick/challenge-rush", headers=player_headers)
        
        assert response.status_code in [401, 403]


class TestUpdateEvent:
    """Tests for PUT /api/engagement/events/{id}"""
    
    def test_update_event_success(self, admin_headers):
        """Test admin can update an existing event"""
        # First create an event
        now = datetime.now(timezone.utc)
        create_response = requests.post(f"{BASE_URL}/api/engagement/events", headers=admin_headers, json={
            "name": "TEST_Event To Update",
            "description": "Will be updated",
            "multiplier": 2.0,
            "event_type": "all",
            "starts_at": now.isoformat(),
            "ends_at": (now + timedelta(hours=2)).isoformat()
        })
        
        assert create_response.status_code == 200
        event_id = create_response.json()['event']['id']
        
        # Update the event
        update_response = requests.put(f"{BASE_URL}/api/engagement/events/{event_id}", headers=admin_headers, json={
            "name": "TEST_Updated Event Name",
            "multiplier": 4.0
        })
        
        assert update_response.status_code == 200
        data = update_response.json()
        
        assert 'message' in data
        assert data['updates']['name'] == "TEST_Updated Event Name"
        assert data['updates']['multiplier'] == 4.0
    
    def test_update_event_not_found(self, admin_headers):
        """Test updating non-existent event returns 404"""
        response = requests.put(f"{BASE_URL}/api/engagement/events/nonexistent-id", headers=admin_headers, json={
            "name": "Should Fail"
        })
        
        assert response.status_code == 404
    
    def test_update_event_invalid_multiplier(self, admin_headers):
        """Test that updating with invalid multiplier fails"""
        # First create an event
        now = datetime.now(timezone.utc)
        create_response = requests.post(f"{BASE_URL}/api/engagement/events", headers=admin_headers, json={
            "name": "TEST_Event For Invalid Update",
            "description": "Test",
            "multiplier": 2.0,
            "event_type": "all",
            "starts_at": now.isoformat(),
            "ends_at": (now + timedelta(hours=2)).isoformat()
        })
        
        event_id = create_response.json()['event']['id']
        
        # Try to update with invalid multiplier
        update_response = requests.put(f"{BASE_URL}/api/engagement/events/{event_id}", headers=admin_headers, json={
            "multiplier": 0.5  # Too low
        })
        
        assert update_response.status_code == 400
    
    def test_update_event_requires_admin(self, player_headers):
        """Test that updating events requires admin role"""
        response = requests.put(f"{BASE_URL}/api/engagement/events/some-id", headers=player_headers, json={
            "name": "Should Fail"
        })
        
        assert response.status_code in [401, 403]


class TestDeleteEvent:
    """Tests for DELETE /api/engagement/events/{id}"""
    
    def test_delete_event_success(self, admin_headers):
        """Test admin can delete an event"""
        # First create an event
        now = datetime.now(timezone.utc)
        create_response = requests.post(f"{BASE_URL}/api/engagement/events", headers=admin_headers, json={
            "name": "TEST_Event To Delete",
            "description": "Will be deleted",
            "multiplier": 2.0,
            "event_type": "all",
            "starts_at": now.isoformat(),
            "ends_at": (now + timedelta(hours=2)).isoformat()
        })
        
        assert create_response.status_code == 200
        event_id = create_response.json()['event']['id']
        
        # Delete the event
        delete_response = requests.delete(f"{BASE_URL}/api/engagement/events/{event_id}", headers=admin_headers)
        
        assert delete_response.status_code == 200
        assert 'message' in delete_response.json()
        
        # Verify it's deleted
        get_response = requests.get(f"{BASE_URL}/api/engagement/events", headers=admin_headers)
        events = get_response.json()['events']
        event_ids = [e['id'] for e in events]
        assert event_id not in event_ids
    
    def test_delete_event_not_found(self, admin_headers):
        """Test deleting non-existent event returns 404"""
        response = requests.delete(f"{BASE_URL}/api/engagement/events/nonexistent-id", headers=admin_headers)
        
        assert response.status_code == 404
    
    def test_delete_event_requires_admin(self, player_headers):
        """Test that deleting events requires admin role"""
        response = requests.delete(f"{BASE_URL}/api/engagement/events/some-id", headers=player_headers)
        
        assert response.status_code in [401, 403]


class TestEngagementStatusWithEvent:
    """Tests for GET /api/engagement/status including active_event"""
    
    def test_engagement_status_includes_active_event(self, player_headers):
        """Test that engagement status includes active_event when one is active"""
        response = requests.get(f"{BASE_URL}/api/engagement/status", headers=player_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # active_event should be present (may be null if no active event)
        assert 'active_event' in data
        
        # If there's an active event, verify structure
        if data['active_event']:
            event = data['active_event']
            assert 'id' in event
            assert 'name' in event
            assert 'description' in event
            assert 'multiplier' in event
            assert 'icon' in event
            assert 'ends_at' in event


class TestXPMultiplierDuringEvent:
    """Tests for XP multiplier being applied during active events"""
    
    def test_xp_multiplied_during_active_event(self, player_headers, admin_headers):
        """Test that XP is multiplied when logging sessions during an active event"""
        # First check if there's an active event
        status_response = requests.get(f"{BASE_URL}/api/engagement/status", headers=player_headers)
        active_event = status_response.json().get('active_event')
        
        if not active_event:
            # Create an active event for testing
            now = datetime.now(timezone.utc)
            create_response = requests.post(f"{BASE_URL}/api/engagement/events", headers=admin_headers, json={
                "name": "TEST_XP Multiplier Test Event",
                "description": "Testing XP multiplier",
                "multiplier": 2.0,
                "event_type": "all",
                "starts_at": now.isoformat(),
                "ends_at": (now + timedelta(hours=1)).isoformat()
            })
            assert create_response.status_code == 200
            multiplier = 2.0
        else:
            multiplier = active_event['multiplier']
        
        # Get current XP
        status_before = requests.get(f"{BASE_URL}/api/engagement/status", headers=player_headers)
        xp_before = status_before.json().get('xp', 0)
        
        # Log a session
        session_response = requests.post(f"{BASE_URL}/api/sessions/complete", headers=player_headers, json={
            "pillar": "Fitness/Training",
            "minutes_spent": 30
        })
        
        assert session_response.status_code == 200
        session_data = session_response.json()
        
        # Verify XP was earned
        assert 'xp_earned' in session_data
        assert session_data['xp_earned'] > 0
        
        # If event is active, check for multiplier info
        if session_data.get('event_active'):
            assert session_data.get('multiplier', 1.0) > 1.0
            # XP earned should be base_xp * multiplier
            if 'base_xp' in session_data:
                expected_xp = int(session_data['base_xp'] * session_data['multiplier'])
                assert session_data['xp_earned'] == expected_xp


class TestCleanupTestEvents:
    """Cleanup test events created during testing"""
    
    def test_cleanup_test_events(self, admin_headers):
        """Delete all TEST_ prefixed events"""
        # Get all events
        response = requests.get(f"{BASE_URL}/api/engagement/events", headers=admin_headers)
        
        if response.status_code == 200:
            events = response.json().get('events', [])
            for event in events:
                if event.get('name', '').startswith('TEST_'):
                    delete_response = requests.delete(
                        f"{BASE_URL}/api/engagement/events/{event['id']}", 
                        headers=admin_headers
                    )
                    print(f"Cleaned up test event: {event['name']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
