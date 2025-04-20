from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from app.models import KnowledgeBaseArticle

class KnowledgeBaseService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.knowledge_base

    async def create_article(self, title: str, content: str, category: str, 
                           tags: List[str] = None) -> KnowledgeBaseArticle:
        article = KnowledgeBaseArticle(
            title=title,
            content=content,
            category=category,
            tags=tags or [],
            views=0,
            helpful_votes=0,
            is_active=True
        )
        
        result = await self.collection.insert_one(article.dict(by_alias=True))
        article.id = result.inserted_id
        return article

    async def get_article(self, article_id: str) -> Optional[KnowledgeBaseArticle]:
        article = await self.collection.find_one({"_id": ObjectId(article_id)})
        return KnowledgeBaseArticle(**article) if article else None

    async def update_article(self, article_id: str, title: Optional[str] = None,
                           content: Optional[str] = None, category: Optional[str] = None,
                           tags: Optional[List[str]] = None, is_active: Optional[bool] = None) -> Optional[KnowledgeBaseArticle]:
        update_data = {"updated_at": datetime.utcnow()}
        
        if title is not None:
            update_data["title"] = title
        if content is not None:
            update_data["content"] = content
        if category is not None:
            update_data["category"] = category
        if tags is not None:
            update_data["tags"] = tags
        if is_active is not None:
            update_data["is_active"] = is_active
            
        result = await self.collection.update_one(
            {"_id": ObjectId(article_id)},
            {"$set": update_data}
        )
        
        if result.modified_count:
            return await self.get_article(article_id)
        return None

    async def delete_article(self, article_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(article_id)})
        return result.deleted_count > 0

    async def get_articles_by_category(self, category: str) -> List[KnowledgeBaseArticle]:
        cursor = self.collection.find({"category": category, "is_active": True})
        articles = await cursor.to_list(length=None)
        return [KnowledgeBaseArticle(**article) for article in articles]

    async def search_articles(self, query: str, category: Optional[str] = None) -> List[KnowledgeBaseArticle]:
        # Create text index if it doesn't exist
        await self.collection.create_index([("title", "text"), ("content", "text")])
        
        search_query = {
            "$text": {"$search": query},
            "is_active": True
        }
        if category:
            search_query["category"] = category
            
        cursor = self.collection.find(
            search_query,
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})])
        
        articles = await cursor.to_list(length=None)
        return [KnowledgeBaseArticle(**article) for article in articles]

    async def increment_views(self, article_id: str) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(article_id)},
            {"$inc": {"views": 1}}
        )
        return result.modified_count > 0

    async def add_helpful_vote(self, article_id: str) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(article_id)},
            {"$inc": {"helpful_votes": 1}}
        )
        return result.modified_count > 0

    async def get_popular_articles(self, limit: int = 10) -> List[KnowledgeBaseArticle]:
        cursor = self.collection.find({"is_active": True}).sort("views", -1).limit(limit)
        articles = await cursor.to_list(length=None)
        return [KnowledgeBaseArticle(**article) for article in articles]

    async def get_categories(self) -> List[str]:
        categories = await self.collection.distinct("category")
        return categories 