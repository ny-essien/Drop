from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItem(BaseModel):
    product_id: str
    quantity: int
    price: float
    name: str
    image_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod123",
                "quantity": 2,
                "price": 29.99,
                "name": "Sample Product",
                "image_url": "https://example.com/image.jpg"
            }
        }

class ShippingAddress(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "street": "123 Main St",
                "city": "Sample City",
                "state": "Sample State",
                "postal_code": "12345",
                "country": "Sample Country"
            }
        }

class Order(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    items: List[OrderItem]
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING
    shipping_address: ShippingAddress
    tracking_number: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "order123",
                "user_id": "user123",
                "items": [{
                    "product_id": "prod123",
                    "quantity": 2,
                    "price": 29.99,
                    "name": "Sample Product",
                    "image_url": "https://example.com/image.jpg"
                }],
                "total_amount": 59.98,
                "status": "pending",
                "shipping_address": {
                    "street": "123 Main St",
                    "city": "Sample City",
                    "state": "Sample State",
                    "postal_code": "12345",
                    "country": "Sample Country"
                },
                "tracking_number": None,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": None
            }
        }

class OrderCreate(BaseModel):
    items: List[OrderItem]
    shipping_address: ShippingAddress

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    tracking_number: Optional[str] = None 