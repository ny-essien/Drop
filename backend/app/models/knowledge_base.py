from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class ArticleCategory(str, Enum):
    GENERAL = "general"
    ORDERS = "orders"
    PAYMENTS = "payments"
    SHIPPING = "shipping"
    RETURNS = "returns"
    ACCOUNT = "account"
    TECHNICAL = "technical"

class KnowledgeBaseArticle(BaseModel):
    id: str = Field(alias="_id")
    title: str
    content: str
    category: ArticleCategory
    status: ArticleStatus = ArticleStatus.DRAFT
    author_id: str
    tags: List[str] = []
    views: int = 0
    helpful_votes: int = 0
    not_helpful_votes: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "article123",
                "title": "How to Track Your Order",
                "content": "To track your order, follow these steps...",
                "category": "orders",
                "status": "published",
                "author_id": "user123",
                "tags": ["tracking", "orders", "shipping"],
                "views": 100,
                "helpful_votes": 50,
                "not_helpful_votes": 2,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": None,
                "published_at": "2023-01-02T00:00:00"
            }
        }

class ArticleCreate(BaseModel):
    title: str
    content: str
    category: ArticleCategory
    tags: List[str] = []

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[ArticleCategory] = None
    status: Optional[ArticleStatus] = None
    tags: Optional[List[str]] = None

class ArticleVote(BaseModel):
    helpful: bool 