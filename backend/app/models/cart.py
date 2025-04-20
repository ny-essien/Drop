from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)
    price: float
    name: str
    image_url: Optional[str] = None
    category: str
    supplier_id: Optional[str] = None
    added_at: datetime = Field(default_factory=datetime.utcnow)

class Cart(BaseModel):
    user_id: str
    items: List[CartItem] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "items": [
                    {
                        "product_id": "prod123",
                        "quantity": 2,
                        "price": 29.99,
                        "name": "Sample Product",
                        "image_url": "https://example.com/image.jpg",
                        "category": "Electronics",
                        "supplier_id": "sup123"
                    }
                ]
            }
        } 