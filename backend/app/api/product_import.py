from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.product import Product, ProductCreate
from app.models.supplier import Supplier, SupplierCreate
from app.dependencies import get_db
from app.services.product import ProductService

router = APIRouter()

@router.post("/suppliers/", response_model=Supplier)
async def create_supplier(supplier: Supplier, db: AsyncIOMotorDatabase = Depends(get_db)):
    product_service = ProductService(db)
    try:
        return await product_service.create_supplier(supplier)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/suppliers/{supplier_id}", response_model=Supplier)
async def get_supplier(supplier_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    product_service = ProductService(db)
    supplier = await product_service.get_supplier(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.post("/import/{source}", response_model=Product)
async def import_product(source: str, data: dict, db: AsyncIOMotorDatabase = Depends(get_db)):
    product_service = ProductService(db)
    try:
        return await product_service.import_product(source, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import/bulk/{source}", response_model=List[Product])
async def bulk_import_products(source: str, products_data: List[dict], db: AsyncIOMotorDatabase = Depends(get_db)):
    product_service = ProductService(db)
    try:
        return await product_service.bulk_import_products(source, products_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 