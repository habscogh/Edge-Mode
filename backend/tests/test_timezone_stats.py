"""
Backend API Tests for Edge Mode App - Timezone Handling Fix
Tests: Stats endpoints with local_date parameter to ensure correct date handling
Bug Fix: Sessions logged on one day were appearing as logged on another day in dashboard stats
         because backend used UTC date while sessions use client's local date.
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestTimezoneStatsComparison:
    """Test /api/stats/comparison endpoint with local_date parameter"""
    
    @pytest.fixture(scope="class")
    def authenticated_user(self):
        """Create and authenticate a test user with pillars"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"tz_comparison_test_{unique_id}@example.com",
            "username": f"tzcompuser_{unique_id}",
            "password": "TestPass123!",
            "age": 16
        }
        
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        user_data["token"] = data["token"]
        user_data["user_id"] = data["user_id"]
        user_data["headers"] = {"Authorization": f"Bearer {data['token']}"}
        
        # Complete onboarding
        pillars_data = {
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 5},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 7},
                {"pillar_name": "Reading/Learning", "weekly_target_sessions": 3}
            ]
        }
        onboard_response = requests.post(
            f"{BASE_URL}/api/onboarding/complete",
            json=pillars_data,
            headers=user_data["headers"]
        )
        assert onboard_response.status_code == 200, f"Onboarding failed: {onboard_response.text}"
        
        print(f"Created test user: {user_data['email']}")
        return user_data
    
    def test_comparison_without_local_date(self, authenticated_user):
        """Test /api/stats/comparison without local_date parameter (fallback to UTC)"""
        response = requests.get(
            f"{BASE_URL}/api/stats/comparison",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "today_sessions" in data
        assert "yesterday_sessions" in data
        assert "today_minutes" in data
        assert "yesterday_minutes" in data
        assert "improvement_pct" in data
        print(f"Comparison without local_date: today={data['today_sessions']}, yesterday={data['yesterday_sessions']}")
    
    def test_comparison_with_local_date(self, authenticated_user):
        """Test /api/stats/comparison with local_date parameter"""
        # Use today's date in local format
        local_date = datetime.now().strftime('%Y-%m-%d')
        
        response = requests.get(
            f"{BASE_URL}/api/stats/comparison?local_date={local_date}",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "today_sessions" in data
        assert "yesterday_sessions" in data
        assert "today_minutes" in data
        assert "yesterday_minutes" in data
        assert "improvement_pct" in data
        print(f"Comparison with local_date={local_date}: today={data['today_sessions']}, yesterday={data['yesterday_sessions']}")
    
    def test_log_session_and_verify_comparison(self, authenticated_user):
        """CRITICAL TEST: Log a session with local_date and verify stats/comparison returns correct count"""
        # Get today's local date
        local_date = datetime.now().strftime('%Y-%m-%d')
        
        # First, get current comparison stats
        before_response = requests.get(
            f"{BASE_URL}/api/stats/comparison?local_date={local_date}",
            headers=authenticated_user["headers"]
        )
        assert before_response.status_code == 200
        before_data = before_response.json()
        before_today_sessions = before_data["today_sessions"]
        print(f"Before logging: today_sessions={before_today_sessions}")
        
        # Log a session with local_date
        session_data = {
            "pillar": "Fitness/Training",
            "minutes_spent": 30,
            "local_date": local_date
        }
        session_response = requests.post(
            f"{BASE_URL}/api/sessions/complete",
            json=session_data,
            headers=authenticated_user["headers"]
        )
        assert session_response.status_code == 200, f"Session creation failed: {session_response.text}"
        session = session_response.json()
        assert session["session"]["date"] == local_date, f"Session date mismatch: expected {local_date}, got {session['session']['date']}"
        print(f"Logged session with date={session['session']['date']}")
        
        # Verify comparison stats now show +1 for today
        after_response = requests.get(
            f"{BASE_URL}/api/stats/comparison?local_date={local_date}",
            headers=authenticated_user["headers"]
        )
        assert after_response.status_code == 200
        after_data = after_response.json()
        after_today_sessions = after_data["today_sessions"]
        
        assert after_today_sessions == before_today_sessions + 1, \
            f"Expected today_sessions to be {before_today_sessions + 1}, got {after_today_sessions}"
        print(f"After logging: today_sessions={after_today_sessions} (correctly incremented by 1)")
    
    def test_comparison_with_specific_date(self, authenticated_user):
        """Test comparison with a specific past date"""
        # Use yesterday's date
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        response = requests.get(
            f"{BASE_URL}/api/stats/comparison?local_date={yesterday}",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # When local_date is yesterday, "today" in comparison should be yesterday
        # and "yesterday" should be day before yesterday
        assert "today_sessions" in data
        assert "yesterday_sessions" in data
        print(f"Comparison for date={yesterday}: today={data['today_sessions']}, yesterday={data['yesterday_sessions']}")


class TestTimezoneStatsWeekly:
    """Test /api/stats/weekly endpoint with local_date parameter"""
    
    @pytest.fixture(scope="class")
    def authenticated_user(self):
        """Create and authenticate a test user with pillars"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"tz_weekly_test_{unique_id}@example.com",
            "username": f"tzweeklyuser_{unique_id}",
            "password": "TestPass123!",
            "age": 17
        }
        
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        user_data["token"] = data["token"]
        user_data["headers"] = {"Authorization": f"Bearer {data['token']}"}
        
        # Complete onboarding
        pillars_data = {
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 5},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 5},
                {"pillar_name": "Skill Development", "weekly_target_sessions": 3}
            ]
        }
        requests.post(
            f"{BASE_URL}/api/onboarding/complete",
            json=pillars_data,
            headers=user_data["headers"]
        )
        
        print(f"Created test user: {user_data['email']}")
        return user_data
    
    def test_weekly_stats_without_local_date(self, authenticated_user):
        """Test /api/stats/weekly without local_date parameter"""
        response = requests.get(
            f"{BASE_URL}/api/stats/weekly",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "consistency_pct" in data
        assert "target_completion_pct" in data
        assert "performance_index" in data
        assert "total_sessions" in data
        assert "total_minutes" in data
        assert "days_logged" in data
        assert "pillars_data" in data
        print(f"Weekly stats without local_date: {data['total_sessions']} sessions, {data['consistency_pct']}% consistency")
    
    def test_weekly_stats_with_local_date(self, authenticated_user):
        """Test /api/stats/weekly with local_date parameter"""
        local_date = datetime.now().strftime('%Y-%m-%d')
        
        response = requests.get(
            f"{BASE_URL}/api/stats/weekly?local_date={local_date}",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "consistency_pct" in data
        assert "total_sessions" in data
        assert "pillars_data" in data
        print(f"Weekly stats with local_date={local_date}: {data['total_sessions']} sessions")
    
    def test_log_session_and_verify_weekly_stats(self, authenticated_user):
        """Log a session and verify weekly stats reflect it correctly"""
        local_date = datetime.now().strftime('%Y-%m-%d')
        
        # Get current weekly stats
        before_response = requests.get(
            f"{BASE_URL}/api/stats/weekly?local_date={local_date}",
            headers=authenticated_user["headers"]
        )
        assert before_response.status_code == 200
        before_data = before_response.json()
        before_sessions = before_data["total_sessions"]
        print(f"Before logging: total_sessions={before_sessions}")
        
        # Log a session
        session_data = {
            "pillar": "Fitness/Training",
            "minutes_spent": 45,
            "local_date": local_date
        }
        session_response = requests.post(
            f"{BASE_URL}/api/sessions/complete",
            json=session_data,
            headers=authenticated_user["headers"]
        )
        assert session_response.status_code == 200
        
        # Verify weekly stats updated
        after_response = requests.get(
            f"{BASE_URL}/api/stats/weekly?local_date={local_date}",
            headers=authenticated_user["headers"]
        )
        assert after_response.status_code == 200
        after_data = after_response.json()
        after_sessions = after_data["total_sessions"]
        
        assert after_sessions == before_sessions + 1, \
            f"Expected total_sessions to be {before_sessions + 1}, got {after_sessions}"
        print(f"After logging: total_sessions={after_sessions} (correctly incremented)")


class TestTimezoneStatsWeeklyReview:
    """Test /api/stats/weekly-review endpoint with local_date parameter"""
    
    @pytest.fixture(scope="class")
    def authenticated_user(self):
        """Create and authenticate a test user with pillars"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"tz_review_test_{unique_id}@example.com",
            "username": f"tzreviewuser_{unique_id}",
            "password": "TestPass123!",
            "age": 15
        }
        
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        user_data["token"] = data["token"]
        user_data["headers"] = {"Authorization": f"Bearer {data['token']}"}
        
        # Complete onboarding
        pillars_data = {
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 5},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 5},
                {"pillar_name": "Reading/Learning", "weekly_target_sessions": 3}
            ]
        }
        requests.post(
            f"{BASE_URL}/api/onboarding/complete",
            json=pillars_data,
            headers=user_data["headers"]
        )
        
        print(f"Created test user: {user_data['email']}")
        return user_data
    
    def test_weekly_review_without_local_date(self, authenticated_user):
        """Test /api/stats/weekly-review without local_date parameter"""
        response = requests.get(
            f"{BASE_URL}/api/stats/weekly-review",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "week_start" in data
        assert "week_end" in data
        assert "improved_pillars" in data
        assert "dropped_pillars" in data
        assert "average_daily_output_change" in data
        assert "total_sessions" in data
        assert "consistency_pct" in data
        assert "performance_index" in data
        print(f"Weekly review without local_date: week_start={data['week_start']}, total_sessions={data['total_sessions']}")
    
    def test_weekly_review_with_local_date(self, authenticated_user):
        """Test /api/stats/weekly-review with local_date parameter"""
        local_date = datetime.now().strftime('%Y-%m-%d')
        
        response = requests.get(
            f"{BASE_URL}/api/stats/weekly-review?local_date={local_date}",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "week_start" in data
        assert "week_end" in data
        assert "total_sessions" in data
        print(f"Weekly review with local_date={local_date}: week_start={data['week_start']}")


class TestTimezoneStatsHistory:
    """Test /api/stats/history endpoint with local_date parameter"""
    
    @pytest.fixture(scope="class")
    def authenticated_user(self):
        """Create and authenticate a test user with pillars"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"tz_history_test_{unique_id}@example.com",
            "username": f"tzhistoryuser_{unique_id}",
            "password": "TestPass123!",
            "age": 18
        }
        
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        user_data["token"] = data["token"]
        user_data["headers"] = {"Authorization": f"Bearer {data['token']}"}
        
        # Complete onboarding
        pillars_data = {
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 5},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 5},
                {"pillar_name": "Personal Project", "weekly_target_sessions": 3}
            ]
        }
        requests.post(
            f"{BASE_URL}/api/onboarding/complete",
            json=pillars_data,
            headers=user_data["headers"]
        )
        
        print(f"Created test user: {user_data['email']}")
        return user_data
    
    def test_history_without_local_date(self, authenticated_user):
        """Test /api/stats/history without local_date parameter"""
        response = requests.get(
            f"{BASE_URL}/api/stats/history?days=30",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "dates" in data
        assert "scores" in data
        assert len(data["dates"]) == 30
        assert len(data["scores"]) == 30
        print(f"History without local_date: {len(data['dates'])} days of data")
    
    def test_history_with_local_date(self, authenticated_user):
        """Test /api/stats/history with local_date parameter"""
        local_date = datetime.now().strftime('%Y-%m-%d')
        
        response = requests.get(
            f"{BASE_URL}/api/stats/history?days=30&local_date={local_date}",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "dates" in data
        assert "scores" in data
        assert len(data["dates"]) == 30
        
        # Verify the last date in history matches local_date
        assert data["dates"][-1] == local_date, \
            f"Expected last date to be {local_date}, got {data['dates'][-1]}"
        print(f"History with local_date={local_date}: last_date={data['dates'][-1]}")
    
    def test_history_with_different_days(self, authenticated_user):
        """Test /api/stats/history with different days parameter"""
        local_date = datetime.now().strftime('%Y-%m-%d')
        
        for days in [7, 14, 30, 60]:
            response = requests.get(
                f"{BASE_URL}/api/stats/history?days={days}&local_date={local_date}",
                headers=authenticated_user["headers"]
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["dates"]) == days
            print(f"History with days={days}: {len(data['dates'])} dates returned")


class TestTodaySessionsWithLocalDate:
    """Test /api/sessions/today endpoint with local_date parameter"""
    
    @pytest.fixture(scope="class")
    def authenticated_user(self):
        """Create and authenticate a test user with pillars"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"tz_today_test_{unique_id}@example.com",
            "username": f"tztodayuser_{unique_id}",
            "password": "TestPass123!",
            "age": 16
        }
        
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        user_data["token"] = data["token"]
        user_data["headers"] = {"Authorization": f"Bearer {data['token']}"}
        
        # Complete onboarding
        pillars_data = {
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 5},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 5},
                {"pillar_name": "Skill Development", "weekly_target_sessions": 3}
            ]
        }
        requests.post(
            f"{BASE_URL}/api/onboarding/complete",
            json=pillars_data,
            headers=user_data["headers"]
        )
        
        print(f"Created test user: {user_data['email']}")
        return user_data
    
    def test_today_sessions_without_local_date(self, authenticated_user):
        """Test /api/sessions/today without local_date parameter"""
        response = requests.get(
            f"{BASE_URL}/api/sessions/today",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Today sessions without local_date: {len(data)} sessions")
    
    def test_today_sessions_with_local_date(self, authenticated_user):
        """Test /api/sessions/today with local_date parameter"""
        local_date = datetime.now().strftime('%Y-%m-%d')
        
        response = requests.get(
            f"{BASE_URL}/api/sessions/today?local_date={local_date}",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Today sessions with local_date={local_date}: {len(data)} sessions")
    
    def test_log_and_verify_today_sessions(self, authenticated_user):
        """Log a session with local_date and verify it appears in today's sessions"""
        local_date = datetime.now().strftime('%Y-%m-%d')
        
        # Get current today sessions count
        before_response = requests.get(
            f"{BASE_URL}/api/sessions/today?local_date={local_date}",
            headers=authenticated_user["headers"]
        )
        assert before_response.status_code == 200
        before_count = len(before_response.json())
        
        # Log a session
        session_data = {
            "pillar": "Skill Development",
            "minutes_spent": 25,
            "local_date": local_date,
            "note": "Testing timezone handling"
        }
        session_response = requests.post(
            f"{BASE_URL}/api/sessions/complete",
            json=session_data,
            headers=authenticated_user["headers"]
        )
        assert session_response.status_code == 200
        created_session = session_response.json()["session"]
        
        # Verify session date matches local_date
        assert created_session["date"] == local_date
        
        # Verify session appears in today's sessions
        after_response = requests.get(
            f"{BASE_URL}/api/sessions/today?local_date={local_date}",
            headers=authenticated_user["headers"]
        )
        assert after_response.status_code == 200
        after_sessions = after_response.json()
        after_count = len(after_sessions)
        
        assert after_count == before_count + 1, \
            f"Expected {before_count + 1} sessions, got {after_count}"
        
        # Verify the new session is in the list
        session_ids = [s["id"] for s in after_sessions]
        assert created_session["id"] in session_ids
        print(f"Session logged and verified in today's sessions: {created_session['id']}")


class TestEndToEndTimezoneFlow:
    """End-to-end test: Create user, complete onboarding, log session, verify stats"""
    
    def test_full_flow_with_timezone_handling(self):
        """Complete end-to-end test of timezone handling fix"""
        unique_id = str(uuid.uuid4())[:8]
        local_date = datetime.now().strftime('%Y-%m-%d')
        
        # Step 1: Register user
        user_data = {
            "email": f"e2e_tz_test_{unique_id}@example.com",
            "username": f"e2etzuser_{unique_id}",
            "password": "TestPass123!",
            "age": 16
        }
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        assert register_response.status_code == 200, f"Registration failed: {register_response.text}"
        token = register_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Step 1: User registered - {user_data['email']}")
        
        # Step 2: Complete onboarding
        pillars_data = {
            "pillars": [
                {"pillar_name": "Fitness/Training", "weekly_target_sessions": 5},
                {"pillar_name": "Study/Academics", "weekly_target_sessions": 5},
                {"pillar_name": "Reading/Learning", "weekly_target_sessions": 3}
            ]
        }
        onboard_response = requests.post(
            f"{BASE_URL}/api/onboarding/complete",
            json=pillars_data,
            headers=headers
        )
        assert onboard_response.status_code == 200, f"Onboarding failed: {onboard_response.text}"
        print("Step 2: Onboarding completed")
        
        # Step 3: Get initial stats (should be 0 sessions)
        initial_comparison = requests.get(
            f"{BASE_URL}/api/stats/comparison?local_date={local_date}",
            headers=headers
        )
        assert initial_comparison.status_code == 200
        initial_today = initial_comparison.json()["today_sessions"]
        assert initial_today == 0, f"Expected 0 initial sessions, got {initial_today}"
        print(f"Step 3: Initial stats - today_sessions={initial_today}")
        
        # Step 4: Log a session with local_date
        session_data = {
            "pillar": "Fitness/Training",
            "minutes_spent": 30,
            "local_date": local_date,
            "note": "E2E timezone test session"
        }
        session_response = requests.post(
            f"{BASE_URL}/api/sessions/complete",
            json=session_data,
            headers=headers
        )
        assert session_response.status_code == 200, f"Session creation failed: {session_response.text}"
        session = session_response.json()["session"]
        assert session["date"] == local_date, f"Session date mismatch: expected {local_date}, got {session['date']}"
        print(f"Step 4: Session logged with date={session['date']}")
        
        # Step 5: Verify stats/comparison shows 1 session for today
        final_comparison = requests.get(
            f"{BASE_URL}/api/stats/comparison?local_date={local_date}",
            headers=headers
        )
        assert final_comparison.status_code == 200
        final_today = final_comparison.json()["today_sessions"]
        assert final_today == 1, f"Expected 1 session for today, got {final_today}"
        print(f"Step 5: Final stats - today_sessions={final_today} (CORRECT!)")
        
        # Step 6: Verify weekly stats also show the session
        weekly_response = requests.get(
            f"{BASE_URL}/api/stats/weekly?local_date={local_date}",
            headers=headers
        )
        assert weekly_response.status_code == 200
        weekly_data = weekly_response.json()
        assert weekly_data["total_sessions"] >= 1, f"Expected at least 1 session in weekly stats"
        print(f"Step 6: Weekly stats - total_sessions={weekly_data['total_sessions']}")
        
        # Step 7: Verify session appears in today's sessions
        today_response = requests.get(
            f"{BASE_URL}/api/sessions/today?local_date={local_date}",
            headers=headers
        )
        assert today_response.status_code == 200
        today_sessions = today_response.json()
        assert len(today_sessions) == 1, f"Expected 1 session in today's list, got {len(today_sessions)}"
        assert today_sessions[0]["date"] == local_date
        print(f"Step 7: Today's sessions verified - {len(today_sessions)} session(s)")
        
        print("\n✅ END-TO-END TIMEZONE HANDLING TEST PASSED!")
        print(f"   - Session logged with local_date={local_date}")
        print(f"   - Stats correctly show today_sessions=1")
        print(f"   - Bug fix verified: Sessions appear on correct day in dashboard")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
