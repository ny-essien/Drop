from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models import CartItem, Product

class CartService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.cart_items

    async def get_cart_items(self, user_id: str) -> List[CartItem]:
        if not ObjectId.is_valid(user_id):
            return []
        cursor = self.collection.find({"user_id": ObjectId(user_id)})
        cart_items = await cursor.to_list(length=None)
        return [CartItem(**item) for item in cart_items]

    async def add_to_cart(self, user_id: str, product_id: str, quantity: int = 1) -> Optional[CartItem]:
        if not all(ObjectId.is_valid(id) for id in [user_id, product_id]):
            return None

        # Check if product exists
        product = await self.db.products.find_one({"_id": ObjectId(product_id)})
        if not product:
            return None

        # Check if item already in cart
        existing_item = await self.collection.find_one({
            "user_id": ObjectId(user_id),
            "product_id": ObjectId(product_id)
        })

        if existing_item:
            # Update quantity
            await self.collection.update_one(
                {"_id": existing_item["_id"]},
                {"$inc": {"quantity": quantity}}
            )
            updated_item = await self.collection.find_one({"_id": existing_item["_id"]})
            return CartItem(**updated_item)
        else:
            # Create new cart item
            cart_item = CartItem(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )
            result = await self.collection.insert_one(cart_item.dict(exclude={"id"}))
            created_item = await self.collection.find_one({"_id": result.inserted_id})
            return CartItem(**created_item)

    async def update_cart_item(self, user_id: str, product_id: str, quantity: int) -> Optional[CartItem]:
        if not all(ObjectId.is_valid(id) for id in [user_id, product_id]):
            return None

        if quantity <= 0:
            await self.collection.delete_one({
                "user_id": ObjectId(user_id),
                "product_id": ObjectId(product_id)
            })
            return None

        await self.collection.update_one(
            {
                "user_id": ObjectId(user_id),
                "product_id": ObjectId(product_id)
            },
            {"$set": {"quantity": quantity}}
        )
        updated_item = await self.collection.find_one({
            "user_id": ObjectId(user_id),
            "product_id": ObjectId(product_id)
        })
        return CartItem(**updated_item) if updated_item else None

    async def remove_from_cart(self, user_id: str, product_id: str) -> bool:
        if not all(ObjectId.is_valid(id) for id in [user_id, product_id]):
            return False
        result = await self.collection.delete_one({
            "user_id": ObjectId(user_id),
            "product_id": ObjectId(product_id)
        })
        return result.deleted_count > 0

    async def clear_cart(self, user_id: str) -> bool:
        if not ObjectId.is_valid(user_id):
            return False
        result = await self.collection.delete_many({"user_id": ObjectId(user_id)})
        return result.deleted_count > 0 