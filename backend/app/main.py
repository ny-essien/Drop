from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, products, cart, orders, admin, supplier_sync, support, faq, knowledge_base, analytics, product_sourcing
from app.core.config import settings

app = FastAPI(
    title="Dropshipping Platform API",
    description="API for the Dropshipping Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(supplier_sync.router, prefix="/api/supplier-sync", tags=["Supplier Sync"])
app.include_router(support.router, prefix="/api/support", tags=["Support"])
app.include_router(faq.router, prefix="/api/faq", tags=["FAQ"])
app.include_router(knowledge_base.router, prefix="/api/knowledge-base", tags=["Knowledge Base"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(product_sourcing.router, prefix="/api/product-sourcing", tags=["Product Sourcing"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Dropshipping Platform API"} 