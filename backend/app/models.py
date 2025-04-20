from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from enum import Enum

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    email: EmailStr
    password: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Supplier(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    email: EmailStr
    phone: str
    address: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Product(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: Optional[str] = None
    supplier_id: Optional[str] = None
    supplier_price: Optional[float] = None
    import_source: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CartItem(BaseModel):
    product_id: str
    quantity: int

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class Order(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    user_id: str
    items: List[CartItem]
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    shipping_address: str
    tracking_number: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class SupportTicket(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    user_id: str
    subject: str
    description: str
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.LOW
    assigned_to: Optional[str] = None
    attachments: List[str] = []
    related_articles: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TicketResponse(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    ticket_id: str
    user_id: str
    message: str
    is_admin: bool = False
    attachments: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FAQCategory(str, Enum):
    GENERAL = "general"
    ORDERS = "orders"
    PAYMENTS = "payments"
    SHIPPING = "shipping"
    RETURNS = "returns"
    ACCOUNT = "account"

class FAQ(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    question: str
    answer: str
    category: FAQCategory
    is_active: bool = True
    tags: List[str] = []
    views: int = 0
    helpful_votes: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class KnowledgeBaseArticle(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    title: str
    content: str
    category: FAQCategory
    tags: List[str] = []
    is_active: bool = True
    views: int = 0
    helpful_votes: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SalesAnalytics(BaseModel):
    date: datetime
    total_sales: float
    total_orders: int
    average_order_value: float
    total_products_sold: int
    top_selling_products: List[Dict[str, Any]]
    sales_by_category: Dict[str, float]
    sales_by_supplier: Dict[str, float]

class ProductAnalytics(BaseModel):
    product_id: str
    total_sales: float
    total_units_sold: int
    average_rating: float
    total_reviews: int
    conversion_rate: float
    return_rate: float
    stock_turnover: float
    profit_margin: float
    last_updated: datetime

class CustomerAnalytics(BaseModel):
    customer_id: str
    total_spent: float
    total_orders: int
    average_order_value: float
    last_purchase_date: datetime
    favorite_categories: List[str]
    purchase_frequency: float
    customer_lifetime_value: float
    churn_risk: float

class SupplierAnalytics(BaseModel):
    supplier_id: str
    total_sales: float
    total_products_sold: int
    average_rating: float
    on_time_delivery_rate: float
    return_rate: float
    profit_margin: float
    stock_availability: float
    last_updated: datetime

class FinancialReport(BaseModel):
    period_start: datetime
    period_end: datetime
    total_revenue: float
    total_cost: float
    gross_profit: float
    operating_expenses: float
    net_profit: float
    profit_margin: float
    sales_by_channel: Dict[str, float]
    expenses_by_category: Dict[str, float]
    cash_flow: Dict[str, float]

class Notification(BaseModel):
    type: str  # order_confirmation, warehouse, cancellation, low_stock, status_update
    title: str
    message: str
    status: str  # sent, failed, pending
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}  # Additional data like order_id, product_id, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        collection = "notifications" 