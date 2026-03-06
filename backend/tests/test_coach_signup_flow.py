"""
Test New Coach Signup Flow
- Coach registration with team creation
- Special code for extended 30-day trials
- Team info public endpoint
- Player join team flow
- Coach dashboard
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://daily-progress-96.preview.emergentagent.com').rstrip('/')

# Valid special codes from server.py
VALID_SPECIAL_CODES = ['EDGE30', 'COACH2024', 'TEAMEDGE', 'PROMO30']


class TestCoachRegistration:
    """Test POST /api/auth/coach/register endpoint"""
    
    def test_01_coach_register_without_special_code(self):
        """Coach registers without special code - has_extended_trial should be False"""
        email = f"coach_nocode_{uuid.uuid4().hex[:6]}@test.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": email,
            "password": "test123456",
            "name": "Coach Without Code",
            "team_name": "Test Team Regular"
        })
        
        assert response.status_code == 200, f"Failed to register coach: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert 'token' in data, "token missing"
        assert 'coach_id' in data, "coach_id missing"
        assert 'team_id' in data, "team_id missing"
        assert 'team_name' in data, "team_name missing"
        assert 'invite_code' in data, "invite_code missing"
        assert 'invite_link' in data, "invite_link missing"
        assert 'has_extended_trial' in data, "has_extended_trial missing"
        
        # Verify has_extended_trial is False without special code
        assert data['has_extended_trial'] == False, f"has_extended_trial should be False, got {data['has_extended_trial']}"
        
        # Verify invite code format
        assert data['invite_code'].startswith('TEAM-'), f"Invite code should start with TEAM-, got {data['invite_code']}"
        
        print(f"Coach registered without code: {email}, has_extended_trial={data['has_extended_trial']}")
        return data
    
    def test_02_coach_register_with_valid_special_code_EDGE30(self):
        """Coach registers with EDGE30 code - has_extended_trial should be True"""
        email = f"coach_edge30_{uuid.uuid4().hex[:6]}@test.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": email,
            "password": "test123456",
            "name": "Coach With EDGE30",
            "team_name": "Test Team Extended",
            "special_code": "EDGE30"
        })
        
        assert response.status_code == 200, f"Failed to register coach: {response.text}"
        data = response.json()
        
        # Verify has_extended_trial is True with valid code
        assert data['has_extended_trial'] == True, f"has_extended_trial should be True with EDGE30, got {data['has_extended_trial']}"
        
        print(f"Coach registered with EDGE30: {email}, has_extended_trial={data['has_extended_trial']}")
        return data
    
    def test_03_coach_register_with_valid_special_code_COACH2024(self):
        """Coach registers with COACH2024 code - has_extended_trial should be True"""
        email = f"coach_2024_{uuid.uuid4().hex[:6]}@test.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": email,
            "password": "test123456",
            "name": "Coach With COACH2024",
            "team_name": "Test Team 2024",
            "special_code": "COACH2024"
        })
        
        assert response.status_code == 200, f"Failed to register coach: {response.text}"
        data = response.json()
        
        assert data['has_extended_trial'] == True, f"has_extended_trial should be True with COACH2024"
        print(f"Coach registered with COACH2024: has_extended_trial={data['has_extended_trial']}")
    
    def test_04_coach_register_with_invalid_special_code(self):
        """Coach registers with invalid code - has_extended_trial should be False"""
        email = f"coach_invalid_{uuid.uuid4().hex[:6]}@test.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": email,
            "password": "test123456",
            "name": "Coach With Invalid Code",
            "team_name": "Test Team Invalid",
            "special_code": "INVALIDCODE123"
        })
        
        assert response.status_code == 200, f"Failed to register coach: {response.text}"
        data = response.json()
        
        # Invalid code should result in has_extended_trial=False
        assert data['has_extended_trial'] == False, f"has_extended_trial should be False with invalid code"
        print(f"Coach registered with invalid code: has_extended_trial={data['has_extended_trial']}")
    
    def test_05_coach_register_with_lowercase_special_code(self):
        """Coach registers with lowercase code - should still work (case insensitive)"""
        email = f"coach_lower_{uuid.uuid4().hex[:6]}@test.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": email,
            "password": "test123456",
            "name": "Coach Lowercase",
            "team_name": "Test Team Lowercase",
            "special_code": "edge30"  # lowercase
        })
        
        assert response.status_code == 200, f"Failed to register coach: {response.text}"
        data = response.json()
        
        # Should work with lowercase (server converts to uppercase)
        assert data['has_extended_trial'] == True, f"has_extended_trial should be True with lowercase edge30"
        print(f"Coach registered with lowercase code: has_extended_trial={data['has_extended_trial']}")
    
    def test_06_coach_duplicate_email_rejected(self):
        """Duplicate email should be rejected"""
        email = f"coach_dup_{uuid.uuid4().hex[:6]}@test.com"
        
        # First registration
        response1 = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": email,
            "password": "test123456",
            "name": "Coach First",
            "team_name": "Team First"
        })
        assert response1.status_code == 200
        
        # Second registration with same email
        response2 = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": email,
            "password": "test123456",
            "name": "Coach Second",
            "team_name": "Team Second"
        })
        
        assert response2.status_code == 400, f"Expected 400 for duplicate email, got {response2.status_code}"
        assert "already registered" in response2.json().get('detail', '').lower()
        print("Duplicate email correctly rejected")


class TestTeamInfoEndpoint:
    """Test GET /api/team/{team_code} public endpoint"""
    
    @pytest.fixture
    def coach_with_extended_trial(self):
        """Create a coach with extended trial"""
        email = f"coach_ext_{uuid.uuid4().hex[:6]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": email,
            "password": "test123456",
            "name": "Coach Extended",
            "team_name": "Extended Trial Team",
            "special_code": "EDGE30"
        })
        assert response.status_code == 200
        return response.json()
    
    @pytest.fixture
    def coach_without_extended_trial(self):
        """Create a coach without extended trial"""
        email = f"coach_reg_{uuid.uuid4().hex[:6]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": email,
            "password": "test123456",
            "name": "Coach Regular",
            "team_name": "Regular Trial Team"
        })
        assert response.status_code == 200
        return response.json()
    
    def test_01_get_team_info_extended_trial(self, coach_with_extended_trial):
        """GET /api/team/{team_code} returns correct info for extended trial team"""
        invite_code = coach_with_extended_trial['invite_code']
        
        response = requests.get(f"{BASE_URL}/api/team/{invite_code}")
        
        assert response.status_code == 200, f"Failed to get team info: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert 'team_name' in data, "team_name missing"
        assert 'coach_name' in data, "coach_name missing"
        assert 'member_count' in data, "member_count missing"
        assert 'has_extended_trial' in data, "has_extended_trial missing"
        assert 'trial_days' in data, "trial_days missing"
        
        # Verify extended trial values
        assert data['has_extended_trial'] == True, "has_extended_trial should be True"
        assert data['trial_days'] == 30, f"trial_days should be 30, got {data['trial_days']}"
        
        print(f"Team info: {data['team_name']}, trial_days={data['trial_days']}")
    
    def test_02_get_team_info_regular_trial(self, coach_without_extended_trial):
        """GET /api/team/{team_code} returns correct info for regular trial team"""
        invite_code = coach_without_extended_trial['invite_code']
        
        response = requests.get(f"{BASE_URL}/api/team/{invite_code}")
        
        assert response.status_code == 200, f"Failed to get team info: {response.text}"
        data = response.json()
        
        # Verify regular trial values
        assert data['has_extended_trial'] == False, "has_extended_trial should be False"
        assert data['trial_days'] == 14, f"trial_days should be 14, got {data['trial_days']}"
        
        print(f"Team info: {data['team_name']}, trial_days={data['trial_days']}")
    
    def test_03_get_team_info_invalid_code(self):
        """GET /api/team/{team_code} returns 404 for invalid code"""
        response = requests.get(f"{BASE_URL}/api/team/TEAM-INVALID123")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Invalid team code correctly returns 404")


class TestPlayerJoinTeam:
    """Test POST /api/auth/player/join-team endpoint"""
    
    @pytest.fixture
    def coach_extended(self):
        """Create coach with extended trial"""
        email = f"coach_pj_ext_{uuid.uuid4().hex[:6]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": email,
            "password": "test123456",
            "name": "Coach PJ Extended",
            "team_name": "Player Join Extended Team",
            "special_code": "EDGE30"
        })
        assert response.status_code == 200
        return response.json()
    
    @pytest.fixture
    def coach_regular(self):
        """Create coach without extended trial"""
        email = f"coach_pj_reg_{uuid.uuid4().hex[:6]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": email,
            "password": "test123456",
            "name": "Coach PJ Regular",
            "team_name": "Player Join Regular Team"
        })
        assert response.status_code == 200
        return response.json()
    
    def test_01_player_joins_extended_trial_team(self, coach_extended):
        """Player joining extended trial team gets 30-day trial"""
        team_code = coach_extended['invite_code']
        player_email = f"player_ext_{uuid.uuid4().hex[:6]}@test.com"
        
        response = requests.post(
            f"{BASE_URL}/api/auth/player/join-team?team_code={team_code}",
            json={
                "email": player_email,
                "username": f"player_{uuid.uuid4().hex[:4]}",
                "password": "test123456",
                "age": 16
            }
        )
        
        assert response.status_code == 200, f"Failed to join team: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert 'token' in data, "token missing"
        assert 'user_id' in data, "user_id missing"
        assert 'trial_ends_at' in data, "trial_ends_at missing"
        assert 'trial_days' in data, "trial_days missing"
        assert 'team_name' in data, "team_name missing"
        
        # Verify 30-day trial
        assert data['trial_days'] == 30, f"trial_days should be 30, got {data['trial_days']}"
        
        # Verify trial_ends_at is approximately 30 days from now
        trial_end = datetime.fromisoformat(data['trial_ends_at'].replace('Z', '+00:00'))
        expected_end = datetime.now().replace(tzinfo=trial_end.tzinfo) + timedelta(days=30)
        diff = abs((trial_end - expected_end).days)
        assert diff <= 1, f"Trial end date should be ~30 days from now, diff={diff} days"
        
        print(f"Player joined extended trial team: trial_days={data['trial_days']}")
        return data
    
    def test_02_player_joins_regular_trial_team(self, coach_regular):
        """Player joining regular trial team gets 14-day trial"""
        team_code = coach_regular['invite_code']
        player_email = f"player_reg_{uuid.uuid4().hex[:6]}@test.com"
        
        response = requests.post(
            f"{BASE_URL}/api/auth/player/join-team?team_code={team_code}",
            json={
                "email": player_email,
                "username": f"player_{uuid.uuid4().hex[:4]}",
                "password": "test123456",
                "age": 15
            }
        )
        
        assert response.status_code == 200, f"Failed to join team: {response.text}"
        data = response.json()
        
        # Verify 14-day trial
        assert data['trial_days'] == 14, f"trial_days should be 14, got {data['trial_days']}"
        
        print(f"Player joined regular trial team: trial_days={data['trial_days']}")
    
    def test_03_player_join_invalid_team_code(self):
        """Player joining with invalid team code gets 404"""
        player_email = f"player_inv_{uuid.uuid4().hex[:6]}@test.com"
        
        response = requests.post(
            f"{BASE_URL}/api/auth/player/join-team?team_code=TEAM-INVALID123",
            json={
                "email": player_email,
                "username": f"player_{uuid.uuid4().hex[:4]}",
                "password": "test123456",
                "age": 16
            }
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Invalid team code correctly rejected")
    
    def test_04_player_duplicate_email_rejected(self, coach_regular):
        """Duplicate email should be rejected when joining team"""
        team_code = coach_regular['invite_code']
        player_email = f"player_dup_{uuid.uuid4().hex[:6]}@test.com"
        
        # First join
        response1 = requests.post(
            f"{BASE_URL}/api/auth/player/join-team?team_code={team_code}",
            json={
                "email": player_email,
                "username": f"player_{uuid.uuid4().hex[:4]}",
                "password": "test123456",
                "age": 16
            }
        )
        assert response1.status_code == 200
        
        # Second join with same email
        response2 = requests.post(
            f"{BASE_URL}/api/auth/player/join-team?team_code={team_code}",
            json={
                "email": player_email,
                "username": f"player_{uuid.uuid4().hex[:4]}",
                "password": "test123456",
                "age": 16
            }
        )
        
        assert response2.status_code == 400, f"Expected 400, got {response2.status_code}"
        print("Duplicate email correctly rejected")


class TestCoachDashboard:
    """Test GET /api/coach/dashboard endpoint"""
    
    def test_01_coach_dashboard_returns_team_info(self):
        """Coach dashboard returns team info and stats"""
        # Create coach
        email = f"coach_dash_{uuid.uuid4().hex[:6]}@test.com"
        reg_response = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": email,
            "password": "test123456",
            "name": "Coach Dashboard Test",
            "team_name": "Dashboard Test Team",
            "special_code": "EDGE30"
        })
        assert reg_response.status_code == 200
        coach_data = reg_response.json()
        
        # Get dashboard
        response = requests.get(
            f"{BASE_URL}/api/coach/dashboard",
            headers={"Authorization": f"Bearer {coach_data['token']}"}
        )
        
        assert response.status_code == 200, f"Failed to get dashboard: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert 'team' in data, "team missing"
        assert 'stats' in data, "stats missing"
        assert 'coach' in data, "coach missing"
        
        # Verify team info
        team = data['team']
        assert 'id' in team, "team.id missing"
        assert 'name' in team, "team.name missing"
        assert 'invite_code' in team, "team.invite_code missing"
        assert 'invite_link' in team, "team.invite_link missing"
        assert 'has_extended_trial' in team, "team.has_extended_trial missing"
        
        # Verify stats
        stats = data['stats']
        assert 'total_players' in stats, "stats.total_players missing"
        assert 'active_players_this_week' in stats, "stats.active_players_this_week missing"
        assert 'total_sessions_this_week' in stats, "stats.total_sessions_this_week missing"
        
        # Verify coach info
        coach = data['coach']
        assert 'name' in coach, "coach.name missing"
        assert 'email' in coach, "coach.email missing"
        
        print(f"Coach dashboard: team={team['name']}, players={stats['total_players']}")
    
    def test_02_non_coach_cannot_access_dashboard(self):
        """Non-coach user cannot access coach dashboard"""
        # Create regular user
        email = f"regular_user_{uuid.uuid4().hex[:6]}@test.com"
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": f"regular_{uuid.uuid4().hex[:4]}",
            "password": "test123456",
            "age": 16
        })
        assert reg_response.status_code == 200
        token = reg_response.json()['token']
        
        # Try to access coach dashboard
        response = requests.get(
            f"{BASE_URL}/api/coach/dashboard",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("Non-coach correctly denied access to coach dashboard")
    
    def test_03_coach_dashboard_with_players(self):
        """Coach dashboard shows correct player count after players join"""
        # Create coach
        email = f"coach_wp_{uuid.uuid4().hex[:6]}@test.com"
        reg_response = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": email,
            "password": "test123456",
            "name": "Coach With Players",
            "team_name": "Team With Players"
        })
        assert reg_response.status_code == 200
        coach_data = reg_response.json()
        
        # Add 2 players
        for i in range(2):
            player_email = f"player_wp_{uuid.uuid4().hex[:6]}@test.com"
            requests.post(
                f"{BASE_URL}/api/auth/player/join-team?team_code={coach_data['invite_code']}",
                json={
                    "email": player_email,
                    "username": f"player_{uuid.uuid4().hex[:4]}",
                    "password": "test123456",
                    "age": 15 + i
                }
            )
        
        # Get dashboard
        response = requests.get(
            f"{BASE_URL}/api/coach/dashboard",
            headers={"Authorization": f"Bearer {coach_data['token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify player count
        assert data['stats']['total_players'] == 2, f"Expected 2 players, got {data['stats']['total_players']}"
        print(f"Coach dashboard shows {data['stats']['total_players']} players")


class TestCoachAccountProperties:
    """Test coach account properties"""
    
    def test_01_coach_account_is_always_free(self):
        """Coach account has subscription_active=True and is_trial=False"""
        email = f"coach_free_{uuid.uuid4().hex[:6]}@test.com"
        
        # Register coach
        reg_response = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": email,
            "password": "test123456",
            "name": "Coach Free Test",
            "team_name": "Free Test Team"
        })
        assert reg_response.status_code == 200
        token = reg_response.json()['token']
        
        # Get user info
        me_response = requests.get(
            f"{BASE_URL}/api/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert me_response.status_code == 200, f"Failed to get user info: {me_response.text}"
        data = me_response.json()
        
        # Verify coach account properties
        assert data.get('subscription_active') == True, "Coach subscription_active should be True"
        assert data.get('is_trial') == False, "Coach is_trial should be False"
        
        print(f"Coach account: subscription_active={data.get('subscription_active')}, is_trial={data.get('is_trial')}")
    
    def test_02_player_joined_via_coach_has_team_id(self):
        """Player joined via team link has team_id and joined_via_coach=True"""
        # Create coach
        coach_email = f"coach_link_{uuid.uuid4().hex[:6]}@test.com"
        coach_response = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": coach_email,
            "password": "test123456",
            "name": "Coach Link Test",
            "team_name": "Link Test Team"
        })
        assert coach_response.status_code == 200
        coach_data = coach_response.json()
        
        # Player joins via team link
        player_email = f"player_link_{uuid.uuid4().hex[:6]}@test.com"
        player_response = requests.post(
            f"{BASE_URL}/api/auth/player/join-team?team_code={coach_data['invite_code']}",
            json={
                "email": player_email,
                "username": f"player_{uuid.uuid4().hex[:4]}",
                "password": "test123456",
                "age": 16
            }
        )
        assert player_response.status_code == 200
        player_token = player_response.json()['token']
        
        # Get player info
        me_response = requests.get(
            f"{BASE_URL}/api/users/me",
            headers={"Authorization": f"Bearer {player_token}"}
        )
        
        assert me_response.status_code == 200
        data = me_response.json()
        
        # Verify player has team_id and joined_via_coach
        assert data.get('team_id') == coach_data['team_id'], f"Player team_id should match coach's team_id"
        assert data.get('joined_via_coach') == True, "Player joined_via_coach should be True"
        
        print(f"Player has team_id={data.get('team_id')}, joined_via_coach={data.get('joined_via_coach')}")


class TestCoachLogin:
    """Test coach login returns is_coach flag"""
    
    def test_01_coach_login_returns_is_coach_true(self):
        """Coach login returns is_coach=True"""
        email = f"coach_login_{uuid.uuid4().hex[:6]}@test.com"
        password = "test123456"
        
        # Register coach
        reg_response = requests.post(f"{BASE_URL}/api/auth/coach/register", json={
            "email": email,
            "password": password,
            "name": "Coach Login Test",
            "team_name": "Login Test Team"
        })
        assert reg_response.status_code == 200
        
        # Login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        
        assert login_response.status_code == 200, f"Failed to login: {login_response.text}"
        data = login_response.json()
        
        assert 'is_coach' in data, "is_coach missing in login response"
        assert data['is_coach'] == True, f"is_coach should be True for coach, got {data['is_coach']}"
        
        print(f"Coach login: is_coach={data['is_coach']}")
    
    def test_02_regular_user_login_returns_is_coach_false(self):
        """Regular user login returns is_coach=False"""
        email = f"regular_login_{uuid.uuid4().hex[:6]}@test.com"
        password = "test123456"
        
        # Register regular user
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": f"regular_{uuid.uuid4().hex[:4]}",
            "password": password,
            "age": 16
        })
        assert reg_response.status_code == 200
        
        # Login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        
        assert login_response.status_code == 200
        data = login_response.json()
        
        assert data.get('is_coach', False) == False, f"is_coach should be False for regular user"
        print(f"Regular user login: is_coach={data.get('is_coach', False)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
