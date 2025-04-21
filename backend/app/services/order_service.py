from typing import List, Dict, Optional
from datetime import datetime
from app.db import get_database
from app.models import Order

class OrderService:
    def __init__(self):
        self.db = None
        self.order_collection = None

    async def initialize(self):
        """Initialize the database connection"""
        self.db = await get_database()
        self.order_collection = self.db["orders"]

    async def get_orders(
        self,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Order]:
        """Get orders with optional filtering"""
        if not self.order_collection:
            await self.initialize()
        query = {}
        if status:
            query["status"] = status
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date

        cursor = self.order_collection.find(query).skip(skip).limit(limit)
        orders = await cursor.to_list(length=limit)
        return [Order(**order) for order in orders]

    async def get_order(self, order_id: str) -> Optional[Order]:
        """Get a specific order by ID"""
        if not self.order_collection:
            await self.initialize()
        order = await self.order_collection.find_one({"_id": order_id})
        return Order(**order) if order else None

    async def create_order(self, order: Order) -> Order:
        """Create a new order"""
        if not self.order_collection:
            await self.initialize()
        order_dict = order.model_dump()
        result = await self.order_collection.insert_one(order_dict)
        order_dict["_id"] = str(result.inserted_id)
        return Order(**order_dict)

    async def update_order(self, order_id: str, order: Order) -> Optional[Order]:
        """Update an existing order"""
        if not self.order_collection:
            await self.initialize()
        order_dict = order.model_dump(exclude={"id"})
        result = await self.order_collection.update_one(
            {"_id": order_id},
            {"$set": order_dict}
        )
        if result.modified_count:
            updated_order = await self.get_order(order_id)
            return updated_order
        return None

    async def delete_order(self, order_id: str) -> bool:
        """Delete an order"""
        if not self.order_collection:
            await self.initialize()
        result = await self.order_collection.delete_one({"_id": order_id})
        return result.deleted_count > 0 