from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class TimeRange(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class MetricType(str, Enum):
    SALES = "sales"
    REVENUE = "revenue"
    ORDERS = "orders"
    PRODUCTS = "products"
    CUSTOMERS = "customers"
    CONVERSION = "conversion"

class SalesAnalytics(BaseModel):
    id: str = Field(alias="_id")
    time_range: TimeRange
    start_date: datetime
    end_date: datetime
    metrics: Dict[MetricType, float]
    product_breakdown: Dict[str, float]  # product_id -> sales/revenue
    category_breakdown: Dict[str, float]  # category -> sales/revenue
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "analytics123",
                "time_range": "daily",
                "start_date": "2023-01-01T00:00:00",
                "end_date": "2023-01-02T00:00:00",
                "metrics": {
                    "sales": 1000.0,
                    "revenue": 5000.0,
                    "orders": 50,
                    "products": 200,
                    "customers": 30,
                    "conversion": 0.15
                },
                "product_breakdown": {
                    "prod123": 1000.0,
                    "prod456": 2000.0
                },
                "category_breakdown": {
                    "Electronics": 2000.0,
                    "Clothing": 1000.0
                }
            }
        }

class AnalyticsRequest(BaseModel):
    time_range: TimeRange
    start_date: datetime
    end_date: datetime
    metrics: List[MetricType]

class AnalyticsResponse(BaseModel):
    analytics: SalesAnalytics
    trend: Dict[MetricType, float]  # metric -> percentage change
    comparison: Dict[MetricType, float]  # metric -> comparison value

class CustomerAnalytics(BaseModel):
    id: str = Field(alias="_id")
    customer_id: str
    total_orders: int
    total_spent: float
    average_order_value: float
    last_order_date: datetime
    favorite_categories: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProductAnalytics(BaseModel):
    id: str = Field(alias="_id")
    product_id: str
    total_sales: int
    total_revenue: float
    views: int
    conversion_rate: float
    average_rating: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SupplierAnalytics(BaseModel):
    id: str = Field(alias="_id")
    supplier_id: str
    total_sales: float
    total_products_sold: int
    average_rating: float
    on_time_delivery_rate: float
    return_rate: float
    profit_margin: float
    stock_availability: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "supplier_analytics123",
                "supplier_id": "sup123",
                "total_sales": 50000.0,
                "total_products_sold": 1000,
                "average_rating": 4.5,
                "on_time_delivery_rate": 0.95,
                "return_rate": 0.02,
                "profit_margin": 0.25,
                "stock_availability": 0.85
            }
        }

class FinancialReport(BaseModel):
    id: str = Field(alias="_id")
    start_date: datetime
    end_date: datetime
    total_revenue: float
    total_cost: float
    gross_profit: float
    operating_expenses: float
    net_profit: float
    sales_by_category: Dict[str, float]
    sales_by_product: Dict[str, float]
    sales_by_supplier: Dict[str, float]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "financial_report123",
                "start_date": "2023-01-01T00:00:00",
                "end_date": "2023-01-31T23:59:59",
                "total_revenue": 100000.0,
                "total_cost": 60000.0,
                "gross_profit": 40000.0,
                "operating_expenses": 20000.0,
                "net_profit": 20000.0,
                "sales_by_category": {
                    "Electronics": 40000.0,
                    "Clothing": 30000.0
                },
                "sales_by_product": {
                    "prod123": 10000.0,
                    "prod456": 15000.0
                },
                "sales_by_supplier": {
                    "sup123": 40000.0,
                    "sup456": 30000.0
                }
            }
        } 