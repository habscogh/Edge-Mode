import requests
import sys
import json
from datetime import datetime, timedelta

class ForgeAPITester:
    def __init__(self, base_url="https://daily-grind-tracker-2.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_email = f"test_{datetime.now().strftime('%H%M%S')}@forge.com"
        self.test_username = f"testuser_{datetime.now().strftime('%H%M%S')}"
        self.test_password = "test1234"

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_register_valid_user(self):
        """Test user registration with valid data"""
        success, response = self.run_test(
            "Register Valid User",
            "POST",
            "auth/register",
            200,
            data={
                "email": self.test_email,
                "username": self.test_username,
                "password": self.test_password,
                "age": 16
            }
        )
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user_id']
            print(f"   Token received: {self.token[:20]}...")
            return True
        return False

    def test_register_invalid_age(self):
        """Test registration with invalid age (should fail)"""
        success, _ = self.run_test(
            "Register Invalid Age (11)",
            "POST",
            "auth/register",
            422,  # Validation error
            data={
                "email": f"invalid_{datetime.now().strftime('%H%M%S')}@forge.com",
                "username": f"invalid_{datetime.now().strftime('%H%M%S')}",
                "password": "test1234",
                "age": 11
            }
        )
        return success

    def test_register_invalid_age_high(self):
        """Test registration with invalid age (should fail)"""
        success, _ = self.run_test(
            "Register Invalid Age (20)",
            "POST",
            "auth/register",
            422,  # Validation error
            data={
                "email": f"invalid2_{datetime.now().strftime('%H%M%S')}@forge.com",
                "username": f"invalid2_{datetime.now().strftime('%H%M%S')}",
                "password": "test1234",
                "age": 20
            }
        )
        return success

    def test_login(self):
        """Test login with created credentials"""
        success, response = self.run_test(
            "Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": self.test_email,
                "password": self.test_password
            }
        )
        if success and 'token' in response:
            self.token = response['token']
            return True
        return False

    def test_get_user_me(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get User Me",
            "GET",
            "users/me",
            200
        )
        if success:
            print(f"   User data: {json.dumps(response, indent=2)}")
        return success

    def test_get_pillars(self):
        """Test getting available pillars"""
        success, response = self.run_test(
            "Get Available Pillars",
            "GET",
            "pillars",
            200
        )
        if success and 'pillars' in response:
            print(f"   Found {len(response['pillars'])} pillars")
            return len(response['pillars']) == 7
        return False

    def test_complete_onboarding(self):
        """Test completing onboarding with pillar selection"""
        pillars_data = [
            {"pillar_name": "Fitness/Training", "weekly_target_minutes": 300},
            {"pillar_name": "Study/Academics", "weekly_target_minutes": 420},
            {"pillar_name": "Skill Development", "weekly_target_minutes": 180}
        ]
        
        success, response = self.run_test(
            "Complete Onboarding",
            "POST",
            "onboarding/complete",
            200,
            data={"pillars": pillars_data}
        )
        return success

    def test_get_user_pillars(self):
        """Test getting user's selected pillars"""
        success, response = self.run_test(
            "Get User Pillars",
            "GET",
            "users/pillars",
            200
        )
        if success:
            print(f"   User has {len(response)} pillars")
            return len(response) == 3
        return False

    def test_create_log(self):
        """Test creating a daily log entry"""
        success, response = self.run_test(
            "Create Log Entry",
            "POST",
            "logs",
            200,
            data={
                "pillar": "Fitness/Training",
                "minutes_logged": 30
            }
        )
        if success:
            print(f"   Log created with ID: {response.get('id', 'N/A')}")
        return success

    def test_get_today_logs(self):
        """Test getting today's logs"""
        success, response = self.run_test(
            "Get Today's Logs",
            "GET",
            "logs/today",
            200
        )
        if success:
            print(f"   Found {len(response)} logs for today")
        return success

    def test_get_weekly_stats(self):
        """Test getting weekly statistics"""
        success, response = self.run_test(
            "Get Weekly Stats",
            "GET",
            "stats/weekly",
            200
        )
        if success:
            print(f"   Weekly stats: {json.dumps(response, indent=2)}")
        return success

    def test_create_group(self):
        """Test creating a group"""
        success, response = self.run_test(
            "Create Group",
            "POST",
            "groups",
            200,
            data={
                "name": "Test Squad",
                "type": "private"
            }
        )
        if success:
            self.group_id = response.get('id')
            print(f"   Group created with ID: {self.group_id}")
        return success

    def test_get_groups(self):
        """Test getting user's groups"""
        success, response = self.run_test(
            "Get User Groups",
            "GET",
            "groups",
            200
        )
        if success:
            print(f"   User is in {len(response)} groups")
        return success

    def test_get_group_leaderboard(self):
        """Test getting group leaderboard"""
        if hasattr(self, 'group_id') and self.group_id:
            success, response = self.run_test(
                "Get Group Leaderboard",
                "GET",
                f"groups/{self.group_id}/leaderboard",
                200
            )
            if success:
                print(f"   Group leaderboard has {len(response)} members")
            return success
        else:
            print("❌ Skipping group leaderboard test - no group ID")
            return False

    def test_toggle_leaderboard_opt_in(self):
        """Test toggling leaderboard opt-in"""
        success, response = self.run_test(
            "Toggle Leaderboard Opt-in",
            "POST",
            "users/leaderboard-opt-in",
            200
        )
        if success:
            print(f"   Leaderboard opt-in status: {response.get('leaderboard_opt_in')}")
        return success

    def test_get_global_leaderboard(self):
        """Test getting global leaderboard"""
        success, response = self.run_test(
            "Get Global Leaderboard",
            "GET",
            "leaderboard/global",
            200
        )
        if success:
            print(f"   Global leaderboard has {len(response)} users")
        return success

    def test_get_global_leaderboard_filtered(self):
        """Test getting filtered global leaderboard"""
        success, response = self.run_test(
            "Get Global Leaderboard (15-17)",
            "GET",
            "leaderboard/global?age_group=15-17",
            200
        )
        if success:
            print(f"   Filtered leaderboard has {len(response)} users")
        return success

def main():
    print("🚀 Starting Forge API Testing...")
    print("=" * 50)
    
    tester = ForgeAPITester()
    
    # Test sequence
    tests = [
        # Authentication tests
        tester.test_register_valid_user,
        tester.test_register_invalid_age,
        tester.test_register_invalid_age_high,
        tester.test_login,
        tester.test_get_user_me,
        
        # Pillar and onboarding tests
        tester.test_get_pillars,
        tester.test_complete_onboarding,
        tester.test_get_user_pillars,
        
        # Logging tests
        tester.test_create_log,
        tester.test_get_today_logs,
        tester.test_get_weekly_stats,
        
        # Group tests
        tester.test_create_group,
        tester.test_get_groups,
        tester.test_get_group_leaderboard,
        
        # Leaderboard tests
        tester.test_toggle_leaderboard_opt_in,
        tester.test_get_global_leaderboard,
        tester.test_get_global_leaderboard_filtered,
    ]
    
    # Run all tests
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS:")
    print(f"   Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())