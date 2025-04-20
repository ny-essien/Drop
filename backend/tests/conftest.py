import pytest
import asyncio
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from datetime import datetime, timedelta
from jose import jwt

from app.main import app
from app.config import settings
from app.db import get_database
from app.models import User

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_db():
    # Use a separate test database
    client = MongoClient(settings.MONGODB_URI)
    db_name = "test_" + settings.MONGODB_DB
    db = client[db_name]
    yield db
    # Cleanup after tests
    client.drop_database(db_name)
    client.close()

@pytest.fixture
async def test_app(test_db):
    app.dependency_overrides[get_database] = lambda: test_db
    with TestClient(app) as client:
        yield client

@pytest.fixture
def test_user():
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
    expire = datetime.utcnow() + timedelta(minutes=30)
    data = {
        "sub": test_user["email"],
        "exp": expire,
        "user_id": test_user["_id"]
    }
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

@pytest.fixture
def admin_token(test_admin):
    expire = datetime.utcnow() + timedelta(minutes=30)
    data = {
        "sub": test_admin["email"],
        "exp": expire,
        "user_id": test_admin["_id"]
    }
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

@pytest.fixture
async def setup_test_db(test_db, test_user, test_admin):
    # Insert test users
    await test_db.users.insert_one(test_user)
    await test_db.users.insert_one(test_admin)
    yield
    # Cleanup
    await test_db.users.delete_many({}) 