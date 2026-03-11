"""
Test Social Proof Feature - Platform Stats & Testimonials
Tests:
- Public /api/platform-stats endpoint (no auth required)
- Admin settings toggle for social proof
- Admin testimonial CRUD operations
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "admin@edgemodeapp.com"
ADMIN_PASSWORD = "EdgeAdmin2024!"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.status_code}")
    return response.json().get("token")


@pytest.fixture
def admin_headers(admin_token):
    """Headers with admin auth token"""
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }


class TestPublicPlatformStats:
    """Test public /api/platform-stats endpoint - NO AUTH REQUIRED"""
    
    def test_platform_stats_no_auth_required(self):
        """Platform stats should be accessible without authentication"""
        response = requests.get(f"{BASE_URL}/api/platform-stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "enabled" in data, "Response should have 'enabled' field"
    
    def test_platform_stats_returns_stats_when_enabled(self, admin_headers):
        """When enabled, platform stats should return stats and testimonials"""
        # First ensure social proof is enabled
        requests.put(
            f"{BASE_URL}/api/admin/settings?social_proof_enabled=true",
            headers=admin_headers
        )
        
        response = requests.get(f"{BASE_URL}/api/platform-stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["enabled"] == True, "Social proof should be enabled"
        assert "stats" in data, "Response should have 'stats' field"
        assert "testimonials" in data, "Response should have 'testimonials' field"
        
        # Verify stats structure
        stats = data["stats"]
        assert "total_users" in stats, "Stats should have total_users"
        assert "sessions_logged" in stats, "Stats should have sessions_logged"
        assert "badges_earned" in stats, "Stats should have badges_earned"
        assert "hours_logged" in stats, "Stats should have hours_logged"
        
        # Verify stats are numbers
        assert isinstance(stats["total_users"], int), "total_users should be int"
        assert isinstance(stats["sessions_logged"], int), "sessions_logged should be int"
        assert isinstance(stats["badges_earned"], int), "badges_earned should be int"
        assert isinstance(stats["hours_logged"], int), "hours_logged should be int"
    
    def test_platform_stats_returns_empty_when_disabled(self, admin_headers):
        """When disabled, platform stats should return enabled=false with empty data"""
        # Disable social proof
        requests.put(
            f"{BASE_URL}/api/admin/settings?social_proof_enabled=false",
            headers=admin_headers
        )
        
        response = requests.get(f"{BASE_URL}/api/platform-stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["enabled"] == False, "Social proof should be disabled"
        assert data["stats"] == {}, "Stats should be empty when disabled"
        assert data["testimonials"] == [], "Testimonials should be empty when disabled"
        
        # Re-enable for other tests
        requests.put(
            f"{BASE_URL}/api/admin/settings?social_proof_enabled=true",
            headers=admin_headers
        )


class TestAdminSiteSettings:
    """Test admin site settings endpoints - REQUIRES ADMIN AUTH"""
    
    def test_get_settings_requires_auth(self):
        """GET /api/admin/settings should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/settings")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_get_settings_with_admin_auth(self, admin_headers):
        """GET /api/admin/settings should return settings for admin"""
        response = requests.get(
            f"{BASE_URL}/api/admin/settings",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data, "Settings should have 'id' field"
        assert "social_proof_enabled" in data, "Settings should have 'social_proof_enabled' field"
        assert "testimonials" in data, "Settings should have 'testimonials' field"
        assert isinstance(data["testimonials"], list), "Testimonials should be a list"
    
    def test_toggle_social_proof_on(self, admin_headers):
        """PUT /api/admin/settings should enable social proof"""
        response = requests.put(
            f"{BASE_URL}/api/admin/settings?social_proof_enabled=true",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["social_proof_enabled"] == True, "Social proof should be enabled"
    
    def test_toggle_social_proof_off(self, admin_headers):
        """PUT /api/admin/settings should disable social proof"""
        response = requests.put(
            f"{BASE_URL}/api/admin/settings?social_proof_enabled=false",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["social_proof_enabled"] == False, "Social proof should be disabled"
        
        # Re-enable for other tests
        requests.put(
            f"{BASE_URL}/api/admin/settings?social_proof_enabled=true",
            headers=admin_headers
        )
    
    def test_update_settings_requires_auth(self):
        """PUT /api/admin/settings should require authentication"""
        response = requests.put(
            f"{BASE_URL}/api/admin/settings?social_proof_enabled=false"
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"


class TestAdminTestimonials:
    """Test admin testimonial CRUD operations - REQUIRES ADMIN AUTH"""
    
    def test_add_testimonial_requires_auth(self):
        """POST /api/admin/testimonials should require authentication"""
        response = requests.post(
            f"{BASE_URL}/api/admin/testimonials?name=Test&role=Test&quote=Test"
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_add_testimonial(self, admin_headers):
        """POST /api/admin/testimonials should add a new testimonial"""
        test_name = f"TEST_User_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(
            f"{BASE_URL}/api/admin/testimonials?name={test_name}&role=Test%20Role&quote=This%20is%20a%20test%20testimonial&avatar_url=",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Testimonial added"
        assert "testimonial" in data
        
        testimonial = data["testimonial"]
        assert testimonial["name"] == test_name
        assert testimonial["role"] == "Test Role"
        assert testimonial["quote"] == "This is a test testimonial"
        assert "id" in testimonial
        assert "created_at" in testimonial
        
        # Cleanup - delete the test testimonial
        requests.delete(
            f"{BASE_URL}/api/admin/testimonials/{testimonial['id']}",
            headers=admin_headers
        )
    
    def test_add_and_verify_testimonial_persistence(self, admin_headers):
        """Testimonial should persist in settings after creation"""
        test_name = f"TEST_Persist_{uuid.uuid4().hex[:8]}"
        
        # Add testimonial
        add_response = requests.post(
            f"{BASE_URL}/api/admin/testimonials?name={test_name}&role=Persistence%20Test&quote=Testing%20persistence&avatar_url=",
            headers=admin_headers
        )
        assert add_response.status_code == 200
        testimonial_id = add_response.json()["testimonial"]["id"]
        
        # Verify in settings
        settings_response = requests.get(
            f"{BASE_URL}/api/admin/settings",
            headers=admin_headers
        )
        assert settings_response.status_code == 200
        
        testimonials = settings_response.json()["testimonials"]
        found = any(t["id"] == testimonial_id for t in testimonials)
        assert found, f"Testimonial {testimonial_id} should be in settings"
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/admin/testimonials/{testimonial_id}",
            headers=admin_headers
        )
    
    def test_delete_testimonial_requires_auth(self):
        """DELETE /api/admin/testimonials/{id} should require authentication"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/testimonials/some-id"
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_delete_testimonial(self, admin_headers):
        """DELETE /api/admin/testimonials/{id} should remove testimonial"""
        test_name = f"TEST_Delete_{uuid.uuid4().hex[:8]}"
        
        # First add a testimonial
        add_response = requests.post(
            f"{BASE_URL}/api/admin/testimonials?name={test_name}&role=Delete%20Test&quote=To%20be%20deleted&avatar_url=",
            headers=admin_headers
        )
        assert add_response.status_code == 200
        testimonial_id = add_response.json()["testimonial"]["id"]
        
        # Delete it
        delete_response = requests.delete(
            f"{BASE_URL}/api/admin/testimonials/{testimonial_id}",
            headers=admin_headers
        )
        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "Testimonial deleted"
        
        # Verify it's gone
        settings_response = requests.get(
            f"{BASE_URL}/api/admin/settings",
            headers=admin_headers
        )
        testimonials = settings_response.json()["testimonials"]
        found = any(t["id"] == testimonial_id for t in testimonials)
        assert not found, f"Testimonial {testimonial_id} should be deleted"
    
    def test_testimonials_appear_in_public_stats(self, admin_headers):
        """Testimonials should appear in public platform-stats when enabled"""
        test_name = f"TEST_Public_{uuid.uuid4().hex[:8]}"
        
        # Ensure social proof is enabled
        requests.put(
            f"{BASE_URL}/api/admin/settings?social_proof_enabled=true",
            headers=admin_headers
        )
        
        # Add testimonial
        add_response = requests.post(
            f"{BASE_URL}/api/admin/testimonials?name={test_name}&role=Public%20Test&quote=Should%20appear%20publicly&avatar_url=",
            headers=admin_headers
        )
        testimonial_id = add_response.json()["testimonial"]["id"]
        
        # Check public endpoint
        public_response = requests.get(f"{BASE_URL}/api/platform-stats")
        assert public_response.status_code == 200
        
        testimonials = public_response.json()["testimonials"]
        found = any(t["id"] == testimonial_id for t in testimonials)
        assert found, "New testimonial should appear in public stats"
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/admin/testimonials/{testimonial_id}",
            headers=admin_headers
        )


class TestIntegration:
    """Integration tests for social proof feature"""
    
    def test_full_toggle_flow(self, admin_headers):
        """Test complete enable/disable flow with verification"""
        # 1. Enable social proof
        enable_response = requests.put(
            f"{BASE_URL}/api/admin/settings?social_proof_enabled=true",
            headers=admin_headers
        )
        assert enable_response.status_code == 200
        
        # 2. Verify public endpoint shows data
        public_enabled = requests.get(f"{BASE_URL}/api/platform-stats")
        assert public_enabled.json()["enabled"] == True
        assert "total_users" in public_enabled.json()["stats"]
        
        # 3. Disable social proof
        disable_response = requests.put(
            f"{BASE_URL}/api/admin/settings?social_proof_enabled=false",
            headers=admin_headers
        )
        assert disable_response.status_code == 200
        
        # 4. Verify public endpoint hides data
        public_disabled = requests.get(f"{BASE_URL}/api/platform-stats")
        assert public_disabled.json()["enabled"] == False
        assert public_disabled.json()["stats"] == {}
        
        # 5. Re-enable for cleanup
        requests.put(
            f"{BASE_URL}/api/admin/settings?social_proof_enabled=true",
            headers=admin_headers
        )
