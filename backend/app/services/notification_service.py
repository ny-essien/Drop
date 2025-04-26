from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.db.mongodb import get_database

class NotificationService:
    def __init__(self):
        self.db = None

    async def initialize(self):
        """Initialize the database connection"""
        self.db = await get_database()

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
        if not self.db:
            await self.initialize()
            
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
        
        result = await self.db.notifications.insert_one(notification_data)
        notification_data["id"] = str(result.inserted_id)
        return Notification(**notification_data)

    async def get_notifications(
        self,
        user_id: Optional[str] = None,
        type: Optional[NotificationType] = None,
        status: Optional[NotificationStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Notification]:
        """Get notifications with optional filters"""
        if not self.db:
            await self.initialize()
            
        query = {}
        if user_id:
            query["user_id"] = user_id
        if type:
            query["type"] = type
        if status:
            query["status"] = status
            
        cursor = self.db.notifications.find(query).skip(skip).limit(limit)
        notifications = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            notifications.append(Notification(**doc))
        return notifications

    async def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get a notification by ID"""
        if not self.db:
            await self.initialize()
            
        try:
            doc = await self.db.notifications.find_one({"_id": ObjectId(notification_id)})
            if doc:
                doc["id"] = str(doc["_id"])
                return Notification(**doc)
            return None
        except:
            return None

    async def update_notification_status(
        self,
        notification_id: str,
        status: NotificationStatus
    ) -> Optional[Notification]:
        """Update notification status"""
        if not self.db:
            await self.initialize()
            
        try:
            result = await self.db.notifications.update_one(
                {"_id": ObjectId(notification_id)},
                {"$set": {"status": status, "updated_at": datetime.utcnow()}}
            )
            if result.modified_count:
                return await self.get_notification(notification_id)
            return None
        except:
            return None

    async def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification"""
        if not self.db:
            await self.initialize()
            
        try:
            result = await self.db.notifications.delete_one({"_id": ObjectId(notification_id)})
            return result.deleted_count > 0
        except:
            return False

    async def get_notification_stats(self, user_id: str) -> Dict[str, int]:
        """Get notification statistics for a user"""
        if not self.db:
            await self.initialize()
            
        stats = {
            "total": await self.db.notifications.count_documents({"user_id": user_id}),
            "unread": await self.db.notifications.count_documents({
                "user_id": user_id,
                "status": NotificationStatus.UNREAD
            }),
            "read": await self.db.notifications.count_documents({
                "user_id": user_id,
                "status": NotificationStatus.READ
            }),
            "archived": await self.db.notifications.count_documents({
                "user_id": user_id,
                "status": NotificationStatus.ARCHIVED
            })
        }
        return stats 