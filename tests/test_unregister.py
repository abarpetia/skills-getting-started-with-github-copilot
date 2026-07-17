from fastapi.testclient import TestClient

from src.app import app


def test_unregister_participant_removes_email_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    client = TestClient(app)

    # Act
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    unregister_response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    activities_response = client.get("/activities")

    # Assert
    assert signup_response.status_code == 200
    assert unregister_response.status_code == 200

    activity = activities_response.json()[activity_name]
    assert email not in activity["participants"]
