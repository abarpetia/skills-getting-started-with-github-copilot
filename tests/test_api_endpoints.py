from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange
    original_state = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original_state))


@pytest.fixture()
def client():
    # Arrange
    return TestClient(app)


def test_root_redirects_to_static_index(client):
    # Arrange
    path = "/"

    # Act
    response = client.get(path, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_catalog(client):
    # Arrange
    path = "/activities"

    # Act
    response = client.get(path)

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_student_to_activity(client):
    # Arrange
    email = "new.student@mergington.edu"
    path = f"/activities/Chess Club/signup?email={email}"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "michael@mergington.edu"
    path = f"/activities/Chess Club/signup?email={email}"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_removes_student_from_activity(client):
    # Arrange
    email = "michael@mergington.edu"
    path = f"/activities/Chess Club/unregister?email={email}"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_rejects_missing_participant(client):
    # Arrange
    email = "missing.student@mergington.edu"
    path = f"/activities/Chess Club/unregister?email={email}"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unknown_activity_returns_not_found(client):
    # Arrange
    path = "/activities/Unknown Activity/signup?email=test@example.com"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
