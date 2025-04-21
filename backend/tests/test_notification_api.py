import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from app.core.security import create_access_token
from app.models import User, Notification

client = TestClient(app)

@pytest.fixture
def auth_token():
    # Create a test token (in a real scenario, use a test user)
    return create_access_token({"sub": "test@example.com", "is_admin": True})

@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.mark.asyncio
async def test_create_notification(auth_headers):
    response = client.post(
        "/api/notifications/",
        headers=auth_headers,
        json={
            "type": "test",
            "title": "Test Notification",
            "message": "This is a test notification",
            "status": "pending"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "test"
    assert data["title"] == "Test Notification"

@pytest.mark.asyncio
async def test_get_notifications(auth_headers):
    response = client.get("/api/notifications/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_notification_by_id(auth_headers):
    # First create a notification
    create_response = client.post(
        "/api/notifications/",
        headers=auth_headers,
        json={
            "type": "test",
            "title": "Test Notification",
            "message": "This is a test notification",
            "status": "pending"
        }
    )
    notification_id = create_response.json()["id"]

    # Then retrieve it
    response = client.get(f"/api/notifications/{notification_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == notification_id

@pytest.mark.asyncio
async def test_update_notification_status(auth_headers):
    # First create a notification
    create_response = client.post(
        "/api/notifications/",
        headers=auth_headers,
        json={
            "type": "test",
            "title": "Test Notification",
            "message": "This is a test notification",
            "status": "pending"
        }
    )
    notification_id = create_response.json()["id"]

    # Then update its status
    response = client.put(
        f"/api/notifications/{notification_id}/status",
        headers=auth_headers,
        json={"status": "sent", "error": "Test error"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "sent"
    assert data["error"] == "Test error"

@pytest.mark.asyncio
async def test_delete_notification(auth_headers):
    # First create a notification
    create_response = client.post(
        "/api/notifications/",
        headers=auth_headers,
        json={
            "type": "test",
            "title": "Test Notification",
            "message": "This is a test notification",
            "status": "pending"
        }
    )
    notification_id = create_response.json()["id"]

    # Then delete it
    response = client.delete(f"/api/notifications/{notification_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify it's deleted
    get_response = client.get(f"/api/notifications/{notification_id}", headers=auth_headers)
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_get_notification_stats(auth_headers):
    response = client.get("/api/notifications/stats/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "sent" in data
    assert "failed" in data
    assert "pending" in data

@pytest.mark.asyncio
async def test_unauthorized_access():
    # Test endpoints without authentication
    response = client.get("/api/notifications/")
    assert response.status_code == 401

    response = client.post(
        "/api/notifications/",
        json={
            "type": "test",
            "title": "Test Notification",
            "message": "This is a test notification"
        }
    )
    assert response.status_code == 401 