"""
Push Notification API Tests for Edge Mode
Tests VAPID key endpoint, subscribe, unsubscribe, status, and test notification endpoints
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "refactortest@example.com"
TEST_PASSWORD = "test123"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get authentication token for test user"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Authentication failed - status {response.status_code}: {response.text}")


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


class TestVAPIDKeyEndpoint:
    """Tests for GET /api/push/vapid-key"""
    
    def test_vapid_key_returns_public_key(self, api_client):
        """Test that VAPID public key endpoint returns the key"""
        response = api_client.get(f"{BASE_URL}/api/push/vapid-key")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "publicKey" in data, "Response should contain 'publicKey'"
        assert isinstance(data["publicKey"], str), "publicKey should be a string"
        assert len(data["publicKey"]) > 50, "publicKey should be a valid VAPID key (>50 chars)"
        
        # VAPID keys are base64url encoded
        assert data["publicKey"].startswith("BL"), "VAPID public key should start with 'BL'"


class TestPushSubscription:
    """Tests for POST /api/push/subscribe"""
    
    def test_subscribe_requires_auth(self, api_client):
        """Test that subscribe endpoint requires authentication"""
        # Remove auth header temporarily
        original_auth = api_client.headers.pop("Authorization", None)
        
        response = api_client.post(f"{BASE_URL}/api/push/subscribe", json={
            "endpoint": "https://test.push.service/test",
            "keys": {"p256dh": "test_key", "auth": "test_auth"}
        })
        
        # Restore auth header
        if original_auth:
            api_client.headers["Authorization"] = original_auth
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
    
    def test_subscribe_with_valid_data(self, authenticated_client):
        """Test subscribing with valid push subscription data"""
        # Generate unique endpoint to avoid conflicts
        unique_endpoint = f"https://test.push.service/TEST_{uuid.uuid4()}"
        
        response = authenticated_client.post(f"{BASE_URL}/api/push/subscribe", json={
            "endpoint": unique_endpoint,
            "keys": {
                "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8QcYP7DkM",
                "auth": "tBHItJI5svbpez7KI4CCXg"
            }
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Response should contain 'message'"
        assert "subscription_id" in data, "Response should contain 'subscription_id'"
        assert data["message"] in ["Subscribed successfully", "Subscription updated"]
    
    def test_subscribe_updates_existing(self, authenticated_client):
        """Test that subscribing with same endpoint updates existing subscription"""
        unique_endpoint = f"https://test.push.service/TEST_update_{uuid.uuid4()}"
        
        # First subscription
        response1 = authenticated_client.post(f"{BASE_URL}/api/push/subscribe", json={
            "endpoint": unique_endpoint,
            "keys": {"p256dh": "key1", "auth": "auth1"}
        })
        assert response1.status_code == 200
        sub_id_1 = response1.json().get("subscription_id")
        
        # Second subscription with same endpoint
        response2 = authenticated_client.post(f"{BASE_URL}/api/push/subscribe", json={
            "endpoint": unique_endpoint,
            "keys": {"p256dh": "key2", "auth": "auth2"}
        })
        assert response2.status_code == 200
        
        data = response2.json()
        assert data["message"] == "Subscription updated"
        assert data["subscription_id"] == sub_id_1, "Should return same subscription ID"


class TestPushStatus:
    """Tests for GET /api/push/status"""
    
    def test_status_requires_auth(self, api_client):
        """Test that status endpoint requires authentication"""
        original_auth = api_client.headers.pop("Authorization", None)
        
        response = api_client.get(f"{BASE_URL}/api/push/status")
        
        if original_auth:
            api_client.headers["Authorization"] = original_auth
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
    
    def test_status_returns_push_info(self, authenticated_client):
        """Test that status endpoint returns push notification info"""
        response = authenticated_client.get(f"{BASE_URL}/api/push/status")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "push_enabled" in data, "Response should contain 'push_enabled'"
        assert "subscribed_devices" in data, "Response should contain 'subscribed_devices'"
        assert "vapid_configured" in data, "Response should contain 'vapid_configured'"
        
        assert isinstance(data["push_enabled"], bool), "push_enabled should be boolean"
        assert isinstance(data["subscribed_devices"], int), "subscribed_devices should be integer"
        assert data["vapid_configured"] == True, "VAPID should be configured"


class TestPushUnsubscribe:
    """Tests for DELETE /api/push/unsubscribe"""
    
    def test_unsubscribe_requires_auth(self, api_client):
        """Test that unsubscribe endpoint requires authentication"""
        original_auth = api_client.headers.pop("Authorization", None)
        
        response = api_client.delete(f"{BASE_URL}/api/push/unsubscribe")
        
        if original_auth:
            api_client.headers["Authorization"] = original_auth
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
    
    def test_unsubscribe_removes_subscriptions(self, authenticated_client):
        """Test that unsubscribe removes all user subscriptions"""
        # First subscribe
        unique_endpoint = f"https://test.push.service/TEST_unsub_{uuid.uuid4()}"
        authenticated_client.post(f"{BASE_URL}/api/push/subscribe", json={
            "endpoint": unique_endpoint,
            "keys": {"p256dh": "test", "auth": "test"}
        })
        
        # Then unsubscribe
        response = authenticated_client.delete(f"{BASE_URL}/api/push/unsubscribe")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Response should contain 'message'"
        assert "removed" in data, "Response should contain 'removed' count"
        assert data["message"] == "Unsubscribed from push notifications"


class TestPushTestNotification:
    """Tests for POST /api/push/test"""
    
    def test_test_notification_requires_auth(self, api_client):
        """Test that test notification endpoint requires authentication"""
        original_auth = api_client.headers.pop("Authorization", None)
        
        response = api_client.post(f"{BASE_URL}/api/push/test")
        
        if original_auth:
            api_client.headers["Authorization"] = original_auth
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
    
    def test_test_notification_without_subscription(self, authenticated_client):
        """Test that test notification fails without active subscription"""
        # First unsubscribe to ensure no subscriptions
        authenticated_client.delete(f"{BASE_URL}/api/push/unsubscribe")
        
        response = authenticated_client.post(f"{BASE_URL}/api/push/test")
        
        # Should return 404 when no subscriptions exist
        assert response.status_code == 404, f"Expected 404 without subscriptions, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "detail" in data, "Response should contain error detail"
        assert "No active push subscriptions" in data["detail"]
    
    def test_test_notification_with_subscription(self, authenticated_client):
        """Test sending test notification with active subscription"""
        # First subscribe
        unique_endpoint = f"https://test.push.service/TEST_testnotif_{uuid.uuid4()}"
        sub_response = authenticated_client.post(f"{BASE_URL}/api/push/subscribe", json={
            "endpoint": unique_endpoint,
            "keys": {
                "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8QcYP7DkM",
                "auth": "tBHItJI5svbpez7KI4CCXg"
            }
        })
        assert sub_response.status_code == 200, f"Subscribe failed: {sub_response.text}"
        
        # Send test notification
        response = authenticated_client.post(f"{BASE_URL}/api/push/test")
        
        # Note: The actual push will fail because the endpoint is fake,
        # but the endpoint should still process the request
        # It may return 200 (if it counts as sent) or 404 (if subscription was cleaned up)
        assert response.status_code in [200, 404], f"Unexpected status {response.status_code}: {response.text}"


class TestServiceWorkerFile:
    """Tests for service worker file availability"""
    
    def test_service_worker_exists(self, api_client):
        """Test that service worker file is accessible"""
        response = api_client.get(f"{BASE_URL}/sw.js")
        
        assert response.status_code == 200, f"Service worker not found, got {response.status_code}"
        
        # Check content type
        content_type = response.headers.get("content-type", "")
        assert "javascript" in content_type or "text" in content_type, f"Unexpected content type: {content_type}"
        
        # Check that it contains push event handler
        content = response.text
        assert "push" in content.lower(), "Service worker should handle push events"
        assert "notificationclick" in content.lower(), "Service worker should handle notification clicks"


class TestSchedulerIntegration:
    """Tests for scheduler push notification integration"""
    
    def test_scheduler_status_endpoint(self, api_client):
        """Test that scheduler status endpoint is accessible"""
        response = api_client.get(f"{BASE_URL}/api/scheduler/status")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "scheduler_running" in data, "Response should contain 'scheduler_running'"
        assert "jobs" in data, "Response should contain 'jobs'"
        assert "schedule" in data, "Response should contain 'schedule'"
        
        # Verify scheduler is running
        assert data["scheduler_running"] == True, "Scheduler should be running"
        
        # Verify expected jobs exist
        job_ids = [job["id"] for job in data["jobs"]]
        expected_jobs = ["streak_reminders", "inactive_reminders", "weekly_summaries"]
        for expected_job in expected_jobs:
            assert expected_job in job_ids, f"Expected job '{expected_job}' not found in scheduler"


class TestPushSubscriptionFlow:
    """End-to-end tests for push subscription flow"""
    
    def test_full_subscription_flow(self, authenticated_client):
        """Test complete subscribe -> status -> unsubscribe flow"""
        # 1. Check initial status
        status_response = authenticated_client.get(f"{BASE_URL}/api/push/status")
        assert status_response.status_code == 200
        initial_status = status_response.json()
        
        # 2. Subscribe
        unique_endpoint = f"https://test.push.service/TEST_flow_{uuid.uuid4()}"
        sub_response = authenticated_client.post(f"{BASE_URL}/api/push/subscribe", json={
            "endpoint": unique_endpoint,
            "keys": {"p256dh": "flow_test_key", "auth": "flow_test_auth"}
        })
        assert sub_response.status_code == 200
        assert sub_response.json()["message"] in ["Subscribed successfully", "Subscription updated"]
        
        # 3. Check status after subscribe
        status_response = authenticated_client.get(f"{BASE_URL}/api/push/status")
        assert status_response.status_code == 200
        subscribed_status = status_response.json()
        assert subscribed_status["subscribed_devices"] >= 1, "Should have at least 1 subscribed device"
        
        # 4. Unsubscribe
        unsub_response = authenticated_client.delete(f"{BASE_URL}/api/push/unsubscribe")
        assert unsub_response.status_code == 200
        
        # 5. Check status after unsubscribe
        status_response = authenticated_client.get(f"{BASE_URL}/api/push/status")
        assert status_response.status_code == 200
        final_status = status_response.json()
        assert final_status["subscribed_devices"] == 0, "Should have 0 subscribed devices after unsubscribe"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
