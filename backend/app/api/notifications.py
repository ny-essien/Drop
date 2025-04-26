from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.services.notification_service import NotificationService
from app.models import Order, Notification, NotificationType, NotificationStatus, NotificationCreate, NotificationUpdate
from app.core.deps import get_current_user
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/notifications")
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

@router.post("/", response_model=Notification, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification: NotificationCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new notification"""
    try:
        return await notification_service.create_notification(
            user_id=current_user.id,
            type=notification.type,
            title=notification.title,
            message=notification.message,
            status=notification.status,
            error=notification.error,
            metadata=notification.metadata
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create notification: {str(e)}"
        )

@router.get("/", response_model=List[Notification])
async def get_notifications(
    type: Optional[NotificationType] = None,
    status: Optional[NotificationStatus] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get notifications for the current user"""
    try:
        return await notification_service.get_notifications(
            user_id=current_user.id,
            type=type,
            status=status,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications: {str(e)}"
        )

@router.get("/{notification_id}", response_model=Notification)
async def get_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific notification"""
    try:
        notification = await notification_service.get_notification(notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this notification"
            )
        return notification
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification: {str(e)}"
        )

@router.patch("/{notification_id}", response_model=Notification)
async def update_notification(
    notification_id: str,
    notification_update: NotificationUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a notification"""
    try:
        # First check if the notification exists and belongs to the user
        notification = await notification_service.get_notification(notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this notification"
            )
            
        # Update the notification status
        updated_notification = await notification_service.update_notification_status(
            notification_id=notification_id,
            status=notification_update.status
        )
        if not updated_notification:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update notification"
            )
        return updated_notification
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notification: {str(e)}"
        )

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a notification"""
    try:
        # First check if the notification exists and belongs to the user
        notification = await notification_service.get_notification(notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this notification"
            )
            
        # Delete the notification
        success = await notification_service.delete_notification(notification_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete notification"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notification: {str(e)}"
        )

@router.get("/stats", response_model=dict)
async def get_notification_stats(
    current_user: User = Depends(get_current_user)
):
    """Get notification statistics for the current user"""
    try:
        return await notification_service.get_notification_stats(current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification stats: {str(e)}"
        ) 