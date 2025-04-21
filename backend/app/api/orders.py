from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Optional
from datetime import datetime
from app.core.deps import get_current_user
from app.services.order_service import OrderService
from app.models import Order, User

router = APIRouter()
order_service = OrderService()

@router.on_event("startup")
async def startup_event():
    """Initialize the order service on startup"""
    await order_service.initialize()

@router.get("/", response_model=List[Order])
async def get_orders(
    status: Optional[str] = Query(None, description="Filter by order status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    limit: int = Query(100, description="Number of orders to return"),
    skip: int = Query(0, description="Number of orders to skip"),
    current_user: User = Depends(get_current_user)
):
    """Get orders with optional filtering"""
    try:
        orders = await order_service.get_orders(
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            skip=skip
        )
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific order by ID"""
    try:
        order = await order_service.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Order)
async def create_order(
    order: Order,
    current_user: User = Depends(get_current_user)
):
    """Create a new order"""
    try:
        new_order = await order_service.create_order(order)
        return new_order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{order_id}", response_model=Order)
async def update_order(
    order_id: str,
    order: Order,
    current_user: User = Depends(get_current_user)
):
    """Update an existing order"""
    try:
        updated_order = await order_service.update_order(order_id, order)
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")
        return updated_order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{order_id}")
async def delete_order(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete an order"""
    try:
        await order_service.delete_order(order_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 