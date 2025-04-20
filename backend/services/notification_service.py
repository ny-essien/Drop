from typing import Dict, Any
from app.models import Order, User
from app.config import settings
import aiohttp
from datetime import datetime

class NotificationService:
    def __init__(self):
        self.email_api_key = settings.EMAIL_API_KEY
        self.sms_api_key = settings.SMS_API_KEY
        self.warehouse_email = settings.WAREHOUSE_EMAIL

    async def send_order_confirmation(self, order: Order) -> Dict[str, Any]:
        """Send order confirmation to customer"""
        customer = await User.get(order.user_id)
        if not customer:
            raise ValueError("Customer not found")

        # Prepare email content
        email_data = {
            "to": customer.email,
            "subject": f"Order Confirmation - #{order.id}",
            "template": "order_confirmation",
            "data": {
                "order_id": order.id,
                "customer_name": customer.name,
                "order_date": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "items": [
                    {
                        "name": item.name,
                        "quantity": item.quantity,
                        "price": item.price
                    }
                    for item in order.items
                ],
                "total": order.total,
                "shipping_address": order.shipping_address,
                "tracking_number": order.tracking_number
            }
        }

        # Send email
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.EMAIL_API_URL}/send",
                headers={"Authorization": f"Bearer {self.email_api_key}"},
                json=email_data
            ) as response:
                if response.status != 200:
                    raise ValueError("Failed to send order confirmation email")

        # Send SMS if phone number is available
        if customer.phone:
            sms_data = {
                "to": customer.phone,
                "message": f"Your order #{order.id} has been confirmed. Tracking number: {order.tracking_number}"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{settings.SMS_API_URL}/send",
                    headers={"Authorization": f"Bearer {self.sms_api_key}"},
                    json=sms_data
                ) as response:
                    if response.status != 200:
                        print("Failed to send SMS notification")

        return {"status": "success", "order_id": order.id}

    async def notify_warehouse(self, order: Order) -> Dict[str, Any]:
        """Notify warehouse about new order"""
        email_data = {
            "to": self.warehouse_email,
            "subject": f"New Order - #{order.id}",
            "template": "warehouse_notification",
            "data": {
                "order_id": order.id,
                "items": [
                    {
                        "name": item.name,
                        "quantity": item.quantity,
                        "sku": item.sku
                    }
                    for item in order.items
                ],
                "shipping_address": order.shipping_address,
                "priority": order.priority
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.EMAIL_API_URL}/send",
                headers={"Authorization": f"Bearer {self.email_api_key}"},
                json=email_data
            ) as response:
                if response.status != 200:
                    raise ValueError("Failed to notify warehouse")

        return {"status": "success", "order_id": order.id}

    async def send_status_update(self, order: Order) -> Dict[str, Any]:
        """Send order status update to customer"""
        customer = await User.get(order.user_id)
        if not customer:
            raise ValueError("Customer not found")

        email_data = {
            "to": customer.email,
            "subject": f"Order Status Update - #{order.id}",
            "template": "status_update",
            "data": {
                "order_id": order.id,
                "customer_name": customer.name,
                "new_status": order.status,
                "tracking_number": order.tracking_number,
                "update_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.EMAIL_API_URL}/send",
                headers={"Authorization": f"Bearer {self.email_api_key}"},
                json=email_data
            ) as response:
                if response.status != 200:
                    raise ValueError("Failed to send status update email")

        return {"status": "success", "order_id": order.id}

    async def send_cancellation_notice(self, order: Order) -> Dict[str, Any]:
        """Send order cancellation notice to customer"""
        customer = await User.get(order.user_id)
        if not customer:
            raise ValueError("Customer not found")

        email_data = {
            "to": customer.email,
            "subject": f"Order Cancelled - #{order.id}",
            "template": "cancellation_notice",
            "data": {
                "order_id": order.id,
                "customer_name": customer.name,
                "cancellation_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "refund_amount": order.total
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.EMAIL_API_URL}/send",
                headers={"Authorization": f"Bearer {self.email_api_key}"},
                json=email_data
            ) as response:
                if response.status != 200:
                    raise ValueError("Failed to send cancellation notice")

        return {"status": "success", "order_id": order.id}

    async def send_low_stock_alert(self, product_id: str) -> Dict[str, Any]:
        """Send low stock alert to warehouse"""
        product = await Product.get(product_id)
        if not product:
            raise ValueError("Product not found")

        email_data = {
            "to": self.warehouse_email,
            "subject": f"Low Stock Alert - {product.name}",
            "template": "low_stock_alert",
            "data": {
                "product_id": product.id,
                "product_name": product.name,
                "current_stock": product.stock,
                "minimum_stock": 10,  # Assuming 10 is the minimum stock threshold
                "alert_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.EMAIL_API_URL}/send",
                headers={"Authorization": f"Bearer {self.email_api_key}"},
                json=email_data
            ) as response:
                if response.status != 200:
                    raise ValueError("Failed to send low stock alert")

        return {"status": "success", "product_id": product_id} 