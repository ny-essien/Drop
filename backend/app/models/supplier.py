from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from enum import Enum

class SyncStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class SupplierBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    status: str = "active"  # active, inactive, pending
    integration_type: Optional[str] = None  # api, manual, etc.
    api_key: Optional[str] = None
    api_secret: Optional[str] = None

class Supplier(SupplierBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    products: List[str] = []  # List of product IDs

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "supplier123",
                "name": "Test Supplier",
                "email": "supplier@example.com",
                "phone": "+1234567890",
                "address": "123 Supplier St",
                "website": "https://supplier.com",
                "description": "Test supplier description",
                "status": "active",
                "integration_type": "api",
                "api_key": None,
                "api_secret": None,
                "products": [],
                "created_at": "2023-01-01T00:00:00",
                "updated_at": None
            }
        }

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    integration_type: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None

class SupplierSync(BaseModel):
    id: str = Field(alias="_id")
    supplier_id: str
    status: SyncStatus = SyncStatus.PENDING
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    products_synced: int = 0
    products_updated: int = 0
    products_failed: int = 0

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "sync123",
                "supplier_id": "supplier123",
                "status": "pending",
                "started_at": "2023-01-01T00:00:00",
                "completed_at": None,
                "error_message": None,
                "products_synced": 0,
                "products_updated": 0,
                "products_failed": 0
            }
        } 