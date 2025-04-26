from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.db.mongodb import get_database

class NotificationService:
    async def create_notification(
        self,
        user_id: str,
        type: NotificationType,
        title: str,
        message: str,
        status: NotificationStatus = NotificationStatus.UNREAD,
        error: Optional[str] = None,
        metadata: Dict[str, Any] = {}
    ) -> Notification:
        """Create a new notification"""
        db = await get_database()
        notification_data = {
            "user_id": user_id,
            "type": type,
            "title": title,
            "message": message,
            "status": status,
            "error": error,
            "metadata": metadata,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await db.notifications.insert_one(notification_data)
        notification_data["_id"] = result.inserted_id
        return Notification(**notification_data)

    async def get_notifications(
        self,
        user_id: Optional[str] = None,
        type: Optional[NotificationType] = None,
        status: Optional[NotificationStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Notification]:
        """Get notifications with optional filtering"""
        db = await get_database()
        query = {}
        
        if user_id:
            query["user_id"] = user_id
        if type:
            query["type"] = type
        if status:
            query["status"] = status
        if start_date:
            query["created_at"] = {"$gte": start_date}
        if end_date:
            query["created_at"] = {"$lte": end_date}
        
        cursor = db.notifications.find(query).sort("created_at", -1).skip(skip).limit(limit)
        notifications = await cursor.to_list(length=None)
        return [Notification(**notification) for notification in notifications]

    async def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get a specific notification by ID"""
        db = await get_database()
        notification = await db.notifications.find_one({"_id": ObjectId(notification_id)})
        if notification:
            return Notification(**notification)
        return None

    async def update_notification_status(
        self,
        notification_id: str,
        status: NotificationStatus,
        error: Optional[str] = None
    ) -> Optional[Notification]:
        """Update notification status"""
        db = await get_database()
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        if error is not None:
            update_data["error"] = error
            
        result = await db.notifications.find_one_and_update(
            {"_id": ObjectId(notification_id)},
            {"$set": update_data},
            return_document=True
        )
        if result:
            return Notification(**result)
        return None

    async def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification"""
        db = await get_database()
        result = await db.notifications.delete_one({"_id": ObjectId(notification_id)})
        return result.deleted_count > 0

    async def get_notification_stats(self, user_id: Optional[str] = None) -> Dict[str, int]:
        """Get notification statistics"""
        db = await get_database()
        query = {}
        if user_id:
            query["user_id"] = user_id
            
        total = await db.notifications.count_documents(query)
        unread = await db.notifications.count_documents({**query, "status": NotificationStatus.UNREAD})
        read = await db.notifications.count_documents({**query, "status": NotificationStatus.READ})
        archived = await db.notifications.count_documents({**query, "status": NotificationStatus.ARCHIVED})
        
        return {
            "total": total,
            "unread": unread,
            "read": read,
            "archived": archived
        } 