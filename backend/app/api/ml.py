from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from app.services.ml_service import MLService
from app.auth import get_current_user
from app.models import User

router = APIRouter()

@router.post("/train/price-optimization")
async def train_price_optimization_model(
    current_user: User = Depends(get_current_user)
):
    """Train the price optimization model"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can train models")
    
    async with MLService() as service:
        score = await service.train_price_optimization_model()
        return {"score": score}

@router.get("/products/{product_id}/optimize-price")
async def optimize_price(
    product_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get optimized price for a product"""
    async with MLService() as service:
        result = await service.optimize_price(product_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result

@router.post("/train/demand-forecasting")
async def train_demand_forecasting_model(
    current_user: User = Depends(get_current_user)
):
    """Train the demand forecasting model"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can train models")
    
    async with MLService() as service:
        score = await service.train_demand_forecasting_model()
        return {"score": score}

@router.get("/products/{product_id}/forecast")
async def forecast_demand(
    product_id: str,
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get demand forecast for a product"""
    async with MLService() as service:
        result = await service.forecast_demand(product_id, days)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result

@router.get("/customers/segments")
async def get_customer_segments(
    current_user: User = Depends(get_current_user)
):
    """Get customer segments"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can view customer segments")
    
    async with MLService() as service:
        segments = await service.segment_customers()
        return segments

@router.get("/users/{user_id}/recommendations")
async def get_product_recommendations(
    user_id: str,
    limit: int = 5,
    current_user: User = Depends(get_current_user)
):
    """Get personalized product recommendations for a user"""
    async with MLService() as service:
        recommendations = await service.get_product_recommendations(user_id, limit)
        return recommendations 