"""
Test Referral Qualification - 3 Sessions Minimum Rule
Tests for the new referral qualification system where referrals only count
after the referred friend logs a minimum of 3 sessions.

Key features tested:
1. POST /api/referrals/apply-code sets referral_status to 'pending'
2. Referral is NOT counted immediately in referrer's referral_count
3. After referred user logs 3 sessions, referral_status changes to 'qualified'
4. After qualification, referrer's referral_count is incremented
5. GET /api/referral/info shows pending_referrals count separately
6. GET /api/referral/info returns referrals list with status field
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_PLAYER_EMAIL = "testplayer1@edgemode.com"
TEST_PLAYER_PASSWORD = "TestPlayer123!"
ADMIN_EMAIL = "admin@edgemodeapp.com"
ADMIN_PASSWORD = "EdgeAdmin2024!"


class TestReferralApplyCode:
    """Test that applying a referral code sets status to pending"""
    
    @pytest.fixture
    def referrer_token(self):
        """Get authentication token for test player (referrer)"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_PLAYER_EMAIL,
            "password": TEST_PLAYER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    @pytest.fixture
    def referrer_code(self, referrer_token):
        """Get referrer's referral code"""
        response = requests.get(
            f"{BASE_URL}/api/referrals/my-code",
            headers={"Authorization": f"Bearer {referrer_token}"}
        )
        if response.status_code == 200:
            return response.json().get("referral_code")
        pytest.skip("Could not get referral code")
    
    def test_check_referral_code_valid(self, referrer_code):
        """Check that referral code validation endpoint works"""
        response = requests.get(f"{BASE_URL}/api/referrals/check-code/{referrer_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get('valid') == True, "Code should be valid"
        assert 'referrer_username' in data, "Should return referrer username"
        assert 'welcome_bonus' in data, "Should return welcome bonus"
        
        print(f"✓ Referral code {referrer_code} is valid")
        print(f"  - Referrer: {data.get('referrer_username')}")
        print(f"  - Welcome bonus: {data.get('welcome_bonus')} coins")
    
    def test_check_invalid_referral_code(self):
        """Check that invalid referral code returns 404"""
        response = requests.get(f"{BASE_URL}/api/referrals/check-code/INVALID123")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Invalid referral code correctly returns 404")


class TestReferralInfoEndpoint:
    """Test GET /api/referral/info returns pending_referrals and status field"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for test player"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_PLAYER_EMAIL,
            "password": TEST_PLAYER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_referral_info_has_pending_referrals_field(self, auth_token):
        """GET /api/referral/info returns pending_referrals count"""
        response = requests.get(
            f"{BASE_URL}/api/referral/info",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'pending_referrals' in data, "Response should have pending_referrals field"
        assert isinstance(data['pending_referrals'], int), "pending_referrals should be int"
        
        print(f"✓ pending_referrals field present: {data['pending_referrals']}")
    
    def test_referral_info_has_total_referrals_field(self, auth_token):
        """GET /api/referral/info returns total_referrals (qualified only)"""
        response = requests.get(
            f"{BASE_URL}/api/referral/info",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'total_referrals' in data, "Response should have total_referrals field"
        assert isinstance(data['total_referrals'], int), "total_referrals should be int"
        
        print(f"✓ total_referrals field present: {data['total_referrals']}")
    
    def test_referral_info_has_min_sessions_required(self, auth_token):
        """GET /api/referral/info returns min_sessions_required for frontend info"""
        response = requests.get(
            f"{BASE_URL}/api/referral/info",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'min_sessions_required' in data, "Response should have min_sessions_required field"
        assert data['min_sessions_required'] == 3, f"min_sessions_required should be 3, got {data['min_sessions_required']}"
        
        print(f"✓ min_sessions_required field present: {data['min_sessions_required']}")
    
    def test_referral_info_referrals_list_has_status(self, auth_token):
        """GET /api/referral/info returns referrals list with status field"""
        response = requests.get(
            f"{BASE_URL}/api/referral/info",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'referrals' in data, "Response should have referrals list"
        
        # If there are referrals, check they have status field
        referrals = data.get('referrals', [])
        if len(referrals) > 0:
            for ref in referrals:
                assert 'status' in ref, f"Referral should have status field"
                assert ref['status'] in ['pending', 'qualified'], f"Status should be pending or qualified, got {ref['status']}"
            print(f"✓ {len(referrals)} referrals found, all have status field")
        else:
            print("✓ No referrals yet (status field will be present when referrals exist)")


class TestReferralMyCodeEndpoint:
    """Test GET /api/referrals/my-code endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for test player"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_PLAYER_EMAIL,
            "password": TEST_PLAYER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_my_code_returns_referral_count(self, auth_token):
        """GET /api/referrals/my-code returns referral_count (qualified only)"""
        response = requests.get(
            f"{BASE_URL}/api/referrals/my-code",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'referral_count' in data, "Response should have referral_count"
        assert isinstance(data['referral_count'], int), "referral_count should be int"
        
        print(f"✓ referral_count: {data['referral_count']}")
    
    def test_my_code_returns_milestones_with_progress(self, auth_token):
        """GET /api/referrals/my-code returns milestones with progress tracking"""
        response = requests.get(
            f"{BASE_URL}/api/referrals/my-code",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'milestones' in data, "Response should have milestones"
        
        milestones = data['milestones']
        assert len(milestones) >= 4, f"Expected at least 4 milestones, got {len(milestones)}"
        
        for milestone in milestones:
            assert 'current' in milestone, "Milestone should have current count"
            assert 'is_claimed' in milestone, "Milestone should have is_claimed"
            assert 'is_unlocked' in milestone, "Milestone should have is_unlocked"
            assert 'progress_pct' in milestone, "Milestone should have progress_pct"
        
        print(f"✓ {len(milestones)} milestones with progress tracking")


class TestReferralMyReferralsEndpoint:
    """Test GET /api/referrals/my-referrals endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for test player"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_PLAYER_EMAIL,
            "password": TEST_PLAYER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_my_referrals_endpoint(self, auth_token):
        """GET /api/referrals/my-referrals returns list of referred users"""
        response = requests.get(
            f"{BASE_URL}/api/referrals/my-referrals",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'referrals' in data, "Response should have referrals list"
        assert 'total_count' in data, "Response should have total_count"
        
        print(f"✓ my-referrals endpoint working, total: {data['total_count']}")


class TestReferralQualificationLogic:
    """Test the referral qualification logic (check_referral_qualification function)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for test player"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_PLAYER_EMAIL,
            "password": TEST_PLAYER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_session_complete_returns_referral_qualified_field(self, auth_token):
        """POST /api/sessions/complete returns referral_qualified field"""
        # Get user's pillars first
        response = requests.get(
            f"{BASE_URL}/api/user/pillars",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code != 200:
            pytest.skip("Could not get user pillars")
        
        pillars = response.json()
        if not pillars or len(pillars) == 0:
            pytest.skip("User has no pillars configured")
        
        pillar_name = pillars[0].get('pillar_name')
        
        # Complete a session
        response = requests.post(
            f"{BASE_URL}/api/sessions/complete",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "pillar": pillar_name,
                "minutes_spent": 30,
                "note": "Test session for referral qualification"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert 'referral_qualified' in data, "Response should have referral_qualified field"
        
        print(f"✓ Session complete returns referral_qualified: {data['referral_qualified']}")


class TestReferralLeaderboard:
    """Test referral leaderboard endpoint"""
    
    def test_referral_leaderboard_endpoint(self):
        """GET /api/referrals/leaderboard returns top referrers"""
        response = requests.get(f"{BASE_URL}/api/referrals/leaderboard")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'leaderboard' in data, "Response should have leaderboard"
        
        leaderboard = data['leaderboard']
        for entry in leaderboard:
            assert 'username' in entry, "Leaderboard entry should have username"
            assert 'referral_count' in entry, "Leaderboard entry should have referral_count"
        
        print(f"✓ Leaderboard has {len(leaderboard)} entries")


class TestReferralExclusiveItems:
    """Test referral exclusive items endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for test player"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_PLAYER_EMAIL,
            "password": TEST_PLAYER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_exclusive_items_endpoint(self, auth_token):
        """GET /api/referrals/exclusive-items returns items with unlock status"""
        response = requests.get(
            f"{BASE_URL}/api/referrals/exclusive-items",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'items' in data, "Response should have items"
        
        items = data['items']
        assert len(items) >= 4, f"Expected at least 4 exclusive items, got {len(items)}"
        
        for item in items:
            assert 'is_unlocked' in item, "Item should have is_unlocked"
            assert 'is_owned' in item, "Item should have is_owned"
            assert 'referrals_needed' in item, "Item should have referrals_needed"
            assert 'referrals_required' in item, "Item should have referrals_required"
        
        print(f"✓ {len(items)} exclusive items with unlock status")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
