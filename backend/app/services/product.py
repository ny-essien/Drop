from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models import Product

class ProductService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.products

    async def get_products(self, skip: int = 0, limit: int = 10) -> List[Product]:
        cursor = self.collection.find().skip(skip).limit(limit)
        products = await cursor.to_list(length=limit)
        return [Product(**product) for product in products]

    async def get_product(self, product_id: str) -> Optional[Product]:
        if not ObjectId.is_valid(product_id):
            return None
        product = await self.collection.find_one({"_id": ObjectId(product_id)})
        return Product(**product) if product else None

    async def create_product(self, product: Product) -> Product:
        product_dict = product.dict(exclude={"id"})
        result = await self.collection.insert_one(product_dict)
        created_product = await self.collection.find_one({"_id": result.inserted_id})
        return Product(**created_product)

    async def update_product(self, product_id: str, product: Product) -> Optional[Product]:
        if not ObjectId.is_valid(product_id):
            return None
        product_dict = product.dict(exclude={"id"})
        await self.collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": product_dict}
        )
        updated_product = await self.collection.find_one({"_id": ObjectId(product_id)})
        return Product(**updated_product) if updated_product else None

    async def delete_product(self, product_id: str) -> bool:
        if not ObjectId.is_valid(product_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(product_id)})
        return result.deleted_count > 0 