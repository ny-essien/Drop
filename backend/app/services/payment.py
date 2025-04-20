from typing import Dict, Optional
import stripe
from datetime import datetime
from app.core.config import settings
from app.models import Order

class PaymentService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    async def create_payment_intent(self, order: Order, payment_method_id: str) -> Dict:
        """Create a payment intent for an order"""
        try:
            # Calculate total amount including shipping and taxes
            total_amount = self._calculate_total_amount(order)
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),  # Convert to cents
                currency=order.currency,
                payment_method=payment_method_id,
                confirm=True,
                return_url=f"{settings.FRONTEND_URL}/orders/{order.id}",
                metadata={
                    "order_id": str(order.id),
                    "user_id": str(order.user_id)
                }
            )
            
            return {
                "client_secret": intent.client_secret,
                "status": intent.status,
                "payment_intent_id": intent.id
            }
        except stripe.error.CardError as e:
            raise Exception(f"Card error: {str(e)}")
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    async def handle_webhook(self, payload: bytes, signature: str) -> Dict:
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
        except ValueError as e:
            raise Exception(f"Invalid payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            raise Exception(f"Invalid signature: {str(e)}")

        # Handle the event
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            await self._handle_successful_payment(payment_intent)
        elif event.type == 'payment_intent.payment_failed':
            payment_intent = event.data.object
            await self._handle_failed_payment(payment_intent)

        return {"status": "success"}

    async def _handle_successful_payment(self, payment_intent: Dict):
        """Handle successful payment"""
        order_id = payment_intent.metadata.get("order_id")
        if not order_id:
            return

        # Update order status
        await self._update_order_status(
            order_id,
            "paid",
            payment_intent.id,
            payment_intent.amount / 100  # Convert from cents
        )

        # TODO: Send order confirmation email
        # TODO: Update inventory
        # TODO: Create shipping label

    async def _handle_failed_payment(self, payment_intent: Dict):
        """Handle failed payment"""
        order_id = payment_intent.metadata.get("order_id")
        if not order_id:
            return

        # Update order status
        await self._update_order_status(
            order_id,
            "payment_failed",
            payment_intent.id,
            payment_intent.amount / 100  # Convert from cents
        )

        # TODO: Send payment failure notification
        # TODO: Attempt alternative payment method if available

    def _calculate_total_amount(self, order: Order) -> float:
        """Calculate total amount including shipping and taxes"""
        subtotal = sum(item.price * item.quantity for item in order.items)
        shipping_cost = self._calculate_shipping_cost(order)
        tax_amount = self._calculate_tax_amount(subtotal, order.shipping_address)
        
        return subtotal + shipping_cost + tax_amount

    def _calculate_shipping_cost(self, order: Order) -> float:
        """Calculate shipping cost based on address and items"""
        # TODO: Implement shipping cost calculation
        # This could integrate with shipping APIs like Shippo or EasyPost
        return 0.0

    def _calculate_tax_amount(self, subtotal: float, shipping_address: Dict) -> float:
        """Calculate tax amount based on shipping address"""
        # TODO: Implement tax calculation
        # This could integrate with tax APIs like TaxJar or Avalara
        return 0.0

    async def _update_order_status(
        self,
        order_id: str,
        status: str,
        payment_id: str,
        amount: float
    ):
        """Update order status in database"""
        # TODO: Implement order status update
        pass

    async def refund_payment(self, order_id: str, amount: Optional[float] = None) -> Dict:
        """Refund a payment"""
        try:
            # Get payment intent ID from order
            order = await self._get_order(order_id)
            if not order or not order.payment_id:
                raise Exception("Order or payment ID not found")

            # Create refund
            refund = stripe.Refund.create(
                payment_intent=order.payment_id,
                amount=int(amount * 100) if amount else None  # Convert to cents
            )

            # Update order status
            await self._update_order_status(
                order_id,
                "refunded" if not amount else "partially_refunded",
                order.payment_id,
                -refund.amount / 100  # Negative amount for refund
            )

            return {
                "refund_id": refund.id,
                "amount": refund.amount / 100,
                "status": refund.status
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Refund failed: {str(e)}")

    async def _get_order(self, order_id: str) -> Optional[Order]:
        """Get order from database"""
        # TODO: Implement order retrieval
        pass 