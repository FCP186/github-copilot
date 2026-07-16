import copy
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app import activities, app


INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_signup_and_unregister_round_trip(client):
    # Arrange
    email = "test.student@mergington.edu"

    # Act
    signup_response = client.post(f"/activities/Chess Club/signup?email={email}")
    activities_after_signup = client.get("/activities").json()
    unregister_response = client.delete(f"/activities/Chess Club/unregister?email={email}")
    activities_after_unregister = client.get("/activities").json()

    # Assert
    assert signup_response.status_code == 200
    assert email in activities_after_signup["Chess Club"]["participants"]
    assert unregister_response.status_code == 200
    assert email not in activities_after_unregister["Chess Club"]["participants"]


def test_duplicate_signup_returns_400(client):
    # Arrange
    email = "dup.student@mergington.edu"

    # Act
    first_signup_response = client.post(f"/activities/Chess Club/signup?email={email}")
    duplicate_signup_response = client.post(f"/activities/Chess Club/signup?email={email}")
    activities_after_attempts = client.get("/activities").json()

    # Assert
    assert first_signup_response.status_code == 200
    assert duplicate_signup_response.status_code == 400
    assert activities_after_attempts["Chess Club"]["participants"].count(email) == 1
