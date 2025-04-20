from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.services.notification_service import NotificationService
from app.models import Order, Notification
from app.auth import get_current_user

router = APIRouter()
notification_service = NotificationService()

@router.post("/orders/{order_id}/confirm", response_model=Dict[str, Any])
async def send_order_confirmation(
    order_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Send order confirmation notification"""
    try:
        order = await Order.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        result = await notification_service.send_order_confirmation(order)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/{order_id}/notify-warehouse", response_model=Dict[str, Any])
async def notify_warehouse(
    order_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Notify warehouse about new order"""
    try:
        order = await Order.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        result = await notification_service.notify_warehouse(order)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/{order_id}/status-update", response_model=Dict[str, Any])
async def send_status_update(
    order_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Send order status update notification"""
    try:
        order = await Order.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        result = await notification_service.send_status_update(order)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/{order_id}/cancel", response_model=Dict[str, Any])
async def send_cancellation_notice(
    order_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Send order cancellation notice"""
    try:
        order = await Order.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        result = await notification_service.send_cancellation_notice(order)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products/{product_id}/low-stock", response_model=Dict[str, Any])
async def send_low_stock_alert(
    product_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Send low stock alert"""
    try:
        result = await notification_service.send_low_stock_alert(product_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Notification])
async def get_notifications(
    type: Optional[str] = Query(None, description="Filter by notification type"),
    status: Optional[str] = Query(None, description="Filter by notification status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    limit: int = Query(100, description="Number of notifications to return"),
    skip: int = Query(0, description="Number of notifications to skip"),
    current_user: dict = Depends(get_current_user)
):
    """Get notifications with optional filtering"""
    try:
        notifications = await notification_service.get_notifications(
            type=type,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            skip=skip
        )
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{notification_id}", response_model=Notification)
async def get_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific notification by ID"""
    try:
        notification = await notification_service.get_notification(notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        return notification
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Notification)
async def create_notification(
    notification: Notification,
    current_user: dict = Depends(get_current_user)
):
    """Create a new notification"""
    try:
        new_notification = await notification_service.create_notification(
            type=notification.type,
            title=notification.title,
            message=notification.message,
            status=notification.status,
            error=notification.error,
            metadata=notification.metadata
        )
        return new_notification
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{notification_id}/status", response_model=Notification)
async def update_notification_status(
    notification_id: str,
    status: str,
    error: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Update notification status"""
    try:
        notification = await notification_service.update_notification_status(
            notification_id=notification_id,
            status=status,
            error=error
        )
        return notification
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a notification"""
    try:
        await notification_service.delete_notification(notification_id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary")
async def get_notification_stats(current_user: dict = Depends(get_current_user)):
    """Get notification statistics"""
    try:
        stats = await notification_service.get_notification_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 