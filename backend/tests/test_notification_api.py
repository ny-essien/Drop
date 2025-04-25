import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.models.notification import NotificationType, NotificationStatus

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    access_token = create_access_token({"sub": "test@example.com"})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.mark.asyncio
async def test_create_notification(test_client, auth_headers):
    response = test_client.post(
        "/api/v1/notifications/",
        headers=auth_headers,
        json={
            "user_id": "test_user_id",
            "type": NotificationType.ORDER,
            "title": "Test Notification",
            "message": "This is a test notification",
            "status": NotificationStatus.UNREAD
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Notification"
    assert data["type"] == NotificationType.ORDER
    assert data["status"] == NotificationStatus.UNREAD

@pytest.mark.asyncio
async def test_get_notifications(test_client, auth_headers):
    response = test_client.get("/api/v1/notifications/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_notification_by_id(test_client, auth_headers):
    # First create a notification
    create_response = test_client.post(
        "/api/v1/notifications/",
        headers=auth_headers,
        json={
            "user_id": "test_user_id",
            "type": NotificationType.ORDER,
            "title": "Test Notification",
            "message": "This is a test notification",
            "status": NotificationStatus.UNREAD
        }
    )
    notification_id = create_response.json()["id"]
    
    # Then get it by ID
    response = test_client.get(f"/api/v1/notifications/{notification_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == notification_id
    assert data["title"] == "Test Notification"

@pytest.mark.asyncio
async def test_update_notification_status(test_client, auth_headers):
    # First create a notification
    create_response = test_client.post(
        "/api/v1/notifications/",
        headers=auth_headers,
        json={
            "user_id": "test_user_id",
            "type": NotificationType.ORDER,
            "title": "Test Notification",
            "message": "This is a test notification",
            "status": NotificationStatus.UNREAD
        }
    )
    notification_id = create_response.json()["id"]
    
    # Then update its status
    response = test_client.put(
        f"/api/v1/notifications/{notification_id}/status",
        headers=auth_headers,
        json={"status": NotificationStatus.READ, "error": None}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == NotificationStatus.READ

@pytest.mark.asyncio
async def test_delete_notification(test_client, auth_headers):
    # First create a notification
    create_response = test_client.post(
        "/api/v1/notifications/",
        headers=auth_headers,
        json={
            "user_id": "test_user_id",
            "type": NotificationType.ORDER,
            "title": "Test Notification",
            "message": "This is a test notification",
            "status": NotificationStatus.UNREAD
        }
    )
    notification_id = create_response.json()["id"]
    
    # Then delete it
    response = test_client.delete(f"/api/v1/notifications/{notification_id}", headers=auth_headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_notification_stats(test_client, auth_headers):
    response = test_client.get("/api/v1/notifications/stats/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert all(key in data for key in ["total", "unread", "read", "archived"])

@pytest.mark.asyncio
async def test_unauthorized_access(test_client):
    # Test endpoints without authentication
    response = test_client.get("/api/v1/notifications/")
    assert response.status_code == 401
    
    response = test_client.post(
        "/api/v1/notifications/",
        json={
            "user_id": "test_user_id",
            "type": NotificationType.ORDER,
            "title": "Test Notification",
            "message": "This is a test notification",
            "status": NotificationStatus.UNREAD
        }
    )
    assert response.status_code == 401 