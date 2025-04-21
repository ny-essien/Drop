from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_to_mongo(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.MONGODB_DB]

    async def close_mongo_connection(self):
        if self.client:
            self.client.close()

mongodb = MongoDB()

async def get_database():
    if not mongodb.client:
        await mongodb.connect_to_mongo()
    return mongodb.db 