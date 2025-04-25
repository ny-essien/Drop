from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models import Product, Supplier, ProductCreate, ProductUpdate
import httpx
from datetime import datetime

class ProductService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.products
        self.supplier_collection = db.suppliers

    async def get_products(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        supplier_id: Optional[str] = None
    ) -> List[Product]:
        """Get all products with optional filtering"""
        query = {}
        if category:
            query["category"] = category
        if supplier_id:
            query["supplier_id"] = supplier_id
        
        cursor = self.collection.find(query).skip(skip).limit(limit)
        products = await cursor.to_list(length=limit)
        return [Product(**product) for product in products]

    async def get_product(self, product_id: str) -> Optional[Product]:
        """Get a product by ID"""
        product = await self.collection.find_one({"_id": ObjectId(product_id)})
        if product:
            return Product(**product)
        return None

    async def create_product(self, product: ProductCreate) -> Product:
        """Create a new product"""
        product_dict = product.model_dump()
        result = await self.collection.insert_one(product_dict)
        created_product = await self.collection.find_one({"_id": result.inserted_id})
        return Product(**created_product)

    async def update_product(self, product_id: str, product: ProductUpdate) -> Optional[Product]:
        """Update a product"""
        update_data = product.model_dump(exclude_unset=True)
        if not update_data:
            return None
        
        result = await self.collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )
        
        if result.modified_count:
            updated_product = await self.collection.find_one({"_id": ObjectId(product_id)})
            return Product(**updated_product)
        return None

    async def delete_product(self, product_id: str) -> bool:
        """Delete a product"""
        result = await self.collection.delete_one({"_id": ObjectId(product_id)})
        return result.deleted_count > 0

    # Supplier Management
    async def create_supplier(self, supplier: Supplier) -> Supplier:
        supplier_dict = supplier.dict(exclude={"id"})
        result = await self.supplier_collection.insert_one(supplier_dict)
        created_supplier = await self.supplier_collection.find_one({"_id": result.inserted_id})
        return Supplier(**created_supplier)

    async def get_supplier(self, supplier_id: str) -> Optional[Supplier]:
        if not ObjectId.is_valid(supplier_id):
            return None
        supplier = await self.supplier_collection.find_one({"_id": ObjectId(supplier_id)})
        return Supplier(**supplier) if supplier else None

    # Product Import
    async def import_product(self, source: str, data: Dict[str, Any]) -> Product:
        # Validate import data
        if not self._validate_import_data(source, data):
            raise ValueError("Invalid import data")

        # Transform data based on source
        product_data = self._transform_import_data(source, data)

        # Create or update product
        existing_product = await self.collection.find_one({"import_source": source, "import_data.id": data.get("id")})
        if existing_product:
            product_data["updated_at"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": existing_product["_id"]},
                {"$set": product_data}
            )
            updated_product = await self.collection.find_one({"_id": existing_product["_id"]})
            return Product(**updated_product)
        else:
            product_data["created_at"] = datetime.utcnow()
            product_data["updated_at"] = datetime.utcnow()
            result = await self.collection.insert_one(product_data)
            created_product = await self.collection.find_one({"_id": result.inserted_id})
            return Product(**created_product)

    def _validate_import_data(self, source: str, data: Dict[str, Any]) -> bool:
        required_fields = ["name", "description", "price", "supplier_id"]
        return all(field in data for field in required_fields)

    def _transform_import_data(self, source: str, data: Dict[str, Any]) -> Dict[str, Any]:
        # Transform data based on source
        transformed = {
            "name": data["name"],
            "description": data["description"],
            "price": float(data["price"]),
            "supplier_id": ObjectId(data["supplier_id"]),
            "import_source": source,
            "import_data": data
        }

        # Add optional fields if present
        optional_fields = ["image_url", "stock", "supplier_price", "min_order_quantity", 
                         "shipping_weight", "shipping_dimensions"]
        for field in optional_fields:
            if field in data:
                transformed[field] = data[field]

        return transformed

    # Bulk Import
    async def bulk_import_products(self, source: str, products_data: List[Dict[str, Any]]) -> List[Product]:
        imported_products = []
        for product_data in products_data:
            try:
                product = await self.import_product(source, product_data)
                imported_products.append(product)
            except Exception as e:
                print(f"Error importing product: {str(e)}")
                continue
        return imported_products 