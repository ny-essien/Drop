from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    ORDER = "order"
    PAYMENT = "payment"
    SHIPMENT = "shipment"
    SYSTEM = "system"
    PROMOTION = "promotion"

class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"

class Notification(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    type: NotificationType
    title: str
    message: str
    status: NotificationStatus = NotificationStatus.UNREAD
    data: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "notification123",
                "user_id": "user123",
                "type": "order",
                "title": "Order Confirmed",
                "message": "Your order #12345 has been confirmed",
                "status": "unread",
                "data": {"order_id": "12345"},
                "created_at": "2023-01-01T00:00:00",
                "read_at": None
            }
        }

class NotificationCreate(BaseModel):
    user_id: str
    type: NotificationType
    title: str
    message: str
    data: Optional[dict] = None

class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    read_at: Optional[datetime] = None 