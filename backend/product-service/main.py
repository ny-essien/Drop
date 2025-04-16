from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Product Sourcing Service")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URL)
db = client.dropshipping

# Models
class ProductSource(BaseModel):
    name: str
    url: str
    api_key: Optional[str] = None
    credentials: Optional[dict] = None

class Product(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    source: str
    source_url: str
    images: List[str] = []

# Routes
@app.get("/")
async def root():
    return {"message": "Product Sourcing Service"}

@app.post("/sources", response_model=ProductSource)
async def create_source(source: ProductSource):
    result = await db.sources.insert_one(source.dict())
    created_source = await db.sources.find_one({"_id": result.inserted_id})
    return created_source

@app.get("/sources", response_model=List[ProductSource])
async def get_sources():
    sources = await db.sources.find().to_list(length=100)
    return sources

@app.post("/products/import")
async def import_products(source_id: str):
    # TODO: Implement product import logic
    return {"message": "Product import started"}

@app.get("/products", response_model=List[Product])
async def get_products():
    products = await db.products.find().to_list(length=100)
    return products

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 