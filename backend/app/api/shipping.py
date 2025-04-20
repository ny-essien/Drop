from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict
from app.services.shipping_service import ShippingService
from app.auth import get_current_user
from app.models import User

router = APIRouter()

@router.get("/orders/{order_id}/carriers")
async def get_available_carriers(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get available shipping carriers for an order"""
    async with ShippingService() as service:
        carriers = await service.get_available_carriers(order_id)
        return carriers

@router.post("/orders/{order_id}/labels")
async def create_shipping_label(
    order_id: str,
    carrier_id: str,
    service_level: str,
    current_user: User = Depends(get_current_user)
):
    """Create a shipping label for an order"""
    async with ShippingService() as service:
        result = await service.create_shipping_label(order_id, carrier_id, service_level)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result

@router.get("/tracking/{tracking_number}")
async def track_shipment(
    tracking_number: str,
    current_user: User = Depends(get_current_user)
):
    """Track a shipment using the tracking number"""
    async with ShippingService() as service:
        result = await service.track_shipment(tracking_number)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result

@router.get("/orders/{order_id}/status")
async def get_shipping_status(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get shipping status for an order"""
    async with ShippingService() as service:
        result = await service.get_shipping_status(order_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result

@router.put("/orders/{order_id}/status")
async def update_shipping_status(
    order_id: str,
    status: str,
    current_user: User = Depends(get_current_user)
):
    """Update shipping status for an order"""
    async with ShippingService() as service:
        result = await service.update_shipping_status(order_id, status)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result

@router.get("/orders/{order_id}/history")
async def get_shipping_history(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get shipping history for an order"""
    async with ShippingService() as service:
        history = await service.get_shipping_history(order_id)
        return history

@router.post("/orders/{order_id}/cancel")
async def cancel_shipment(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel a shipment"""
    async with ShippingService() as service:
        result = await service.cancel_shipment(order_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result 