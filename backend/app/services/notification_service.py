from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models import Notification
from app.config import settings

class NotificationService:
    async def create_notification(
        self,
        type: str,
        title: str,
        message: str,
        status: str = "pending",
        error: Optional[str] = None,
        metadata: Dict[str, Any] = {}
    ) -> Notification:
        """Create a new notification"""
        notification = Notification(
            type=type,
            title=title,
            message=message,
            status=status,
            error=error,
            metadata=metadata
        )
        await notification.save()
        return notification

    async def get_notifications(
        self,
        type: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Notification]:
        """Get notifications with optional filtering"""
        query = {}
        
        if type:
            query["type"] = type
        if status:
            query["status"] = status
        if start_date:
            query["created_at"] = {"$gte": start_date}
        if end_date:
            query["created_at"] = {"$lte": end_date}
        
        notifications = await Notification.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
        return notifications

    async def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get a specific notification by ID"""
        return await Notification.get(notification_id)

    async def update_notification_status(
        self,
        notification_id: str,
        status: str,
        error: Optional[str] = None
    ) -> Notification:
        """Update notification status"""
        notification = await Notification.get(notification_id)
        if not notification:
            raise ValueError("Notification not found")
        
        notification.status = status
        notification.error = error
        notification.updated_at = datetime.utcnow()
        await notification.save()
        return notification

    async def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification"""
        notification = await Notification.get(notification_id)
        if not notification:
            raise ValueError("Notification not found")
        
        await notification.delete()
        return True

    async def get_notification_stats(self) -> Dict[str, int]:
        """Get notification statistics"""
        total = await Notification.count_documents({})
        sent = await Notification.count_documents({"status": "sent"})
        failed = await Notification.count_documents({"status": "failed"})
        pending = await Notification.count_documents({"status": "pending"})
        
        return {
            "total": total,
            "sent": sent,
            "failed": failed,
            "pending": pending
        } 