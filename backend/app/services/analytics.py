from typing import Dict, List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models import (
    SalesAnalytics,
    ProductAnalytics,
    CustomerAnalytics,
    SupplierAnalytics,
    FinancialReport
)

class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.sales_collection = db.sales_analytics
        self.product_collection = db.product_analytics
        self.customer_collection = db.customer_analytics
        self.supplier_collection = db.supplier_analytics
        self.financial_collection = db.financial_reports

    async def generate_sales_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> SalesAnalytics:
        # Get orders within date range
        orders = await self.db.orders.find({
            "created_at": {"$gte": start_date, "$lte": end_date}
        }).to_list(length=None)

        total_sales = sum(order["total_amount"] for order in orders)
        total_orders = len(orders)
        average_order_value = total_sales / total_orders if total_orders > 0 else 0

        # Get product sales data
        product_sales = {}
        category_sales = {}
        supplier_sales = {}
        total_products_sold = 0

        for order in orders:
            for item in order["items"]:
                product_id = str(item["product_id"])
                quantity = item["quantity"]
                price = item["price"]
                category = item.get("category", "uncategorized")
                supplier_id = str(item.get("supplier_id", "unknown"))

                product_sales[product_id] = product_sales.get(product_id, 0) + (quantity * price)
                category_sales[category] = category_sales.get(category, 0) + (quantity * price)
                supplier_sales[supplier_id] = supplier_sales.get(supplier_id, 0) + (quantity * price)
                total_products_sold += quantity

        # Get top selling products
        top_products = sorted(
            product_sales.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        analytics = SalesAnalytics(
            date=end_date,
            total_sales=total_sales,
            total_orders=total_orders,
            average_order_value=average_order_value,
            total_products_sold=total_products_sold,
            top_selling_products=[
                {"product_id": pid, "total_sales": sales}
                for pid, sales in top_products
            ],
            sales_by_category=category_sales,
            sales_by_supplier=supplier_sales
        )

        await self.sales_collection.insert_one(analytics.dict())
        return analytics

    async def generate_product_analytics(self, product_id: str) -> ProductAnalytics:
        # Get product orders
        orders = await self.db.orders.find({
            "items.product_id": ObjectId(product_id)
        }).to_list(length=None)

        total_sales = 0
        total_units_sold = 0
        for order in orders:
            for item in order["items"]:
                if str(item["product_id"]) == product_id:
                    total_sales += item["quantity"] * item["price"]
                    total_units_sold += item["quantity"]

        # Get product reviews
        reviews = await self.db.reviews.find({
            "product_id": ObjectId(product_id)
        }).to_list(length=None)

        total_reviews = len(reviews)
        average_rating = sum(review["rating"] for review in reviews) / total_reviews if total_reviews > 0 else 0

        # Get product views
        views = await self.db.product_views.find({
            "product_id": ObjectId(product_id)
        }).count()

        conversion_rate = total_units_sold / views if views > 0 else 0

        # Get returns
        returns = await self.db.returns.find({
            "product_id": ObjectId(product_id)
        }).count()

        return_rate = returns / total_units_sold if total_units_sold > 0 else 0

        # Get stock data
        product = await self.db.products.find_one({"_id": ObjectId(product_id)})
        stock_turnover = total_units_sold / product["stock"] if product["stock"] > 0 else 0

        # Calculate profit margin
        cost = product.get("cost_price", 0)
        profit_margin = (total_sales - (cost * total_units_sold)) / total_sales if total_sales > 0 else 0

        analytics = ProductAnalytics(
            product_id=product_id,
            total_sales=total_sales,
            total_units_sold=total_units_sold,
            average_rating=average_rating,
            total_reviews=total_reviews,
            conversion_rate=conversion_rate,
            return_rate=return_rate,
            stock_turnover=stock_turnover,
            profit_margin=profit_margin,
            last_updated=datetime.utcnow()
        )

        await self.product_collection.insert_one(analytics.dict())
        return analytics

    async def generate_customer_analytics(self, customer_id: str) -> CustomerAnalytics:
        # Get customer orders
        orders = await self.db.orders.find({
            "user_id": ObjectId(customer_id)
        }).to_list(length=None)

        total_spent = sum(order["total_amount"] for order in orders)
        total_orders = len(orders)
        average_order_value = total_spent / total_orders if total_orders > 0 else 0

        # Get last purchase date
        last_purchase = max(order["created_at"] for order in orders) if orders else None

        # Get favorite categories
        category_counts = {}
        for order in orders:
            for item in order["items"]:
                category = item.get("category", "uncategorized")
                category_counts[category] = category_counts.get(category, 0) + 1

        favorite_categories = sorted(
            category_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        favorite_categories = [cat for cat, _ in favorite_categories]

        # Calculate purchase frequency
        if orders:
            first_purchase = min(order["created_at"] for order in orders)
            days_since_first_purchase = (datetime.utcnow() - first_purchase).days
            purchase_frequency = total_orders / (days_since_first_purchase / 30)  # orders per month
        else:
            purchase_frequency = 0

        # Calculate customer lifetime value
        average_customer_lifespan = 365  # days
        customer_lifetime_value = total_spent * (average_customer_lifespan / 30)  # monthly value

        # Calculate churn risk
        days_since_last_purchase = (datetime.utcnow() - last_purchase).days if last_purchase else 0
        churn_risk = min(1, days_since_last_purchase / 90)  # risk increases after 90 days

        analytics = CustomerAnalytics(
            customer_id=customer_id,
            total_spent=total_spent,
            total_orders=total_orders,
            average_order_value=average_order_value,
            last_purchase_date=last_purchase,
            favorite_categories=favorite_categories,
            purchase_frequency=purchase_frequency,
            customer_lifetime_value=customer_lifetime_value,
            churn_risk=churn_risk
        )

        await self.customer_collection.insert_one(analytics.dict())
        return analytics

    async def generate_supplier_analytics(self, supplier_id: str) -> SupplierAnalytics:
        # Get supplier products
        products = await self.db.products.find({
            "supplier_id": ObjectId(supplier_id)
        }).to_list(length=None)

        # Get product orders
        total_sales = 0
        total_products_sold = 0
        for product in products:
            orders = await self.db.orders.find({
                "items.product_id": product["_id"]
            }).to_list(length=None)

            for order in orders:
                for item in order["items"]:
                    if str(item["product_id"]) == str(product["_id"]):
                        total_sales += item["quantity"] * item["price"]
                        total_products_sold += item["quantity"]

        # Get supplier reviews
        reviews = await self.db.supplier_reviews.find({
            "supplier_id": ObjectId(supplier_id)
        }).to_list(length=None)

        total_reviews = len(reviews)
        average_rating = sum(review["rating"] for review in reviews) / total_reviews if total_reviews > 0 else 0

        # Get delivery performance
        deliveries = await self.db.deliveries.find({
            "supplier_id": ObjectId(supplier_id)
        }).to_list(length=None)

        on_time_deliveries = sum(1 for d in deliveries if d["delivered_on_time"])
        on_time_delivery_rate = on_time_deliveries / len(deliveries) if deliveries else 0

        # Get returns
        returns = await self.db.returns.find({
            "supplier_id": ObjectId(supplier_id)
        }).count()

        return_rate = returns / total_products_sold if total_products_sold > 0 else 0

        # Calculate profit margin
        total_cost = sum(p["cost_price"] for p in products)
        profit_margin = (total_sales - total_cost) / total_sales if total_sales > 0 else 0

        # Calculate stock availability
        total_stock = sum(p["stock"] for p in products)
        total_demand = sum(p["demand"] for p in products)
        stock_availability = total_stock / total_demand if total_demand > 0 else 0

        analytics = SupplierAnalytics(
            supplier_id=supplier_id,
            total_sales=total_sales,
            total_products_sold=total_products_sold,
            average_rating=average_rating,
            on_time_delivery_rate=on_time_delivery_rate,
            return_rate=return_rate,
            profit_margin=profit_margin,
            stock_availability=stock_availability,
            last_updated=datetime.utcnow()
        )

        await self.supplier_collection.insert_one(analytics.dict())
        return analytics

    async def generate_financial_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> FinancialReport:
        # Get all orders in period
        orders = await self.db.orders.find({
            "created_at": {"$gte": start_date, "$lte": end_date}
        }).to_list(length=None)

        # Calculate revenue
        total_revenue = sum(order["total_amount"] for order in orders)

        # Calculate costs
        total_cost = 0
        for order in orders:
            for item in order["items"]:
                product = await self.db.products.find_one({"_id": item["product_id"]})
                if product:
                    total_cost += item["quantity"] * product["cost_price"]

        # Calculate gross profit
        gross_profit = total_revenue - total_cost

        # Get operating expenses
        expenses = await self.db.expenses.find({
            "date": {"$gte": start_date, "$lte": end_date}
        }).to_list(length=None)

        operating_expenses = sum(expense["amount"] for expense in expenses)

        # Calculate net profit
        net_profit = gross_profit - operating_expenses
        profit_margin = net_profit / total_revenue if total_revenue > 0 else 0

        # Calculate sales by channel
        sales_by_channel = {}
        for order in orders:
            channel = order.get("channel", "direct")
            sales_by_channel[channel] = sales_by_channel.get(channel, 0) + order["total_amount"]

        # Calculate expenses by category
        expenses_by_category = {}
        for expense in expenses:
            category = expense.get("category", "uncategorized")
            expenses_by_category[category] = expenses_by_category.get(category, 0) + expense["amount"]

        # Calculate cash flow
        cash_flow = {
            "inflow": total_revenue,
            "outflow": total_cost + operating_expenses,
            "net": total_revenue - (total_cost + operating_expenses)
        }

        report = FinancialReport(
            period_start=start_date,
            period_end=end_date,
            total_revenue=total_revenue,
            total_cost=total_cost,
            gross_profit=gross_profit,
            operating_expenses=operating_expenses,
            net_profit=net_profit,
            profit_margin=profit_margin,
            sales_by_channel=sales_by_channel,
            expenses_by_category=expenses_by_category,
            cash_flow=cash_flow
        )

        await self.financial_collection.insert_one(report.dict())
        return report

    async def get_sales_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[SalesAnalytics]:
        analytics = await self.sales_collection.find({
            "date": {"$gte": start_date, "$lte": end_date}
        }).to_list(length=None)
        return [SalesAnalytics(**a) for a in analytics]

    async def get_product_analytics(self, product_id: str) -> Optional[ProductAnalytics]:
        analytics = await self.product_collection.find_one({"product_id": product_id})
        return ProductAnalytics(**analytics) if analytics else None

    async def get_customer_analytics(self, customer_id: str) -> Optional[CustomerAnalytics]:
        analytics = await self.customer_collection.find_one({"customer_id": customer_id})
        return CustomerAnalytics(**analytics) if analytics else None

    async def get_supplier_analytics(self, supplier_id: str) -> Optional[SupplierAnalytics]:
        analytics = await self.supplier_collection.find_one({"supplier_id": supplier_id})
        return SupplierAnalytics(**analytics) if analytics else None

    async def get_financial_reports(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[FinancialReport]:
        reports = await self.financial_collection.find({
            "period_start": {"$gte": start_date},
            "period_end": {"$lte": end_date}
        }).to_list(length=None)
        return [FinancialReport(**r) for r in reports] 