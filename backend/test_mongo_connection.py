from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test_connection():
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.test_db
        await db.command("ping")
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection()) 