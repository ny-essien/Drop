from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class FAQCategory(str, Enum):
    GENERAL = "general"
    ORDERS = "orders"
    PAYMENTS = "payments"
    SHIPPING = "shipping"
    RETURNS = "returns"
    ACCOUNT = "account"
    TECHNICAL = "technical"

class FAQ(BaseModel):
    id: str = Field(alias="_id")
    question: str
    answer: str
    category: FAQCategory
    tags: List[str] = []
    views: int = 0
    helpful_votes: int = 0
    not_helpful_votes: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "faq123",
                "question": "How do I track my order?",
                "answer": "You can track your order by...",
                "category": "orders",
                "tags": ["tracking", "orders", "shipping"],
                "views": 100,
                "helpful_votes": 50,
                "not_helpful_votes": 2,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": None
            }
        }

class FAQCreate(BaseModel):
    question: str
    answer: str
    category: FAQCategory
    tags: List[str] = []

class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[FAQCategory] = None
    tags: Optional[List[str]] = None 