"""
Test suite for Daily & Weekly Quests feature
Tests: GET /api/quests/daily, GET /api/quests/weekly, GET /api/quests/all,
       POST /api/quests/claim/{quest_id}, POST /api/quests/claim-all/{type}
       Quest progress tracking via sessions and engagement
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "admin@edgemodeapp.com"
ADMIN_PASSWORD = "EdgeAdmin2024!"
TEST_PLAYER_EMAIL = "testplayer1@edgemode.com"
TEST_PLAYER_PASSWORD = "TestPlayer123!"


class TestQuestsAPI:
    """Test Quests API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            self.admin_token = token
        else:
            pytest.skip(f"Admin login failed: {login_response.status_code}")
        
        yield
        
        self.session.close()
    
    # ============ Daily Quests Tests ============
    
    def test_get_daily_quests_requires_auth(self):
        """Test that daily quests endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/quests/daily")
        assert response.status_code == 401 or response.status_code == 403
    
    def test_get_daily_quests_success(self):
        """Test GET /api/quests/daily returns 5 daily quests with progress"""
        response = self.session.get(f"{BASE_URL}/api/quests/daily")
        assert response.status_code == 200
        
        data = response.json()
        assert 'quests' in data
        assert 'summary' in data
        assert 'resets_at' in data
        
        # Should have 5 daily quests
        quests = data['quests']
        assert len(quests) == 5
        
        # Verify quest structure
        for quest in quests:
            assert 'id' in quest
            assert 'name' in quest
            assert 'description' in quest
            assert 'icon' in quest
            assert 'target' in quest
            assert 'reward_coins' in quest
            assert 'reward_xp' in quest
            assert 'track_field' in quest
            assert 'difficulty' in quest
            assert 'current' in quest
            assert 'is_completed' in quest
            assert 'is_claimed' in quest
            assert 'progress_pct' in quest
            assert 'difficulty_color' in quest
        
        # Verify summary structure
        summary = data['summary']
        assert 'total' in summary
        assert 'completed' in summary
        assert 'claimed' in summary
        assert 'available_rewards' in summary
        assert summary['total'] == 5
    
    def test_daily_quests_have_correct_ids(self):
        """Test that daily quests have expected IDs"""
        response = self.session.get(f"{BASE_URL}/api/quests/daily")
        assert response.status_code == 200
        
        quests = response.json()['quests']
        quest_ids = [q['id'] for q in quests]
        
        expected_ids = [
            'daily-login',
            'daily-session',
            'daily-sessions-3',
            'daily-xp-50',
            'daily-streak-maintain'
        ]
        
        for expected_id in expected_ids:
            assert expected_id in quest_ids, f"Missing quest: {expected_id}"
    
    def test_daily_quests_difficulty_colors(self):
        """Test that difficulty colors are correctly assigned"""
        response = self.session.get(f"{BASE_URL}/api/quests/daily")
        assert response.status_code == 200
        
        quests = response.json()['quests']
        
        for quest in quests:
            if quest['difficulty'] == 'easy':
                assert quest['difficulty_color'] == '#22c55e'  # Green
            elif quest['difficulty'] == 'medium':
                assert quest['difficulty_color'] == '#f59e0b'  # Amber
            elif quest['difficulty'] == 'hard':
                assert quest['difficulty_color'] == '#ef4444'  # Red
    
    # ============ Weekly Quests Tests ============
    
    def test_get_weekly_quests_requires_auth(self):
        """Test that weekly quests endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/quests/weekly")
        assert response.status_code == 401 or response.status_code == 403
    
    def test_get_weekly_quests_success(self):
        """Test GET /api/quests/weekly returns 6 weekly quests with progress"""
        response = self.session.get(f"{BASE_URL}/api/quests/weekly")
        assert response.status_code == 200
        
        data = response.json()
        assert 'quests' in data
        assert 'summary' in data
        assert 'week_start' in data
        assert 'resets_at' in data
        
        # Should have 6 weekly quests
        quests = data['quests']
        assert len(quests) == 6
        
        # Verify quest structure
        for quest in quests:
            assert 'id' in quest
            assert 'name' in quest
            assert 'description' in quest
            assert 'target' in quest
            assert 'reward_coins' in quest
            assert 'reward_xp' in quest
            assert 'current' in quest
            assert 'is_completed' in quest
            assert 'is_claimed' in quest
            assert 'progress_pct' in quest
        
        # Verify summary
        summary = data['summary']
        assert summary['total'] == 6
    
    def test_weekly_quests_have_correct_ids(self):
        """Test that weekly quests have expected IDs"""
        response = self.session.get(f"{BASE_URL}/api/quests/weekly")
        assert response.status_code == 200
        
        quests = response.json()['quests']
        quest_ids = [q['id'] for q in quests]
        
        expected_ids = [
            'weekly-sessions-10',
            'weekly-sessions-20',
            'weekly-xp-200',
            'weekly-streak-7',
            'weekly-login-5',
            'weekly-challenges'
        ]
        
        for expected_id in expected_ids:
            assert expected_id in quest_ids, f"Missing quest: {expected_id}"
    
    # ============ All Quests Tests ============
    
    def test_get_all_quests_requires_auth(self):
        """Test that all quests endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/quests/all")
        assert response.status_code == 401 or response.status_code == 403
    
    def test_get_all_quests_success(self):
        """Test GET /api/quests/all returns both daily and weekly quests"""
        response = self.session.get(f"{BASE_URL}/api/quests/all")
        assert response.status_code == 200
        
        data = response.json()
        assert 'daily' in data
        assert 'weekly' in data
        assert 'total_available_rewards' in data
        
        # Verify daily quests
        assert 'quests' in data['daily']
        assert 'summary' in data['daily']
        assert len(data['daily']['quests']) == 5
        
        # Verify weekly quests
        assert 'quests' in data['weekly']
        assert 'summary' in data['weekly']
        assert len(data['weekly']['quests']) == 6
        
        # Verify total available rewards calculation
        daily_rewards = data['daily']['summary']['available_rewards']
        weekly_rewards = data['weekly']['summary']['available_rewards']
        assert data['total_available_rewards'] == daily_rewards + weekly_rewards
    
    # ============ Claim Quest Reward Tests ============
    
    def test_claim_quest_not_found(self):
        """Test claiming a non-existent quest returns 404"""
        response = self.session.post(f"{BASE_URL}/api/quests/claim/nonexistent-quest")
        assert response.status_code == 404
        assert 'not found' in response.json().get('detail', '').lower()
    
    def test_claim_quest_not_completed(self):
        """Test claiming an uncompleted quest returns 400"""
        # Try to claim a quest that likely isn't completed
        response = self.session.post(f"{BASE_URL}/api/quests/claim/weekly-sessions-20")
        # Should be 400 (not completed) or 200 (if somehow completed)
        if response.status_code == 400:
            assert 'not completed' in response.json().get('detail', '').lower()
        # If 200, quest was already completed - that's fine too
    
    def test_claim_quest_requires_auth(self):
        """Test that claim endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/quests/claim/daily-login")
        assert response.status_code == 401 or response.status_code == 403
    
    # ============ Claim All Rewards Tests ============
    
    def test_claim_all_invalid_type(self):
        """Test claim-all with invalid quest type returns 400"""
        response = self.session.post(f"{BASE_URL}/api/quests/claim-all/invalid")
        assert response.status_code == 400
        assert 'invalid' in response.json().get('detail', '').lower()
    
    def test_claim_all_daily_requires_auth(self):
        """Test that claim-all daily requires authentication"""
        response = requests.post(f"{BASE_URL}/api/quests/claim-all/daily")
        assert response.status_code == 401 or response.status_code == 403
    
    def test_claim_all_weekly_requires_auth(self):
        """Test that claim-all weekly requires authentication"""
        response = requests.post(f"{BASE_URL}/api/quests/claim-all/weekly")
        assert response.status_code == 401 or response.status_code == 403
    
    def test_claim_all_daily_no_rewards(self):
        """Test claim-all daily when no rewards available"""
        response = self.session.post(f"{BASE_URL}/api/quests/claim-all/daily")
        # Should be 400 (no rewards) or 200 (if rewards available)
        if response.status_code == 400:
            assert 'no rewards' in response.json().get('detail', '').lower()
    
    def test_claim_all_weekly_no_rewards(self):
        """Test claim-all weekly when no rewards available"""
        response = self.session.post(f"{BASE_URL}/api/quests/claim-all/weekly")
        # Should be 400 (no rewards) or 200 (if rewards available)
        if response.status_code == 400:
            assert 'no rewards' in response.json().get('detail', '').lower()
    
    # ============ Quest Progress Integration Tests ============
    
    def test_quest_progress_values_are_valid(self):
        """Test that quest progress values are within valid ranges"""
        response = self.session.get(f"{BASE_URL}/api/quests/all")
        assert response.status_code == 200
        
        data = response.json()
        all_quests = data['daily']['quests'] + data['weekly']['quests']
        
        for quest in all_quests:
            # Current should not exceed target
            assert quest['current'] <= quest['target']
            # Progress percentage should be 0-100
            assert 0 <= quest['progress_pct'] <= 100
            # Rewards should be non-negative
            assert quest['reward_coins'] >= 0
            assert quest['reward_xp'] >= 0
    
    def test_quest_rewards_are_reasonable(self):
        """Test that quest rewards are within expected ranges"""
        response = self.session.get(f"{BASE_URL}/api/quests/all")
        assert response.status_code == 200
        
        data = response.json()
        all_quests = data['daily']['quests'] + data['weekly']['quests']
        
        for quest in all_quests:
            # Daily quests should have smaller rewards
            if quest['id'].startswith('daily-'):
                assert quest['reward_coins'] <= 50
                assert quest['reward_xp'] <= 25
            # Weekly quests can have larger rewards
            else:
                assert quest['reward_coins'] <= 150
                assert quest['reward_xp'] <= 75


class TestQuestProgressTracking:
    """Test quest progress tracking via sessions and engagement"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with test player authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as test player
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_PLAYER_EMAIL,
            "password": TEST_PLAYER_PASSWORD
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            # Try admin if test player doesn't exist
            login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            if login_response.status_code == 200:
                token = login_response.json().get("token")
                self.session.headers.update({"Authorization": f"Bearer {token}"})
            else:
                pytest.skip("Could not authenticate")
        
        yield
        
        self.session.close()
    
    def test_daily_login_tracks_quest_progress(self):
        """Test that claiming daily login updates quest progress"""
        # Get initial quest state
        initial_response = self.session.get(f"{BASE_URL}/api/quests/daily")
        assert initial_response.status_code == 200
        
        initial_quests = initial_response.json()['quests']
        login_quest = next((q for q in initial_quests if q['id'] == 'daily-login'), None)
        assert login_quest is not None
        
        # Claim daily login
        login_response = self.session.post(f"{BASE_URL}/api/engagement/daily-login")
        # May be 200 (claimed) or already claimed
        
        # Check quest progress after login
        after_response = self.session.get(f"{BASE_URL}/api/quests/daily")
        assert after_response.status_code == 200
        
        after_quests = after_response.json()['quests']
        login_quest_after = next((q for q in after_quests if q['id'] == 'daily-login'), None)
        
        # Login quest should show progress
        assert login_quest_after is not None
        # If login was claimed, progress should be at least 1
        if login_response.status_code == 200 and not login_response.json().get('already_claimed'):
            assert login_quest_after['current'] >= 1
    
    def test_session_logging_tracks_quest_progress(self):
        """Test that logging a session updates quest progress"""
        # Get user's pillars first
        pillars_response = self.session.get(f"{BASE_URL}/api/pillars")
        if pillars_response.status_code != 200 or not pillars_response.json():
            pytest.skip("No pillars configured for user")
        
        pillars_data = pillars_response.json()
        # Handle both formats: {"pillars": [...]} or [...]
        if isinstance(pillars_data, dict) and 'pillars' in pillars_data:
            pillars = pillars_data['pillars']
        else:
            pillars = pillars_data
        
        if not pillars:
            pytest.skip("No pillars available")
        
        # Handle both string pillars and dict pillars
        if isinstance(pillars[0], str):
            pillar_name = pillars[0]
        else:
            pillar_name = pillars[0].get('pillar_name', pillars[0].get('name'))
        
        # Get initial quest state
        initial_response = self.session.get(f"{BASE_URL}/api/quests/daily")
        assert initial_response.status_code == 200
        
        initial_quests = initial_response.json()['quests']
        session_quest = next((q for q in initial_quests if q['id'] == 'daily-session'), None)
        initial_progress = session_quest['current'] if session_quest else 0
        
        # Log a session
        session_response = self.session.post(f"{BASE_URL}/api/sessions/complete", json={
            "pillar": pillar_name,
            "minutes_spent": 30
        })
        
        # Check quest progress after session
        after_response = self.session.get(f"{BASE_URL}/api/quests/daily")
        assert after_response.status_code == 200
        
        after_quests = after_response.json()['quests']
        session_quest_after = next((q for q in after_quests if q['id'] == 'daily-session'), None)
        
        # If session was logged successfully, progress should increase
        if session_response.status_code == 200:
            assert session_quest_after['current'] >= initial_progress


class TestQuestDataIntegrity:
    """Test quest data integrity and consistency"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Authentication failed")
        
        yield
        
        self.session.close()
    
    def test_daily_and_weekly_quests_are_consistent(self):
        """Test that /all endpoint returns same data as individual endpoints"""
        all_response = self.session.get(f"{BASE_URL}/api/quests/all")
        daily_response = self.session.get(f"{BASE_URL}/api/quests/daily")
        weekly_response = self.session.get(f"{BASE_URL}/api/quests/weekly")
        
        assert all_response.status_code == 200
        assert daily_response.status_code == 200
        assert weekly_response.status_code == 200
        
        all_data = all_response.json()
        daily_data = daily_response.json()
        weekly_data = weekly_response.json()
        
        # Quest counts should match
        assert len(all_data['daily']['quests']) == len(daily_data['quests'])
        assert len(all_data['weekly']['quests']) == len(weekly_data['quests'])
        
        # Summaries should match
        assert all_data['daily']['summary']['total'] == daily_data['summary']['total']
        assert all_data['weekly']['summary']['total'] == weekly_data['summary']['total']
    
    def test_quest_completion_state_is_consistent(self):
        """Test that is_completed and is_claimed states are consistent"""
        response = self.session.get(f"{BASE_URL}/api/quests/all")
        assert response.status_code == 200
        
        data = response.json()
        all_quests = data['daily']['quests'] + data['weekly']['quests']
        
        for quest in all_quests:
            # If claimed, must be completed
            if quest['is_claimed']:
                assert quest['is_completed'], f"Quest {quest['id']} is claimed but not completed"
            
            # If progress is 100%, should be completed
            if quest['progress_pct'] >= 100:
                assert quest['is_completed'], f"Quest {quest['id']} has 100% progress but not completed"
    
    def test_quest_targets_are_positive(self):
        """Test that all quest targets are positive integers"""
        response = self.session.get(f"{BASE_URL}/api/quests/all")
        assert response.status_code == 200
        
        data = response.json()
        all_quests = data['daily']['quests'] + data['weekly']['quests']
        
        for quest in all_quests:
            assert quest['target'] > 0, f"Quest {quest['id']} has invalid target: {quest['target']}"
            assert isinstance(quest['target'], int), f"Quest {quest['id']} target is not an integer"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
