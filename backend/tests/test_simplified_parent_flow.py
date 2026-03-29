"""
Test Simplified Parent Access Flow
- POST /api/parent/add - adds parent email directly (status becomes 'active' immediately)
- GET /api/student/linked-parents - returns list of parent emails with added_at timestamp
- DELETE /api/parent/remove/{link_id} - removes parent from receiving reports
- Maximum 2 parents per student validation
- Duplicate email validation
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSimplifiedParentFlow:
    """Test simplified parent access flow - no account needed for parents"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with auth and clean up existing parents"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as coach to get token
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testcoach@edgemode.com",
            "password": "TestCoach123!"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            self.token = token
            
            # Clean up any existing parents to start fresh
            self._cleanup_parents()
        else:
            pytest.skip("Authentication failed - skipping tests")
    
    def _cleanup_parents(self):
        """Helper to remove all existing parents"""
        try:
            list_response = self.session.get(f"{BASE_URL}/api/student/linked-parents")
            if list_response.status_code == 200:
                for parent in list_response.json().get("parents", []):
                    self.session.delete(f"{BASE_URL}/api/parent/remove/{parent['link_id']}")
        except Exception:
            pass
    
    # ============ POST /api/parent/add Tests ============
    
    def test_add_parent_email_success(self):
        """Test adding a parent email - should be immediately active"""
        unique_email = f"testparent_{uuid.uuid4().hex[:8]}@example.com"
        
        response = self.session.post(f"{BASE_URL}/api/parent/add", json={
            "parent_email": unique_email
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "message" in data
        assert "parent_email" in data
        assert unique_email in data["parent_email"]
        assert "will receive weekly reports" in data["message"]
        
        print(f"PASS: Added parent email {unique_email} successfully")
    
    def test_add_parent_duplicate_email_rejected(self):
        """Test that duplicate parent email is rejected"""
        unique_email = f"testparent_dup_{uuid.uuid4().hex[:8]}@example.com"
        
        # Add first time
        response1 = self.session.post(f"{BASE_URL}/api/parent/add", json={
            "parent_email": unique_email
        })
        assert response1.status_code == 200
        
        # Try to add same email again
        response2 = self.session.post(f"{BASE_URL}/api/parent/add", json={
            "parent_email": unique_email
        })
        
        assert response2.status_code == 400, f"Expected 400 for duplicate, got {response2.status_code}"
        data = response2.json()
        assert "already added" in data.get("detail", "").lower()
        
        print("PASS: Duplicate parent email correctly rejected")
    
    def test_add_parent_case_insensitive_email(self):
        """Test that email comparison is case-insensitive"""
        unique_email = f"TestParent_Case_{uuid.uuid4().hex[:8]}@Example.COM"
        
        # Add with mixed case
        response1 = self.session.post(f"{BASE_URL}/api/parent/add", json={
            "parent_email": unique_email
        })
        assert response1.status_code == 200
        
        # Try to add same email with different case
        response2 = self.session.post(f"{BASE_URL}/api/parent/add", json={
            "parent_email": unique_email.lower()
        })
        
        assert response2.status_code == 400, f"Expected 400 for case-insensitive duplicate, got {response2.status_code}"
        
        print("PASS: Email comparison is case-insensitive")
    
    def test_add_parent_requires_auth(self):
        """Test that adding parent requires authentication"""
        no_auth_session = requests.Session()
        no_auth_session.headers.update({"Content-Type": "application/json"})
        
        response = no_auth_session.post(f"{BASE_URL}/api/parent/add", json={
            "parent_email": "noauth@example.com"
        })
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        
        print("PASS: Add parent requires authentication")
    
    # ============ GET /api/student/linked-parents Tests ============
    
    def test_get_linked_parents_returns_list(self):
        """Test getting linked parents returns proper structure"""
        response = self.session.get(f"{BASE_URL}/api/student/linked-parents")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "parents" in data
        assert "max_parents" in data
        assert "slots_remaining" in data
        assert data["max_parents"] == 2
        assert isinstance(data["parents"], list)
        
        print(f"PASS: Get linked parents returns proper structure with {len(data['parents'])} parents")
    
    def test_linked_parents_have_required_fields(self):
        """Test that each parent in list has required fields"""
        # First add a parent to ensure we have data
        unique_email = f"testparent_fields_{uuid.uuid4().hex[:8]}@example.com"
        self.session.post(f"{BASE_URL}/api/parent/add", json={
            "parent_email": unique_email
        })
        
        response = self.session.get(f"{BASE_URL}/api/student/linked-parents")
        assert response.status_code == 200
        data = response.json()
        
        if data["parents"]:
            parent = data["parents"][0]
            assert "link_id" in parent, "Missing link_id field"
            assert "parent_email" in parent, "Missing parent_email field"
            assert "added_at" in parent, "Missing added_at field"
            
            print(f"PASS: Parent has all required fields: link_id, parent_email, added_at")
        else:
            print("SKIP: No parents to verify fields")
    
    def test_linked_parents_requires_auth(self):
        """Test that getting linked parents requires authentication"""
        no_auth_session = requests.Session()
        
        response = no_auth_session.get(f"{BASE_URL}/api/student/linked-parents")
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        
        print("PASS: Get linked parents requires authentication")
    
    # ============ DELETE /api/parent/remove/{link_id} Tests ============
    
    def test_remove_parent_success(self):
        """Test removing a parent successfully"""
        # First add a parent
        unique_email = f"testparent_remove_{uuid.uuid4().hex[:8]}@example.com"
        add_response = self.session.post(f"{BASE_URL}/api/parent/add", json={
            "parent_email": unique_email
        })
        assert add_response.status_code == 200
        
        # Get the link_id
        list_response = self.session.get(f"{BASE_URL}/api/student/linked-parents")
        assert list_response.status_code == 200
        parents = list_response.json()["parents"]
        
        # Find the parent we just added
        link_id = None
        for parent in parents:
            if parent["parent_email"] == unique_email.lower():
                link_id = parent["link_id"]
                break
        
        assert link_id is not None, "Could not find added parent"
        
        # Remove the parent
        remove_response = self.session.delete(f"{BASE_URL}/api/parent/remove/{link_id}")
        
        assert remove_response.status_code == 200, f"Expected 200, got {remove_response.status_code}: {remove_response.text}"
        data = remove_response.json()
        assert "message" in data
        assert "removed" in data["message"].lower()
        
        print(f"PASS: Removed parent {unique_email} successfully")
    
    def test_remove_parent_invalid_link_id(self):
        """Test removing with invalid link_id returns 404"""
        fake_link_id = str(uuid.uuid4())
        
        response = self.session.delete(f"{BASE_URL}/api/parent/remove/{fake_link_id}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        
        print("PASS: Remove with invalid link_id returns 404")
    
    def test_remove_parent_requires_auth(self):
        """Test that removing parent requires authentication"""
        no_auth_session = requests.Session()
        
        response = no_auth_session.delete(f"{BASE_URL}/api/parent/remove/some-link-id")
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        
        print("PASS: Remove parent requires authentication")
    
    # ============ Maximum 2 Parents Validation ============
    
    def test_maximum_two_parents_validation(self):
        """Test that maximum 2 parents can be added"""
        # First, clean up any existing parents by getting and removing them
        list_response = self.session.get(f"{BASE_URL}/api/student/linked-parents")
        if list_response.status_code == 200:
            for parent in list_response.json().get("parents", []):
                self.session.delete(f"{BASE_URL}/api/parent/remove/{parent['link_id']}")
        
        # Add first parent
        email1 = f"testparent_max1_{uuid.uuid4().hex[:8]}@example.com"
        response1 = self.session.post(f"{BASE_URL}/api/parent/add", json={
            "parent_email": email1
        })
        assert response1.status_code == 200, f"Failed to add first parent: {response1.text}"
        
        # Add second parent
        email2 = f"testparent_max2_{uuid.uuid4().hex[:8]}@example.com"
        response2 = self.session.post(f"{BASE_URL}/api/parent/add", json={
            "parent_email": email2
        })
        assert response2.status_code == 200, f"Failed to add second parent: {response2.text}"
        
        # Try to add third parent - should fail
        email3 = f"testparent_max3_{uuid.uuid4().hex[:8]}@example.com"
        response3 = self.session.post(f"{BASE_URL}/api/parent/add", json={
            "parent_email": email3
        })
        
        assert response3.status_code == 400, f"Expected 400 for third parent, got {response3.status_code}"
        data = response3.json()
        assert "maximum" in data.get("detail", "").lower() or "2" in data.get("detail", "")
        
        print("PASS: Maximum 2 parents validation works correctly")
    
    # ============ Legacy Endpoint Backwards Compatibility ============
    
    def test_legacy_invite_endpoint_works(self):
        """Test that legacy /api/parent/invite endpoint still works"""
        unique_email = f"testparent_legacy_{uuid.uuid4().hex[:8]}@example.com"
        
        response = self.session.post(f"{BASE_URL}/api/parent/invite", json={
            "parent_email": unique_email
        })
        
        # Should work and redirect to new flow
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data
        
        print("PASS: Legacy /api/parent/invite endpoint works (backwards compatible)")
    
    # ============ Slots Remaining Calculation ============
    
    def test_slots_remaining_calculation(self):
        """Test that slots_remaining is calculated correctly"""
        # Clean up existing parents
        list_response = self.session.get(f"{BASE_URL}/api/student/linked-parents")
        if list_response.status_code == 200:
            for parent in list_response.json().get("parents", []):
                self.session.delete(f"{BASE_URL}/api/parent/remove/{parent['link_id']}")
        
        # Check initial slots (should be 2)
        response1 = self.session.get(f"{BASE_URL}/api/student/linked-parents")
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["slots_remaining"] == 2, f"Expected 2 slots, got {data1['slots_remaining']}"
        
        # Add one parent
        email1 = f"testparent_slots_{uuid.uuid4().hex[:8]}@example.com"
        self.session.post(f"{BASE_URL}/api/parent/add", json={"parent_email": email1})
        
        # Check slots (should be 1)
        response2 = self.session.get(f"{BASE_URL}/api/student/linked-parents")
        data2 = response2.json()
        assert data2["slots_remaining"] == 1, f"Expected 1 slot, got {data2['slots_remaining']}"
        
        # Add second parent
        email2 = f"testparent_slots2_{uuid.uuid4().hex[:8]}@example.com"
        self.session.post(f"{BASE_URL}/api/parent/add", json={"parent_email": email2})
        
        # Check slots (should be 0)
        response3 = self.session.get(f"{BASE_URL}/api/student/linked-parents")
        data3 = response3.json()
        assert data3["slots_remaining"] == 0, f"Expected 0 slots, got {data3['slots_remaining']}"
        
        print("PASS: Slots remaining calculation is correct")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
