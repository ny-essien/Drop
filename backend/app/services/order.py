from typing import List, Optional, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models import Order, CartItem, Product
from datetime import datetime

class OrderService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.orders
        self.products_collection = db.products
        self.cart_collection = db.cart_items

    async def create_order(self, user_id: str, shipping_address: Dict, billing_address: Dict, payment_method: str) -> Optional[Order]:
        if not ObjectId.is_valid(user_id):
            return None

        # Get cart items
        cart_items = await self.cart_collection.find({"user_id": ObjectId(user_id)}).to_list(length=None)
        if not cart_items:
            return None

        # Calculate total amount and validate stock
        total_amount = 0
        order_items = []
        
        for item in cart_items:
            product = await self.products_collection.find_one({"_id": ObjectId(item["product_id"])})
            if not product or product["stock"] < item["quantity"]:
                return None
            
            total_amount += product["price"] * item["quantity"]
            order_items.append(CartItem(**item))

        # Create order
        order = Order(
            user_id=user_id,
            items=order_items,
            total_amount=total_amount,
            shipping_address=shipping_address,
            billing_address=billing_address,
            payment_method=payment_method,
            status="pending",
            payment_status="pending"
        )

        # Start transaction
        async with await self.db.client.start_session() as session:
            async with session.start_transaction():
                # Insert order
                result = await self.collection.insert_one(order.dict(exclude={"id"}), session=session)
                
                # Update product stock
                for item in cart_items:
                    await self.products_collection.update_one(
                        {"_id": ObjectId(item["product_id"])},
                        {"$inc": {"stock": -item["quantity"]}},
                        session=session
                    )
                
                # Clear cart
                await self.cart_collection.delete_many({"user_id": ObjectId(user_id)}, session=session)

        created_order = await self.collection.find_one({"_id": result.inserted_id})
        return Order(**created_order) if created_order else None

    async def get_order(self, order_id: str) -> Optional[Order]:
        if not ObjectId.is_valid(order_id):
            return None
        order = await self.collection.find_one({"_id": ObjectId(order_id)})
        return Order(**order) if order else None

    async def get_user_orders(self, user_id: str) -> List[Order]:
        if not ObjectId.is_valid(user_id):
            return []
        cursor = self.collection.find({"user_id": ObjectId(user_id)})
        orders = await cursor.to_list(length=None)
        return [Order(**order) for order in orders]

    async def update_order_status(self, order_id: str, status: str) -> Optional[Order]:
        if not ObjectId.is_valid(order_id):
            return None
        await self.collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        updated_order = await self.collection.find_one({"_id": ObjectId(order_id)})
        return Order(**updated_order) if updated_order else None

    async def update_payment_status(self, order_id: str, payment_status: str) -> Optional[Order]:
        if not ObjectId.is_valid(order_id):
            return None
        await self.collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"payment_status": payment_status, "updated_at": datetime.utcnow()}}
        )
        updated_order = await self.collection.find_one({"_id": ObjectId(order_id)})
        return Order(**updated_order) if updated_order else None

    async def add_tracking_number(self, order_id: str, tracking_number: str) -> Optional[Order]:
        if not ObjectId.is_valid(order_id):
            return None
        await self.collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"tracking_number": tracking_number, "updated_at": datetime.utcnow()}}
        )
        updated_order = await self.collection.find_one({"_id": ObjectId(order_id)})
        return Order(**updated_order) if updated_order else None

    async def cancel_order(self, order_id: str, user_id: str, is_admin: bool = False) -> Optional[Order]:
        if not ObjectId.is_valid(order_id):
            return None

        order = await self.collection.find_one({"_id": ObjectId(order_id)})
        if not order:
            return None

        # Check if user is authorized to cancel the order
        if not is_admin and str(order["user_id"]) != str(user_id):
            return None

        # Only allow cancellation of pending or processing orders
        if order["status"] not in ["pending", "processing"]:
            return None

        # Start transaction
        async with await self.db.client.start_session() as session:
            async with session.start_transaction():
                # Update order status
                await self.collection.update_one(
                    {"_id": ObjectId(order_id)},
                    {
                        "$set": {
                            "status": "cancelled",
                            "updated_at": datetime.utcnow()
                        }
                    },
                    session=session
                )

                # Restore product stock
                for item in order["items"]:
                    await self.products_collection.update_one(
                        {"_id": ObjectId(item["product_id"])},
                        {"$inc": {"stock": item["quantity"]}},
                        session=session
                    )

        updated_order = await self.collection.find_one({"_id": ObjectId(order_id)})
        return Order(**updated_order) if updated_order else None

    async def get_all_orders(
        self,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
        payment_status: Optional[str] = None
    ) -> List[Order]:
        query = {}
        if status:
            query["status"] = status
        if payment_status:
            query["payment_status"] = payment_status

        cursor = self.collection.find(query).skip(skip).limit(limit)
        orders = await cursor.to_list(length=None)
        return [Order(**order) for order in orders]

    async def get_orders_count(
        self,
        status: Optional[str] = None,
        payment_status: Optional[str] = None
    ) -> int:
        query = {}
        if status:
            query["status"] = status
        if payment_status:
            query["payment_status"] = payment_status

        return await self.collection.count_documents(query) 