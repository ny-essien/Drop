import pytest
from datetime import datetime, timedelta
from app.services.notification_service import NotificationService
from app.models import Notification

@pytest.fixture
async def notification_service():
    return NotificationService()

@pytest.fixture
async def sample_notification(notification_service):
    notification = await notification_service.create_notification(
        type="test",
        title="Test Notification",
        message="This is a test notification",
        status="pending"
    )
    return notification

@pytest.mark.asyncio
async def test_create_notification(notification_service):
    notification = await notification_service.create_notification(
        type="test",
        title="Test Notification",
        message="This is a test notification",
        status="pending"
    )
    assert notification.type == "test"
    assert notification.title == "Test Notification"
    assert notification.status == "pending"

@pytest.mark.asyncio
async def test_get_notification(notification_service, sample_notification):
    retrieved = await notification_service.get_notification(sample_notification.id)
    assert retrieved.id == sample_notification.id
    assert retrieved.type == "test"

@pytest.mark.asyncio
async def test_get_notifications_with_filter(notification_service):
    # Create multiple notifications with different types
    await notification_service.create_notification(
        type="type1",
        title="Type 1",
        message="Message 1",
        status="sent"
    )
    await notification_service.create_notification(
        type="type2",
        title="Type 2",
        message="Message 2",
        status="pending"
    )

    # Test type filter
    type1_notifications = await notification_service.get_notifications(type="type1")
    assert len(type1_notifications) == 1
    assert type1_notifications[0].type == "type1"

    # Test status filter
    pending_notifications = await notification_service.get_notifications(status="pending")
    assert len(pending_notifications) >= 1
    assert all(n.status == "pending" for n in pending_notifications)

@pytest.mark.asyncio
async def test_update_notification_status(notification_service, sample_notification):
    updated = await notification_service.update_notification_status(
        sample_notification.id,
        status="sent",
        error="Test error"
    )
    assert updated.status == "sent"
    assert updated.error == "Test error"

@pytest.mark.asyncio
async def test_delete_notification(notification_service, sample_notification):
    result = await notification_service.delete_notification(sample_notification.id)
    assert result is True
    
    # Verify deletion
    with pytest.raises(ValueError):
        await notification_service.get_notification(sample_notification.id)

@pytest.mark.asyncio
async def test_get_notification_stats(notification_service):
    # Create notifications with different statuses
    await notification_service.create_notification(
        type="test",
        title="Sent",
        message="Sent message",
        status="sent"
    )
    await notification_service.create_notification(
        type="test",
        title="Failed",
        message="Failed message",
        status="failed"
    )
    await notification_service.create_notification(
        type="test",
        title="Pending",
        message="Pending message",
        status="pending"
    )

    stats = await notification_service.get_notification_stats()
    assert "total" in stats
    assert "sent" in stats
    assert "failed" in stats
    assert "pending" in stats
    assert stats["total"] >= 3 