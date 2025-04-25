import pytest
from datetime import datetime
from app.services.notification_service import NotificationService
from app.models.notification import Notification, NotificationType, NotificationStatus

@pytest.fixture
async def notification_service():
    return NotificationService()

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
async def test_create_notification(notification_service):
    notification = await notification_service.create_notification(
        user_id="test_user_id",
        type=NotificationType.ORDER,
        title="Test Notification",
        message="This is a test notification",
        status=NotificationStatus.UNREAD
    )
    assert notification.type == NotificationType.ORDER
    assert notification.title == "Test Notification"
    assert notification.status == NotificationStatus.UNREAD

@pytest.mark.asyncio
async def test_get_notification(notification_service, sample_notification):
    retrieved = await notification_service.get_notification(sample_notification.id)
    assert retrieved.id == sample_notification.id
    assert retrieved.title == sample_notification.title

@pytest.mark.asyncio
async def test_get_notifications_with_filter(notification_service):
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
async def test_update_notification_status(notification_service, sample_notification):
    updated = await notification_service.update_notification_status(
        sample_notification.id,
        status=NotificationStatus.READ,
        error="Test error"
    )
    assert updated.status == NotificationStatus.READ
    assert updated.error == "Test error"

@pytest.mark.asyncio
async def test_delete_notification(notification_service, sample_notification):
    result = await notification_service.delete_notification(sample_notification.id)
    assert result is True

@pytest.mark.asyncio
async def test_get_notification_stats(notification_service):
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
        type=NotificationType.PAYMENT,
        title="Read",
        message="Read message",
        status=NotificationStatus.READ
    )
    await notification_service.create_notification(
        user_id="test_user_id",
        type=NotificationType.SHIPMENT,
        title="Archived",
        message="Archived message",
        status=NotificationStatus.ARCHIVED
    )

    stats = await notification_service.get_notification_stats()
    assert isinstance(stats, dict)
    assert all(key in stats for key in ["total", "unread", "read", "archived"])
    assert stats["total"] >= 3
    assert stats["unread"] >= 1
    assert stats["read"] >= 1
    assert stats["archived"] >= 1 