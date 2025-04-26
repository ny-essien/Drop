import pytest
import asyncio
import sys
import os
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from jose import jwt

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
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def mongo_client(event_loop):
    """Create a MongoDB client for testing."""
    client = AsyncIOMotorClient(settings.MONGODB_URI, io_loop=event_loop)
    yield client
    await client.close()

@pytest.fixture(scope="session")
async def test_db(mongo_client):
    """Create a test database."""
    db_name = "test_" + settings.MONGODB_DB
    db = mongo_client[db_name]
    yield db
    await mongo_client.drop_database(db_name)

@pytest.fixture
async def test_app(test_db):
    """Create a test app with overridden database."""
    async def override_get_database():
        return test_db
    app.dependency_overrides[get_database] = override_get_database
    with TestClient(app) as client:
        yield client

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

@pytest.fixture
def auth_headers(test_token):
    """Create authentication headers for testing."""
    return {"Authorization": test_token}

@pytest.fixture
async def setup_test_db(test_db, test_user, test_admin):
    """Set up the test database with initial data."""
    # Insert test users
    await test_db.users.insert_one(test_user)
    await test_db.users.insert_one(test_admin)
    yield
    # Clean up
    await test_db.users.delete_many({})
    await test_db.notifications.delete_many({})
    await test_db.orders.delete_many({})
    await test_db.products.delete_many({})

@pytest.fixture
def client():
    return TestClient(app) 