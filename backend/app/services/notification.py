from typing import Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
from app.models import Order, User

class NotificationService:
    def __init__(self):
        self.mail_config = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_TLS=settings.MAIL_TLS,
            MAIL_SSL=settings.MAIL_SSL,
            USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS
        )
        self.fastmail = FastMail(self.mail_config)

    async def send_order_confirmation(self, order: Order, user: User) -> None:
        message = MessageSchema(
            subject="Order Confirmation",
            recipients=[user.email],
            body=f"""
            <h1>Order Confirmation</h1>
            <p>Thank you for your order!</p>
            <p>Order ID: {order.id}</p>
            <p>Total Amount: ${order.total_amount}</p>
            <p>Status: {order.status}</p>
            <p>We'll notify you when your order ships.</p>
            """,
            subtype="html"
        )
        await self.fastmail.send_message(message)

    async def send_order_status_update(self, order: Order, user: User) -> None:
        message = MessageSchema(
            subject="Order Status Update",
            recipients=[user.email],
            body=f"""
            <h1>Order Status Update</h1>
            <p>Your order status has been updated.</p>
            <p>Order ID: {order.id}</p>
            <p>New Status: {order.status}</p>
            {f'<p>Tracking Number: {order.tracking_number}</p>' if order.tracking_number else ''}
            """,
            subtype="html"
        )
        await self.fastmail.send_message(message)

    async def send_payment_failure(self, order: Order, user: User) -> None:
        message = MessageSchema(
            subject="Payment Failed",
            recipients=[user.email],
            body=f"""
            <h1>Payment Failed</h1>
            <p>We were unable to process your payment for order {order.id}.</p>
            <p>Please update your payment information and try again.</p>
            """,
            subtype="html"
        )
        await self.fastmail.send_message(message) 