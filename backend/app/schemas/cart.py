from pydantic import BaseModel, Field
from typing import Optional

class CartItemBase(BaseModel):
    quantity: int = Field(..., gt=0)

class CartItemCreate(CartItemBase):
    productId: str

class CartItemUpdate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: str
    name: str
    price: float
    image: str

    class Config:
        from_attributes = True 