import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def reset_state():
    """Reset app.activities to initial state before each test"""
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app"""
    return TestClient(app)


def test_get_activities(client, reset_state):
    """Test retrieving all activities"""
    # Arrange
    expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    assert response.status_code == 200
    assert isinstance(data, dict)
    for activity in expected_activities:
        assert activity in data


def test_signup_successful(client, reset_state):
    """Test successfully signing up for an activity"""
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    
    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    assert email in activities_response.json()[activity]["participants"]


def test_signup_duplicate_error(client, reset_state):
    """Test duplicate signup returns 400 error"""
    # Arrange
    email = "duplicate@mergington.edu"
    activity = "Chess Club"
    
    # Act - First signup
    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Act - Attempt duplicate signup
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_remove_participant(client, reset_state):
    """Test removing a participant from an activity"""
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"
    
    # Act
    response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity]["participants"]


def test_remove_nonexistent_participant(client, reset_state):
    """Test removing a non-existent participant returns 404"""
    # Arrange
    email = "nonexistent@mergington.edu"
    activity = "Chess Club"
    
    # Act
    response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_signup_unknown_activity_404(client, reset_state):
    """Test signing up for unknown activity returns 404"""
    # Arrange
    email = "student@mergington.edu"
    activity = "Unknown Activity"
    
    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
