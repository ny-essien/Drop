from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.db import get_database
from app.models.product import Product
from motor.motor_asyncio import AsyncIOMotorDatabase

class ProductService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.product_collection = None

    async def initialize(self):
        """Initialize database collections"""
        if self.product_collection is None:
            self.product_collection = self.db["products"]

    async def create_product(self, product: Product) -> Product:
        """Create a new product"""
        await self.initialize()
        product_dict = product.model_dump(exclude={"id"})
        result = await self.product_collection.insert_one(product_dict)
        product_dict["_id"] = str(result.inserted_id)
        return Product(**product_dict)

    async def get_product(self, product_id: str) -> Optional[Product]:
        """Get a product by ID"""
        await self.initialize()
        try:
            product = await self.product_collection.find_one({"_id": ObjectId(product_id)})
            if product:
                product["_id"] = str(product["_id"])
                return Product(**product)
            return None
        except:
            return None

    async def update_product(self, product_id: str, product: Product) -> Optional[Product]:
        """Update a product"""
        await self.initialize()
        try:
            product_dict = product.model_dump(exclude={"id"})
            result = await self.product_collection.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": product_dict}
            )
            if result.modified_count:
                updated_product = await self.get_product(product_id)
                return updated_product
            return None
        except:
            return None

    async def delete_product(self, product_id: str) -> bool:
        """Delete a product"""
        await self.initialize()
        try:
            result = await self.product_collection.delete_one({"_id": ObjectId(product_id)})
            return result.deleted_count > 0
        except:
            return False

    async def get_products(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Product]:
        """List products with optional search"""
        await self.initialize()
        query = {}
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        cursor = self.product_collection.find(query).skip(skip).limit(limit)
        products = await cursor.to_list(length=limit)
        return [Product(**{**product, "_id": str(product["_id"])}) for product in products] 