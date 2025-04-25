from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str
    description: str
    price: float
    image_url: str
    category: str
    supplier_id: str
    stock_quantity: int
    sku: str
    status: str = "active"  # active, inactive, out_of_stock
    tags: List[str] = []
    specifications: dict = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid)
        }
        json_schema_extra = {
            "example": {
                "name": "Wireless Earbuds",
                "description": "High-quality wireless earbuds with noise cancellation",
                "price": 99.99,
                "image_url": "https://example.com/images/earbuds.jpg",
                "category": "Electronics",
                "supplier_id": "supplier123",
                "stock_quantity": 100,
                "sku": "WE-001",
                "status": "active",
                "tags": ["wireless", "audio", "electronics"],
                "specifications": {
                    "battery_life": "6 hours",
                    "charging_time": "1.5 hours",
                    "bluetooth_version": "5.0"
                }
            }
        }

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    image_url: str
    category: str
    supplier_id: str
    stock_quantity: int
    sku: str
    tags: Optional[List[str]] = []
    specifications: Optional[dict] = {}

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    supplier_id: Optional[str] = None
    stock_quantity: Optional[int] = None
    sku: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    specifications: Optional[dict] = None 