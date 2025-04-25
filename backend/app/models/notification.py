from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
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
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    type: NotificationType
    title: str
    message: str
    status: NotificationStatus = NotificationStatus.UNREAD
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "type": "order",
                "title": "Order Status Update",
                "message": "Your order has been shipped",
                "status": "unread",
                "metadata": {
                    "order_id": "order123"
                }
            }
        }

class NotificationCreate(BaseModel):
    user_id: str
    type: NotificationType
    title: str
    message: str
    status: NotificationStatus = NotificationStatus.UNREAD
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None 