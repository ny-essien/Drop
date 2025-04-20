from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models import FAQ, FAQCategory
from datetime import datetime

class FAQService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.faq_collection = db.faqs

    async def create_faq(self, question: str, answer: str, category: FAQCategory) -> FAQ:
        faq = FAQ(
            question=question,
            answer=answer,
            category=category
        )
        result = await self.faq_collection.insert_one(faq.dict(exclude={"id"}))
        faq.id = str(result.inserted_id)
        return faq

    async def get_faq(self, faq_id: str) -> Optional[FAQ]:
        if not ObjectId.is_valid(faq_id):
            return None
        faq = await self.faq_collection.find_one({"_id": ObjectId(faq_id)})
        return FAQ(**faq) if faq else None

    async def get_all_faqs(
        self,
        category: Optional[FAQCategory] = None,
        active_only: bool = True
    ) -> List[FAQ]:
        query = {}
        if category:
            query["category"] = category
        if active_only:
            query["is_active"] = True
            
        faqs = await self.faq_collection.find(query).sort("created_at", 1).to_list(length=None)
        return [FAQ(**faq) for faq in faqs]

    async def update_faq(
        self,
        faq_id: str,
        question: Optional[str] = None,
        answer: Optional[str] = None,
        category: Optional[FAQCategory] = None,
        is_active: Optional[bool] = None
    ) -> Optional[FAQ]:
        if not ObjectId.is_valid(faq_id):
            return None
            
        update_data = {"updated_at": datetime.utcnow()}
        if question is not None:
            update_data["question"] = question
        if answer is not None:
            update_data["answer"] = answer
        if category is not None:
            update_data["category"] = category
        if is_active is not None:
            update_data["is_active"] = is_active
            
        result = await self.faq_collection.update_one(
            {"_id": ObjectId(faq_id)},
            {"$set": update_data}
        )
        
        if result.modified_count:
            return await self.get_faq(faq_id)
        return None

    async def delete_faq(self, faq_id: str) -> bool:
        if not ObjectId.is_valid(faq_id):
            return False
        result = await self.faq_collection.delete_one({"_id": ObjectId(faq_id)})
        return result.deleted_count > 0

    async def search_faqs(self, query: str) -> List[FAQ]:
        # Create a text index if it doesn't exist
        indexes = await self.faq_collection.index_information()
        if "question_text" not in indexes:
            await self.faq_collection.create_index([("question", "text"), ("answer", "text")])
            
        faqs = await self.faq_collection.find(
            {"$text": {"$search": query}, "is_active": True}
        ).to_list(length=None)
        return [FAQ(**faq) for faq in faqs] 