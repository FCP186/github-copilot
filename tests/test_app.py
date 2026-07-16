import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app import app


def test_unregister_participant_removes_email_from_activity():
    with TestClient(app) as client:
        signup_response = client.post(
            "/activities/Chess Club/signup?email=test.student@mergington.edu"
        )
        assert signup_response.status_code == 200

        unregister_response = client.delete(
            "/activities/Chess Club/unregister?email=test.student@mergington.edu"
        )
        assert unregister_response.status_code == 200

        activities = client.get("/activities").json()
        assert "test.student@mergington.edu" not in activities["Chess Club"]["participants"]
