"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoints:
    """Test suite for activities endpoints"""

    def test_get_activities(self):
        """Test fetching all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        # Verify structure of activity
        first_activity = next(iter(data.values()))
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity

    def test_get_activities_specific_activity(self):
        """Test that specific activities are present"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Basketball Team" in data
        assert "Chess Club" in data
        assert "Programming Class" in data


class TestSignupEndpoints:
    """Test suite for signup endpoints"""

    def test_signup_for_activity_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Art%20Studio/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]
        assert "Art Studio" in data["message"]

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistent%20Activity/signup?email=unique-test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email(self):
        """Test that duplicate email signup is rejected"""
        # First signup
        email = "duplicate@mergington.edu"
        response1 = client.post(
            "/activities/Volleyball%20Club/signup?email=duplicate@mergington.edu"
        )
        assert response1.status_code == 200

        # Second signup with same email
        response2 = client.post(
            "/activities/Drama%20Club/signup?email=duplicate@mergington.edu"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_participants_list_updated(self):
        """Test that participants list is updated after signup"""
        email = "newstudent@mergington.edu"
        # Get initial state
        response1 = client.get("/activities")
        initial_participants = response1.json()["Debate Team"]["participants"].copy()

        # Sign up
        response2 = client.post(
            f"/activities/Debate%20Team/signup?email={email}"
        )
        assert response2.status_code == 200

        # Verify participants list updated
        response3 = client.get("/activities")
        updated_participants = response3.json()["Debate Team"]["participants"]
        assert email in updated_participants
        assert len(updated_participants) == len(initial_participants) + 1


class TestUnregisterEndpoints:
    """Test suite for unregister endpoints"""

    def test_unregister_success(self):
        """Test successful unregister from activity"""
        email = "unregister@mergington.edu"
        # First signup
        client.post("/activities/Robotics%20Club/signup?email=unregister@mergington.edu")

        # Verify participant was added
        response1 = client.get("/activities")
        assert email in response1.json()["Robotics Club"]["participants"]

        # Unregister
        response2 = client.delete(
            f"/activities/Robotics%20Club/unregister?email={email}"
        )
        assert response2.status_code == 200
        data = response2.json()
        assert "Unregistered" in data["message"]

        # Verify participant was removed
        response3 = client.get("/activities")
        assert email not in response3.json()["Robotics Club"]["participants"]

    def test_unregister_not_found_activity(self):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/NonExistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_participant_not_found(self):
        """Test unregister of non-existent participant"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]


class TestRootEndpoint:
    """Test suite for root endpoint"""

    def test_root_redirect(self):
        """Test that root endpoint redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
