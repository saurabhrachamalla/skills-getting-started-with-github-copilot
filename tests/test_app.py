import copy
import urllib.parse

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


def activity_path(activity_name: str) -> str:
    return f"/activities/{urllib.parse.quote(activity_name, safe='')}/signup"


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = copy.deepcopy(ORIGINAL_ACTIVITIES)
    yield


def test_get_activities_returns_activity_data():
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"

    # Act
    response = client.post(activity_path(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activity_response = client.get("/activities").json()
    assert email in activity_response[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"

    client.post(activity_path(activity_name), params={"email": email})

    # Act
    response = client.post(activity_path(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_invalid_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(activity_path(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_participant_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{urllib.parse.quote(activity_name, safe='')}/participants/{urllib.parse.quote(email, safe='')}" )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    activity_response = client.get("/activities").json()
    assert email not in activity_response[activity_name]["participants"]


def test_delete_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "nobody@mergington.edu"

    # Act
    response = client.delete(f"/activities/{urllib.parse.quote(activity_name, safe='')}/participants/{urllib.parse.quote(email, safe='')}" )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
