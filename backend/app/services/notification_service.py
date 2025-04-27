from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.db.mongodb import get_database

class NotificationService:
    def __init__(self):
        self.db = None

    async def initialize(self):
        """Initialize the database connection if not already initialized"""
        if self.db is None:
            self.db = await get_database()

    async def create_notification(
        self,
        user_id: str,
        type: NotificationType,
        title: str,
        message: str,
        status: NotificationStatus = NotificationStatus.UNREAD,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Create a new notification"""
        await self.initialize()
        
        notification_data = {
            "user_id": user_id,
            "type": type,
            "title": title,
            "message": message,
            "status": status,
            "error": error,
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.db.notifications.insert_one(notification_data)
        notification_data["_id"] = result.inserted_id
        return Notification(**notification_data)

    async def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get a notification by ID"""
        await self.initialize()
        
        result = await self.db.notifications.find_one({"_id": ObjectId(notification_id)})
        if result:
            return Notification(**result)
        return None

    async def get_notifications(
        self,
        user_id: str,
        type: Optional[NotificationType] = None,
        status: Optional[NotificationStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Notification]:
        """Get notifications with optional filters"""
        await self.initialize()
        
        query = {"user_id": user_id}
        if type:
            query["type"] = type
        if status:
            query["status"] = status

        cursor = self.db.notifications.find(query).skip(skip).limit(limit)
        notifications = []
        async for doc in cursor:
            notifications.append(Notification(**doc))
        return notifications

    async def update_notification_status(
        self,
        notification_id: str,
        status: NotificationStatus
    ) -> Optional[Notification]:
        """Update the status of a notification"""
        await self.initialize()
        
        result = await self.db.notifications.find_one_and_update(
            {"_id": ObjectId(notification_id)},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        if result:
            return Notification(**result)
        return None

    async def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification"""
        await self.initialize()
        
        result = await self.db.notifications.delete_one({"_id": ObjectId(notification_id)})
        return result.deleted_count > 0

    async def get_notification_stats(self, user_id: str) -> Dict[NotificationStatus, int]:
        """Get notification statistics for a user"""
        await self.initialize()
        
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        stats = {status: 0 for status in NotificationStatus}
        async for doc in self.db.notifications.aggregate(pipeline):
            stats[doc["_id"]] = doc["count"]
        
        return stats 