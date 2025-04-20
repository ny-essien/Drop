from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import Order, User
from app.services.order import OrderService
from app.core.deps import get_db, get_current_user, get_current_admin
from app.services.notification import NotificationService

router = APIRouter()
notification_service = NotificationService()

@router.get("/orders", response_model=List[Order])
async def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    order_service = OrderService(db)
    return await order_service.get_all_orders(skip, limit, status, payment_status)

@router.get("/orders/count")
async def get_orders_count(
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    order_service = OrderService(db)
    count = await order_service.get_orders_count(status, payment_status)
    return {"count": count}

@router.put("/orders/{order_id}/status", response_model=Order)
async def update_order_status(
    order_id: str,
    status: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    order_service = OrderService(db)
    order = await order_service.update_order_status(order_id, status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Send notification to user
    user = await db.users.find_one({"_id": order.user_id})
    if user:
        await notification_service.send_order_status_update(order, User(**user))
    
    return order

@router.put("/orders/{order_id}/tracking", response_model=Order)
async def add_tracking_number(
    order_id: str,
    tracking_number: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    order_service = OrderService(db)
    order = await order_service.add_tracking_number(order_id, tracking_number)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Send notification to user
    user = await db.users.find_one({"_id": order.user_id})
    if user:
        await notification_service.send_order_status_update(order, User(**user))
    
    return order

@router.post("/orders/{order_id}/cancel", response_model=Order)
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    order_service = OrderService(db)
    order = await order_service.cancel_order(order_id, str(current_user.id), is_admin=True)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or cannot be cancelled")
    
    # Send notification to user
    user = await db.users.find_one({"_id": order.user_id})
    if user:
        await notification_service.send_order_status_update(order, User(**user))
    
    return order 