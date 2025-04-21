from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketMessage(BaseModel):
    user_id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    attachments: List[str] = []

class SupportTicket(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    subject: str
    description: str
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.MEDIUM
    category: Optional[str] = None
    assigned_to: Optional[str] = None
    messages: List[TicketMessage] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "ticket123",
                "user_id": "user123",
                "subject": "Order Issue",
                "description": "Having trouble with my recent order",
                "status": "open",
                "priority": "medium",
                "category": "orders",
                "assigned_to": None,
                "messages": [],
                "created_at": "2023-01-01T00:00:00",
                "updated_at": None,
                "resolved_at": None
            }
        }

class TicketCreate(BaseModel):
    subject: str
    description: str
    category: Optional[str] = None
    priority: TicketPriority = TicketPriority.MEDIUM

class TicketUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[str] = None
    assigned_to: Optional[str] = None

class MessageCreate(BaseModel):
    message: str
    attachments: List[str] = []

class TicketResponse(SupportTicket):
    messages_count: int = 0
    last_message: Optional[TicketMessage] = None
    time_to_resolution: Optional[float] = None  # in hours

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "ticket123",
                "user_id": "user123",
                "subject": "Order Issue",
                "description": "Having trouble with my recent order",
                "status": "open",
                "priority": "medium",
                "category": "orders",
                "assigned_to": None,
                "messages": [],
                "created_at": "2023-01-01T00:00:00",
                "updated_at": None,
                "resolved_at": None,
                "messages_count": 0,
                "last_message": None,
                "time_to_resolution": None
            }
        } 