import pytest
from datetime import datetime
from app.services.notification_service import NotificationService
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.db.mongodb import get_database

@pytest.fixture
async def notification_service():
    return NotificationService()

@pytest.fixture
async def test_db():
    db = await get_database()
    yield db
    await db.notifications.delete_many({})

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
    notification = await notification_service.create_notification(
        user_id="test_user_id",
        type=NotificationType.ORDER,
        title="Test Notification",
        message="This is a test notification",
        status=NotificationStatus.UNREAD
    )
    assert notification.user_id == "test_user_id"
    assert notification.type == NotificationType.ORDER
    assert notification.title == "Test Notification"
    assert notification.message == "This is a test notification"
    assert notification.status == NotificationStatus.UNREAD

@pytest.mark.asyncio
async def test_get_notification(notification_service, test_db):
    # First create a notification
    created_notification = await notification_service.create_notification(
        user_id="test_user_id",
        type=NotificationType.ORDER,
        title="Test Notification",
        message="This is a test notification",
        status=NotificationStatus.UNREAD
    )
    
    # Then get it by ID
    notification = await notification_service.get_notification(created_notification.id)
    assert notification is not None
    assert notification.id == created_notification.id
    assert notification.title == "Test Notification"

@pytest.mark.asyncio
async def test_get_notifications_with_filter(notification_service, test_db):
    # Create multiple notifications with different types
    await notification_service.create_notification(
        user_id="test_user_id",
        type=NotificationType.ORDER,
        title="Order Notification",
        message="Order message",
        status=NotificationStatus.UNREAD
    )
    await notification_service.create_notification(
        user_id="test_user_id",
        type=NotificationType.PAYMENT,
        title="Payment Notification",
        message="Payment message",
        status=NotificationStatus.UNREAD
    )

    # Test filtering by type
    order_notifications = await notification_service.get_notifications(type=NotificationType.ORDER)
    assert len(order_notifications) >= 1
    assert all(n.type == NotificationType.ORDER for n in order_notifications)

    # Test filtering by status
    unread_notifications = await notification_service.get_notifications(status=NotificationStatus.UNREAD)
    assert len(unread_notifications) >= 1
    assert all(n.status == NotificationStatus.UNREAD for n in unread_notifications)

@pytest.mark.asyncio
async def test_update_notification_status(notification_service, test_db):
    # Create a notification
    notification = await notification_service.create_notification(
        user_id="test_user_id",
        type=NotificationType.ORDER,
        title="Test Notification",
        message="This is a test notification",
        status=NotificationStatus.UNREAD
    )
    
    # Update its status
    updated_notification = await notification_service.update_notification_status(
        notification.id,
        NotificationStatus.READ
    )
    assert updated_notification.status == NotificationStatus.READ

@pytest.mark.asyncio
async def test_delete_notification(notification_service, test_db):
    # Create a notification
    notification = await notification_service.create_notification(
        user_id="test_user_id",
        type=NotificationType.ORDER,
        title="Test Notification",
        message="This is a test notification",
        status=NotificationStatus.UNREAD
    )
    
    # Delete it
    result = await notification_service.delete_notification(notification.id)
    assert result is True
    
    # Verify it's deleted
    deleted_notification = await notification_service.get_notification(notification.id)
    assert deleted_notification is None

@pytest.mark.asyncio
async def test_get_notification_stats(notification_service, test_db):
    # Create notifications with different statuses
    await notification_service.create_notification(
        user_id="test_user_id",
        type=NotificationType.ORDER,
        title="Unread",
        message="Unread message",
        status=NotificationStatus.UNREAD
    )
    await notification_service.create_notification(
        user_id="test_user_id",
        type=NotificationType.ORDER,
        title="Read",
        message="Read message",
        status=NotificationStatus.READ
    )
    await notification_service.create_notification(
        user_id="test_user_id",
        type=NotificationType.ORDER,
        title="Archived",
        message="Archived message",
        status=NotificationStatus.ARCHIVED
    )
    
    stats = await notification_service.get_notification_stats()
    assert stats["total"] >= 3
    assert stats["unread"] >= 1
    assert stats["read"] >= 1
    assert stats["archived"] >= 1 