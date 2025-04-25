import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.product_service import ProductService
from app.models.product import Product, ProductCreate, ProductUpdate
from app.db import get_database
import asyncio
from datetime import datetime

@pytest.fixture
async def product_service():
    db = await get_database()
    return ProductService(db)

@pytest.fixture
def test_client():
    return TestClient(app)

class TestProductService:
    @pytest.mark.asyncio
    async def test_create_product(self, product_service):
        product = ProductCreate(
            name="Test Product",
            description="Test Description",
            price=10.99,
            image_url="https://example.com/test.jpg",
            category="Test Category",
            supplier_id="test_supplier_123",
            stock_quantity=100,
            sku="TEST-001"
        )
        created_product = await product_service.create_product(product)
        assert created_product.name == "Test Product"
        assert created_product.price == 10.99

    @pytest.mark.asyncio
    async def test_get_product(self, product_service):
        product = ProductCreate(
            name="Test Product",
            description="Test Description",
            price=10.99,
            image_url="https://example.com/test.jpg",
            category="Test Category",
            supplier_id="test_supplier_123",
            stock_quantity=100,
            sku="TEST-001"
        )
        created_product = await product_service.create_product(product)
        retrieved_product = await product_service.get_product(created_product.id)
        assert retrieved_product.name == product.name
        assert retrieved_product.price == product.price

    @pytest.mark.asyncio
    async def test_update_product(self, product_service):
        product = ProductCreate(
            name="Test Product",
            description="Test Description",
            price=10.99,
            image_url="https://example.com/test.jpg",
            category="Test Category",
            supplier_id="test_supplier_123",
            stock_quantity=100,
            sku="TEST-001"
        )
        created_product = await product_service.create_product(product)
        update_data = ProductUpdate(price=15.99)
        updated_product = await product_service.update_product(created_product.id, update_data)
        assert updated_product.price == 15.99

    @pytest.mark.asyncio
    async def test_delete_product(self, product_service):
        product = ProductCreate(
            name="Test Product",
            description="Test Description",
            price=10.99,
            image_url="https://example.com/test.jpg",
            category="Test Category",
            supplier_id="test_supplier_123",
            stock_quantity=100,
            sku="TEST-001"
        )
        created_product = await product_service.create_product(product)
        result = await product_service.delete_product(created_product.id)
        assert result is True

    @pytest.mark.asyncio
    async def test_get_products(self, product_service):
        # Create multiple products
        products = [
            ProductCreate(
                name=f"Product {i}",
                description=f"Description {i}",
                price=10.99,
                image_url=f"https://example.com/test{i}.jpg",
                category="Test Category",
                supplier_id="test_supplier_123",
                stock_quantity=100,
                sku=f"TEST-00{i}"
            )
            for i in range(5)
        ]
        for product in products:
            await product_service.create_product(product)
        
        all_products = await product_service.get_products()
        assert len(all_products) >= 5

class TestProductAPI:
    def test_create_product(self, test_client, auth_headers):
        response = test_client.post(
            "/api/v1/products/",
            headers=auth_headers,
            json={
                "name": "Test Product",
                "description": "Test Description",
                "price": 10.99,
                "image_url": "https://example.com/test.jpg",
                "category": "Test Category",
                "supplier_id": "test_supplier_123",
                "stock_quantity": 100,
                "sku": "TEST-001"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Product"

    def test_get_product(self, test_client, auth_headers):
        # First create a product
        create_response = test_client.post(
            "/api/v1/products/",
            headers=auth_headers,
            json={
                "name": "Test Product",
                "description": "Test Description",
                "price": 10.99,
                "image_url": "https://example.com/test.jpg",
                "category": "Test Category",
                "supplier_id": "test_supplier_123",
                "stock_quantity": 100,
                "sku": "TEST-001"
            }
        )
        product_id = create_response.json()["id"]
        
        # Then get the product
        response = test_client.get(f"/api/v1/products/{product_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Product"

    def test_update_product(self, test_client, auth_headers):
        # First create a product
        create_response = test_client.post(
            "/api/v1/products/",
            headers=auth_headers,
            json={
                "name": "Test Product",
                "description": "Test Description",
                "price": 10.99,
                "image_url": "https://example.com/test.jpg",
                "category": "Test Category",
                "supplier_id": "test_supplier_123",
                "stock_quantity": 100,
                "sku": "TEST-001"
            }
        )
        product_id = create_response.json()["id"]
        
        # Then update the product
        response = test_client.put(
            f"/api/v1/products/{product_id}",
            headers=auth_headers,
            json={"price": 15.99}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["price"] == 15.99

    def test_delete_product(self, test_client, auth_headers):
        # First create a product
        create_response = test_client.post(
            "/api/v1/products/",
            headers=auth_headers,
            json={
                "name": "Test Product",
                "description": "Test Description",
                "price": 10.99,
                "image_url": "https://example.com/test.jpg",
                "category": "Test Category",
                "supplier_id": "test_supplier_123",
                "stock_quantity": 100,
                "sku": "TEST-001"
            }
        )
        product_id = create_response.json()["id"]
        
        # Then delete the product
        response = test_client.delete(f"/api/v1/products/{product_id}", headers=auth_headers)
        assert response.status_code == 200

    def test_list_products(self, test_client, auth_headers):
        # Create multiple products
        for i in range(3):
            test_client.post(
                "/api/v1/products/",
                headers=auth_headers,
                json={
                    "name": f"Product {i}",
                    "description": f"Description {i}",
                    "price": 10.99,
                    "image_url": f"https://example.com/test{i}.jpg",
                    "category": "Test Category",
                    "supplier_id": "test_supplier_123",
                    "stock_quantity": 100,
                    "sku": f"TEST-00{i}"
                }
            )
        
        # List all products
        response = test_client.get("/api/v1/products/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3 