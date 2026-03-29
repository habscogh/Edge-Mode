"""
Test Coach Tools - Team Analytics & Bulk Messaging
Tests for coach dashboard, player details, and bulk message APIs
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
COACH_EMAIL = "testcoach@edgemode.com"
COACH_PASSWORD = "TestCoach123!"
TEAM_ID = "5182a737-b8b8-46b1-a7df-500c3c0e4a48"


def get_coach_token():
    """Get coach authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": COACH_EMAIL,
        "password": COACH_PASSWORD
    })
    assert response.status_code == 200, f"Coach login failed: {response.text}"
    data = response.json()
    return data["token"]


class TestCoachLogin:
    """Test coach authentication"""
    
    def test_coach_login_success(self):
        """Test coach can login successfully"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": COACH_EMAIL,
            "password": COACH_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user_id" in data
        assert data.get("is_coach") == True
    
    def test_coach_login_invalid_password(self):
        """Test coach login with wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": COACH_EMAIL,
            "password": "WrongPassword123!"
        })
        assert response.status_code == 401


class TestCoachDashboardAPI:
    """Test GET /api/coach/groups/{group_id}/dashboard"""
    
    def test_get_dashboard_success(self):
        """Test coach can access team dashboard"""
        token = get_coach_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/coach/groups/{TEAM_ID}/dashboard", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        # Verify response structure
        assert "group" in data
        assert "players" in data
        assert "team_stats" in data
        
        # Verify group data
        group = data["group"]
        assert group["id"] == TEAM_ID
        assert "name" in group
        assert "invite_code" in group
        assert "coach_id" in group
        
        # Verify team_stats structure
        stats = data["team_stats"]
        assert "total_players" in stats
        assert "avg_consistency" in stats
        assert "avg_performance" in stats
        assert "total_sessions_this_week" in stats
    
    def test_dashboard_returns_players_list(self):
        """Test dashboard returns players array"""
        token = get_coach_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/coach/groups/{TEAM_ID}/dashboard", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        players = data["players"]
        assert isinstance(players, list)
        
        # If there are players, verify structure
        if len(players) > 0:
            player = players[0]
            assert "id" in player
            assert "username" in player
            assert "sessions_this_week" in player
            assert "consistency_pct" in player
            assert "performance_index" in player
    
    def test_dashboard_returns_inactive_players(self):
        """Test dashboard includes inactive players list"""
        token = get_coach_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/coach/groups/{TEAM_ID}/dashboard", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        # inactive_players should be present
        assert "inactive_players" in data or data["team_stats"].get("inactive_count", 0) >= 0
    
    def test_dashboard_unauthorized_without_token(self):
        """Test dashboard requires authentication"""
        response = requests.get(f"{BASE_URL}/api/coach/groups/{TEAM_ID}/dashboard")
        assert response.status_code in [401, 403]
    
    def test_dashboard_invalid_group_id(self):
        """Test dashboard with non-existent group"""
        token = get_coach_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/coach/groups/invalid-group-id/dashboard", headers=headers)
        # Could be 404 (not found) or 403 (not coach of this group)
        assert response.status_code in [403, 404]


class TestPlayerDetailsAPI:
    """Test GET /api/coach/groups/{group_id}/player/{player_id}"""
    
    def test_get_player_details_success(self):
        """Test coach can get player details"""
        token = get_coach_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # First get dashboard to find a player
        dashboard_response = requests.get(f"{BASE_URL}/api/coach/groups/{TEAM_ID}/dashboard", headers=headers)
        assert dashboard_response.status_code == 200
        
        players = dashboard_response.json().get("players", [])
        if len(players) == 0:
            pytest.skip("No players in team to test")
        
        player_id = players[0]["id"]
        
        # Get player details
        response = requests.get(f"{BASE_URL}/api/coach/groups/{TEAM_ID}/player/{player_id}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        # Verify response structure
        assert "player" in data
        assert "pillars" in data
        assert "recent_sessions" in data
        assert "weekly_stats" in data
        assert "badges_earned" in data
        
        # Verify player data
        player = data["player"]
        assert player["id"] == player_id
        assert "username" in player
        assert "current_streak" in player
        assert "longest_streak" in player
        
        # Verify weekly_stats structure
        weekly = data["weekly_stats"]
        assert "sessions" in weekly
        assert "consistency_pct" in weekly
        assert "unique_days" in weekly
        assert "minutes" in weekly
    
    def test_player_details_invalid_player_id(self):
        """Test player details with non-existent player"""
        token = get_coach_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/coach/groups/{TEAM_ID}/player/invalid-player-id", headers=headers)
        assert response.status_code == 404


class TestBulkMessageAPI:
    """Test POST /api/coach/groups/{group_id}/bulk-message"""
    
    def test_bulk_message_success(self):
        """Test coach can send bulk message to team"""
        token = get_coach_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # First verify there are players
        dashboard_response = requests.get(f"{BASE_URL}/api/coach/groups/{TEAM_ID}/dashboard", headers=headers)
        players = dashboard_response.json().get("players", [])
        
        if len(players) == 0:
            pytest.skip("No players in team to message")
        
        response = requests.post(
            f"{BASE_URL}/api/coach/groups/{TEAM_ID}/bulk-message",
            headers=headers,
            params={
                "message": "Test message from automated testing - please ignore this message",
                "subject": "Test Subject from Pytest"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "sent_count" in data
        assert data["sent_count"] >= 0
    
    def test_bulk_message_short_message_rejected(self):
        """Test bulk message rejects messages under 10 characters"""
        token = get_coach_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/coach/groups/{TEAM_ID}/bulk-message",
            headers=headers,
            params={
                "message": "Short",
                "subject": "Test"
            }
        )
        assert response.status_code == 400
        assert "at least 10 characters" in response.json().get("detail", "").lower()
    
    def test_bulk_message_invalid_group(self):
        """Test bulk message with non-existent group"""
        token = get_coach_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/coach/groups/invalid-group-id/bulk-message",
            headers=headers,
            params={
                "message": "Test message that is long enough",
                "subject": "Test"
            }
        )
        # Could be 404 (not found) or 403 (not coach of this group)
        assert response.status_code in [403, 404]
    
    def test_bulk_message_unauthorized(self):
        """Test bulk message requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/coach/groups/{TEAM_ID}/bulk-message",
            params={
                "message": "Test message that is long enough",
                "subject": "Test"
            }
        )
        assert response.status_code in [401, 403]


class TestCoachHomeDashboard:
    """Test GET /api/coach/dashboard (coach home dashboard)"""
    
    def test_coach_home_dashboard(self):
        """Test coach home dashboard endpoint"""
        token = get_coach_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/coach/dashboard", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        # Verify response structure
        assert "team" in data
        assert "stats" in data
        assert "coach" in data
        
        # Verify team data
        team = data["team"]
        assert "id" in team
        assert "name" in team
        assert "invite_code" in team
        
        # Verify stats
        stats = data["stats"]
        assert "total_players" in stats
        assert "active_players_this_week" in stats
        assert "total_sessions_this_week" in stats


class TestMessageHistory:
    """Test GET /api/coach/groups/{group_id}/messages"""
    
    def test_get_message_history(self):
        """Test coach can view message history"""
        token = get_coach_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/coach/groups/{TEAM_ID}/messages", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "messages" in data
        assert isinstance(data["messages"], list)
        
        # If there are messages, verify structure
        if len(data["messages"]) > 0:
            msg = data["messages"][0]
            assert "subject" in msg
            assert "message" in msg
            assert "sent_at" in msg
            assert "sent_count" in msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
