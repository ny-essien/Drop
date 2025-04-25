import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.product_service import ProductService
from app.models.product import Product
from app.db import get_database
import asyncio

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
        product = Product(
            name="Test Product",
            description="Test Description",
            price=10.99,
            stock=100
        )
        created_product = await product_service.create_product(product)
        assert created_product.name == product.name
        assert created_product.description == product.description
        assert created_product.price == product.price
        assert created_product.stock == product.stock

    @pytest.mark.asyncio
    async def test_get_product(self, product_service):
        product = Product(
            name="Test Product",
            description="Test Description",
            price=10.99,
            stock=100
        )
        created_product = await product_service.create_product(product)
        retrieved_product = await product_service.get_product(str(created_product.id))
        assert retrieved_product is not None
        assert retrieved_product.name == product.name

    @pytest.mark.asyncio
    async def test_update_product(self, product_service):
        product = Product(
            name="Test Product",
            description="Test Description",
            price=10.99,
            stock=100
        )
        created_product = await product_service.create_product(product)
        updated_product = Product(
            name="Updated Product",
            description="Updated Description",
            price=15.99,
            stock=50
        )
        result = await product_service.update_product(str(created_product.id), updated_product)
        assert result is not None
        assert result.name == updated_product.name
        assert result.description == updated_product.description
        assert result.price == updated_product.price
        assert result.stock == updated_product.stock

    @pytest.mark.asyncio
    async def test_delete_product(self, product_service):
        product = Product(
            name="Test Product",
            description="Test Description",
            price=10.99,
            stock=100
        )
        created_product = await product_service.create_product(product)
        result = await product_service.delete_product(str(created_product.id))
        assert result is True
        deleted_product = await product_service.get_product(str(created_product.id))
        assert deleted_product is None

    @pytest.mark.asyncio
    async def test_get_products(self, product_service):
        # Create multiple products
        products = [
            Product(name=f"Product {i}", description=f"Description {i}", price=10.99, stock=100)
            for i in range(5)
        ]
        for product in products:
            await product_service.create_product(product)

        # Test listing all products
        listed_products = await product_service.get_products()
        assert len(listed_products) >= 5

        # Test search functionality
        searched_products = await product_service.get_products(search="Product 1")
        assert len(searched_products) > 0
        assert any(p.name == "Product 1" for p in searched_products)

class TestProductAPI:
    def test_create_product(self, test_client):
        response = test_client.post(
            "/api/products/",
            json={
                "name": "Test Product",
                "description": "Test Description",
                "price": 10.99,
                "stock": 100
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Product"
        assert data["description"] == "Test Description"
        assert data["price"] == 10.99
        assert data["stock"] == 100

    def test_get_product(self, test_client):
        # First create a product
        create_response = test_client.post(
            "/api/products/",
            json={
                "name": "Test Product",
                "description": "Test Description",
                "price": 10.99,
                "stock": 100
            }
        )
        product_id = create_response.json()["id"]

        # Then get it
        response = test_client.get(f"/api/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Product"
        assert data["id"] == product_id

    def test_update_product(self, test_client):
        # First create a product
        create_response = test_client.post(
            "/api/products/",
            json={
                "name": "Test Product",
                "description": "Test Description",
                "price": 10.99,
                "stock": 100
            }
        )
        product_id = create_response.json()["id"]

        # Then update it
        response = test_client.put(
            f"/api/products/{product_id}",
            json={
                "name": "Updated Product",
                "description": "Updated Description",
                "price": 15.99,
                "stock": 50
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product"
        assert data["price"] == 15.99
        assert data["stock"] == 50

    def test_delete_product(self, test_client):
        # First create a product
        create_response = test_client.post(
            "/api/products/",
            json={
                "name": "Test Product",
                "description": "Test Description",
                "price": 10.99,
                "stock": 100
            }
        )
        product_id = create_response.json()["id"]

        # Then delete it
        response = test_client.delete(f"/api/products/{product_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Product deleted successfully"

        # Verify it's deleted
        get_response = test_client.get(f"/api/products/{product_id}")
        assert get_response.status_code == 404

    def test_list_products(self, test_client):
        # Create multiple products
        for i in range(3):
            test_client.post(
                "/api/products/",
                json={
                    "name": f"Product {i}",
                    "description": f"Description {i}",
                    "price": 10.99,
                    "stock": 100
                }
            )

        # List all products
        response = test_client.get("/api/products/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

        # Test search
        search_response = test_client.get("/api/products/?search=Product 1")
        assert search_response.status_code == 200
        search_data = search_response.json()
        assert len(search_data) > 0
        assert any(p["name"] == "Product 1" for p in search_data) 