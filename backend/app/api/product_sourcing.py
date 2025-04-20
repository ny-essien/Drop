from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Optional
from app.services.product_sourcing import ProductSourcingService
from app.auth import get_current_user
from app.models import User

router = APIRouter()

@router.get("/suppliers/search")
async def search_suppliers(
    query: str,
    filters: Optional[Dict] = None,
    current_user: User = Depends(get_current_user)
):
    """Search for suppliers based on query and filters"""
    async with ProductSourcingService() as service:
        suppliers = await service.search_suppliers(query, filters)
        return suppliers

@router.get("/products/{product_id}/price-comparison")
async def compare_prices(
    product_id: str,
    current_user: User = Depends(get_current_user)
):
    """Compare prices across different suppliers for a product"""
    async with ProductSourcingService() as service:
        comparisons = await service.compare_prices(product_id)
        return comparisons

@router.post("/products/bulk-import")
async def bulk_import_products(
    supplier_id: str,
    category: str,
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
):
    """Bulk import products from a supplier"""
    async with ProductSourcingService() as service:
        result = await service.bulk_import_products(supplier_id, category, limit)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result

@router.get("/products/{product_id}/variations")
async def get_product_variations(
    product_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all variations of a product"""
    async with ProductSourcingService() as service:
        variations = await service.get_product_variations(product_id)
        return variations

@router.post("/products/{product_id}/variations")
async def create_product_variation(
    product_id: str,
    variation_data: Dict,
    current_user: User = Depends(get_current_user)
):
    """Create a new variation for a product"""
    async with ProductSourcingService() as service:
        result = await service.create_product_variation(product_id, variation_data)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result

@router.get("/products/search")
async def search_products(
    query: str,
    filters: Optional[Dict] = None,
    current_user: User = Depends(get_current_user)
):
    """Advanced product search with filters"""
    async with ProductSourcingService() as service:
        result = await service.search_products(query, filters)
        return result 