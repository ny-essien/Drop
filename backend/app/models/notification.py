from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from bson import ObjectId
from enum import Enum

class NotificationType(str, Enum):
    ORDER = "order"
    PAYMENT = "payment"
    SHIPPING = "shipping"
    SYSTEM = "system"
    INFO = "info"

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
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("id", mode="before")
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid)
        }
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "type": "order",
                "title": "Order Confirmation",
                "message": "Your order has been confirmed",
                "status": "unread",
                "metadata": {"order_id": "order123"}
            }
        }

class NotificationCreate(BaseModel):
    type: NotificationType
    title: str
    message: str
    status: NotificationStatus = NotificationStatus.UNREAD
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

class NotificationUpdate(BaseModel):
    status: NotificationStatus
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None 