from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.analytics import AnalyticsService
from app.models import (
    SalesAnalytics,
    ProductAnalytics,
    CustomerAnalytics,
    SupplierAnalytics,
    FinancialReport
)
from app.dependencies import get_db, get_current_admin

router = APIRouter()

@router.get("/sales", response_model=List[SalesAnalytics])
async def get_sales_analytics(
    start_date: datetime = Query(..., description="Start date for analytics"),
    end_date: datetime = Query(..., description="End date for analytics"),
    db=Depends(get_db),
    _=Depends(get_current_admin)
):
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_sales_analytics(start_date, end_date)

@router.post("/sales/generate", response_model=SalesAnalytics)
async def generate_sales_analytics(
    start_date: datetime = Query(..., description="Start date for analytics"),
    end_date: datetime = Query(..., description="End date for analytics"),
    db=Depends(get_db),
    _=Depends(get_current_admin)
):
    analytics_service = AnalyticsService(db)
    return await analytics_service.generate_sales_analytics(start_date, end_date)

@router.get("/products/{product_id}", response_model=ProductAnalytics)
async def get_product_analytics(
    product_id: str,
    db=Depends(get_db),
    _=Depends(get_current_admin)
):
    analytics_service = AnalyticsService(db)
    analytics = await analytics_service.get_product_analytics(product_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Product analytics not found")
    return analytics

@router.post("/products/{product_id}/generate", response_model=ProductAnalytics)
async def generate_product_analytics(
    product_id: str,
    db=Depends(get_db),
    _=Depends(get_current_admin)
):
    analytics_service = AnalyticsService(db)
    return await analytics_service.generate_product_analytics(product_id)

@router.get("/customers/{customer_id}", response_model=CustomerAnalytics)
async def get_customer_analytics(
    customer_id: str,
    db=Depends(get_db),
    _=Depends(get_current_admin)
):
    analytics_service = AnalyticsService(db)
    analytics = await analytics_service.get_customer_analytics(customer_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Customer analytics not found")
    return analytics

@router.post("/customers/{customer_id}/generate", response_model=CustomerAnalytics)
async def generate_customer_analytics(
    customer_id: str,
    db=Depends(get_db),
    _=Depends(get_current_admin)
):
    analytics_service = AnalyticsService(db)
    return await analytics_service.generate_customer_analytics(customer_id)

@router.get("/suppliers/{supplier_id}", response_model=SupplierAnalytics)
async def get_supplier_analytics(
    supplier_id: str,
    db=Depends(get_db),
    _=Depends(get_current_admin)
):
    analytics_service = AnalyticsService(db)
    analytics = await analytics_service.get_supplier_analytics(supplier_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Supplier analytics not found")
    return analytics

@router.post("/suppliers/{supplier_id}/generate", response_model=SupplierAnalytics)
async def generate_supplier_analytics(
    supplier_id: str,
    db=Depends(get_db),
    _=Depends(get_current_admin)
):
    analytics_service = AnalyticsService(db)
    return await analytics_service.generate_supplier_analytics(supplier_id)

@router.get("/financial", response_model=List[FinancialReport])
async def get_financial_reports(
    start_date: datetime = Query(..., description="Start date for reports"),
    end_date: datetime = Query(..., description="End date for reports"),
    db=Depends(get_db),
    _=Depends(get_current_admin)
):
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_financial_reports(start_date, end_date)

@router.post("/financial/generate", response_model=FinancialReport)
async def generate_financial_report(
    start_date: datetime = Query(..., description="Start date for report"),
    end_date: datetime = Query(..., description="End date for report"),
    db=Depends(get_db),
    _=Depends(get_current_admin)
):
    analytics_service = AnalyticsService(db)
    return await analytics_service.generate_financial_report(start_date, end_date) 