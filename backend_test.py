import requests
import sys
from datetime import datetime
import json

class ForgeAPITester:
    def __init__(self, base_url="https://gamify-teens.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()

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
                response = self.session.get(url, headers=test_headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text}")

            return success, response.json() if response.text else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_register(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        user_data = {
            "email": f"sessionuser@forge.com",
            "username": "sessionuser",
            "password": "test1234",
            "age": 17
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user_id']
            return True
        return False

    def test_login(self):
        """Test user login"""
        login_data = {
            "email": "sessionuser@forge.com",
            "password": "test1234"
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user_id']
            return True
        return False

    def test_get_pillars(self):
        """Test getting available pillars"""
        success, response = self.run_test(
            "Get Available Pillars",
            "GET",
            "pillars",
            200
        )
        return success and 'pillars' in response

    def test_complete_onboarding(self):
        """Test completing onboarding with 3 pillars"""
        onboarding_data = {
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 5},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 5},
                {"pillar_name": "Reading/Learning", "weekly_target_sessions": 5}
            ]
        }
        
        success, response = self.run_test(
            "Complete Onboarding",
            "POST",
            "onboarding/complete",
            200,
            data=onboarding_data
        )
        return success

    def test_get_user_pillars(self):
        """Test getting user pillars"""
        success, response = self.run_test(
            "Get User Pillars",
            "GET",
            "users/pillars",
            200
        )
        return success and len(response) == 3

    def test_complete_session(self):
        """Test completing a session"""
        session_data = {
            "pillar": "Fitness/Training",
            "minutes_spent": 30
        }
        
        success, response = self.run_test(
            "Complete Session",
            "POST",
            "sessions/complete",
            200,
            data=session_data
        )
        return success and 'id' in response

    def test_get_today_sessions(self):
        """Test getting today's sessions"""
        success, response = self.run_test(
            "Get Today Sessions",
            "GET",
            "sessions/today",
            200
        )
        return success

    def test_get_weekly_stats(self):
        """Test getting weekly stats"""
        success, response = self.run_test(
            "Get Weekly Stats",
            "GET",
            "stats/weekly",
            200
        )
        return success and 'performance_index' in response

    def test_get_daily_comparison(self):
        """Test getting yesterday vs today comparison"""
        success, response = self.run_test(
            "Get Daily Comparison",
            "GET",
            "stats/comparison",
            200
        )
        return success and 'today_sessions' in response

    def test_get_performance_history(self):
        """Test getting 30-day performance history"""
        success, response = self.run_test(
            "Get Performance History (30 days)",
            "GET",
            "stats/history?days=30",
            200
        )
        return success and 'dates' in response and 'scores' in response

    def test_get_weekly_review(self):
        """Test getting weekly review"""
        success, response = self.run_test(
            "Get Weekly Review",
            "GET",
            "stats/weekly-review",
            200
        )
        return success and 'performance_index' in response

    def test_create_group(self):
        """Test creating a group"""
        group_data = {
            "name": "Test Squad",
            "type": "private"
        }
        
        success, response = self.run_test(
            "Create Group",
            "POST",
            "groups",
            200,
            data=group_data
        )
        
        if success and 'invite_code' in response:
            self.invite_code = response['invite_code']
            self.group_id = response['id']
            return True
        return False

    def test_get_groups(self):
        """Test getting user groups"""
        success, response = self.run_test(
            "Get User Groups",
            "GET",
            "groups",
            200
        )
        return success

    def test_join_group(self):
        """Test joining a group with invite code"""
        if not hasattr(self, 'invite_code'):
            print("⚠️  Skipping join group test - no invite code available")
            return True
            
        join_data = {
            "invite_code": self.invite_code
        }
        
        success, response = self.run_test(
            "Join Group",
            "POST",
            "groups/join",
            200,
            data=join_data
        )
        return success

    def test_group_leaderboard(self):
        """Test getting group leaderboard"""
        if not hasattr(self, 'group_id'):
            print("⚠️  Skipping group leaderboard test - no group ID available")
            return True
            
        success, response = self.run_test(
            "Get Group Leaderboard",
            "GET",
            f"groups/{self.group_id}/leaderboard",
            200
        )
        return success

    def test_global_leaderboard(self):
        """Test getting global leaderboard"""
        success, response = self.run_test(
            "Get Global Leaderboard",
            "GET",
            "leaderboard/global",
            200
        )
        return success

    def test_global_leaderboard_age_filter(self):
        """Test getting global leaderboard with age filter"""
        success, response = self.run_test(
            "Get Global Leaderboard (15-17)",
            "GET",
            "leaderboard/global?age_group=15-17",
            200
        )
        return success

    def test_leaderboard_opt_in(self):
        """Test toggling leaderboard opt-in"""
        success, response = self.run_test(
            "Toggle Leaderboard Opt-in",
            "POST",
            "users/leaderboard-opt-in",
            200
        )
        return success and 'leaderboard_opt_in' in response

def main():
    print("🚀 Starting Forge API Tests...")
    tester = ForgeAPITester()
    
    # Test sequence
    tests = [
        ("Register User", tester.test_register),
        ("Get Available Pillars", tester.test_get_pillars),
        ("Complete Onboarding", tester.test_complete_onboarding),
        ("Get User Pillars", tester.test_get_user_pillars),
        ("Complete Session", tester.test_complete_session),
        ("Get Today Sessions", tester.test_get_today_sessions),
        ("Get Weekly Stats", tester.test_get_weekly_stats),
        ("Get Daily Comparison", tester.test_get_daily_comparison),
        ("Get Performance History", tester.test_get_performance_history),
        ("Get Weekly Review", tester.test_get_weekly_review),
        ("Create Group", tester.test_create_group),
        ("Get User Groups", tester.test_get_groups),
        ("Join Group", tester.test_join_group),
        ("Get Group Leaderboard", tester.test_group_leaderboard),
        ("Toggle Leaderboard Opt-in", tester.test_leaderboard_opt_in),
        ("Get Global Leaderboard", tester.test_global_leaderboard),
        ("Get Global Leaderboard (Age Filter)", tester.test_global_leaderboard_age_filter),
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            failed_tests.append(test_name)
    
    # Print results
    print(f"\n📊 Test Results:")
    print(f"   Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"   Success rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print(f"\n✅ All tests passed!")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())