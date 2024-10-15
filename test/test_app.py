import sqlite3

import pytest
from fastapi.testclient import TestClient

from app import app  # Assuming your FastAPI app is in a file called `app.py`
from db import create_table, get_db

client = TestClient(app)


# Fixture to create an in-memory database for each test
@pytest.fixture(scope="function")
def db_connection():
    # Create an in-memory SQLite database
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    create_table(conn)  # Create the table structure
    yield conn  # Provide the connection to the test
    conn.close()  # Teardown: Close the connection after the test


# Override the get_db dependency with an in-memory database for tests
@pytest.fixture(scope="function")
def override_get_db(db_connection):
    def _override_get_db():
        db_ = db_connection
        yield db_

    # Override the dependency
    app.dependency_overrides[get_db] = _override_get_db


# Test creating a subscription
def test_create_subscription(override_get_db):
    payload = {
        "user_name": "John Doe",
        "plan": "basic"
    }
    response = client.post("/subscriptions/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["user_name"] == "John Doe"
    assert data["plan"] == "basic"
    assert data["cancelled"] is False
    assert data["paused"] is False


def test_update_subscription_wrong_id(override_get_db):
    # Update the subscription plan
    update_payload = {
        "plan": "premium"
    }
    response = client.put(f"/subscriptions/4/plan", json=update_payload)
    assert response.status_code == 404


# Test updating a subscription plan
def test_update_subscription_plan(override_get_db):
    # First, create a subscription
    payload = {
        "user_name": "John Doe",
        "plan": "basic"
    }
    create_response = client.post("/subscriptions/", json=payload)
    subscription_id = create_response.json()["id"]

    # Update the subscription plan
    update_payload = {
        "plan": "premium"
    }
    response = client.put(f"/subscriptions/{subscription_id}/plan", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["plan"] == "premium"


# Test pausing a subscription
def test_pause_subscription(override_get_db):
    # First, create a subscription
    payload = {
        "user_name": "John Doe",
        "plan": "basic"
    }
    create_response = client.post("/subscriptions/", json=payload)
    subscription_id = create_response.json()["id"]

    # Pause the subscription
    response = client.post(f"/subscriptions/{subscription_id}/pause")
    assert response.status_code == 200
    data = response.json()
    assert data["paused"] is True
    assert data["paused_at"] is not None


# Test resuming a subscription
def test_resume_subscription(override_get_db):
    # First, create a subscription and pause it
    payload = {
        "user_name": "John Doe",
        "plan": "basic"
    }
    create_response = client.post("/subscriptions/", json=payload)
    subscription_id = create_response.json()["id"]

    # Pause the subscription first
    client.post(f"/subscriptions/{subscription_id}/pause")

    # Resume the subscription
    response = client.post(f"/subscriptions/{subscription_id}/resume")
    assert response.status_code == 200
    data = response.json()
    assert data["paused"] is False
    assert data["resumed_at"] is not None


def test_resume_subscription_wrong_id(override_get_db):
    # Update the subscription plan
    update_payload = {
        "plan": "premium"
    }
    response = client.post(f"/subscriptions/4/resume", json=update_payload)
    assert response.status_code == 404


# Test retrieving all subscriptions
def test_get_all_subscriptions(override_get_db):
    # Create two subscriptions
    payload_1 = {
        "user_name": "John Doe",
        "plan": "basic"
    }
    payload_2 = {
        "user_name": "Jane Doe",
        "plan": "premium"
    }
    client.post("/subscriptions/", json=payload_1)
    client.post("/subscriptions/", json=payload_2)

    # Retrieve all subscriptions
    response = client.get("/subscriptions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["user_name"] == "John Doe"
    assert data[1]["user_name"] == "Jane Doe"


# Test pausing a non-existent subscription
def test_pause_non_existent_subscription(override_get_db):
    response = client.post("/subscriptions/9999/pause")
    assert response.status_code == 404
    assert response.json()["detail"] == "Subscription not found"
