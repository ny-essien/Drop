from typing import Dict, List, Optional
import shippo
from datetime import datetime
from app.core.config import settings
from app.models import Order, OrderItem

class ShippingService:
    def __init__(self):
        shippo.api_key = settings.SHIPPO_API_KEY
        self.default_carrier = settings.DEFAULT_SHIPPING_CARRIER
        self.default_service = settings.DEFAULT_SHIPPING_SERVICE

    async def calculate_shipping_cost(
        self,
        order: Order,
        address: Dict,
        items: List[OrderItem]
    ) -> Dict:
        """Calculate shipping cost for an order"""
        try:
            # Create shipment
            shipment = self._create_shipment(order, address, items)
            
            # Get shipping rates
            rates = shippo.Shipment.get_rates(
                shipment.object_id,
                async=False
            )
            
            # Filter and sort rates
            available_rates = self._filter_rates(rates.results)
            
            return {
                "rates": available_rates,
                "selected_rate": self._select_best_rate(available_rates),
                "shipment_id": shipment.object_id
            }
        except shippo.error.Error as e:
            raise Exception(f"Shipping calculation failed: {str(e)}")

    async def create_shipping_label(
        self,
        order: Order,
        address: Dict,
        items: List[OrderItem],
        rate_id: str
    ) -> Dict:
        """Create shipping label for an order"""
        try:
            # Create transaction
            transaction = shippo.Transaction.create(
                rate=rate_id,
                label_file_type="PDF",
                async=False
            )
            
            # Update order with tracking information
            await self._update_order_tracking(
                order.id,
                transaction.tracking_number,
                transaction.tracking_url_provider,
                transaction.label_url
            )
            
            return {
                "tracking_number": transaction.tracking_number,
                "tracking_url": transaction.tracking_url_provider,
                "label_url": transaction.label_url,
                "estimated_delivery": transaction.eta
            }
        except shippo.error.Error as e:
            raise Exception(f"Label creation failed: {str(e)}")

    def _create_shipment(
        self,
        order: Order,
        address: Dict,
        items: List[OrderItem]
    ) -> shippo.Shipment:
        """Create a shipment object"""
        # Prepare address objects
        from_address = {
            "name": settings.STORE_NAME,
            "street1": settings.STORE_ADDRESS_STREET1,
            "city": settings.STORE_ADDRESS_CITY,
            "state": settings.STORE_ADDRESS_STATE,
            "zip": settings.STORE_ADDRESS_ZIP,
            "country": settings.STORE_ADDRESS_COUNTRY,
            "phone": settings.STORE_PHONE,
            "email": settings.STORE_EMAIL
        }

        to_address = {
            "name": address.get("name"),
            "street1": address.get("street1"),
            "street2": address.get("street2"),
            "city": address.get("city"),
            "state": address.get("state"),
            "zip": address.get("zip"),
            "country": address.get("country"),
            "phone": address.get("phone"),
            "email": address.get("email")
        }

        # Calculate total weight and dimensions
        total_weight = sum(item.weight * item.quantity for item in items)
        dimensions = self._calculate_package_dimensions(items)

        # Create shipment
        return shippo.Shipment.create(
            address_from=from_address,
            address_to=to_address,
            parcels=[{
                "length": dimensions["length"],
                "width": dimensions["width"],
                "height": dimensions["height"],
                "distance_unit": "in",
                "weight": total_weight,
                "mass_unit": "lb"
            }],
            async=False
        )

    def _filter_rates(self, rates: List[Dict]) -> List[Dict]:
        """Filter and sort shipping rates"""
        # Filter out rates with errors
        valid_rates = [rate for rate in rates if not rate.get("messages")]
        
        # Sort by price
        return sorted(valid_rates, key=lambda x: float(x["amount"]))

    def _select_best_rate(self, rates: List[Dict]) -> Dict:
        """Select the best shipping rate"""
        # Try to find the default carrier and service
        for rate in rates:
            if (rate["provider"] == self.default_carrier and 
                rate["servicelevel"]["token"] == self.default_service):
                return rate
        
        # If not found, return the cheapest rate
        return rates[0]

    def _calculate_package_dimensions(self, items: List[OrderItem]) -> Dict:
        """Calculate package dimensions based on items"""
        # This is a simplified calculation
        # In a real application, you would need to consider:
        # - Individual item dimensions
        # - Packing efficiency
        # - Package type (box, envelope, etc.)
        return {
            "length": 10,  # inches
            "width": 8,    # inches
            "height": 6    # inches
        }

    async def _update_order_tracking(
        self,
        order_id: str,
        tracking_number: str,
        tracking_url: str,
        label_url: str
    ):
        """Update order with tracking information"""
        # TODO: Implement order tracking update
        pass

    async def track_shipment(self, tracking_number: str) -> Dict:
        """Track a shipment"""
        try:
            tracking = shippo.Track.get_status(
                tracking_number,
                carrier=self.default_carrier
            )
            
            return {
                "status": tracking.tracking_status.status,
                "location": tracking.tracking_status.location,
                "estimated_delivery": tracking.tracking_status.eta,
                "history": [
                    {
                        "status": event.status,
                        "location": event.location,
                        "date": event.date
                    }
                    for event in tracking.tracking_history
                ]
            }
        except shippo.error.Error as e:
            raise Exception(f"Tracking failed: {str(e)}")

    async def validate_address(self, address: Dict) -> Dict:
        """Validate a shipping address"""
        try:
            validated = shippo.Address.validate(
                street1=address.get("street1"),
                street2=address.get("street2"),
                city=address.get("city"),
                state=address.get("state"),
                zip=address.get("zip"),
                country=address.get("country")
            )
            
            return {
                "is_valid": validated.is_valid,
                "messages": validated.messages,
                "suggested_address": validated.suggested_address if not validated.is_valid else None
            }
        except shippo.error.Error as e:
            raise Exception(f"Address validation failed: {str(e)}") 