import pytest
import asyncio
import sys
import os
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from jose import jwt
import uuid

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock external dependencies
sys.modules['stripe'] = MagicMock()
sys.modules['app.services.payment'] = MagicMock()
sys.modules['fastapi_mail'] = MagicMock()
sys.modules['app.services.notification'] = MagicMock()

from app.main import app
from app.core.config import settings
from app.db import get_database

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def mongo_client():
    """Create a MongoDB client for testing."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    yield client
    client.close()

@pytest.fixture(scope="session")
async def test_db():
    """Create a test database and clean it up after tests."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_name = f"test_dropshipping_{uuid.uuid4().hex[:8]}"
    db = client[db_name]
    
    # Initialize collections
    await db.users.create_index("email", unique=True)
    await db.products.create_index("sku", unique=True)
    await db.orders.create_index("_id", unique=True)
    
    try:
        yield db
    finally:
        await db.client.drop_database(db_name)
        await db.client.close()

@pytest.fixture(scope="session")
def test_app():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def test_user():
    """Create a test user."""
    return {
        "_id": "test_user_id",
        "email": "test@example.com",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYqeScNazS",  # password: test123
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.utcnow()
    }

@pytest.fixture
def test_admin():
    """Create a test admin user."""
    return {
        "_id": "test_admin_id",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYqeScNazS",
        "is_active": True,
        "is_admin": True,
        "created_at": datetime.utcnow()
    }

@pytest.fixture
def test_token(test_user):
    """Create a test JWT token."""
    expire = datetime.utcnow() + timedelta(minutes=30)
    data = {
        "sub": test_user["email"],
        "exp": expire,
        "user_id": test_user["_id"]
    }
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return f"Bearer {token}"

@pytest.fixture
def admin_token(test_admin):
    """Create a test admin JWT token."""
    expire = datetime.utcnow() + timedelta(minutes=30)
    data = {
        "sub": test_admin["email"],
        "exp": expire,
        "user_id": test_admin["_id"]
    }
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return f"Bearer {token}"

@pytest.fixture(scope="session")
def auth_headers():
    """Create authentication headers for testing."""
    return {"Authorization": "Bearer test_token"}

@pytest.fixture(autouse=True)
async def setup_teardown(test_db):
    """Clean up database before and after each test."""
    # Clean up before test
    collections = await test_db.list_collection_names()
    for collection in collections:
        await test_db[collection].delete_many({})
    yield
    # Clean up after test
    collections = await test_db.list_collection_names()
    for collection in collections:
        await test_db[collection].delete_many({})

@pytest.fixture(scope="session")
async def setup_test_db(test_db):
    """Set up test database and return a test user."""
    # Create test user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYqeScNazS",  # test123
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.utcnow(),
        "updated_at": None
    }
    
    await test_db.users.insert_one(user_data)
    return user_data

@pytest.fixture
def client():
    return TestClient(app) 