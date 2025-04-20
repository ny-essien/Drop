from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
from app.db import get_database
from app.config import settings

class ShippingService:
    def __init__(self):
        self.db = get_database()
        self.order_collection = self.db["orders"]
        self.shipping_collection = self.db["shipping"]
        self.carrier_collection = self.db["carriers"]
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_available_carriers(self, order_id: str) -> List[Dict]:
        """Get available shipping carriers for an order"""
        order = await self.order_collection.find_one({"_id": order_id})
        if not order:
            return []

        carriers = await self.carrier_collection.find({
            "is_active": True,
            "supported_countries": order["shipping_address"]["country"]
        }).to_list(length=100)

        available_carriers = []
        for carrier in carriers:
            if self.session:
                async with self.session.get(
                    f"{carrier['api_url']}/rates",
                    headers={"Authorization": f"Bearer {carrier['api_key']}"},
                    json={
                        "weight": order["total_weight"],
                        "dimensions": order["dimensions"],
                        "from": {
                            "country": settings.WAREHOUSE_COUNTRY,
                            "postal_code": settings.WAREHOUSE_POSTAL_CODE
                        },
                        "to": order["shipping_address"]
                    }
                ) as response:
                    if response.status == 200:
                        rates = await response.json()
                        available_carriers.append({
                            "carrier_id": carrier["_id"],
                            "name": carrier["name"],
                            "rates": rates,
                            "estimated_delivery": rates[0]["estimated_delivery"] if rates else None
                        })

        return available_carriers

    async def create_shipping_label(self, order_id: str, carrier_id: str, service_level: str) -> Dict:
        """Create a shipping label for an order"""
        order = await self.order_collection.find_one({"_id": order_id})
        carrier = await self.carrier_collection.find_one({"_id": carrier_id})
        
        if not order or not carrier:
            return {"error": "Order or carrier not found"}

        if self.session:
            async with self.session.post(
                f"{carrier['api_url']}/labels",
                headers={"Authorization": f"Bearer {carrier['api_key']}"},
                json={
                    "order_id": order_id,
                    "service_level": service_level,
                    "from": {
                        "name": settings.WAREHOUSE_NAME,
                        "address": settings.WAREHOUSE_ADDRESS,
                        "city": settings.WAREHOUSE_CITY,
                        "state": settings.WAREHOUSE_STATE,
                        "country": settings.WAREHOUSE_COUNTRY,
                        "postal_code": settings.WAREHOUSE_POSTAL_CODE
                    },
                    "to": order["shipping_address"],
                    "packages": [{
                        "weight": order["total_weight"],
                        "dimensions": order["dimensions"]
                    }]
                }
            ) as response:
                if response.status == 200:
                    label_data = await response.json()
                    
                    # Store shipping information
                    shipping_info = {
                        "order_id": order_id,
                        "carrier_id": carrier_id,
                        "tracking_number": label_data["tracking_number"],
                        "label_url": label_data["label_url"],
                        "service_level": service_level,
                        "created_at": datetime.utcnow(),
                        "status": "created"
                    }
                    
                    await self.shipping_collection.insert_one(shipping_info)
                    return shipping_info

        return {"error": "Failed to create shipping label"}

    async def track_shipment(self, tracking_number: str) -> Dict:
        """Track a shipment using the tracking number"""
        shipping_info = await self.shipping_collection.find_one({"tracking_number": tracking_number})
        if not shipping_info:
            return {"error": "Shipping information not found"}

        carrier = await self.carrier_collection.find_one({"_id": shipping_info["carrier_id"]})
        if not carrier:
            return {"error": "Carrier not found"}

        if self.session:
            async with self.session.get(
                f"{carrier['api_url']}/track/{tracking_number}",
                headers={"Authorization": f"Bearer {carrier['api_key']}"}
            ) as response:
                if response.status == 200:
                    tracking_data = await response.json()
                    
                    # Update shipping status
                    await self.shipping_collection.update_one(
                        {"tracking_number": tracking_number},
                        {"$set": {
                            "status": tracking_data["status"],
                            "last_updated": datetime.utcnow(),
                            "tracking_history": tracking_data["history"]
                        }}
                    )
                    
                    return tracking_data

        return {"error": "Failed to track shipment"}

    async def get_shipping_status(self, order_id: str) -> Dict:
        """Get shipping status for an order"""
        shipping_info = await self.shipping_collection.find_one({"order_id": order_id})
        if not shipping_info:
            return {"error": "Shipping information not found"}

        return {
            "tracking_number": shipping_info["tracking_number"],
            "status": shipping_info["status"],
            "carrier": shipping_info["carrier_id"],
            "last_updated": shipping_info["last_updated"],
            "tracking_history": shipping_info.get("tracking_history", [])
        }

    async def update_shipping_status(self, order_id: str, status: str) -> Dict:
        """Update shipping status for an order"""
        result = await self.shipping_collection.update_one(
            {"order_id": order_id},
            {"$set": {
                "status": status,
                "last_updated": datetime.utcnow()
            }}
        )
        
        if result.modified_count == 0:
            return {"error": "Failed to update shipping status"}
        
        return {"status": "success"}

    async def get_shipping_history(self, order_id: str) -> List[Dict]:
        """Get shipping history for an order"""
        shipping_info = await self.shipping_collection.find_one({"order_id": order_id})
        if not shipping_info:
            return []

        return shipping_info.get("tracking_history", [])

    async def cancel_shipment(self, order_id: str) -> Dict:
        """Cancel a shipment"""
        shipping_info = await self.shipping_collection.find_one({"order_id": order_id})
        if not shipping_info:
            return {"error": "Shipping information not found"}

        carrier = await self.carrier_collection.find_one({"_id": shipping_info["carrier_id"]})
        if not carrier:
            return {"error": "Carrier not found"}

        if self.session:
            async with self.session.post(
                f"{carrier['api_url']}/cancel",
                headers={"Authorization": f"Bearer {carrier['api_key']}"},
                json={"tracking_number": shipping_info["tracking_number"]}
            ) as response:
                if response.status == 200:
                    await self.shipping_collection.update_one(
                        {"order_id": order_id},
                        {"$set": {
                            "status": "cancelled",
                            "last_updated": datetime.utcnow()
                        }}
                    )
                    return {"status": "success"}

        return {"error": "Failed to cancel shipment"} 