from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from app.models import CartItem
from app.services.cart import CartService
from app.database import get_database
from app.middleware.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[CartItem])
async def get_cart(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    cart_service = CartService(db)
    return await cart_service.get_cart_items(current_user["id"])

@router.post("/items/{product_id}", response_model=CartItem)
async def add_to_cart(
    product_id: str,
    quantity: int = 1,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    cart_service = CartService(db)
    cart_item = await cart_service.add_to_cart(current_user["id"], product_id, quantity)
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return cart_item

@router.put("/items/{product_id}", response_model=CartItem)
async def update_cart_item(
    product_id: str,
    quantity: int,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    cart_service = CartService(db)
    cart_item = await cart_service.update_cart_item(current_user["id"], product_id, quantity)
    if not cart_item and quantity > 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found in cart"
        )
    return cart_item

@router.delete("/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    cart_service = CartService(db)
    success = await cart_service.remove_from_cart(current_user["id"], product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found in cart"
        )

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    cart_service = CartService(db)
    await cart_service.clear_cart(current_user["id"]) 