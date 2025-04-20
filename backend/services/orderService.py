from typing import List, Dict, Any
from datetime import datetime
from app.models import Order, OrderItem, Product, User
from app.services.shipping_service import ShippingService
from app.services.notification_service import NotificationService
from app.services.inventory_service import InventoryService

class OrderService:
    def __init__(self):
        self.shipping_service = ShippingService()
        self.notification_service = NotificationService()
        self.inventory_service = InventoryService()

    async def process_order(self, order_id: str) -> Dict[str, Any]:
        """Process a new order through the fulfillment pipeline"""
        order = await Order.get(order_id)
        if not order:
            raise ValueError("Order not found")

        try:
            # 1. Validate inventory
            await self._validate_inventory(order.items)

            # 2. Reserve inventory
            await self._reserve_inventory(order.items)

            # 3. Process payment (assuming payment is already processed)
            
            # 4. Create shipping label
            shipping_label = await self.shipping_service.create_shipping_label(
                order=order,
                shipping_method=order.shipping_method
            )

            # 5. Update order status
            order.status = "processing"
            order.shipping_label = shipping_label
            order.updated_at = datetime.utcnow()
            await order.save()

            # 6. Notify customer
            await self.notification_service.send_order_confirmation(order)

            # 7. Notify warehouse
            await self.notification_service.notify_warehouse(order)

            return {
                "status": "success",
                "order_id": order.id,
                "shipping_label": shipping_label
            }

        except Exception as e:
            # Handle any errors and rollback inventory
            await self._release_inventory(order.items)
            raise e

    async def _validate_inventory(self, items: List[OrderItem]) -> None:
        """Validate that all items are in stock"""
        for item in items:
            product = await Product.get(item.product_id)
            if not product or product.stock < item.quantity:
                raise ValueError(f"Insufficient stock for product {item.product_id}")

    async def _reserve_inventory(self, items: List[OrderItem]) -> None:
        """Reserve inventory for the order"""
        for item in items:
            await self.inventory_service.reserve_stock(
                product_id=item.product_id,
                quantity=item.quantity
            )

    async def _release_inventory(self, items: List[OrderItem]) -> None:
        """Release reserved inventory"""
        for item in items:
            await self.inventory_service.release_stock(
                product_id=item.product_id,
                quantity=item.quantity
            )

    async def update_order_status(self, order_id: str, status: str) -> Dict[str, Any]:
        """Update the status of an order"""
        order = await Order.get(order_id)
        if not order:
            raise ValueError("Order not found")

        order.status = status
        order.updated_at = datetime.utcnow()
        await order.save()

        # Notify customer of status change
        await self.notification_service.send_status_update(order)

        return {
            "status": "success",
            "order_id": order.id,
            "new_status": status
        }

    async def track_order(self, order_id: str) -> Dict[str, Any]:
        """Get tracking information for an order"""
        order = await Order.get(order_id)
        if not order:
            raise ValueError("Order not found")

        tracking_info = await self.shipping_service.get_tracking_info(
            tracking_number=order.tracking_number
        )

        return {
            "order_id": order.id,
            "status": order.status,
            "tracking_info": tracking_info
        }

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order and release inventory"""
        order = await Order.get(order_id)
        if not order:
            raise ValueError("Order not found")

        if order.status not in ["pending", "processing"]:
            raise ValueError("Order cannot be cancelled in current state")

        # Release inventory
        await self._release_inventory(order.items)

        # Update order status
        order.status = "cancelled"
        order.updated_at = datetime.utcnow()
        await order.save()

        # Notify customer
        await self.notification_service.send_cancellation_notice(order)

        return {
            "status": "success",
            "order_id": order.id,
            "new_status": "cancelled"
        } 