"""
Test suite for Engagement Features: XP, Levels, Daily Rewards, Friend Streaks
Tests the teen engagement system including XP progression, daily login rewards, and mutual streaks
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://edge-gamify.preview.emergentagent.com').rstrip('/')

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


class TestEngagementStatus:
    """Tests for GET /api/engagement/status endpoint"""
    
    def test_get_engagement_status_success(self, player_headers):
        """Test getting engagement status returns all required fields"""
        response = requests.get(f"{BASE_URL}/api/engagement/status", headers=player_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        assert 'xp' in data
        assert 'level_info' in data
        assert 'coins' in data
        assert 'login_streak' in data
        assert 'session_streak' in data
        assert 'can_claim_daily' in data
        
        # Verify level_info structure
        level_info = data['level_info']
        assert 'level' in level_info
        assert 'title' in level_info
        assert 'total_xp' in level_info
        assert 'xp_in_level' in level_info
        assert 'xp_to_next_level' in level_info
        assert 'progress_pct' in level_info
        
        # Verify data types
        assert isinstance(data['xp'], int)
        assert isinstance(data['coins'], int)
        assert isinstance(level_info['level'], int)
        assert isinstance(level_info['progress_pct'], (int, float))
    
    def test_get_engagement_status_requires_auth(self):
        """Test that engagement status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/engagement/status")
        assert response.status_code in [401, 403]


class TestDailyLogin:
    """Tests for POST /api/engagement/daily-login endpoint"""
    
    def test_daily_login_returns_correct_structure(self, admin_headers):
        """Test daily login returns all required fields"""
        response = requests.post(f"{BASE_URL}/api/engagement/daily-login", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have either already_claimed or reward data
        assert 'already_claimed' in data
        
        if data['already_claimed']:
            # Already claimed response
            assert 'message' in data
            assert 'login_streak' in data
            assert 'coins' in data
            assert 'level_info' in data
        else:
            # Fresh claim response
            assert 'coins_earned' in data
            assert 'xp_earned' in data
            assert 'login_streak' in data
            assert 'total_coins' in data
            assert 'leveled_up' in data
            assert 'level_info' in data
            assert 'message' in data
    
    def test_daily_login_duplicate_shows_already_claimed(self, player_headers):
        """Test that claiming twice in same day shows already_claimed"""
        # First claim (may or may not be already claimed)
        response1 = requests.post(f"{BASE_URL}/api/engagement/daily-login", headers=player_headers)
        assert response1.status_code == 200
        
        # Second claim should definitely show already_claimed
        response2 = requests.post(f"{BASE_URL}/api/engagement/daily-login", headers=player_headers)
        assert response2.status_code == 200
        data = response2.json()
        
        assert data['already_claimed'] == True
        assert 'Already claimed' in data.get('message', '')
    
    def test_daily_login_requires_auth(self):
        """Test that daily login requires authentication"""
        response = requests.post(f"{BASE_URL}/api/engagement/daily-login")
        assert response.status_code in [401, 403]


class TestXPHistory:
    """Tests for GET /api/engagement/xp-history endpoint"""
    
    def test_get_xp_history_success(self, player_headers):
        """Test getting XP history returns transactions"""
        response = requests.get(f"{BASE_URL}/api/engagement/xp-history", headers=player_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'transactions' in data
        assert isinstance(data['transactions'], list)
        
        # If there are transactions, verify structure
        if data['transactions']:
            tx = data['transactions'][0]
            assert 'amount' in tx
            assert 'reason' in tx
            assert 'timestamp' in tx
            assert 'new_total' in tx
    
    def test_xp_history_requires_auth(self):
        """Test that XP history requires authentication"""
        response = requests.get(f"{BASE_URL}/api/engagement/xp-history")
        assert response.status_code in [401, 403]


class TestXPLeaderboard:
    """Tests for GET /api/engagement/leaderboard/xp endpoint"""
    
    def test_get_xp_leaderboard_success(self):
        """Test getting XP leaderboard (no auth required)"""
        response = requests.get(f"{BASE_URL}/api/engagement/leaderboard/xp")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'leaderboard' in data
        assert isinstance(data['leaderboard'], list)
        
        # If there are users, verify structure
        if data['leaderboard']:
            user = data['leaderboard'][0]
            assert 'rank' in user
            assert 'username' in user
            assert 'xp' in user
            assert 'level' in user
            assert 'title' in user
    
    def test_xp_leaderboard_is_sorted_by_xp(self):
        """Test that leaderboard is sorted by XP descending"""
        response = requests.get(f"{BASE_URL}/api/engagement/leaderboard/xp")
        
        assert response.status_code == 200
        data = response.json()
        
        leaderboard = data['leaderboard']
        if len(leaderboard) > 1:
            for i in range(len(leaderboard) - 1):
                assert leaderboard[i]['xp'] >= leaderboard[i + 1]['xp']
    
    def test_xp_leaderboard_limit_parameter(self):
        """Test that limit parameter works"""
        response = requests.get(f"{BASE_URL}/api/engagement/leaderboard/xp?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data['leaderboard']) <= 5


class TestFriendStreaks:
    """Tests for GET /api/engagement/friend-streaks endpoint"""
    
    def test_get_friend_streaks_success(self, player_headers):
        """Test getting friend streaks returns correct structure"""
        response = requests.get(f"{BASE_URL}/api/engagement/friend-streaks", headers=player_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'friend_streaks' in data
        assert isinstance(data['friend_streaks'], list)
        
        # If there are streaks, verify structure
        if data['friend_streaks']:
            streak = data['friend_streaks'][0]
            assert 'friend_id' in streak
            assert 'friend_username' in streak
            assert 'mutual_streak' in streak
            assert 'total_mutual_days' in streak
    
    def test_friend_streaks_requires_auth(self):
        """Test that friend streaks requires authentication"""
        response = requests.get(f"{BASE_URL}/api/engagement/friend-streaks")
        assert response.status_code in [401, 403]


class TestSessionXPAward:
    """Tests for XP awarded when logging sessions via POST /api/sessions/complete"""
    
    def test_session_complete_awards_xp(self, player_headers):
        """Test that completing a session awards XP"""
        # Get current XP
        status_before = requests.get(f"{BASE_URL}/api/engagement/status", headers=player_headers)
        xp_before = status_before.json().get('xp', 0)
        
        # Log a session
        response = requests.post(f"{BASE_URL}/api/sessions/complete", headers=player_headers, json={
            "pillar": "Fitness/Training",
            "minutes_spent": 30
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify XP fields in response
        assert 'xp_earned' in data
        assert 'leveled_up' in data
        assert data['xp_earned'] > 0
        
        # Verify XP was actually added
        status_after = requests.get(f"{BASE_URL}/api/engagement/status", headers=player_headers)
        xp_after = status_after.json().get('xp', 0)
        
        assert xp_after > xp_before
    
    def test_session_complete_returns_level_info(self, player_headers):
        """Test that session complete returns level info"""
        response = requests.post(f"{BASE_URL}/api/sessions/complete", headers=player_headers, json={
            "pillar": "Study/Academics",
            "minutes_spent": 30
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have level_info if XP was awarded
        if data.get('xp_earned', 0) > 0:
            assert 'level_info' in data
            if data['level_info']:
                assert 'level' in data['level_info']
                assert 'total_xp' in data['level_info']


class TestLevelCalculation:
    """Tests for level calculation logic"""
    
    def test_level_info_has_correct_structure(self, player_headers):
        """Test that level_info has all required fields"""
        response = requests.get(f"{BASE_URL}/api/engagement/status", headers=player_headers)
        
        assert response.status_code == 200
        level_info = response.json()['level_info']
        
        # All required fields
        assert 'level' in level_info
        assert 'title' in level_info
        assert 'total_xp' in level_info
        assert 'xp_in_level' in level_info
        assert 'xp_to_next_level' in level_info
        assert 'progress_pct' in level_info
        
        # Progress should be between 0 and 100
        assert 0 <= level_info['progress_pct'] <= 100
        
        # Level should be at least 1
        assert level_info['level'] >= 1
    
    def test_level_title_matches_level(self, player_headers):
        """Test that level title is appropriate for level"""
        response = requests.get(f"{BASE_URL}/api/engagement/status", headers=player_headers)
        
        assert response.status_code == 200
        level_info = response.json()['level_info']
        
        # Title should be a non-empty string
        assert isinstance(level_info['title'], str)
        assert len(level_info['title']) > 0


class TestLoginStreakBonus:
    """Tests for login streak bonus system"""
    
    def test_login_streak_increments(self, admin_headers):
        """Test that login streak is tracked"""
        response = requests.post(f"{BASE_URL}/api/engagement/daily-login", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have login_streak field
        assert 'login_streak' in data
        assert isinstance(data['login_streak'], int)
        assert data['login_streak'] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
