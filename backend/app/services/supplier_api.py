from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import aiohttp
from app.models import Product, Supplier
from app.core.config import settings
from datetime import datetime

class SupplierAPI(ABC):
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = self.get_base_url()
        self.session = None

    @abstractmethod
    def get_base_url(self) -> str:
        """Return the base URL for the supplier's API"""
        pass

    @abstractmethod
    async def authenticate(self) -> Dict:
        """Authenticate with the supplier's API"""
        pass

    @abstractmethod
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Get a single product from the supplier"""
        pass

    @abstractmethod
    async def search_products(self, query: str, limit: int = 10) -> List[Product]:
        """Search for products from the supplier"""
        pass

    @abstractmethod
    async def get_product_price(self, product_id: str) -> float:
        """Get the current price of a product"""
        pass

    @abstractmethod
    async def get_product_stock(self, product_id: str) -> int:
        """Get the current stock level of a product"""
        pass

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def search_products(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        raise NotImplementedError

    async def get_product_details(self, product_id: str) -> Dict:
        raise NotImplementedError

    async def place_order(self, product_id: str, quantity: int, shipping_address: Dict) -> Dict:
        raise NotImplementedError

class AliExpressAPI(SupplierAPI):
    def __init__(self, api_key: str, api_secret: str):
        super().__init__(api_key, api_secret)
        self.base_url = "https://api.aliexpress.com/v2"
        self.affiliate_id = settings.ALIEXPRESS_AFFILIATE_ID

    async def search_products(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        params = {
            "keywords": query,
            "pageSize": 50,
            "pageNo": 1,
            "sort": "price_asc",
            "appKey": self.api_key,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if filters:
            params.update(filters)

        async with self.session.get(f"{self.base_url}/product/search", params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._transform_search_results(data)
            else:
                raise Exception(f"Failed to search products: {response.status}")

    async def get_product_details(self, product_id: str) -> Dict:
        params = {
            "productId": product_id,
            "appKey": self.api_key,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

        async with self.session.get(f"{self.base_url}/product/get", params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._transform_product_details(data)
            else:
                raise Exception(f"Failed to get product details: {response.status}")

    async def get_product_price(self, product_id: str) -> float:
        details = await self.get_product_details(product_id)
        return float(details.get("price", 0))

    async def get_product_stock(self, product_id: str) -> int:
        details = await self.get_product_details(product_id)
        return int(details.get("stock", 0))

    async def place_order(self, product_id: str, quantity: int, shipping_address: Dict) -> Dict:
        params = {
            "productId": product_id,
            "quantity": quantity,
            "shippingAddress": shipping_address,
            "appKey": self.api_key,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

        async with self.session.post(f"{self.base_url}/order/create", json=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._transform_order_response(data)
            else:
                raise Exception(f"Failed to place order: {response.status}")

    def _transform_search_results(self, data: Dict) -> List[Dict]:
        products = []
        for item in data.get("products", []):
            products.append({
                "id": item.get("productId"),
                "title": item.get("productTitle"),
                "price": float(item.get("salePrice", 0)),
                "stock": int(item.get("stock", 0)),
                "image_url": item.get("imageUrl"),
                "supplier_url": item.get("productUrl"),
                "supplier": "AliExpress"
            })
        return products

    def _transform_product_details(self, data: Dict) -> Dict:
        return {
            "id": data.get("productId"),
            "title": data.get("productTitle"),
            "description": data.get("description"),
            "price": float(data.get("salePrice", 0)),
            "stock": int(data.get("stock", 0)),
            "images": data.get("imageUrls", []),
            "specifications": data.get("specifications", {}),
            "shipping_info": data.get("shippingInfo", {}),
            "supplier": "AliExpress"
        }

    def _transform_order_response(self, data: Dict) -> Dict:
        return {
            "order_id": data.get("orderId"),
            "status": data.get("status"),
            "tracking_number": data.get("trackingNumber"),
            "estimated_delivery": data.get("estimatedDeliveryDate"),
            "total_amount": float(data.get("totalAmount", 0))
        }

class AmazonAPI(SupplierAPI):
    def __init__(self, api_key: str, api_secret: str, marketplace: str = "US"):
        super().__init__(api_key, api_secret)
        self.base_url = f"https://sellingpartnerapi-na.amazon.com"
        self.marketplace = marketplace

    async def search_products(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        params = {
            "Keywords": query,
            "MarketplaceId": self._get_marketplace_id(),
            "ItemCondition": "New"
        }
        
        if filters:
            params.update(filters)

        headers = self._get_auth_headers("GET", "/catalog/2022-04-01/items")
        
        async with self.session.get(f"{self.base_url}/catalog/2022-04-01/items", 
                                  params=params, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return self._transform_search_results(data)
            else:
                raise Exception(f"Failed to search products: {response.status}")

    async def get_product_details(self, product_id: str) -> Dict:
        headers = self._get_auth_headers("GET", f"/catalog/2022-04-01/items/{product_id}")
        
        async with self.session.get(f"{self.base_url}/catalog/2022-04-01/items/{product_id}", 
                                  headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return self._transform_product_details(data)
            else:
                raise Exception(f"Failed to get product details: {response.status}")

    async def get_product_price(self, product_id: str) -> float:
        details = await self.get_product_details(product_id)
        return float(details.get("price", 0))

    async def get_product_stock(self, product_id: str) -> int:
        details = await self.get_product_details(product_id)
        return int(details.get("stock", 0))

    async def place_order(self, product_id: str, quantity: int, shipping_address: Dict) -> Dict:
        order_data = {
            "productId": product_id,
            "quantity": quantity,
            "shippingAddress": shipping_address,
            "marketplaceId": self._get_marketplace_id()
        }

        headers = self._get_auth_headers("POST", "/orders/v0/orders")
        
        async with self.session.post(f"{self.base_url}/orders/v0/orders", 
                                   json=order_data, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return self._transform_order_response(data)
            else:
                raise Exception(f"Failed to place order: {response.status}")

    def _get_marketplace_id(self) -> str:
        marketplace_ids = {
            "US": "ATVPDKIKX0DER",
            "CA": "A2EUQ1WTGCTBG2",
            "UK": "A1F83G8C2ARO7P",
            "DE": "A1PA6795UKMFR9",
            "FR": "A13V1IB3VIYZZH",
            "IT": "APJ6JRA9NG5V4",
            "ES": "A1RKKUPIHCS9HS",
            "JP": "A1VC38T7YXB528"
        }
        return marketplace_ids.get(self.marketplace, marketplace_ids["US"])

    def _get_auth_headers(self, method: str, path: str) -> Dict:
        # Implement Amazon SP-API authentication
        # This is a simplified version - actual implementation would require
        # AWS Signature Version 4 signing process
        return {
            "x-amz-access-token": self.api_key,
            "x-amz-date": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            "host": "sellingpartnerapi-na.amazon.com"
        }

    def _transform_search_results(self, data: Dict) -> List[Dict]:
        products = []
        for item in data.get("items", []):
            products.append({
                "id": item.get("asin"),
                "title": item.get("attributes", {}).get("title", {}).get("value"),
                "price": float(item.get("attributes", {}).get("list_price", {}).get("value", 0)),
                "stock": int(item.get("attributes", {}).get("quantity", {}).get("value", 0)),
                "image_url": item.get("attributes", {}).get("main_image", {}).get("value"),
                "supplier_url": f"https://www.amazon.com/dp/{item.get('asin')}",
                "supplier": "Amazon"
            })
        return products

    def _transform_product_details(self, data: Dict) -> Dict:
        return {
            "id": data.get("asin"),
            "title": data.get("attributes", {}).get("title", {}).get("value"),
            "description": data.get("attributes", {}).get("product_description", {}).get("value"),
            "price": float(data.get("attributes", {}).get("list_price", {}).get("value", 0)),
            "stock": int(data.get("attributes", {}).get("quantity", {}).get("value", 0)),
            "images": [data.get("attributes", {}).get("main_image", {}).get("value")],
            "specifications": data.get("attributes", {}).get("product_specifications", {}),
            "shipping_info": data.get("attributes", {}).get("shipping", {}),
            "supplier": "Amazon"
        }

    def _transform_order_response(self, data: Dict) -> Dict:
        return {
            "order_id": data.get("orderId"),
            "status": data.get("orderStatus"),
            "tracking_number": data.get("trackingNumber"),
            "estimated_delivery": data.get("estimatedDeliveryDate"),
            "total_amount": float(data.get("orderTotal", {}).get("amount", 0))
        }

class SupplierAPIFactory:
    @staticmethod
    def create_api(supplier: Supplier) -> SupplierAPI:
        if supplier.name.lower() == "aliexpress":
            return AliExpressAPI(supplier.api_key, supplier.api_secret)
        elif supplier.name.lower() == "amazon":
            return AmazonAPI(supplier.api_key, supplier.api_secret)
        else:
            raise ValueError(f"Unsupported supplier: {supplier.name}") 