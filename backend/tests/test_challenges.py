"""
Test suite for Challenge feature endpoints
Tests: GET /api/challenges, GET /api/challenges/my, POST /api/challenges/join, 
       POST /api/challenges/leave/{id}, GET /api/challenges/{id}/leaderboard
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestChallengesAPI:
    """Test suite for Challenge endpoints"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user for challenge testing"""
        unique_id = str(uuid.uuid4())[:8]
        email = f"challengetest_{unique_id}@test.com"
        password = "test123456"
        username = f"ChallengeUser{unique_id}"
        
        # Register user
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": username,
            "password": password,
            "age": 16
        })
        
        if register_response.status_code != 200:
            pytest.skip(f"Failed to create test user: {register_response.text}")
        
        token = register_response.json()["token"]
        user_id = register_response.json()["user_id"]
        
        # Complete onboarding with 3 pillars
        onboarding_response = requests.post(
            f"{BASE_URL}/api/onboarding/complete",
            json={
                "pillars": [
                    {"pillar_name": "Fitness/Training", "weekly_target_sessions": 3},
                    {"pillar_name": "Study/Academics", "weekly_target_sessions": 4},
                    {"pillar_name": "Reading/Learning", "weekly_target_sessions": 2}
                ]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if onboarding_response.status_code != 200:
            pytest.skip(f"Failed to complete onboarding: {onboarding_response.text}")
        
        return {
            "email": email,
            "password": password,
            "username": username,
            "token": token,
            "user_id": user_id
        }
    
    @pytest.fixture(scope="class")
    def auth_headers(self, test_user):
        """Get auth headers for API calls"""
        return {"Authorization": f"Bearer {test_user['token']}"}
    
    # ============ GET /api/challenges Tests ============
    
    def test_get_all_challenges_returns_200(self, auth_headers):
        """Test GET /api/challenges returns 200 and list of challenges"""
        response = requests.get(f"{BASE_URL}/api/challenges", headers=auth_headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Found {len(data)} challenges")
    
    def test_get_challenges_has_required_fields(self, auth_headers):
        """Test that each challenge has required fields"""
        response = requests.get(f"{BASE_URL}/api/challenges", headers=auth_headers)
        
        assert response.status_code == 200
        challenges = response.json()
        
        if len(challenges) > 0:
            challenge = challenges[0]
            required_fields = ['id', 'name', 'description', 'challenge_type', 'metric_type', 
                             'start_date', 'end_date', 'status', 'participant_count', 'is_participating']
            for field in required_fields:
                assert field in challenge, f"Challenge missing required field: {field}"
            print(f"Challenge fields verified: {list(challenge.keys())}")
    
    def test_get_challenges_filter_by_status(self, auth_headers):
        """Test filtering challenges by status"""
        response = requests.get(f"{BASE_URL}/api/challenges?status=active", headers=auth_headers)
        
        assert response.status_code == 200
        challenges = response.json()
        
        for challenge in challenges:
            assert challenge['status'] == 'active', f"Expected active status, got {challenge['status']}"
        print(f"Found {len(challenges)} active challenges")
    
    def test_get_challenges_filter_by_type(self, auth_headers):
        """Test filtering challenges by type (weekly/monthly)"""
        # Test weekly filter
        weekly_response = requests.get(f"{BASE_URL}/api/challenges?challenge_type=weekly", headers=auth_headers)
        assert weekly_response.status_code == 200
        weekly_challenges = weekly_response.json()
        
        for challenge in weekly_challenges:
            assert challenge['challenge_type'] == 'weekly', f"Expected weekly type, got {challenge['challenge_type']}"
        print(f"Found {len(weekly_challenges)} weekly challenges")
        
        # Test monthly filter
        monthly_response = requests.get(f"{BASE_URL}/api/challenges?challenge_type=monthly", headers=auth_headers)
        assert monthly_response.status_code == 200
        monthly_challenges = monthly_response.json()
        
        for challenge in monthly_challenges:
            assert challenge['challenge_type'] == 'monthly', f"Expected monthly type, got {challenge['challenge_type']}"
        print(f"Found {len(monthly_challenges)} monthly challenges")
    
    def test_get_challenges_without_auth_returns_401(self):
        """Test that GET /api/challenges requires authentication"""
        response = requests.get(f"{BASE_URL}/api/challenges")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    # ============ GET /api/challenges/my Tests ============
    
    def test_get_my_challenges_returns_200(self, auth_headers):
        """Test GET /api/challenges/my returns 200"""
        response = requests.get(f"{BASE_URL}/api/challenges/my", headers=auth_headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"User has joined {len(data)} challenges")
    
    def test_get_my_challenges_all_have_is_participating_true(self, auth_headers):
        """Test that all challenges in /my have is_participating=True"""
        response = requests.get(f"{BASE_URL}/api/challenges/my", headers=auth_headers)
        
        assert response.status_code == 200
        challenges = response.json()
        
        for challenge in challenges:
            assert challenge.get('is_participating') == True, "All my challenges should have is_participating=True"
    
    # ============ POST /api/challenges/join Tests ============
    
    def test_join_challenge_success(self, auth_headers, test_user):
        """Test joining an active challenge"""
        # First get list of active challenges
        challenges_response = requests.get(f"{BASE_URL}/api/challenges?status=active", headers=auth_headers)
        assert challenges_response.status_code == 200
        challenges = challenges_response.json()
        
        if len(challenges) == 0:
            pytest.skip("No active challenges available to join")
        
        # Find a challenge user hasn't joined yet
        challenge_to_join = None
        for challenge in challenges:
            if not challenge.get('is_participating'):
                challenge_to_join = challenge
                break
        
        if not challenge_to_join:
            pytest.skip("User has already joined all active challenges")
        
        # Join the challenge
        join_response = requests.post(
            f"{BASE_URL}/api/challenges/join",
            json={"challenge_id": challenge_to_join['id']},
            headers=auth_headers
        )
        
        assert join_response.status_code == 200, f"Expected 200, got {join_response.status_code}: {join_response.text}"
        data = join_response.json()
        assert 'message' in data, "Response should contain message"
        assert 'participant' in data, "Response should contain participant info"
        print(f"Successfully joined challenge: {challenge_to_join['name']}")
        
        # Store challenge_id for later tests
        test_user['joined_challenge_id'] = challenge_to_join['id']
    
    def test_join_challenge_already_joined_returns_400(self, auth_headers, test_user):
        """Test that joining an already joined challenge returns 400"""
        if 'joined_challenge_id' not in test_user:
            pytest.skip("No challenge was joined in previous test")
        
        join_response = requests.post(
            f"{BASE_URL}/api/challenges/join",
            json={"challenge_id": test_user['joined_challenge_id']},
            headers=auth_headers
        )
        
        assert join_response.status_code == 400, f"Expected 400, got {join_response.status_code}"
        assert 'already joined' in join_response.json().get('detail', '').lower()
    
    def test_join_nonexistent_challenge_returns_404(self, auth_headers):
        """Test joining a non-existent challenge returns 404"""
        fake_id = str(uuid.uuid4())
        join_response = requests.post(
            f"{BASE_URL}/api/challenges/join",
            json={"challenge_id": fake_id},
            headers=auth_headers
        )
        
        assert join_response.status_code == 404, f"Expected 404, got {join_response.status_code}"
    
    # ============ GET /api/challenges/{id}/leaderboard Tests ============
    
    def test_get_leaderboard_returns_200(self, auth_headers, test_user):
        """Test GET /api/challenges/{id}/leaderboard returns 200"""
        if 'joined_challenge_id' not in test_user:
            # Get any active challenge
            challenges_response = requests.get(f"{BASE_URL}/api/challenges?status=active", headers=auth_headers)
            if challenges_response.status_code != 200 or len(challenges_response.json()) == 0:
                pytest.skip("No active challenges available")
            challenge_id = challenges_response.json()[0]['id']
        else:
            challenge_id = test_user['joined_challenge_id']
        
        response = requests.get(f"{BASE_URL}/api/challenges/{challenge_id}/leaderboard", headers=auth_headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert 'challenge' in data, "Response should contain challenge info"
        assert 'leaderboard' in data, "Response should contain leaderboard"
        assert 'user_participating' in data, "Response should contain user_participating"
        assert isinstance(data['leaderboard'], list), "Leaderboard should be a list"
        print(f"Leaderboard has {len(data['leaderboard'])} participants")
    
    def test_leaderboard_has_correct_participant_fields(self, auth_headers, test_user):
        """Test that leaderboard participants have required fields"""
        if 'joined_challenge_id' not in test_user:
            pytest.skip("No challenge joined")
        
        response = requests.get(
            f"{BASE_URL}/api/challenges/{test_user['joined_challenge_id']}/leaderboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if len(data['leaderboard']) > 0:
            participant = data['leaderboard'][0]
            required_fields = ['id', 'challenge_id', 'user_id', 'username', 'current_score', 'rank']
            for field in required_fields:
                assert field in participant, f"Participant missing field: {field}"
            print(f"Participant fields verified: {list(participant.keys())}")
    
    def test_leaderboard_user_rank_when_participating(self, auth_headers, test_user):
        """Test that user_rank is returned when user is participating"""
        if 'joined_challenge_id' not in test_user:
            pytest.skip("No challenge joined")
        
        response = requests.get(
            f"{BASE_URL}/api/challenges/{test_user['joined_challenge_id']}/leaderboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['user_participating'] == True, "User should be participating"
        assert data['user_rank'] is not None, "User rank should be returned"
        assert data['user_score'] is not None, "User score should be returned"
        print(f"User rank: {data['user_rank']}, score: {data['user_score']}")
    
    def test_leaderboard_nonexistent_challenge_returns_404(self, auth_headers):
        """Test leaderboard for non-existent challenge returns 404"""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/challenges/{fake_id}/leaderboard", headers=auth_headers)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    # ============ POST /api/challenges/leave/{id} Tests ============
    
    def test_leave_challenge_success(self, auth_headers, test_user):
        """Test leaving a challenge"""
        if 'joined_challenge_id' not in test_user:
            pytest.skip("No challenge joined to leave")
        
        leave_response = requests.post(
            f"{BASE_URL}/api/challenges/leave/{test_user['joined_challenge_id']}",
            headers=auth_headers
        )
        
        assert leave_response.status_code == 200, f"Expected 200, got {leave_response.status_code}: {leave_response.text}"
        data = leave_response.json()
        assert 'message' in data, "Response should contain message"
        print(f"Successfully left challenge")
        
        # Verify user is no longer in the challenge
        my_challenges = requests.get(f"{BASE_URL}/api/challenges/my", headers=auth_headers)
        assert my_challenges.status_code == 200
        
        challenge_ids = [c['id'] for c in my_challenges.json()]
        assert test_user['joined_challenge_id'] not in challenge_ids, "User should no longer be in the challenge"
    
    def test_leave_challenge_not_participating_returns_400(self, auth_headers, test_user):
        """Test leaving a challenge user hasn't joined returns 400"""
        # Get a challenge user hasn't joined
        challenges_response = requests.get(f"{BASE_URL}/api/challenges?status=active", headers=auth_headers)
        if challenges_response.status_code != 200:
            pytest.skip("Could not get challenges")
        
        challenges = challenges_response.json()
        not_joined = [c for c in challenges if not c.get('is_participating')]
        
        if len(not_joined) == 0:
            pytest.skip("User has joined all challenges")
        
        leave_response = requests.post(
            f"{BASE_URL}/api/challenges/leave/{not_joined[0]['id']}",
            headers=auth_headers
        )
        
        assert leave_response.status_code == 400, f"Expected 400, got {leave_response.status_code}"
    
    def test_leave_nonexistent_challenge_returns_404(self, auth_headers):
        """Test leaving a non-existent challenge returns 404"""
        fake_id = str(uuid.uuid4())
        leave_response = requests.post(
            f"{BASE_URL}/api/challenges/leave/{fake_id}",
            headers=auth_headers
        )
        
        assert leave_response.status_code == 404, f"Expected 404, got {leave_response.status_code}"


class TestChallengeScoreCalculation:
    """Test challenge score calculation based on metric types"""
    
    @pytest.fixture(scope="class")
    def test_user_with_sessions(self):
        """Create a test user with some sessions for score testing"""
        unique_id = str(uuid.uuid4())[:8]
        email = f"challengescore_{unique_id}@test.com"
        password = "test123456"
        username = f"ScoreUser{unique_id}"
        
        # Register user
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": username,
            "password": password,
            "age": 17
        })
        
        if register_response.status_code != 200:
            pytest.skip(f"Failed to create test user: {register_response.text}")
        
        token = register_response.json()["token"]
        user_id = register_response.json()["user_id"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Complete onboarding
        requests.post(
            f"{BASE_URL}/api/onboarding/complete",
            json={
                "pillars": [
                    {"pillar_name": "Fitness/Training", "weekly_target_sessions": 3},
                    {"pillar_name": "Study/Academics", "weekly_target_sessions": 4},
                    {"pillar_name": "Reading/Learning", "weekly_target_sessions": 2}
                ]
            },
            headers=headers
        )
        
        # Log some sessions
        today = datetime.now().strftime('%Y-%m-%d')
        sessions_to_log = [
            {"pillar": "Fitness/Training", "minutes_spent": 45, "local_date": today},
            {"pillar": "Fitness/Training", "minutes_spent": 30, "local_date": today},
            {"pillar": "Study/Academics", "minutes_spent": 60, "local_date": today},
        ]
        
        for session in sessions_to_log:
            requests.post(f"{BASE_URL}/api/sessions/complete", json=session, headers=headers)
        
        return {
            "email": email,
            "token": token,
            "user_id": user_id,
            "headers": headers
        }
    
    def test_score_updates_after_joining(self, test_user_with_sessions):
        """Test that score is calculated when joining a challenge"""
        headers = test_user_with_sessions['headers']
        
        # Get active challenges
        challenges_response = requests.get(f"{BASE_URL}/api/challenges?status=active", headers=headers)
        if challenges_response.status_code != 200 or len(challenges_response.json()) == 0:
            pytest.skip("No active challenges")
        
        challenges = challenges_response.json()
        not_joined = [c for c in challenges if not c.get('is_participating')]
        
        if len(not_joined) == 0:
            pytest.skip("User has joined all challenges")
        
        challenge = not_joined[0]
        
        # Join the challenge
        join_response = requests.post(
            f"{BASE_URL}/api/challenges/join",
            json={"challenge_id": challenge['id']},
            headers=headers
        )
        
        assert join_response.status_code == 200
        participant = join_response.json().get('participant', {})
        
        # Score should be calculated based on existing sessions
        print(f"Challenge metric: {challenge['metric_type']}, Initial score: {participant.get('current_score', 0)}")
        
        # Leave the challenge for cleanup
        requests.post(f"{BASE_URL}/api/challenges/leave/{challenge['id']}", headers=headers)


class TestChallengeDataIntegrity:
    """Test data integrity for challenges"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Create a test user and get auth headers"""
        unique_id = str(uuid.uuid4())[:8]
        email = f"challengedata_{unique_id}@test.com"
        
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": f"DataUser{unique_id}",
            "password": "test123456",
            "age": 15
        })
        
        if register_response.status_code != 200:
            pytest.skip("Failed to create test user")
        
        token = register_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Complete onboarding
        requests.post(
            f"{BASE_URL}/api/onboarding/complete",
            json={
                "pillars": [
                    {"pillar_name": "Fitness/Training", "weekly_target_sessions": 3},
                    {"pillar_name": "Study/Academics", "weekly_target_sessions": 4},
                    {"pillar_name": "Skill Development", "weekly_target_sessions": 2}
                ]
            },
            headers=headers
        )
        
        return headers
    
    def test_participant_count_increases_on_join(self, auth_headers):
        """Test that participant_count increases when joining"""
        # Get active challenges
        challenges_response = requests.get(f"{BASE_URL}/api/challenges?status=active", headers=auth_headers)
        if challenges_response.status_code != 200 or len(challenges_response.json()) == 0:
            pytest.skip("No active challenges")
        
        challenges = challenges_response.json()
        not_joined = [c for c in challenges if not c.get('is_participating')]
        
        if len(not_joined) == 0:
            pytest.skip("User has joined all challenges")
        
        challenge = not_joined[0]
        initial_count = challenge['participant_count']
        
        # Join
        join_response = requests.post(
            f"{BASE_URL}/api/challenges/join",
            json={"challenge_id": challenge['id']},
            headers=auth_headers
        )
        assert join_response.status_code == 200
        
        # Check count increased
        updated_challenges = requests.get(f"{BASE_URL}/api/challenges?status=active", headers=auth_headers)
        updated_challenge = next((c for c in updated_challenges.json() if c['id'] == challenge['id']), None)
        
        assert updated_challenge is not None
        assert updated_challenge['participant_count'] == initial_count + 1, \
            f"Expected count {initial_count + 1}, got {updated_challenge['participant_count']}"
        print(f"Participant count increased from {initial_count} to {updated_challenge['participant_count']}")
        
        # Leave for cleanup
        requests.post(f"{BASE_URL}/api/challenges/leave/{challenge['id']}", headers=auth_headers)
    
    def test_participant_count_decreases_on_leave(self, auth_headers):
        """Test that participant_count decreases when leaving"""
        # Get active challenges
        challenges_response = requests.get(f"{BASE_URL}/api/challenges?status=active", headers=auth_headers)
        if challenges_response.status_code != 200 or len(challenges_response.json()) == 0:
            pytest.skip("No active challenges")
        
        challenges = challenges_response.json()
        not_joined = [c for c in challenges if not c.get('is_participating')]
        
        if len(not_joined) == 0:
            pytest.skip("User has joined all challenges")
        
        challenge = not_joined[0]
        
        # Join first
        requests.post(
            f"{BASE_URL}/api/challenges/join",
            json={"challenge_id": challenge['id']},
            headers=auth_headers
        )
        
        # Get count after joining
        updated_challenges = requests.get(f"{BASE_URL}/api/challenges?status=active", headers=auth_headers)
        joined_challenge = next((c for c in updated_challenges.json() if c['id'] == challenge['id']), None)
        count_after_join = joined_challenge['participant_count']
        
        # Leave
        leave_response = requests.post(
            f"{BASE_URL}/api/challenges/leave/{challenge['id']}",
            headers=auth_headers
        )
        assert leave_response.status_code == 200
        
        # Check count decreased
        final_challenges = requests.get(f"{BASE_URL}/api/challenges?status=active", headers=auth_headers)
        final_challenge = next((c for c in final_challenges.json() if c['id'] == challenge['id']), None)
        
        assert final_challenge is not None
        assert final_challenge['participant_count'] == count_after_join - 1, \
            f"Expected count {count_after_join - 1}, got {final_challenge['participant_count']}"
        print(f"Participant count decreased from {count_after_join} to {final_challenge['participant_count']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
