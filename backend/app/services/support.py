from typing import Dict, List, Optional
from fastapi import UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
import os
import shutil
from app.models import SupportTicket, TicketResponse, KnowledgeBaseArticle, User
from app.services.notification import NotificationService
from app.core.config import settings

class SupportService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.notification_service = NotificationService(db)
        self.upload_dir = "uploads/support"
        self.ticket_collection = db.support_tickets
        self.user_collection = db.users
        os.makedirs(self.upload_dir, exist_ok=True)

    async def create_ticket(
        self,
        user_id: str,
        subject: str,
        message: str,
        priority: str = "medium",
        category: str = "general"
    ) -> Dict:
        """Create a new support ticket"""
        ticket = {
            "user_id": ObjectId(user_id),
            "subject": subject,
            "message": message,
            "priority": priority,
            "category": category,
            "status": "open",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "messages": [{
                "user_id": ObjectId(user_id),
                "message": message,
                "created_at": datetime.utcnow()
            }]
        }

        result = await self.ticket_collection.insert_one(ticket)
        ticket["_id"] = result.inserted_id
        return ticket

    async def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """Get a support ticket by ID"""
        return await self.ticket_collection.find_one({"_id": ObjectId(ticket_id)})

    async def get_user_tickets(
        self,
        user_id: str,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> Dict:
        """Get tickets for a specific user"""
        query = {"user_id": ObjectId(user_id)}
        if status:
            query["status"] = status

        total = await self.ticket_collection.count_documents(query)
        tickets = await self.ticket_collection.find(query) \
            .sort("created_at", -1) \
            .skip((page - 1) * per_page) \
            .limit(per_page) \
            .to_list(per_page)

        return {
            "tickets": tickets,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    async def add_message(
        self,
        ticket_id: str,
        user_id: str,
        message: str
    ) -> Dict:
        """Add a message to a support ticket"""
        message_data = {
            "user_id": ObjectId(user_id),
            "message": message,
            "created_at": datetime.utcnow()
        }

        result = await self.ticket_collection.update_one(
            {"_id": ObjectId(ticket_id)},
            {
                "$push": {"messages": message_data},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        if result.modified_count:
            return message_data
        return None

    async def update_ticket_status(
        self,
        ticket_id: str,
        status: str,
        admin_id: Optional[str] = None
    ) -> bool:
        """Update the status of a support ticket"""
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }

        if admin_id:
            update_data["assigned_to"] = ObjectId(admin_id)

        result = await self.ticket_collection.update_one(
            {"_id": ObjectId(ticket_id)},
            {"$set": update_data}
        )

        return result.modified_count > 0

    async def assign_ticket(
        self,
        ticket_id: str,
        admin_id: str
    ) -> bool:
        """Assign a ticket to an admin"""
        return await self.update_ticket_status(
            ticket_id,
            "assigned",
            admin_id
        )

    async def close_ticket(
        self,
        ticket_id: str,
        admin_id: Optional[str] = None
    ) -> bool:
        """Close a support ticket"""
        return await self.update_ticket_status(
            ticket_id,
            "closed",
            admin_id
        )

    async def get_admin_tickets(
        self,
        status: Optional[str] = None,
        assigned_to: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> Dict:
        """Get tickets for admin view"""
        query = {}
        if status:
            query["status"] = status
        if assigned_to:
            query["assigned_to"] = ObjectId(assigned_to)

        total = await self.ticket_collection.count_documents(query)
        tickets = await self.ticket_collection.find(query) \
            .sort("created_at", -1) \
            .skip((page - 1) * per_page) \
            .limit(per_page) \
            .to_list(per_page)

        return {
            "tickets": tickets,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    async def get_ticket_stats(self) -> Dict:
        """Get support ticket statistics"""
        total = await self.ticket_collection.count_documents({})
        open_tickets = await self.ticket_collection.count_documents({"status": "open"})
        assigned_tickets = await self.ticket_collection.count_documents({"status": "assigned"})
        closed_tickets = await self.ticket_collection.count_documents({"status": "closed"})

        return {
            "total": total,
            "open": open_tickets,
            "assigned": assigned_tickets,
            "closed": closed_tickets
        }

    async def search_tickets(
        self,
        query: str,
        page: int = 1,
        per_page: int = 10
    ) -> Dict:
        """Search support tickets"""
        search_query = {
            "$or": [
                {"subject": {"$regex": query, "$options": "i"}},
                {"message": {"$regex": query, "$options": "i"}},
                {"messages.message": {"$regex": query, "$options": "i"}}
            ]
        }

        total = await self.ticket_collection.count_documents(search_query)
        tickets = await self.ticket_collection.find(search_query) \
            .sort("created_at", -1) \
            .skip((page - 1) * per_page) \
            .limit(per_page) \
            .to_list(per_page)

        return {
            "tickets": tickets,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    async def get_ticket_responses(self, ticket_id: str) -> List[TicketResponse]:
        cursor = self.db.ticket_responses.find({"ticket_id": ticket_id})
        responses = await cursor.to_list(length=None)
        return [TicketResponse(**response) for response in responses]

    async def find_related_articles(self, subject: str, description: str) -> List[KnowledgeBaseArticle]:
        # Create text index if it doesn't exist
        await self.db.knowledge_base.create_index([("title", "text"), ("content", "text")])
        
        # Search for related articles
        cursor = self.db.knowledge_base.find(
            {
                "$text": {"$search": f"{subject} {description}"},
                "is_active": True
            },
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(5)
        
        articles = await cursor.to_list(length=None)
        return [KnowledgeBaseArticle(**article) for article in articles]

    async def get_attachment(self, file_path: str) -> Optional[bytes]:
        if not os.path.exists(file_path):
            return None
        with open(file_path, "rb") as f:
            return f.read()

    async def delete_attachment(self, file_path: str) -> bool:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False 