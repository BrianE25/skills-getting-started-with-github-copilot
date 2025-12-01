"""
Tests for Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the school soccer team and compete in local tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu", "sarah@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and participate in inter-school games",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "emily@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore various art mediums including painting, drawing, and sculpture",
            "schedule": "Thursdays, 3:00 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["lily@mergington.edu", "ryan@mergington.edu"]
        },
        "Drama Club": {
            "description": "Develop acting skills and perform in school theater productions",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["grace@mergington.edu", "nathan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabelle@mergington.edu", "lucas@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science competitions and conduct experiments",
            "schedule": "Fridays, 3:00 PM - 4:30 PM",
            "max_participants": 14,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_activities_have_required_fields(self, client):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_adds_to_participants_list(self, client):
        """Test that signup correctly adds student to participants list"""
        initial_count = len(activities["Chess Club"]["participants"])
        
        client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
        
        assert len(activities["Chess Club"]["participants"]) == initial_count + 1
        assert "test@mergington.edu" in activities["Chess Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_from_activity_success(self, client):
        """Test successful unregistration from an activity"""
        # First, verify the participant exists
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]
        
        # Verify participant was removed
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregister from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_student_not_registered(self, client):
        """Test unregister for a student who is not registered"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Student not registered for this activity"
    
    def test_unregister_removes_from_participants_list(self, client):
        """Test that unregister correctly removes student from participants list"""
        initial_count = len(activities["Chess Club"]["participants"])
        
        client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        
        assert len(activities["Chess Club"]["participants"]) == initial_count - 1
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


class TestEndToEndScenarios:
    """End-to-end test scenarios"""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test the complete workflow of signing up and then unregistering"""
        email = "workflow@mergington.edu"
        activity = "Chess Club"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity]["participants"]
        assert email not in initial_participants
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup = client.get("/activities")
        after_signup_participants = after_signup.json()[activity]["participants"]
        assert email in after_signup_participants
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        after_unregister = client.get("/activities")
        after_unregister_participants = after_unregister.json()[activity]["participants"]
        assert email not in after_unregister_participants
    
    def test_multiple_signups_for_same_activity(self, client):
        """Test multiple students signing up for the same activity"""
        activity = "Programming Class"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all students are registered
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity]["participants"]
        
        for email in emails:
            assert email in participants
