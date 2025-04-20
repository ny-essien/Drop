import pytest
import numpy as np
from datetime import datetime, timedelta
from app.services.ml_service import MLService

@pytest.fixture
def test_orders():
    return [
        {
            "_id": "order1",
            "user_id": "test_user_id",
            "items": [
                {"product_id": "prod1", "price": 100, "category": "electronics"}
            ],
            "total": 100,
            "created_at": datetime.utcnow() - timedelta(days=5)
        },
        {
            "_id": "order2",
            "user_id": "test_user_id",
            "items": [
                {"product_id": "prod1", "price": 110, "category": "electronics"}
            ],
            "total": 110,
            "created_at": datetime.utcnow() - timedelta(days=3)
        }
    ]

@pytest.fixture
def test_products():
    return [
        {
            "_id": "prod1",
            "name": "Test Product",
            "category": "electronics",
            "price": 100,
            "cost_price": 80
        },
        {
            "_id": "prod2",
            "name": "Test Product 2",
            "category": "electronics",
            "price": 120,
            "cost_price": 90
        }
    ]

async def test_prepare_price_data(test_db, test_orders, test_products):
    # Insert test data
    await test_db.orders.insert_many(test_orders)
    await test_db.products.insert_many(test_products)
    
    ml_service = MLService()
    data = await ml_service.prepare_price_data()
    
    assert len(data) == len(test_products)
    assert "total_sales" in data.columns
    assert "avg_price" in data.columns
    assert "total_revenue" in data.columns

async def test_train_price_optimization_model(test_db, test_orders, test_products):
    await test_db.orders.insert_many(test_orders)
    await test_db.products.insert_many(test_products)
    
    ml_service = MLService()
    score = await ml_service.train_price_optimization_model()
    
    assert isinstance(score, float)
    assert 0 <= score <= 1

async def test_optimize_price(test_db, test_orders, test_products):
    await test_db.orders.insert_many(test_orders)
    await test_db.products.insert_many(test_products)
    
    ml_service = MLService()
    await ml_service.train_price_optimization_model()
    result = await ml_service.optimize_price("prod1")
    
    assert "current_price" in result
    assert "optimal_price" in result
    assert "predicted_revenue_increase" in result
    assert "price_suggestions" in result
    assert len(result["price_suggestions"]) > 0

async def test_forecast_demand(test_db, test_orders, test_products):
    await test_db.orders.insert_many(test_orders)
    await test_db.products.insert_many(test_products)
    
    ml_service = MLService()
    await ml_service.train_demand_forecasting_model()
    result = await ml_service.forecast_demand("prod1")
    
    assert "forecast" in result
    assert len(result["forecast"]) == 30  # default forecast days
    assert "total_predicted_sales" in result
    assert "average_daily_sales" in result

async def test_segment_customers(test_db, test_orders):
    await test_db.orders.insert_many(test_orders)
    await test_db.users.insert_one({
        "_id": "test_user_id",
        "email": "test@example.com",
        "created_at": datetime.utcnow()
    })
    
    ml_service = MLService()
    segments = await ml_service.segment_customers()
    
    assert isinstance(segments, dict)
    assert len(segments) > 0
    for segment_name, data in segments.items():
        assert "count" in data
        assert "avg_total_orders" in data
        assert "avg_total_spent" in data

async def test_get_product_recommendations(test_db, test_orders, test_products):
    await test_db.orders.insert_many(test_orders)
    await test_db.products.insert_many(test_products)
    
    ml_service = MLService()
    recommendations = await ml_service.get_product_recommendations("test_user_id")
    
    assert isinstance(recommendations, list)
    if len(recommendations) > 0:
        assert "product_id" in recommendations[0]
        assert "score" in recommendations[0]
        assert "price" in recommendations[0]
        assert "category" in recommendations[0] 