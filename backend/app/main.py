from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, products, notifications, orders
from app.db.mongodb import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(products.router, prefix=f"{settings.API_V1_STR}/products", tags=["products"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}/notifications", tags=["notifications"])
app.include_router(orders.router, prefix=f"{settings.API_V1_STR}/orders", tags=["orders"])

@app.on_event("startup")
async def startup_db_client():
    await get_database()

@app.on_event("shutdown")
async def shutdown_db_client():
    pass  # MongoDB client will be closed automatically

@app.get("/")
async def root():
    return {"message": "Welcome to the Dropshipping Platform API"} 