from typing import Dict, List, Optional
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models import Product, Supplier
from app.services.supplier_api import SupplierAPIFactory
from app.core.config import settings

class SupplierSyncService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.product_collection = db.products
        self.supplier_collection = db.suppliers
        self.sync_collection = db.sync_logs
        self.sync_interval = settings.SYNC_INTERVAL_MINUTES
        self.price_change_threshold = settings.PRICE_CHANGE_THRESHOLD
        self.stock_alert_threshold = settings.STOCK_ALERT_THRESHOLD

    async def start_auto_sync(self):
        """Start the automatic synchronization process"""
        while True:
            try:
                await self.sync_all_products()
                await asyncio.sleep(self.sync_interval * 60)
            except Exception as e:
                print(f"Error in auto sync: {str(e)}")
                await asyncio.sleep(60)  # Wait a minute before retrying

    async def sync_all_products(self):
        """Sync all products with their suppliers"""
        products = await self.product_collection.find({}).to_list(None)
        for product in products:
            try:
                await self.sync_product(product)
            except Exception as e:
                print(f"Error syncing product {product['_id']}: {str(e)}")

    async def sync_product(self, product: Dict):
        """Sync a single product with its supplier"""
        supplier = await self.supplier_collection.find_one({"_id": ObjectId(product["supplier_id"])})
        if not supplier:
            return

        api = SupplierAPIFactory.create_api(supplier["name"], supplier["api_key"], supplier["api_secret"])
        
        async with api:
            # Get current supplier data
            supplier_data = await api.get_product_details(product["supplier_product_id"])
            
            # Check price changes
            new_price = float(supplier_data["price"])
            price_change = abs(new_price - product["supplier_price"]) / product["supplier_price"] * 100
            
            if price_change >= self.price_change_threshold:
                await self._handle_price_change(product, new_price, price_change)
            
            # Check stock changes
            new_stock = int(supplier_data["stock"])
            if new_stock <= self.stock_alert_threshold and product["stock"] > self.stock_alert_threshold:
                await self._handle_low_stock(product, new_stock)
            
            # Update product
            await self._update_product(product, supplier_data)
            
            # Log sync
            await self._log_sync(product, supplier_data)

    async def _handle_price_change(self, product: Dict, new_price: float, price_change: float):
        """Handle price changes and notify relevant parties"""
        # Update product price
        await self.product_collection.update_one(
            {"_id": product["_id"]},
            {"$set": {
                "supplier_price": new_price,
                "price": new_price * (1 + product["markup_percentage"] / 100),
                "last_price_update": datetime.utcnow()
            }}
        )
        
        # Log price change
        await self.sync_collection.insert_one({
            "product_id": product["_id"],
            "type": "price_change",
            "old_price": product["supplier_price"],
            "new_price": new_price,
            "change_percentage": price_change,
            "timestamp": datetime.utcnow()
        })
        
        # TODO: Notify admin about significant price changes
        if price_change >= settings.PRICE_CHANGE_NOTIFICATION_THRESHOLD:
            pass

    async def _handle_low_stock(self, product: Dict, new_stock: int):
        """Handle low stock situations"""
        # Update product stock
        await self.product_collection.update_one(
            {"_id": product["_id"]},
            {"$set": {
                "stock": new_stock,
                "last_stock_update": datetime.utcnow()
            }}
        )
        
        # Log stock alert
        await self.sync_collection.insert_one({
            "product_id": product["_id"],
            "type": "low_stock",
            "old_stock": product["stock"],
            "new_stock": new_stock,
            "timestamp": datetime.utcnow()
        })
        
        # TODO: Notify admin about low stock
        pass

    async def _update_product(self, product: Dict, supplier_data: Dict):
        """Update product with latest supplier data"""
        update_data = {
            "supplier_price": float(supplier_data["price"]),
            "price": float(supplier_data["price"]) * (1 + product["markup_percentage"] / 100),
            "stock": int(supplier_data["stock"]),
            "last_sync": datetime.utcnow(),
            "supplier_data": {
                "title": supplier_data["title"],
                "description": supplier_data["description"],
                "images": supplier_data["images"],
                "specifications": supplier_data["specifications"],
                "shipping_info": supplier_data["shipping_info"]
            }
        }
        
        await self.product_collection.update_one(
            {"_id": product["_id"]},
            {"$set": update_data}
        )

    async def _log_sync(self, product: Dict, supplier_data: Dict):
        """Log synchronization details"""
        await self.sync_collection.insert_one({
            "product_id": product["_id"],
            "type": "sync",
            "supplier_data": supplier_data,
            "timestamp": datetime.utcnow()
        })

    async def get_sync_history(self, product_id: str, days: int = 7) -> List[Dict]:
        """Get synchronization history for a product"""
        start_date = datetime.utcnow() - timedelta(days=days)
        return await self.sync_collection.find({
            "product_id": ObjectId(product_id),
            "timestamp": {"$gte": start_date}
        }).sort("timestamp", -1).to_list(None)

    async def get_price_history(self, product_id: str, days: int = 30) -> List[Dict]:
        """Get price history for a product"""
        start_date = datetime.utcnow() - timedelta(days=days)
        return await self.sync_collection.find({
            "product_id": ObjectId(product_id),
            "type": "price_change",
            "timestamp": {"$gte": start_date}
        }).sort("timestamp", -1).to_list(None)

    async def get_stock_alerts(self, threshold: Optional[int] = None) -> List[Dict]:
        """Get products with low stock alerts"""
        query = {"stock": {"$lte": threshold or self.stock_alert_threshold}}
        return await self.product_collection.find(query).to_list(None)

    async def get_price_changes(self, threshold: Optional[float] = None) -> List[Dict]:
        """Get products with significant price changes"""
        threshold = threshold or self.price_change_threshold
        start_date = datetime.utcnow() - timedelta(days=7)
        
        pipeline = [
            {"$match": {
                "type": "price_change",
                "timestamp": {"$gte": start_date},
                "change_percentage": {"$gte": threshold}
            }},
            {"$group": {
                "_id": "$product_id",
                "latest_change": {"$first": "$$ROOT"}
            }}
        ]
        
        return await self.sync_collection.aggregate(pipeline).to_list(None) 