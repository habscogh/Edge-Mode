"""
Test Coach and Parent Features
- Coach Dashboard: Create coach groups, view team stats, view player details
- Parent-Student Linking: Invite parents, accept invites, view student progress
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://one-percent-better-2.preview.emergentagent.com').rstrip('/')

# Test data
COACH_EMAIL = f"coach_test_{uuid.uuid4().hex[:6]}@test.com"
COACH_PASSWORD = "test123456"
STUDENT_EMAIL = f"student_test_{uuid.uuid4().hex[:6]}@test.com"
STUDENT_PASSWORD = "test123456"
PARENT_EMAIL = f"parent_test_{uuid.uuid4().hex[:6]}@test.com"
PARENT_PASSWORD = "test123456"
PLAYER_EMAIL = f"player_test_{uuid.uuid4().hex[:6]}@test.com"
PLAYER_PASSWORD = "test123456"


class TestCoachFeature:
    """Test Coach Dashboard functionality"""
    
    coach_token = None
    player_token = None
    coach_group_id = None
    player_id = None
    
    @pytest.fixture(autouse=True)
    def setup(self, request):
        """Setup test users and group"""
        # Register coach
        coach_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": COACH_EMAIL,
            "username": f"coach_{uuid.uuid4().hex[:4]}",
            "password": COACH_PASSWORD,
            "age": 18
        })
        if coach_response.status_code == 200:
            TestCoachFeature.coach_token = coach_response.json().get('token')
        elif coach_response.status_code == 400:
            # User exists, login
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": COACH_EMAIL,
                "password": COACH_PASSWORD
            })
            if login_resp.status_code == 200:
                TestCoachFeature.coach_token = login_resp.json().get('token')
        
        # Register player
        player_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": PLAYER_EMAIL,
            "username": f"player_{uuid.uuid4().hex[:4]}",
            "password": PLAYER_PASSWORD,
            "age": 16
        })
        if player_response.status_code == 200:
            TestCoachFeature.player_token = player_response.json().get('token')
            TestCoachFeature.player_id = player_response.json().get('user_id')
        elif player_response.status_code == 400:
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": PLAYER_EMAIL,
                "password": PLAYER_PASSWORD
            })
            if login_resp.status_code == 200:
                TestCoachFeature.player_token = login_resp.json().get('token')
                # Get user ID
                me_resp = requests.get(f"{BASE_URL}/api/users/me", headers={
                    "Authorization": f"Bearer {TestCoachFeature.player_token}"
                })
                if me_resp.status_code == 200:
                    TestCoachFeature.player_id = me_resp.json().get('id')
    
    def test_01_create_coach_group(self):
        """Create a group with is_coach=true, verify coach_id is set"""
        if not TestCoachFeature.coach_token:
            pytest.skip("Coach token not available")
        
        response = requests.post(
            f"{BASE_URL}/api/groups",
            json={
                "name": f"Test Team {uuid.uuid4().hex[:4]}",
                "type": "private",
                "is_coach": True
            },
            headers={"Authorization": f"Bearer {TestCoachFeature.coach_token}"}
        )
        
        assert response.status_code == 200, f"Failed to create coach group: {response.text}"
        data = response.json()
        
        # Verify coach_id is set
        assert 'coach_id' in data, "coach_id field missing in response"
        assert data['coach_id'] is not None, "coach_id should not be None for coach group"
        assert 'id' in data, "Group ID missing"
        assert 'invite_code' in data, "Invite code missing"
        
        TestCoachFeature.coach_group_id = data['id']
        print(f"Created coach group: {data['id']} with invite code: {data['invite_code']}")
    
    def test_02_player_joins_coach_group(self):
        """Player joins the coach's group"""
        if not TestCoachFeature.coach_group_id or not TestCoachFeature.player_token:
            pytest.skip("Coach group or player token not available")
        
        # Get invite code
        groups_resp = requests.get(
            f"{BASE_URL}/api/groups",
            headers={"Authorization": f"Bearer {TestCoachFeature.coach_token}"}
        )
        assert groups_resp.status_code == 200
        
        coach_group = next((g for g in groups_resp.json() if g['id'] == TestCoachFeature.coach_group_id), None)
        assert coach_group is not None, "Coach group not found"
        
        invite_code = coach_group['invite_code']
        
        # Player joins
        join_resp = requests.post(
            f"{BASE_URL}/api/groups/join",
            json={"invite_code": invite_code},
            headers={"Authorization": f"Bearer {TestCoachFeature.player_token}"}
        )
        
        assert join_resp.status_code == 200, f"Failed to join group: {join_resp.text}"
        print(f"Player joined coach group successfully")
    
    def test_03_coach_dashboard_returns_team_stats(self):
        """GET /api/groups/{id}/coach/dashboard - returns team stats and player list"""
        if not TestCoachFeature.coach_group_id or not TestCoachFeature.coach_token:
            pytest.skip("Coach group or token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/groups/{TestCoachFeature.coach_group_id}/coach/dashboard",
            headers={"Authorization": f"Bearer {TestCoachFeature.coach_token}"}
        )
        
        assert response.status_code == 200, f"Failed to get coach dashboard: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert 'group' in data, "group field missing"
        assert 'players' in data, "players field missing"
        assert 'team_stats' in data, "team_stats field missing"
        
        # Verify team_stats structure
        team_stats = data['team_stats']
        assert 'total_players' in team_stats, "total_players missing"
        assert 'avg_consistency' in team_stats, "avg_consistency missing"
        assert 'avg_performance' in team_stats, "avg_performance missing"
        assert 'total_sessions_this_week' in team_stats, "total_sessions_this_week missing"
        
        print(f"Coach dashboard: {team_stats['total_players']} players, avg consistency: {team_stats['avg_consistency']}%")
    
    def test_04_coach_view_player_details(self):
        """GET /api/groups/{id}/coach/player/{player_id} - returns detailed player stats"""
        if not TestCoachFeature.coach_group_id or not TestCoachFeature.coach_token or not TestCoachFeature.player_id:
            pytest.skip("Required data not available")
        
        response = requests.get(
            f"{BASE_URL}/api/groups/{TestCoachFeature.coach_group_id}/coach/player/{TestCoachFeature.player_id}",
            headers={"Authorization": f"Bearer {TestCoachFeature.coach_token}"}
        )
        
        assert response.status_code == 200, f"Failed to get player details: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert 'player' in data, "player field missing"
        assert 'pillars' in data, "pillars field missing"
        assert 'weekly_stats' in data, "weekly_stats field missing"
        assert 'badges_earned' in data, "badges_earned field missing"
        
        # Verify player info
        player = data['player']
        assert 'id' in player, "player id missing"
        assert 'username' in player, "player username missing"
        assert 'current_streak' in player, "current_streak missing"
        
        print(f"Player details: {player['username']}, streak: {player['current_streak']}")
    
    def test_05_non_coach_cannot_access_dashboard(self):
        """Non-coach cannot access coach dashboard (403 error)"""
        if not TestCoachFeature.coach_group_id or not TestCoachFeature.player_token:
            pytest.skip("Required data not available")
        
        response = requests.get(
            f"{BASE_URL}/api/groups/{TestCoachFeature.coach_group_id}/coach/dashboard",
            headers={"Authorization": f"Bearer {TestCoachFeature.player_token}"}
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("Non-coach correctly denied access to coach dashboard")
    
    def test_06_non_coach_cannot_view_player_details(self):
        """Non-coach cannot access player details (403 error)"""
        if not TestCoachFeature.coach_group_id or not TestCoachFeature.player_token or not TestCoachFeature.player_id:
            pytest.skip("Required data not available")
        
        response = requests.get(
            f"{BASE_URL}/api/groups/{TestCoachFeature.coach_group_id}/coach/player/{TestCoachFeature.player_id}",
            headers={"Authorization": f"Bearer {TestCoachFeature.player_token}"}
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("Non-coach correctly denied access to player details")


class TestParentFeature:
    """Test Parent-Student Linking functionality"""
    
    student_token = None
    student_id = None
    parent_token = None
    parent_id = None
    invite_code = None
    link_id = None
    
    @pytest.fixture(autouse=True)
    def setup(self, request):
        """Setup test users"""
        # Register student
        student_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": STUDENT_EMAIL,
            "username": f"student_{uuid.uuid4().hex[:4]}",
            "password": STUDENT_PASSWORD,
            "age": 15
        })
        if student_response.status_code == 200:
            TestParentFeature.student_token = student_response.json().get('token')
            TestParentFeature.student_id = student_response.json().get('user_id')
        elif student_response.status_code == 400:
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": STUDENT_EMAIL,
                "password": STUDENT_PASSWORD
            })
            if login_resp.status_code == 200:
                TestParentFeature.student_token = login_resp.json().get('token')
                me_resp = requests.get(f"{BASE_URL}/api/users/me", headers={
                    "Authorization": f"Bearer {TestParentFeature.student_token}"
                })
                if me_resp.status_code == 200:
                    TestParentFeature.student_id = me_resp.json().get('id')
        
        # Register parent
        parent_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": PARENT_EMAIL,
            "username": f"parent_{uuid.uuid4().hex[:4]}",
            "password": PARENT_PASSWORD,
            "age": 19  # Using max allowed age for testing
        })
        if parent_response.status_code == 200:
            TestParentFeature.parent_token = parent_response.json().get('token')
            TestParentFeature.parent_id = parent_response.json().get('user_id')
        elif parent_response.status_code == 400:
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": PARENT_EMAIL,
                "password": PARENT_PASSWORD
            })
            if login_resp.status_code == 200:
                TestParentFeature.parent_token = login_resp.json().get('token')
                me_resp = requests.get(f"{BASE_URL}/api/users/me", headers={
                    "Authorization": f"Bearer {TestParentFeature.parent_token}"
                })
                if me_resp.status_code == 200:
                    TestParentFeature.parent_id = me_resp.json().get('id')
    
    def test_01_student_invites_parent(self):
        """POST /api/parent/invite - student sends invite to parent email"""
        if not TestParentFeature.student_token:
            pytest.skip("Student token not available")
        
        # Use a unique email for this test
        test_parent_email = f"testparent_{uuid.uuid4().hex[:6]}@test.com"
        
        response = requests.post(
            f"{BASE_URL}/api/parent/invite",
            json={"parent_email": test_parent_email},
            headers={"Authorization": f"Bearer {TestParentFeature.student_token}"}
        )
        
        assert response.status_code == 200, f"Failed to invite parent: {response.text}"
        data = response.json()
        
        # Verify response
        assert 'invite_code' in data, "invite_code missing in response"
        assert 'message' in data, "message missing in response"
        assert data['invite_code'].startswith('PARENT-'), "Invite code should start with PARENT-"
        
        TestParentFeature.invite_code = data['invite_code']
        print(f"Parent invite sent, code: {data['invite_code']}")
    
    def test_02_student_views_linked_parents(self):
        """GET /api/student/linked-parents - student sees pending/active parent links"""
        if not TestParentFeature.student_token:
            pytest.skip("Student token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/student/linked-parents",
            headers={"Authorization": f"Bearer {TestParentFeature.student_token}"}
        )
        
        assert response.status_code == 200, f"Failed to get linked parents: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert 'active_parents' in data, "active_parents missing"
        assert 'pending_invites' in data, "pending_invites missing"
        assert 'max_parents' in data, "max_parents missing"
        assert 'slots_remaining' in data, "slots_remaining missing"
        
        # Verify max parents is 2
        assert data['max_parents'] == 2, f"max_parents should be 2, got {data['max_parents']}"
        
        print(f"Student has {len(data['active_parents'])} active parents, {len(data['pending_invites'])} pending")
    
    def test_03_parent_accepts_invite(self):
        """POST /api/parent/accept - parent accepts with invite code"""
        if not TestParentFeature.parent_token:
            pytest.skip("Parent token not available")
        
        # First, create a fresh invite for this test
        test_parent_email = f"accepttest_{uuid.uuid4().hex[:6]}@test.com"
        
        invite_resp = requests.post(
            f"{BASE_URL}/api/parent/invite",
            json={"parent_email": test_parent_email},
            headers={"Authorization": f"Bearer {TestParentFeature.student_token}"}
        )
        
        if invite_resp.status_code != 200:
            pytest.skip(f"Could not create invite: {invite_resp.text}")
        
        invite_code = invite_resp.json().get('invite_code')
        
        # Parent accepts
        response = requests.post(
            f"{BASE_URL}/api/parent/accept",
            json={"invite_code": invite_code},
            headers={"Authorization": f"Bearer {TestParentFeature.parent_token}"}
        )
        
        assert response.status_code == 200, f"Failed to accept invite: {response.text}"
        data = response.json()
        
        assert 'message' in data, "message missing"
        assert 'student' in data, "student info missing"
        
        print(f"Parent accepted invite: {data['message']}")
    
    def test_04_parent_views_linked_students(self):
        """GET /api/parent/linked-students - parent sees linked students"""
        if not TestParentFeature.parent_token:
            pytest.skip("Parent token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/parent/linked-students",
            headers={"Authorization": f"Bearer {TestParentFeature.parent_token}"}
        )
        
        assert response.status_code == 200, f"Failed to get linked students: {response.text}"
        data = response.json()
        
        assert 'students' in data, "students field missing"
        
        # Should have at least one linked student from previous test
        if len(data['students']) > 0:
            student = data['students'][0]
            assert 'id' in student, "student id missing"
            assert 'username' in student, "student username missing"
            TestParentFeature.student_id = student['id']
        
        print(f"Parent has {len(data['students'])} linked students")
    
    def test_05_parent_views_student_dashboard(self):
        """GET /api/parent/student/{id}/dashboard - parent views student progress"""
        if not TestParentFeature.parent_token or not TestParentFeature.student_id:
            pytest.skip("Parent token or student ID not available")
        
        response = requests.get(
            f"{BASE_URL}/api/parent/student/{TestParentFeature.student_id}/dashboard",
            headers={"Authorization": f"Bearer {TestParentFeature.parent_token}"}
        )
        
        assert response.status_code == 200, f"Failed to get student dashboard: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert 'student' in data, "student field missing"
        assert 'weekly_stats' in data, "weekly_stats missing"
        assert 'monthly_stats' in data, "monthly_stats missing"
        assert 'pillars' in data, "pillars missing"
        assert 'badges_earned' in data, "badges_earned missing"
        
        # Verify student info
        student = data['student']
        assert 'id' in student, "student id missing"
        assert 'username' in student, "student username missing"
        assert 'current_streak' in student, "current_streak missing"
        
        print(f"Parent viewing student: {student['username']}, streak: {student['current_streak']}")
    
    def test_06_max_parents_limit_enforced(self):
        """Max 2 parents limit enforced"""
        if not TestParentFeature.student_token:
            pytest.skip("Student token not available")
        
        # Create a new student for this test
        new_student_email = f"limitstudent_{uuid.uuid4().hex[:6]}@test.com"
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": new_student_email,
            "username": f"limitstudent_{uuid.uuid4().hex[:4]}",
            "password": "test123456",
            "age": 15
        })
        
        if reg_resp.status_code != 200:
            pytest.skip("Could not create test student")
        
        new_student_token = reg_resp.json().get('token')
        
        # Invite first parent
        resp1 = requests.post(
            f"{BASE_URL}/api/parent/invite",
            json={"parent_email": f"parent1_{uuid.uuid4().hex[:6]}@test.com"},
            headers={"Authorization": f"Bearer {new_student_token}"}
        )
        assert resp1.status_code == 200, f"First invite failed: {resp1.text}"
        
        # Invite second parent
        resp2 = requests.post(
            f"{BASE_URL}/api/parent/invite",
            json={"parent_email": f"parent2_{uuid.uuid4().hex[:6]}@test.com"},
            headers={"Authorization": f"Bearer {new_student_token}"}
        )
        assert resp2.status_code == 200, f"Second invite failed: {resp2.text}"
        
        # Try to invite third parent - should fail
        resp3 = requests.post(
            f"{BASE_URL}/api/parent/invite",
            json={"parent_email": f"parent3_{uuid.uuid4().hex[:6]}@test.com"},
            headers={"Authorization": f"Bearer {new_student_token}"}
        )
        
        assert resp3.status_code == 400, f"Expected 400 for third parent, got {resp3.status_code}"
        assert "Maximum of 2 parents" in resp3.json().get('detail', ''), "Error message should mention max 2 parents"
        
        print("Max 2 parents limit correctly enforced")
    
    def test_07_unlink_parent(self):
        """DELETE /api/parent/unlink/{link_id} - unlink parent"""
        if not TestParentFeature.student_token:
            pytest.skip("Student token not available")
        
        # Get linked parents to find a link_id
        response = requests.get(
            f"{BASE_URL}/api/student/linked-parents",
            headers={"Authorization": f"Bearer {TestParentFeature.student_token}"}
        )
        
        if response.status_code != 200:
            pytest.skip("Could not get linked parents")
        
        data = response.json()
        
        # Find a link to unlink (prefer pending)
        link_id = None
        if data.get('pending_invites'):
            link_id = data['pending_invites'][0].get('link_id')
        elif data.get('active_parents'):
            link_id = data['active_parents'][0].get('link_id')
        
        if not link_id:
            pytest.skip("No links to unlink")
        
        # Unlink
        unlink_resp = requests.delete(
            f"{BASE_URL}/api/parent/unlink/{link_id}",
            headers={"Authorization": f"Bearer {TestParentFeature.student_token}"}
        )
        
        assert unlink_resp.status_code == 200, f"Failed to unlink: {unlink_resp.text}"
        assert 'message' in unlink_resp.json(), "message missing in response"
        
        print(f"Successfully unlinked parent link: {link_id}")
    
    def test_08_invalid_invite_code_rejected(self):
        """Invalid invite code returns 404"""
        if not TestParentFeature.parent_token:
            pytest.skip("Parent token not available")
        
        response = requests.post(
            f"{BASE_URL}/api/parent/accept",
            json={"invite_code": "PARENT-INVALID123"},
            headers={"Authorization": f"Bearer {TestParentFeature.parent_token}"}
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Invalid invite code correctly rejected")


class TestCoachGroupCreation:
    """Additional tests for coach group creation"""
    
    def test_create_regular_group_no_coach_id(self):
        """Creating regular group (is_coach=false) should not set coach_id"""
        # Register a user
        email = f"regulargroup_{uuid.uuid4().hex[:6]}@test.com"
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": f"regular_{uuid.uuid4().hex[:4]}",
            "password": "test123456",
            "age": 16
        })
        
        if reg_resp.status_code != 200:
            pytest.skip("Could not create test user")
        
        token = reg_resp.json().get('token')
        
        # Create regular group
        response = requests.post(
            f"{BASE_URL}/api/groups",
            json={
                "name": f"Regular Group {uuid.uuid4().hex[:4]}",
                "type": "private",
                "is_coach": False
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Failed to create group: {response.text}"
        data = response.json()
        
        # coach_id should be None for regular groups
        assert data.get('coach_id') is None, f"coach_id should be None for regular group, got {data.get('coach_id')}"
        print("Regular group created without coach_id")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
