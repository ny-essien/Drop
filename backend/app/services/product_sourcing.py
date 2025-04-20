from typing import List, Dict, Optional
from datetime import datetime
import aiohttp
import asyncio
from app.models import Product, Supplier
from app.db import get_database
from app.config import settings

class ProductSourcingService:
    def __init__(self):
        self.db = get_database()
        self.product_collection = self.db["products"]
        self.supplier_collection = self.db["suppliers"]
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def search_suppliers(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search for suppliers based on query and filters"""
        search_filters = {"$text": {"$search": query}}
        if filters:
            search_filters.update(filters)
        
        suppliers = await self.supplier_collection.find(search_filters).to_list(length=100)
        return suppliers

    async def compare_prices(self, product_id: str) -> List[Dict]:
        """Compare prices across different suppliers for a product"""
        product = await self.product_collection.find_one({"_id": product_id})
        if not product:
            return []

        suppliers = await self.supplier_collection.find({
            "product_categories": {"$in": product["categories"]}
        }).to_list(length=100)

        price_comparisons = []
        for supplier in suppliers:
            if self.session:
                async with self.session.get(
                    f"{supplier['api_url']}/products/{product_id}/price",
                    headers={"Authorization": f"Bearer {supplier['api_key']}"}
                ) as response:
                    if response.status == 200:
                        price_data = await response.json()
                        price_comparisons.append({
                            "supplier_id": supplier["_id"],
                            "supplier_name": supplier["name"],
                            "price": price_data["price"],
                            "shipping_cost": price_data.get("shipping_cost", 0),
                            "stock_quantity": price_data.get("stock_quantity", 0),
                            "estimated_delivery": price_data.get("estimated_delivery", None)
                        })

        return sorted(price_comparisons, key=lambda x: x["price"] + x["shipping_cost"])

    async def bulk_import_products(self, supplier_id: str, category: str, limit: int = 100) -> Dict:
        """Bulk import products from a supplier"""
        supplier = await self.supplier_collection.find_one({"_id": supplier_id})
        if not supplier:
            return {"error": "Supplier not found"}

        if self.session:
            async with self.session.get(
                f"{supplier['api_url']}/products",
                params={"category": category, "limit": limit},
                headers={"Authorization": f"Bearer {supplier['api_key']}"}
            ) as response:
                if response.status == 200:
                    products = await response.json()
                    
                    # Process and insert products
                    processed_products = []
                    for product in products:
                        processed_product = {
                            "name": product["name"],
                            "description": product.get("description", ""),
                            "price": product["price"],
                            "categories": [category],
                            "supplier_id": supplier_id,
                            "stock_quantity": product.get("stock_quantity", 0),
                            "images": product.get("images", []),
                            "attributes": product.get("attributes", {}),
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                        processed_products.append(processed_product)

                    if processed_products:
                        result = await self.product_collection.insert_many(processed_products)
                        return {
                            "imported_count": len(result.inserted_ids),
                            "products": processed_products
                        }

        return {"error": "Failed to import products"}

    async def get_product_variations(self, product_id: str) -> List[Dict]:
        """Get all variations of a product"""
        product = await self.product_collection.find_one({"_id": product_id})
        if not product:
            return []

        variations = await self.product_collection.find({
            "parent_id": product_id,
            "is_variation": True
        }).to_list(length=100)

        return variations

    async def create_product_variation(self, product_id: str, variation_data: Dict) -> Dict:
        """Create a new variation for a product"""
        product = await self.product_collection.find_one({"_id": product_id})
        if not product:
            return {"error": "Product not found"}

        variation = {
            **variation_data,
            "parent_id": product_id,
            "is_variation": True,
            "base_product": product["name"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = await self.product_collection.insert_one(variation)
        return {"variation_id": str(result.inserted_id), "variation": variation}

    async def search_products(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Advanced product search with filters"""
        search_filters = {"$text": {"$search": query}}
        if filters:
            search_filters.update(filters)
        
        # Add sorting and pagination
        sort_by = filters.get("sort_by", "created_at")
        sort_order = filters.get("sort_order", -1)
        page = filters.get("page", 1)
        per_page = filters.get("per_page", 20)
        
        products = await self.product_collection.find(search_filters).sort(
            sort_by, sort_order
        ).skip((page - 1) * per_page).limit(per_page).to_list(length=per_page)
        
        total = await self.product_collection.count_documents(search_filters)
        
        return {
            "products": products,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        } 