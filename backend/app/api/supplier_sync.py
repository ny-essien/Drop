from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import Product, Supplier
from app.services.supplier_sync import SupplierSyncService
from app.core.deps import get_db, get_current_admin

router = APIRouter()

@router.post("/suppliers/{supplier_id}/sync", response_model=List[Product])
async def sync_supplier_products(
    supplier_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    sync_service = SupplierSyncService(db)
    updated_products = await sync_service.sync_supplier_products(supplier_id)
    return updated_products

@router.post("/suppliers/sync-all", response_model=List[Product])
async def sync_all_suppliers(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    sync_service = SupplierSyncService(db)
    updated_products = await sync_service.sync_all_suppliers()
    return updated_products

@router.get("/suppliers/{supplier_id}/search", response_model=List[Product])
async def search_supplier_products(
    supplier_id: str,
    query: str,
    limit: int = 10,
    current_user: User = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    sync_service = SupplierSyncService(db)
    products = await sync_service.search_supplier_products(supplier_id, query, limit)
    return products

@router.post("/suppliers/{supplier_id}/products/{product_id}", response_model=Product)
async def import_supplier_product(
    supplier_id: str,
    product_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    sync_service = SupplierSyncService(db)
    product = await sync_service.import_supplier_product(supplier_id, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/suppliers/auto-sync")
async def start_auto_sync(
    interval_minutes: int = 60,
    current_user: User = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    sync_service = SupplierSyncService(db)
    background_tasks.add_task(sync_service.start_auto_sync, interval_minutes)
    return {"message": "Auto sync started"}

@router.get("/suppliers/{supplier_id}/stats")
async def get_supplier_stats(
    supplier_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    sync_service = SupplierSyncService(db)
    stats = await sync_service.get_supplier_stats(supplier_id)
    return stats 