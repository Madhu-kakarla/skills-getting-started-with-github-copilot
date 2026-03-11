"""
Comprehensive test suite for Mergington High School API

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test fixtures and data
- Act: Execute the operation being tested
- Assert: Verify the results
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture providing a TestClient for the FastAPI application.
    
    Yields:
        TestClient: A test client for making requests to the API
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture to reset activities to their initial state before each test.
    
    This ensures test isolation by ensuring each test starts with a clean state.
    """
    # Store original activities
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
        "Basketball Team": {
            "description": "Competitive basketball training and match participation",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and compete in tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "claire@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["maya@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through debate competitions",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["james@mergington.edu", "rachel@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore science topics through hands-on projects",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["david@mergington.edu"]
        }
    }
    
    yield
    
    # Reset activities after each test
    activities.clear()
    activities.update(original_activities)


# ==================== ROOT ENDPOINT TESTS ====================

class TestRootEndpoint:
    """Tests for the root endpoint (GET /)"""
    
    def test_root_redirect(self, client, reset_activities):
        """
        Test that the root endpoint redirects to the static index.html page.
        
        Arrange: Create a test client
        Act: Make a GET request to the root endpoint
        Assert: Verify a redirect response with correct URL
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


# ==================== GET ACTIVITIES ENDPOINT TESTS ====================

class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_success(self, client, reset_activities):
        """
        Test that GET /activities returns all activities with correct structure.
        
        Arrange: Create a test client with activities loaded
        Act: Make a GET request to /activities
        Assert: Verify all activities are returned with correct fields
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
        assert data["Chess Club"]["max_participants"] == 12
        assert isinstance(data["Chess Club"]["participants"], list)
    
    def test_get_activities_contains_all_fields(self, client, reset_activities):
        """
        Test that each activity contains all required fields.
        
        Arrange: Create a test client
        Act: Make a GET request to /activities
        Assert: Verify each activity has description, schedule, max_participants, and participants
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        required_fields = {"description", "schedule", "max_participants", "participants"}
        for activity_name, activity_data in data.items():
            assert required_fields.issubset(set(activity_data.keys()))


# ==================== SIGNUP ENDPOINT TESTS ====================

class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """
        Test successful student signup for an activity.
        
        Arrange: Create a test client and prepare a new student email
        Act: Make a POST request to signup with valid activity and email
        Assert: Verify success message and participant is added
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_prevention(self, client, reset_activities):
        """
        Test that duplicate signups are prevented with 400 status code.
        
        Arrange: Create a test client and use an already-enrolled student
        Act: Attempt to sign up a student who is already enrolled
        Assert: Verify 400 error response with appropriate message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already enrolled
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"
    
    def test_signup_invalid_activity(self, client, reset_activities):
        """
        Test that signup for non-existent activity returns 404.
        
        Arrange: Create a test client and prepare invalid activity name
        Act: Make a POST request with non-existent activity name
        Assert: Verify 404 error response with appropriate message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_multiple_students(self, client, reset_activities):
        """
        Test that multiple students can sign up for the same activity.
        
        Arrange: Create a test client and prepare multiple email addresses
        Act: Sign up multiple students to the same activity
        Assert: Verify all signups succeed and all are recorded
        """
        # Arrange
        activity_name = "Programming Class"
        students = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Act
        for email in students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            # Assert after each signup
            assert response.status_code == 200
        
        # Assert final state
        for email in students:
            assert email in activities[activity_name]["participants"]


# ==================== REMOVE PARTICIPANT ENDPOINT TESTS ====================

class TestRemoveParticipantEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants endpoint"""
    
    def test_remove_participant_success(self, client, reset_activities):
        """
        Test successful removal of an enrolled student from an activity.
        
        Arrange: Create a test client and identify an enrolled student
        Act: Make a DELETE request to remove the participant
        Assert: Verify success message and participant is removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already enrolled
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
    
    def test_remove_not_enrolled_participant(self, client, reset_activities):
        """
        Test that removing non-enrolled student returns 404.
        
        Arrange: Create a test client and use a non-enrolled student email
        Act: Make a DELETE request for a non-enrolled student
        Assert: Verify 404 error response with appropriate message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notstudent@mergington.edu"  # Not enrolled
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
    
    def test_remove_from_invalid_activity(self, client, reset_activities):
        """
        Test that removing from non-existent activity returns 404.
        
        Arrange: Create a test client and prepare invalid activity name
        Act: Make a DELETE request with non-existent activity name
        Assert: Verify 404 error response with appropriate message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_remove_multiple_participants(self, client, reset_activities):
        """
        Test removing multiple participants from an activity.
        
        Arrange: Create a test client with an activity that has multiple participants
        Act: Remove multiple participants one by one
        Assert: Verify all removals succeed and participants list is updated correctly
        """
        # Arrange
        activity_name = "Drama Club"
        participants_to_remove = ["lucas@mergington.edu", "claire@mergington.edu"]
        
        # Act & Assert
        for email in participants_to_remove:
            response = client.delete(
                f"/activities/{activity_name}/participants",
                params={"email": email}
            )
            assert response.status_code == 200
            assert email not in activities[activity_name]["participants"]
        
        # Assert final state - both should be removed
        assert "lucas@mergington.edu" not in activities[activity_name]["participants"]
        assert "claire@mergington.edu" not in activities[activity_name]["participants"]


# ==================== INTEGRATION TESTS ====================

class TestIntegration:
    """Integration tests combining multiple operations"""
    
    def test_signup_then_remove_flow(self, client, reset_activities):
        """
        Test the complete flow of signing up and then removing a student.
        
        Arrange: Create a test client and prepare test data
        Act: Sign up a student, then remove them
        Assert: Verify both operations succeed and final state is correct
        """
        # Arrange
        activity_name = "Tennis Club"
        email = "integration@mergington.edu"
        
        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]
        
        # Act - Remove
        remove_response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert remove_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
    
    def test_signup_remove_signup_flow(self, client, reset_activities):
        """
        Test that a student can sign up, be removed, and sign up again.
        
        Arrange: Create a test client and prepare test data
        Act: Sign up, remove, and sign up again for the same activity
        Assert: Verify all operations succeed
        """
        # Arrange
        activity_name = "Art Studio"
        email = "reusable@mergington.edu"
        
        # Act - First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Act - Remove
        response2 = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Act - Second signup
        response3 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response3.status_code == 200
        assert email in activities[activity_name]["participants"]
