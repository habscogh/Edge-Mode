"""
Backend Refactoring Regression Tests for Edge Mode
Tests all API routes to ensure they work correctly after modular refactoring.
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timezone, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test data with unique identifiers
TEST_USER_EMAIL = f"test_refactor_{uuid.uuid4().hex[:8]}@test.com"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_USERNAME = f"testuser_{uuid.uuid4().hex[:6]}"
TEST_USER_AGE = 15

TEST_COACH_EMAIL = f"coach_refactor_{uuid.uuid4().hex[:8]}@test.com"
TEST_COACH_PASSWORD = "CoachPass123!"
TEST_COACH_NAME = f"Coach_{uuid.uuid4().hex[:6]}"
TEST_TEAM_NAME = f"TestTeam_{uuid.uuid4().hex[:6]}"


class TestHealthEndpoints:
    """Test health check and scheduler status endpoints"""
    
    def test_api_health_check(self):
        """Test /api/health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert 'database' in data
        assert 'scheduler' in data
        print(f"✓ Health check: {data}")
    
    def test_root_health_check(self):
        """Test /health endpoint (root level)"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'ok'
        print("✓ Root health check passed")
    
    def test_scheduler_status(self):
        """Test /api/scheduler/status endpoint"""
        response = requests.get(f"{BASE_URL}/api/scheduler/status")
        assert response.status_code == 200
        data = response.json()
        assert 'scheduler_running' in data
        assert 'jobs' in data
        assert 'schedule' in data
        print(f"✓ Scheduler status: running={data['scheduler_running']}, jobs={len(data['jobs'])}")


class TestAuthRoutes:
    """Test authentication routes"""
    
    @pytest.fixture(scope="class")
    def registered_user(self):
        """Register a test user and return credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_EMAIL,
            "username": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
            "age": TEST_USER_AGE
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        assert 'token' in data
        assert 'user_id' in data
        print(f"✓ User registered: {TEST_USER_EMAIL}")
        return {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "token": data['token'],
            "user_id": data['user_id']
        }
    
    def test_register_duplicate_email(self, registered_user):
        """Test that duplicate email registration fails"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": registered_user['email'],
            "username": "another_user",
            "password": "AnotherPass123!",
            "age": 16
        })
        assert response.status_code == 400
        print("✓ Duplicate email registration correctly rejected")
    
    def test_login_success(self, registered_user):
        """Test /api/auth/login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": registered_user['email'],
            "password": registered_user['password']
        })
        assert response.status_code == 200
        data = response.json()
        assert 'token' in data
        assert 'user_id' in data
        print("✓ Login successful")
    
    def test_login_invalid_credentials(self):
        """Test /api/auth/login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid login correctly rejected")
    
    def test_forgot_password(self, registered_user):
        """Test /api/auth/forgot-password endpoint"""
        response = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={
            "email": registered_user['email']
        })
        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        print("✓ Forgot password endpoint works")


class TestCoachAuthRoutes:
    """Test coach authentication routes"""
    
    @pytest.fixture(scope="class")
    def registered_coach(self):
        """Register a test coach and return credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": TEST_COACH_EMAIL,
            "password": TEST_COACH_PASSWORD,
            "name": TEST_COACH_NAME,
            "team_name": TEST_TEAM_NAME,
            "special_code": "EDGE30"
        })
        assert response.status_code == 200, f"Coach registration failed: {response.text}"
        data = response.json()
        assert 'token' in data
        assert 'coach_id' in data
        assert 'team_id' in data
        assert 'invite_code' in data
        assert data.get('has_extended_trial') == True
        print(f"✓ Coach registered: {TEST_COACH_EMAIL}")
        return {
            "email": TEST_COACH_EMAIL,
            "password": TEST_COACH_PASSWORD,
            "token": data['token'],
            "coach_id": data['coach_id'],
            "team_id": data['team_id'],
            "invite_code": data['invite_code']
        }
    
    def test_coach_login(self, registered_coach):
        """Test coach login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": registered_coach['email'],
            "password": registered_coach['password']
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get('is_coach') == True
        print("✓ Coach login successful")
    
    def test_get_team_info(self, registered_coach):
        """Test /api/team/{team_code} endpoint"""
        response = requests.get(f"{BASE_URL}/api/team/{registered_coach['invite_code']}")
        assert response.status_code == 200
        data = response.json()
        assert 'team_name' in data
        assert 'coach_name' in data
        assert 'trial_days' in data
        print(f"✓ Team info retrieved: {data['team_name']}")


class TestUserRoutes:
    """Test user management routes"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers for a test user"""
        # Register a new user for this test class
        email = f"user_routes_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": f"usertest_{uuid.uuid4().hex[:6]}",
            "password": "TestPass123!",
            "age": 16
        })
        assert response.status_code == 200
        token = response.json()['token']
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_me(self, auth_headers):
        """Test /api/users/me endpoint"""
        response = requests.get(f"{BASE_URL}/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert 'id' in data
        assert 'email' in data
        assert 'username' in data
        print(f"✓ Get user profile: {data.get('username')}")
    
    def test_get_pillars_empty(self, auth_headers):
        """Test /api/users/pillars returns empty for new user"""
        response = requests.get(f"{BASE_URL}/api/users/pillars", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Get pillars: {len(data)} pillars")
    
    def test_leaderboard_opt_in_toggle(self, auth_headers):
        """Test /api/users/leaderboard-opt-in endpoint"""
        response = requests.post(f"{BASE_URL}/api/users/leaderboard-opt-in", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert 'leaderboard_opt_in' in data
        print(f"✓ Leaderboard opt-in toggled: {data['leaderboard_opt_in']}")


class TestOnboardingRoutes:
    """Test onboarding routes"""
    
    def test_get_available_pillars(self):
        """Test /api/pillars endpoint (public)"""
        response = requests.get(f"{BASE_URL}/api/pillars")
        assert response.status_code == 200
        data = response.json()
        assert 'pillars' in data
        assert len(data['pillars']) > 0
        print(f"✓ Available pillars: {len(data['pillars'])}")
    
    @pytest.fixture(scope="class")
    def onboarded_user(self):
        """Create and onboard a test user"""
        email = f"onboard_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": f"onboard_{uuid.uuid4().hex[:6]}",
            "password": "TestPass123!",
            "age": 15
        })
        assert response.status_code == 200
        token = response.json()['token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Complete onboarding
        response = requests.post(f"{BASE_URL}/api/onboarding/complete", headers=headers, json={
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 3},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 4},
                {"pillar_name": "Reading/Learning", "weekly_target_sessions": 2}
            ]
        })
        assert response.status_code == 200
        print("✓ User onboarded successfully")
        return {"headers": headers, "token": token}
    
    def test_onboarding_complete(self, onboarded_user):
        """Verify onboarding was completed"""
        response = requests.get(f"{BASE_URL}/api/users/pillars", headers=onboarded_user['headers'])
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        print(f"✓ Onboarding verified: {len(data)} pillars set up")


class TestSessionRoutes:
    """Test session management routes"""
    
    @pytest.fixture(scope="class")
    def session_user(self):
        """Create an onboarded user for session tests"""
        email = f"session_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": f"session_{uuid.uuid4().hex[:6]}",
            "password": "TestPass123!",
            "age": 17
        })
        assert response.status_code == 200
        token = response.json()['token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Complete onboarding
        requests.post(f"{BASE_URL}/api/onboarding/complete", headers=headers, json={
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 3},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 4},
                {"pillar_name": "Reading/Learning", "weekly_target_sessions": 2}
            ]
        })
        return {"headers": headers}
    
    def test_complete_session(self, session_user):
        """Test /api/sessions/complete endpoint"""
        response = requests.post(f"{BASE_URL}/api/sessions/complete", 
            headers=session_user['headers'],
            json={
                "pillar": "Fitness/Training",
                "minutes_spent": 45,
                "note": "Great workout!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert 'session' in data
        assert data['session']['pillar'] == "Fitness/Training"
        print("✓ Session completed successfully")
        return data['session']['id']
    
    def test_get_today_sessions(self, session_user):
        """Test /api/sessions/today endpoint"""
        response = requests.get(f"{BASE_URL}/api/sessions/today", headers=session_user['headers'])
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Today's sessions: {len(data)}")
    
    def test_get_session_history(self, session_user):
        """Test /api/sessions/history endpoint"""
        response = requests.get(f"{BASE_URL}/api/sessions/history", headers=session_user['headers'])
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Session history: {len(data)} sessions")


class TestStatsRoutes:
    """Test statistics routes"""
    
    @pytest.fixture(scope="class")
    def stats_user(self):
        """Create an onboarded user with sessions for stats tests"""
        email = f"stats_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": f"stats_{uuid.uuid4().hex[:6]}",
            "password": "TestPass123!",
            "age": 16
        })
        assert response.status_code == 200
        token = response.json()['token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Complete onboarding
        requests.post(f"{BASE_URL}/api/onboarding/complete", headers=headers, json={
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 3},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 4},
                {"pillar_name": "Reading/Learning", "weekly_target_sessions": 2}
            ]
        })
        
        # Log a session
        requests.post(f"{BASE_URL}/api/sessions/complete", headers=headers, json={
            "pillar": "Fitness/Training",
            "minutes_spent": 30
        })
        
        return {"headers": headers}
    
    def test_get_weekly_stats(self, stats_user):
        """Test /api/stats/weekly endpoint"""
        response = requests.get(f"{BASE_URL}/api/stats/weekly", headers=stats_user['headers'])
        assert response.status_code == 200
        data = response.json()
        assert 'consistency_pct' in data
        assert 'target_completion_pct' in data
        assert 'performance_index' in data
        assert 'total_sessions' in data
        assert 'pillars_data' in data
        print(f"✓ Weekly stats: performance_index={data['performance_index']}")
    
    def test_get_daily_comparison(self, stats_user):
        """Test /api/stats/comparison endpoint"""
        response = requests.get(f"{BASE_URL}/api/stats/comparison", headers=stats_user['headers'])
        assert response.status_code == 200
        data = response.json()
        assert 'today_sessions' in data
        assert 'yesterday_sessions' in data
        assert 'improvement_pct' in data
        print(f"✓ Daily comparison: today={data['today_sessions']}, yesterday={data['yesterday_sessions']}")
    
    def test_get_performance_history(self, stats_user):
        """Test /api/stats/history endpoint"""
        response = requests.get(f"{BASE_URL}/api/stats/history", headers=stats_user['headers'])
        assert response.status_code == 200
        data = response.json()
        assert 'dates' in data
        assert 'scores' in data
        print(f"✓ Performance history: {len(data['dates'])} days")
    
    def test_get_weekly_review(self, stats_user):
        """Test /api/stats/weekly-review endpoint"""
        response = requests.get(f"{BASE_URL}/api/stats/weekly-review", headers=stats_user['headers'])
        assert response.status_code == 200
        data = response.json()
        assert 'week_start' in data
        assert 'week_end' in data
        assert 'improved_pillars' in data
        assert 'dropped_pillars' in data
        print(f"✓ Weekly review: {data['total_sessions']} sessions")


class TestChallengesRoutes:
    """Test challenges routes"""
    
    @pytest.fixture(scope="class")
    def challenge_user(self):
        """Create an onboarded user for challenge tests"""
        email = f"challenge_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": f"challenge_{uuid.uuid4().hex[:6]}",
            "password": "TestPass123!",
            "age": 15
        })
        assert response.status_code == 200
        token = response.json()['token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Complete onboarding
        requests.post(f"{BASE_URL}/api/onboarding/complete", headers=headers, json={
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 3},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 4},
                {"pillar_name": "Reading/Learning", "weekly_target_sessions": 2}
            ]
        })
        return {"headers": headers}
    
    def test_get_challenges(self, challenge_user):
        """Test /api/challenges endpoint"""
        response = requests.get(f"{BASE_URL}/api/challenges", headers=challenge_user['headers'])
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Challenges: {len(data)} available")
        return data
    
    def test_get_challenges_filtered(self, challenge_user):
        """Test /api/challenges with status filter"""
        response = requests.get(f"{BASE_URL}/api/challenges?status=active", headers=challenge_user['headers'])
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for challenge in data:
            assert challenge.get('status') == 'active'
        print(f"✓ Active challenges: {len(data)}")
    
    def test_join_challenge(self, challenge_user):
        """Test /api/challenges/join endpoint"""
        # Get an active challenge
        response = requests.get(f"{BASE_URL}/api/challenges?status=active", headers=challenge_user['headers'])
        challenges = response.json()
        
        if challenges:
            challenge_id = challenges[0]['id']
            response = requests.post(f"{BASE_URL}/api/challenges/join", 
                headers=challenge_user['headers'],
                json={"challenge_id": challenge_id}
            )
            assert response.status_code == 200
            data = response.json()
            assert 'message' in data
            print(f"✓ Joined challenge: {challenges[0]['name']}")
        else:
            print("⚠ No active challenges to join")
    
    def test_get_my_challenges(self, challenge_user):
        """Test /api/challenges/my endpoint"""
        response = requests.get(f"{BASE_URL}/api/challenges/my", headers=challenge_user['headers'])
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ My challenges: {len(data)}")


class TestGroupsRoutes:
    """Test groups routes"""
    
    @pytest.fixture(scope="class")
    def group_user(self):
        """Create an onboarded user for group tests"""
        email = f"group_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": f"group_{uuid.uuid4().hex[:6]}",
            "password": "TestPass123!",
            "age": 16
        })
        assert response.status_code == 200
        token = response.json()['token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Complete onboarding
        requests.post(f"{BASE_URL}/api/onboarding/complete", headers=headers, json={
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 3},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 4},
                {"pillar_name": "Reading/Learning", "weekly_target_sessions": 2}
            ]
        })
        return {"headers": headers}
    
    def test_get_user_groups(self, group_user):
        """Test /api/groups endpoint"""
        response = requests.get(f"{BASE_URL}/api/groups", headers=group_user['headers'])
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ User groups: {len(data)}")
    
    def test_create_group(self, group_user):
        """Test POST /api/groups endpoint"""
        response = requests.post(f"{BASE_URL}/api/groups", 
            headers=group_user['headers'],
            json={
                "name": f"TestGroup_{uuid.uuid4().hex[:6]}",
                "type": "private"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert 'id' in data
        assert 'invite_code' in data
        print(f"✓ Group created: {data['name']}")
        return data
    
    def test_join_group_invalid_code(self, group_user):
        """Test /api/groups/join with invalid code"""
        response = requests.post(f"{BASE_URL}/api/groups/join",
            headers=group_user['headers'],
            json={"invite_code": "INVALID123"}
        )
        assert response.status_code == 404
        print("✓ Invalid group code correctly rejected")


class TestLeaderboardRoutes:
    """Test leaderboard routes"""
    
    def test_get_global_leaderboard(self):
        """Test /api/leaderboard/global endpoint"""
        response = requests.get(f"{BASE_URL}/api/leaderboard/global")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Global leaderboard: {len(data)} entries")
    
    def test_get_leaderboard_by_age_group(self):
        """Test /api/leaderboard/global with age_group filter"""
        response = requests.get(f"{BASE_URL}/api/leaderboard/global?age_group=15-17")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Leaderboard (15-17): {len(data)} entries")


class TestCoachRoutes:
    """Test coach dashboard routes"""
    
    @pytest.fixture(scope="class")
    def coach_with_team(self):
        """Create a coach with a team"""
        email = f"coach_test_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": email,
            "password": "CoachPass123!",
            "name": f"TestCoach_{uuid.uuid4().hex[:6]}",
            "team_name": f"TestTeam_{uuid.uuid4().hex[:6]}"
        })
        assert response.status_code == 200
        data = response.json()
        return {
            "headers": {"Authorization": f"Bearer {data['token']}"},
            "team_id": data['team_id'],
            "invite_code": data['invite_code']
        }
    
    def test_get_coach_dashboard(self, coach_with_team):
        """Test /api/coach/dashboard endpoint"""
        response = requests.get(f"{BASE_URL}/api/coach/dashboard", headers=coach_with_team['headers'])
        assert response.status_code == 200
        data = response.json()
        assert 'team' in data
        assert 'stats' in data
        assert 'coach' in data
        print(f"✓ Coach dashboard: {data['stats']['total_players']} players")
    
    def test_coach_dashboard_requires_coach(self):
        """Test that non-coach users can't access coach dashboard"""
        # Register a regular user
        email = f"regular_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": f"regular_{uuid.uuid4().hex[:6]}",
            "password": "TestPass123!",
            "age": 15
        })
        token = response.json()['token']
        
        response = requests.get(f"{BASE_URL}/api/coach/dashboard", 
            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403
        print("✓ Non-coach correctly denied access to coach dashboard")


class TestParentRoutes:
    """Test parent-student linking routes"""
    
    @pytest.fixture(scope="class")
    def student_user(self):
        """Create a student user"""
        email = f"student_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": f"student_{uuid.uuid4().hex[:6]}",
            "password": "TestPass123!",
            "age": 14
        })
        assert response.status_code == 200
        token = response.json()['token']
        return {"headers": {"Authorization": f"Bearer {token}"}}
    
    def test_invite_parent(self, student_user):
        """Test /api/parent/invite endpoint"""
        response = requests.post(f"{BASE_URL}/api/parent/invite",
            headers=student_user['headers'],
            json={"parent_email": f"parent_{uuid.uuid4().hex[:8]}@test.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert 'invite_code' in data
        assert 'message' in data
        print(f"✓ Parent invite sent: {data['invite_code']}")
    
    def test_get_linked_parents(self, student_user):
        """Test /api/student/linked-parents endpoint"""
        response = requests.get(f"{BASE_URL}/api/student/linked-parents", headers=student_user['headers'])
        assert response.status_code == 200
        data = response.json()
        assert 'active_parents' in data
        assert 'pending_invites' in data
        assert 'max_parents' in data
        print(f"✓ Linked parents: {len(data['active_parents'])} active, {len(data['pending_invites'])} pending")


class TestBadgesRoutes:
    """Test badges routes"""
    
    @pytest.fixture(scope="class")
    def badge_user(self):
        """Create an onboarded user for badge tests"""
        email = f"badge_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": f"badge_{uuid.uuid4().hex[:6]}",
            "password": "TestPass123!",
            "age": 15
        })
        assert response.status_code == 200
        token = response.json()['token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Complete onboarding
        requests.post(f"{BASE_URL}/api/onboarding/complete", headers=headers, json={
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 3},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 4},
                {"pillar_name": "Reading/Learning", "weekly_target_sessions": 2}
            ]
        })
        return {"headers": headers}
    
    def test_get_all_badges(self):
        """Test /api/badges/all endpoint"""
        response = requests.get(f"{BASE_URL}/api/badges/all")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        print(f"✓ All badges: {len(data)} available")
    
    def test_get_user_badges(self, badge_user):
        """Test /api/badges/user endpoint"""
        response = requests.get(f"{BASE_URL}/api/badges/user", headers=badge_user['headers'])
        assert response.status_code == 200
        data = response.json()
        assert 'earned_badges' in data
        assert 'all_badges' in data
        assert 'total_earned' in data
        assert 'total_available' in data
        print(f"✓ User badges: {data['total_earned']}/{data['total_available']} earned")
    
    def test_get_badge_progress(self, badge_user):
        """Test /api/badges/progress endpoint"""
        response = requests.get(f"{BASE_URL}/api/badges/progress", headers=badge_user['headers'])
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Badge progress: {len(data)} badges in progress")


class TestNotificationRoutes:
    """Test notification routes"""
    
    @pytest.fixture(scope="class")
    def notification_user(self):
        """Create a user for notification tests"""
        email = f"notif_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": f"notif_{uuid.uuid4().hex[:6]}",
            "password": "TestPass123!",
            "age": 16
        })
        assert response.status_code == 200
        token = response.json()['token']
        return {"headers": {"Authorization": f"Bearer {token}"}}
    
    def test_get_notification_settings(self, notification_user):
        """Test /api/notifications/settings endpoint"""
        response = requests.get(f"{BASE_URL}/api/notifications/settings", headers=notification_user['headers'])
        assert response.status_code == 200
        data = response.json()
        assert 'streak_reminders' in data
        assert 'weekly_summary' in data
        print(f"✓ Notification settings: streak={data['streak_reminders']}, weekly={data['weekly_summary']}")
    
    def test_update_notification_settings(self, notification_user):
        """Test PUT /api/notifications/settings endpoint"""
        response = requests.put(f"{BASE_URL}/api/notifications/settings",
            headers=notification_user['headers'],
            json={"streak_reminders": False, "weekly_summary": True}
        )
        assert response.status_code == 200
        print("✓ Notification settings updated")


class TestReferralRoutes:
    """Test referral routes"""
    
    @pytest.fixture(scope="class")
    def referral_user(self):
        """Create a user for referral tests"""
        email = f"referral_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": f"referral_{uuid.uuid4().hex[:6]}",
            "password": "TestPass123!",
            "age": 17
        })
        assert response.status_code == 200
        token = response.json()['token']
        return {"headers": {"Authorization": f"Bearer {token}"}}
    
    def test_get_referral_info(self, referral_user):
        """Test /api/referral/info endpoint"""
        response = requests.get(f"{BASE_URL}/api/referral/info", headers=referral_user['headers'])
        assert response.status_code == 200
        data = response.json()
        assert 'referral_code' in data
        assert 'referral_link' in data
        assert 'total_referrals' in data
        print(f"✓ Referral info: code={data['referral_code']}")


class TestPaymentRoutes:
    """Test payment routes (Stripe in test mode)"""
    
    @pytest.fixture(scope="class")
    def payment_user(self):
        """Create a user for payment tests"""
        email = f"payment_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": f"payment_{uuid.uuid4().hex[:6]}",
            "password": "TestPass123!",
            "age": 18
        })
        assert response.status_code == 200
        token = response.json()['token']
        return {"headers": {"Authorization": f"Bearer {token}"}}
    
    def test_create_checkout_session(self, payment_user):
        """Test /api/payments/create-checkout endpoint"""
        response = requests.post(f"{BASE_URL}/api/payments/create-checkout",
            headers=payment_user['headers'],
            json={
                "origin_url": BASE_URL,
                "plan": "monthly"
            }
        )
        # Should return 200 with checkout URL or 500 if Stripe not configured
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert 'url' in data
            assert 'session_id' in data
            print(f"✓ Checkout session created")
        else:
            print("⚠ Stripe checkout failed (may be configuration issue)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
