from typing import Dict, Any, List
import aiohttp
from app.config import settings
from app.models import Order

class ShippingService:
    def __init__(self):
        self.api_key = settings.SHIPPING_API_KEY
        self.base_url = settings.SHIPPING_API_URL
        self.supported_carriers = ["fedex", "ups", "usps"]

    async def create_shipping_label(self, order: Order, shipping_method: str) -> Dict[str, Any]:
        """Create a shipping label for an order"""
        carrier = self._get_carrier(shipping_method)
        
        # Prepare shipping data
        shipping_data = {
            "carrier": carrier,
            "service": shipping_method,
            "package": {
                "weight": self._calculate_package_weight(order.items),
                "dimensions": self._calculate_package_dimensions(order.items)
            },
            "from_address": {
                "name": settings.WAREHOUSE_NAME,
                "street1": settings.WAREHOUSE_STREET,
                "city": settings.WAREHOUSE_CITY,
                "state": settings.WAREHOUSE_STATE,
                "zip": settings.WAREHOUSE_ZIP,
                "country": settings.WAREHOUSE_COUNTRY
            },
            "to_address": {
                "name": order.shipping_address.name,
                "street1": order.shipping_address.street1,
                "street2": order.shipping_address.street2,
                "city": order.shipping_address.city,
                "state": order.shipping_address.state,
                "zip": order.shipping_address.zip,
                "country": order.shipping_address.country
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/labels",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=shipping_data
            ) as response:
                if response.status != 200:
                    raise ValueError("Failed to create shipping label")
                
                result = await response.json()
                return {
                    "label_url": result["label_url"],
                    "tracking_number": result["tracking_number"],
                    "carrier": carrier
                }

    async def get_tracking_info(self, tracking_number: str) -> Dict[str, Any]:
        """Get tracking information for a shipment"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/tracking/{tracking_number}",
                headers={"Authorization": f"Bearer {this.api_key}"}
            ) as response:
                if response.status != 200:
                    raise ValueError("Failed to get tracking information")
                
                return await response.json()

    async def get_shipping_rates(self, order: Order) -> List[Dict[str, Any]]:
        """Get available shipping rates for an order"""
        shipping_data = {
            "from_address": {
                "zip": settings.WAREHOUSE_ZIP,
                "country": settings.WAREHOUSE_COUNTRY
            },
            "to_address": {
                "zip": order.shipping_address.zip,
                "country": order.shipping_address.country
            },
            "package": {
                "weight": self._calculate_package_weight(order.items),
                "dimensions": self._calculate_package_dimensions(order.items)
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/rates",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=shipping_data
            ) as response:
                if response.status != 200:
                    raise ValueError("Failed to get shipping rates")
                
                return await response.json()

    def _get_carrier(self, shipping_method: str) -> str:
        """Determine carrier from shipping method"""
        for carrier in self.supported_carriers:
            if carrier in shipping_method.lower():
                return carrier
        return "usps"  # Default to USPS

    def _calculate_package_weight(self, items: List[Any]) -> float:
        """Calculate total package weight"""
        return sum(item.weight * item.quantity for item in items)

    def _calculate_package_dimensions(self, items: List[Any]) -> Dict[str, float]:
        """Calculate package dimensions based on items"""
        # This is a simplified calculation
        # In a real system, you'd want to use a more sophisticated algorithm
        total_volume = sum(
            item.length * item.width * item.height * item.quantity
            for item in items
        )
        
        # Calculate cube root for a roughly cubic package
        side_length = total_volume ** (1/3)
        
        return {
            "length": side_length,
            "width": side_length,
            "height": side_length
        } 