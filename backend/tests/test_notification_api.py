import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.notification import NotificationType, NotificationStatus
from app.db.mongodb import get_database

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
async def test_db():
    db = await get_database()
    yield db
    await db.notifications.delete_many({})

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test_token"}

@pytest.mark.asyncio
async def test_create_notification(test_client, auth_headers, test_db):
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
async def test_get_notifications(test_client, auth_headers, test_db):
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
    assert create_response.status_code == 200
    
    # Then get all notifications
    response = test_client.get("/api/v1/notifications/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(n["title"] == "Test Notification" for n in data)

@pytest.mark.asyncio
async def test_get_notification_by_id(test_client, auth_headers, test_db):
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
    assert create_response.status_code == 200
    notification_id = create_response.json()["id"]
    
    # Then get it by ID
    response = test_client.get(f"/api/v1/notifications/{notification_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == notification_id
    assert data["title"] == "Test Notification"

@pytest.mark.asyncio
async def test_update_notification_status(test_client, auth_headers, test_db):
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
    assert create_response.status_code == 200
    notification_id = create_response.json()["id"]
    
    # Then update its status
    response = test_client.put(
        f"/api/v1/notifications/{notification_id}/status",
        headers=auth_headers,
        json={
            "status": NotificationStatus.READ
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == NotificationStatus.READ

@pytest.mark.asyncio
async def test_delete_notification(test_client, auth_headers, test_db):
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
    assert create_response.status_code == 200
    notification_id = create_response.json()["id"]
    
    # Then delete it
    response = test_client.delete(f"/api/v1/notifications/{notification_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify it's deleted
    get_response = test_client.get(f"/api/v1/notifications/{notification_id}", headers=auth_headers)
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_get_notification_stats(test_client, auth_headers, test_db):
    # Create notifications with different statuses
    for status in [NotificationStatus.UNREAD, NotificationStatus.READ, NotificationStatus.ARCHIVED]:
        response = test_client.post(
            "/api/v1/notifications/",
            headers=auth_headers,
            json={
                "user_id": "test_user_id",
                "type": NotificationType.ORDER,
                "title": f"Test {status}",
                "message": f"This is a {status} notification",
                "status": status
            }
        )
        assert response.status_code == 200
    
    # Get stats
    response = test_client.get("/api/v1/notifications/stats/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert data["unread"] >= 1
    assert data["read"] >= 1
    assert data["archived"] >= 1

@pytest.mark.asyncio
async def test_unauthorized_access(test_client, test_db):
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