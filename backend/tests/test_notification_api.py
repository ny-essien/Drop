import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app
from app.models.notification import Notification, NotificationType, NotificationStatus, NotificationCreate, NotificationUpdate
from app.models.user import User
from app.core.security import create_access_token
from datetime import datetime, timedelta
from bson import ObjectId

client = TestClient(app)

@pytest.fixture
def test_user():
    return User(
        id=str(ObjectId()),
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False
    )

@pytest.fixture
def test_token(test_user):
    return create_access_token(data={"sub": test_user.email})

@pytest.fixture
def test_notification(test_user):
    return Notification(
        id=str(ObjectId()),
        user_id=test_user.id,
        type=NotificationType.INFO,
        title="Test Notification",
        message="This is a test notification",
        status=NotificationStatus.UNREAD,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

def test_create_notification(test_token, test_user):
    notification_data = {
        "type": NotificationType.INFO,
        "title": "Test Notification",
        "message": "This is a test notification",
        "status": NotificationStatus.UNREAD
    }
    
    response = client.post(
        "/api/v1/notifications/",
        json=notification_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["type"] == notification_data["type"]
    assert data["title"] == notification_data["title"]
    assert data["message"] == notification_data["message"]
    assert data["status"] == notification_data["status"]
    assert data["user_id"] == test_user.id

def test_get_notifications(test_token, test_user, test_notification):
    response = client.get(
        "/api/v1/notifications/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["user_id"] == test_user.id

def test_get_notification(test_token, test_user, test_notification):
    response = client.get(
        f"/api/v1/notifications/{test_notification.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_notification.id
    assert data["user_id"] == test_user.id

def test_update_notification(test_token, test_user, test_notification):
    update_data = {
        "status": NotificationStatus.READ
    }
    
    response = client.patch(
        f"/api/v1/notifications/{test_notification.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_notification.id
    assert data["status"] == update_data["status"]

def test_delete_notification(test_token, test_user, test_notification):
    response = client.delete(
        f"/api/v1/notifications/{test_notification.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify the notification was deleted
    response = client.get(
        f"/api/v1/notifications/{test_notification.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_notification_stats(test_token, test_user, test_notification):
    response = client.get(
        "/api/v1/notifications/stats",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, dict)
    assert "total" in data
    assert "unread" in data
    assert "read" in data

def test_unauthorized_access():
    response = client.get("/api/v1/notifications/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_forbidden_access(test_token, test_user):
    # Create a notification for a different user
    other_user_id = str(ObjectId())
    other_notification = Notification(
        id=str(ObjectId()),
        user_id=other_user_id,
        type=NotificationType.INFO,
        title="Other User's Notification",
        message="This is another user's notification",
        status=NotificationStatus.UNREAD,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    response = client.get(
        f"/api/v1/notifications/{other_notification.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN 