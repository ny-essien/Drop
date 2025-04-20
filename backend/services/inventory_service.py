from typing import Dict, Any
from app.models import Product, InventoryTransaction
from datetime import datetime

class InventoryService:
    async def reserve_stock(self, product_id: str, quantity: int) -> Dict[str, Any]:
        """Reserve stock for an order"""
        product = await Product.get(product_id)
        if not product:
            raise ValueError("Product not found")

        if product.stock < quantity:
            raise ValueError("Insufficient stock")

        # Create inventory transaction
        transaction = InventoryTransaction(
            product_id=product_id,
            quantity=-quantity,  # Negative for outgoing
            type="reservation",
            status="pending",
            created_at=datetime.utcnow()
        )
        await transaction.save()

        # Update product stock
        product.stock -= quantity
        product.reserved_stock += quantity
        await product.save()

        return {
            "status": "success",
            "product_id": product_id,
            "reserved_quantity": quantity,
            "remaining_stock": product.stock
        }

    async def release_stock(self, product_id: str, quantity: int) -> Dict[str, Any]:
        """Release reserved stock"""
        product = await Product.get(product_id)
        if not product:
            raise ValueError("Product not found")

        if product.reserved_stock < quantity:
            raise ValueError("Insufficient reserved stock")

        # Create inventory transaction
        transaction = InventoryTransaction(
            product_id=product_id,
            quantity=quantity,  # Positive for incoming
            type="release",
            status="completed",
            created_at=datetime.utcnow()
        )
        await transaction.save()

        # Update product stock
        product.stock += quantity
        product.reserved_stock -= quantity
        await product.save()

        return {
            "status": "success",
            "product_id": product_id,
            "released_quantity": quantity,
            "current_stock": product.stock
        }

    async def update_stock(self, product_id: str, quantity: int, type: str = "adjustment") -> Dict[str, Any]:
        """Update stock levels (for receiving new inventory)"""
        product = await Product.get(product_id)
        if not product:
            raise ValueError("Product not found")

        # Create inventory transaction
        transaction = InventoryTransaction(
            product_id=product_id,
            quantity=quantity,
            type=type,
            status="completed",
            created_at=datetime.utcnow()
        )
        await transaction.save()

        # Update product stock
        product.stock += quantity
        await product.save()

        return {
            "status": "success",
            "product_id": product_id,
            "new_quantity": quantity,
            "total_stock": product.stock
        }

    async def get_stock_levels(self, product_id: str = None) -> Dict[str, Any]:
        """Get current stock levels"""
        if product_id:
            product = await Product.get(product_id)
            if not product:
                raise ValueError("Product not found")
            
            return {
                "product_id": product_id,
                "available_stock": product.stock,
                "reserved_stock": product.reserved_stock,
                "total_stock": product.stock + product.reserved_stock
            }
        else:
            # Get all products with low stock
            low_stock_products = await Product.find(
                {"stock": {"$lt": 10}}  # Assuming 10 is the low stock threshold
            ).to_list(length=None)
            
            return {
                "low_stock_products": [
                    {
                        "product_id": p.id,
                        "name": p.name,
                        "available_stock": p.stock,
                        "reserved_stock": p.reserved_stock
                    }
                    for p in low_stock_products
                ]
            }

    async def get_inventory_history(self, product_id: str, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Get inventory transaction history"""
        query = {"product_id": product_id}
        
        if start_date:
            query["created_at"] = {"$gte": start_date}
        if end_date:
            query["created_at"] = {"$lte": end_date}
        
        transactions = await InventoryTransaction.find(query).sort("created_at", -1).to_list(length=None)
        
        return {
            "product_id": product_id,
            "transactions": [
                {
                    "id": t.id,
                    "type": t.type,
                    "quantity": t.quantity,
                    "status": t.status,
                    "created_at": t.created_at
                }
                for t in transactions
            ]
        } 