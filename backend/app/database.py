from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import AsyncGenerator

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "dropshipping"

# Async client for FastAPI
async def get_database() -> AsyncGenerator[AsyncIOMotorClient, None]:
    client = AsyncIOMotorClient(MONGODB_URL)
    try:
        yield client[DATABASE_NAME]
    finally:
        client.close()

# Sync client for testing and development
def get_sync_database():
    client = MongoClient(MONGODB_URL)
    try:
        return client[DATABASE_NAME]
    finally:
        client.close()
 