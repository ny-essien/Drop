import pytest
from fastapi.testclient import TestClient
from app.models.product import Product
from app.services.product_service import ProductService
from app.api.products import router as product_router
from datetime import datetime

@pytest.fixture
def product_service():
    return ProductService()

@pytest.fixture
def test_client():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(product_router)
    return TestClient(app)

@pytest.fixture
def sample_product():
    return {
        "name": "Test Product",
        "description": "A test product for unit testing",
        "price": 29.99,
        "stock": 100,
        "category": "Test Category",
        "supplier_id": "test_supplier_123",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

class TestProductService:
    def test_create_product(self, product_service, sample_product):
        product = product_service.create_product(sample_product)
        assert product.name == sample_product["name"]
        assert product.price == sample_product["price"]
        assert product.stock == sample_product["stock"]

    def test_get_product(self, product_service, sample_product):
        created_product = product_service.create_product(sample_product)
        retrieved_product = product_service.get_product(str(created_product.id))
        assert retrieved_product.name == sample_product["name"]

    def test_update_product(self, product_service, sample_product):
        created_product = product_service.create_product(sample_product)
        updates = {"price": 39.99, "stock": 150}
        updated_product = product_service.update_product(str(created_product.id), updates)
        assert updated_product.price == 39.99
        assert updated_product.stock == 150

    def test_delete_product(self, product_service, sample_product):
        created_product = product_service.create_product(sample_product)
        product_service.delete_product(str(created_product.id))
        with pytest.raises(Exception):
            product_service.get_product(str(created_product.id))

    def test_list_products(self, product_service, sample_product):
        product_service.create_product(sample_product)
        products = product_service.list_products()
        assert len(products) > 0

class TestProductAPI:
    def test_create_product_api(self, test_client, sample_product):
        response = test_client.post("/products/", json=sample_product)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_product["name"]

    def test_get_product_api(self, test_client, sample_product):
        create_response = test_client.post("/products/", json=sample_product)
        product_id = create_response.json()["id"]
        
        response = test_client.get(f"/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_product["name"]

    def test_update_product_api(self, test_client, sample_product):
        create_response = test_client.post("/products/", json=sample_product)
        product_id = create_response.json()["id"]
        
        updates = {"price": 39.99, "stock": 150}
        response = test_client.put(f"/products/{product_id}", json=updates)
        assert response.status_code == 200
        data = response.json()
        assert data["price"] == 39.99
        assert data["stock"] == 150

    def test_delete_product_api(self, test_client, sample_product):
        create_response = test_client.post("/products/", json=sample_product)
        product_id = create_response.json()["id"]
        
        response = test_client.delete(f"/products/{product_id}")
        assert response.status_code == 204

    def test_list_products_api(self, test_client, sample_product):
        test_client.post("/products/", json=sample_product)
        response = test_client.get("/products/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_search_products_api(self, test_client, sample_product):
        test_client.post("/products/", json=sample_product)
        response = test_client.get("/products/search?query=Test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert "Test" in data[0]["name"] 