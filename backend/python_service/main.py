from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import requests
from datetime import datetime

# Load environment variables
load_dotenv()

app = FastAPI()

# MongoDB connection
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.dropshipping

# Supplier product synchronization
@app.post("/api/supplier/sync")
async def sync_supplier_products(supplier_id: str):
    try:
        # Get supplier details
        supplier = db.suppliers.find_one({"_id": supplier_id})
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")

        # Fetch products from supplier API
        response = requests.get(supplier["api_url"])
        products = response.json()

        # Update products in database
        for product in products:
            db.products.update_one(
                {"supplier_id": supplier_id, "sku": product["sku"]},
                {"$set": {
                    "name": product["name"],
                    "price": product["price"],
                    "stock": product["stock"],
                    "last_updated": datetime.utcnow()
                }},
                upsert=True
            )

        return {"message": "Products synchronized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Order fulfillment
@app.post("/api/order/fulfill")
async def fulfill_order(order_id: str):
    try:
        # Get order details
        order = db.orders.find_one({"_id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Get product details
        product = db.products.find_one({"_id": order["product_id"]})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Get supplier details
        supplier = db.suppliers.find_one({"_id": product["supplier_id"]})
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")

        # Place order with supplier
        response = requests.post(
            f"{supplier['api_url']}/orders",
            json={
                "product_id": product["supplier_product_id"],
                "quantity": order["quantity"],
                "shipping_address": order["shipping_address"]
            }
        )

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to place order with supplier")

        # Update order status
        db.orders.update_one(
            {"_id": order_id},
            {"$set": {
                "status": "fulfilled",
                "fulfillment_date": datetime.utcnow(),
                "tracking_number": response.json()["tracking_number"]
            }}
        )

        return {"message": "Order fulfilled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Price monitoring
@app.get("/api/price/monitor")
async def monitor_prices():
    try:
        # Get all products
        products = list(db.products.find())
        
        price_changes = []
        for product in products:
            # Get supplier price
            supplier = db.suppliers.find_one({"_id": product["supplier_id"]})
            response = requests.get(f"{supplier['api_url']}/products/{product['supplier_product_id']}")
            current_price = response.json()["price"]
            
            # Check for price changes
            if current_price != product["price"]:
                price_changes.append({
                    "product_id": str(product["_id"]),
                    "old_price": product["price"],
                    "new_price": current_price,
                    "change_percentage": ((current_price - product["price"]) / product["price"]) * 100
                })
                
                # Update product price
                db.products.update_one(
                    {"_id": product["_id"]},
                    {"$set": {"price": current_price}}
                )
        
        return {"price_changes": price_changes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stock level monitoring
@app.get("/api/stock/monitor")
async def monitor_stock():
    try:
        # Get all products
        products = list(db.products.find())
        
        stock_changes = []
        for product in products:
            # Get supplier stock
            supplier = db.suppliers.find_one({"_id": product["supplier_id"]})
            response = requests.get(f"{supplier['api_url']}/products/{product['supplier_product_id']}")
            current_stock = response.json()["stock"]
            
            # Check for stock changes
            if current_stock != product["stock"]:
                stock_changes.append({
                    "product_id": str(product["_id"]),
                    "old_stock": product["stock"],
                    "new_stock": current_stock
                })
                
                # Update product stock
                db.products.update_one(
                    {"_id": product["_id"]},
                    {"$set": {"stock": current_stock}}
                )
        
        return {"stock_changes": stock_changes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 