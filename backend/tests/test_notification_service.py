import pytest
from datetime import datetime
from bson import ObjectId
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.services.notification_service import NotificationService
from app.db.mongodb import get_database

@pytest.fixture
async def notification_service(test_db):
    """Create a notification service instance"""
    service = NotificationService()
    service.db = test_db
    return service

@pytest.fixture
async def sample_notification(notification_service):
    notification = await notification_service.create_notification(
        user_id="test_user_id",
        type=NotificationType.ORDER,
        title="Test Notification",
        message="This is a test notification",
        status=NotificationStatus.UNREAD
    )
    yield notification
    await notification_service.delete_notification(notification.id)

@pytest.mark.asyncio
async def test_create_notification(notification_service, test_db):
    """Test creating a notification"""
    notification = await notification_service.create_notification(
        user_id="test_user",
        type=NotificationType.INFO,
        title="Test Notification",
        message="This is a test notification"
    )
    assert notification.user_id == "test_user"
    assert notification.type == NotificationType.INFO
    assert notification.title == "Test Notification"
    assert notification.message == "This is a test notification"
    assert notification.status == NotificationStatus.UNREAD
    assert notification.created_at is not None
    assert notification.updated_at is not None

@pytest.mark.asyncio
async def test_get_notification(notification_service, test_db):
    """Test getting a notification by ID"""
    # Create a test notification
    notification = await notification_service.create_notification(
        user_id="test_user",
        type=NotificationType.INFO,
        title="Test Notification",
        message="This is a test notification"
    )
    
    # Get the notification
    retrieved_notification = await notification_service.get_notification(notification.id)
    assert retrieved_notification is not None
    assert retrieved_notification.id == notification.id
    assert retrieved_notification.user_id == notification.user_id
    assert retrieved_notification.type == notification.type
    assert retrieved_notification.title == notification.title
    assert retrieved_notification.message == notification.message

@pytest.mark.asyncio
async def test_get_notifications_with_filter(notification_service, test_db):
    """Test getting notifications with filters"""
    # Create test notifications
    await notification_service.create_notification(
        user_id="test_user",
        type=NotificationType.INFO,
        title="Test Notification 1",
        message="This is a test notification"
    )
    await notification_service.create_notification(
        user_id="test_user",
        type=NotificationType.SYSTEM,
        title="Test Notification 2",
        message="This is a system notification"
    )
    
    # Get notifications with type filter
    info_notifications = await notification_service.get_notifications(
        user_id="test_user",
        type=NotificationType.INFO
    )
    assert len(info_notifications) == 1
    assert info_notifications[0].type == NotificationType.INFO
    
    # Get notifications with status filter
    unread_notifications = await notification_service.get_notifications(
        user_id="test_user",
        status=NotificationStatus.UNREAD
    )
    assert len(unread_notifications) == 2
    assert all(n.status == NotificationStatus.UNREAD for n in unread_notifications)

@pytest.mark.asyncio
async def test_update_notification_status(notification_service, test_db):
    """Test updating notification status"""
    # Create a test notification
    notification = await notification_service.create_notification(
        user_id="test_user",
        type=NotificationType.INFO,
        title="Test Notification",
        message="This is a test notification"
    )
    
    # Update the notification status
    updated_notification = await notification_service.update_notification_status(
        notification.id,
        NotificationStatus.READ
    )
    assert updated_notification is not None
    assert updated_notification.id == notification.id
    assert updated_notification.status == NotificationStatus.READ

@pytest.mark.asyncio
async def test_delete_notification(notification_service, test_db):
    """Test deleting a notification"""
    # Create a test notification
    notification = await notification_service.create_notification(
        user_id="test_user",
        type=NotificationType.INFO,
        title="Test Notification",
        message="This is a test notification"
    )
    
    # Delete the notification
    result = await notification_service.delete_notification(notification.id)
    assert result is True
    
    # Verify the notification is deleted
    deleted_notification = await notification_service.get_notification(notification.id)
    assert deleted_notification is None

@pytest.mark.asyncio
async def test_get_notification_stats(notification_service, test_db):
    """Test getting notification statistics"""
    # Create test notifications with different statuses
    await notification_service.create_notification(
        user_id="test_user",
        type=NotificationType.INFO,
        title="Test Notification 1",
        message="This is a test notification"
    )
    await notification_service.create_notification(
        user_id="test_user",
        type=NotificationType.SYSTEM,
        title="Test Notification 2",
        message="This is a system notification"
    )
    
    # Update one notification to READ status
    notifications = await notification_service.get_notifications(user_id="test_user")
    await notification_service.update_notification_status(
        notifications[0].id,
        NotificationStatus.READ
    )
    
    # Get statistics
    stats = await notification_service.get_notification_stats("test_user")
    assert stats[NotificationStatus.UNREAD] == 1
    assert stats[NotificationStatus.READ] == 1 