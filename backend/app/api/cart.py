from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import CartItem, Order, User
from app.services.cart import CartService
from app.services.order import OrderService
from app.services.payment import PaymentService
from app.services.notification import NotificationService
from app.core.deps import get_current_user
from app.db import get_database

router = APIRouter()
payment_service = PaymentService()
notification_service = NotificationService()

@router.get("/items", response_model=List[CartItem])
async def get_cart_items(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    cart_service = CartService(db)
    return await cart_service.get_cart_items(str(current_user.id))

@router.post("/items/{product_id}", response_model=CartItem)
async def add_to_cart(
    product_id: str,
    quantity: int = 1,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    cart_service = CartService(db)
    cart_item = await cart_service.add_to_cart(str(current_user.id), product_id, quantity)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Product not found or invalid quantity")
    return cart_item

@router.put("/items/{product_id}", response_model=CartItem)
async def update_cart_item(
    product_id: str,
    quantity: int,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    cart_service = CartService(db)
    cart_item = await cart_service.update_cart_item(str(current_user.id), product_id, quantity)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return cart_item

@router.delete("/items/{product_id}")
async def remove_from_cart(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    cart_service = CartService(db)
    success = await cart_service.remove_from_cart(str(current_user.id), product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Item removed from cart"}

@router.delete("/clear")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    cart_service = CartService(db)
    await cart_service.clear_cart(str(current_user.id))
    return {"message": "Cart cleared"}

@router.post("/checkout", response_model=Dict)
async def checkout(
    shipping_address: Dict,
    billing_address: Dict,
    payment_method: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    order_service = OrderService(db)
    order = await order_service.create_order(
        str(current_user.id),
        shipping_address,
        billing_address,
        payment_method
    )
    if not order:
        raise HTTPException(status_code=400, detail="Failed to create order. Check cart items and stock availability.")
    
    # Create payment intent
    payment_intent = await payment_service.create_payment_intent(order)
    
    # Send order confirmation email
    await notification_service.send_order_confirmation(order, current_user)
    
    return {
        "order": order,
        "payment_intent": payment_intent
    }

@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncIOMotorDatabase = Depends(get_database)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        webhook_data = await payment_service.handle_webhook(payload, sig_header)
        if webhook_data:
            order_service = OrderService(db)
            order = await order_service.get_order(webhook_data['order_id'])
            user = await db.users.find_one({"_id": order.user_id})
            
            if webhook_data['status'] == 'succeeded':
                await order_service.update_payment_status(webhook_data['order_id'], 'paid')
                await notification_service.send_order_status_update(order, User(**user))
            else:
                await notification_service.send_payment_failure(order, User(**user))
            
            return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"status": "ignored"}

@router.get("/orders/{order_id}/status", response_model=Dict)
async def get_order_status(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    order_service = OrderService(db)
    order = await order_service.get_order(order_id)
    if not order or str(order.user_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {
        "status": order.status,
        "payment_status": order.payment_status,
        "tracking_number": order.tracking_number
    }

@router.get("/orders", response_model=List[Order])
async def get_user_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    order_service = OrderService(db)
    return await order_service.get_user_orders(str(current_user.id))

@router.get("/orders/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    order_service = OrderService(db)
    order = await order_service.get_order(order_id)
    if not order or str(order.user_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/orders/{order_id}/cancel", response_model=Order)
async def cancel_user_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    order_service = OrderService(db)
    order = await order_service.cancel_order(order_id, str(current_user.id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or cannot be cancelled")
    
    # Send notification to user
    await notification_service.send_order_status_update(order, current_user)
    
    return order 