import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import joblib
import os
from typing import Dict, List, Optional
from app.db import get_database
from app.config import settings

class MLService:
    def __init__(self):
        self.db = get_database()
        self.orders_collection = self.db["orders"]
        self.products_collection = self.db["products"]
        self.models_dir = "ml_models"
        os.makedirs(self.models_dir, exist_ok=True)
        
    async def prepare_price_data(self) -> pd.DataFrame:
        """Prepare data for price optimization model"""
        products = await self.products_collection.find({}).to_list(length=None)
        orders = await self.orders_collection.find({}).to_list(length=None)
        
        # Convert to pandas DataFrames
        products_df = pd.DataFrame(products)
        orders_df = pd.DataFrame(orders)
        
        # Calculate features
        features = []
        for product in products:
            product_orders = orders_df[orders_df['product_id'] == product['_id']]
            
            # Sales metrics
            total_sales = len(product_orders)
            avg_price = product_orders['price'].mean()
            total_revenue = product_orders['price'].sum()
            
            # Time-based features
            current_date = datetime.now()
            last_month_sales = len(product_orders[product_orders['created_at'] > current_date - timedelta(days=30)])
            
            # Competition features
            similar_products = products_df[
                (products_df['category'] == product['category']) & 
                (products_df['_id'] != product['_id'])
            ]
            avg_competitor_price = similar_products['price'].mean()
            
            features.append({
                'product_id': product['_id'],
                'category': product['category'],
                'total_sales': total_sales,
                'avg_price': avg_price,
                'total_revenue': total_revenue,
                'last_month_sales': last_month_sales,
                'avg_competitor_price': avg_competitor_price,
                'current_price': product['price']
            })
            
        return pd.DataFrame(features)
    
    async def train_price_optimization_model(self):
        """Train model for price optimization"""
        data = await self.prepare_price_data()
        
        # Prepare features and target
        X = data[['total_sales', 'last_month_sales', 'avg_competitor_price', 'current_price']]
        y = data['total_revenue']
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Save model and scaler
        joblib.dump(model, os.path.join(self.models_dir, 'price_optimization_model.joblib'))
        joblib.dump(scaler, os.path.join(self.models_dir, 'price_scaler.joblib'))
        
        return model.score(X_test, y_test)
    
    async def optimize_price(self, product_id: str) -> Dict:
        """Get optimized price for a product"""
        try:
            # Load model and scaler
            model = joblib.load(os.path.join(self.models_dir, 'price_optimization_model.joblib'))
            scaler = joblib.load(os.path.join(self.models_dir, 'price_scaler.joblib'))
            
            # Get product data
            product = await self.products_collection.find_one({"_id": product_id})
            if not product:
                return {"error": "Product not found"}
            
            # Prepare features
            data = await self.prepare_price_data()
            product_data = data[data['product_id'] == product_id].iloc[0]
            
            # Generate price suggestions
            current_price = product_data['current_price']
            price_range = np.linspace(current_price * 0.8, current_price * 1.2, 20)
            
            predictions = []
            for price in price_range:
                features = np.array([[
                    product_data['total_sales'],
                    product_data['last_month_sales'],
                    product_data['avg_competitor_price'],
                    price
                ]])
                features_scaled = scaler.transform(features)
                predicted_revenue = model.predict(features_scaled)[0]
                predictions.append({
                    'price': price,
                    'predicted_revenue': predicted_revenue,
                    'profit_margin': (price - product['cost_price']) / price if product['cost_price'] else None
                })
            
            # Find optimal price
            optimal_price = max(predictions, key=lambda x: x['predicted_revenue'])
            
            return {
                'current_price': current_price,
                'optimal_price': optimal_price['price'],
                'predicted_revenue_increase': (optimal_price['predicted_revenue'] - product_data['total_revenue']) / product_data['total_revenue'] * 100,
                'profit_margin': optimal_price['profit_margin'],
                'price_suggestions': predictions
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def prepare_demand_data(self) -> pd.DataFrame:
        """Prepare data for demand forecasting"""
        orders = await self.orders_collection.find({}).to_list(length=None)
        products = await self.products_collection.find({}).to_list(length=None)
        
        # Convert to pandas DataFrame
        orders_df = pd.DataFrame(orders)
        products_df = pd.DataFrame(products)
        
        # Create time series data
        orders_df['date'] = pd.to_datetime(orders_df['created_at'])
        orders_df.set_index('date', inplace=True)
        
        # Aggregate daily sales
        daily_sales = orders_df.groupby([pd.Grouper(freq='D'), 'product_id']).size().reset_index()
        daily_sales.columns = ['date', 'product_id', 'sales']
        
        # Add product features
        daily_sales = daily_sales.merge(products_df[['_id', 'category', 'price']], 
                                      left_on='product_id', right_on='_id')
        
        # Add time features
        daily_sales['day_of_week'] = daily_sales['date'].dt.dayofweek
        daily_sales['month'] = daily_sales['date'].dt.month
        daily_sales['year'] = daily_sales['date'].dt.year
        
        return daily_sales
    
    async def train_demand_forecasting_model(self):
        """Train model for demand forecasting"""
        data = await self.prepare_demand_data()
        
        # Prepare features and target
        X = data[['day_of_week', 'month', 'year', 'price', 'category']]
        X = pd.get_dummies(X, columns=['category'])
        y = data['sales']
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Save model and scaler
        joblib.dump(model, os.path.join(self.models_dir, 'demand_forecasting_model.joblib'))
        joblib.dump(scaler, os.path.join(self.models_dir, 'demand_scaler.joblib'))
        
        return model.score(X_test, y_test)
    
    async def forecast_demand(self, product_id: str, days: int = 30) -> Dict:
        """Forecast demand for a product"""
        try:
            # Load model and scaler
            model = joblib.load(os.path.join(self.models_dir, 'demand_forecasting_model.joblib'))
            scaler = joblib.load(os.path.join(self.models_dir, 'demand_scaler.joblib'))
            
            # Get product data
            product = await self.products_collection.find_one({"_id": product_id})
            if not product:
                return {"error": "Product not found"}
            
            # Prepare future dates
            future_dates = pd.date_range(start=datetime.now(), periods=days, freq='D')
            
            # Create features for future dates
            features = []
            for date in future_dates:
                features.append({
                    'day_of_week': date.dayofweek,
                    'month': date.month,
                    'year': date.year,
                    'price': product['price'],
                    'category': product['category']
                })
            
            features_df = pd.DataFrame(features)
            features_df = pd.get_dummies(features_df, columns=['category'])
            
            # Scale features
            features_scaled = scaler.transform(features_df)
            
            # Make predictions
            predictions = model.predict(features_scaled)
            
            # Format results
            forecast = []
            for i, date in enumerate(future_dates):
                forecast.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'predicted_sales': int(predictions[i]),
                    'confidence_interval': {
                        'lower': int(predictions[i] * 0.8),
                        'upper': int(predictions[i] * 1.2)
                    }
                })
            
            return {
                'product_id': product_id,
                'forecast': forecast,
                'total_predicted_sales': int(sum(predictions)),
                'average_daily_sales': int(np.mean(predictions))
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def segment_customers(self) -> Dict:
        """Segment customers based on their behavior"""
        orders = await self.orders_collection.find({}).to_list(length=None)
        users = await self.db["users"].find({}).to_list(length=None)
        
        # Convert to pandas DataFrames
        orders_df = pd.DataFrame(orders)
        users_df = pd.DataFrame(users)
        
        # Calculate customer metrics
        customer_metrics = []
        for user in users:
            user_orders = orders_df[orders_df['user_id'] == user['_id']]
            
            metrics = {
                'user_id': user['_id'],
                'total_orders': len(user_orders),
                'total_spent': user_orders['total'].sum(),
                'avg_order_value': user_orders['total'].mean(),
                'days_since_last_order': (datetime.now() - pd.to_datetime(user_orders['created_at'].max())).days if len(user_orders) > 0 else 999,
                'unique_products': len(user_orders['items'].explode().unique()),
                'favorite_category': user_orders['items'].explode()['category'].mode()[0] if len(user_orders) > 0 else None
            }
            customer_metrics.append(metrics)
        
        metrics_df = pd.DataFrame(customer_metrics)
        
        # Prepare features for clustering
        X = metrics_df[['total_orders', 'total_spent', 'avg_order_value', 'days_since_last_order', 'unique_products']]
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Perform clustering
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=4, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Add cluster labels
        metrics_df['segment'] = clusters
        
        # Define segment names based on characteristics
        segment_names = {
            0: 'High-Value Loyal',
            1: 'At-Risk',
            2: 'New Customers',
            3: 'Occasional Shoppers'
        }
        
        # Format results
        segments = {}
        for segment_id, segment_name in segment_names.items():
            segment_data = metrics_df[metrics_df['segment'] == segment_id]
            segments[segment_name] = {
                'count': len(segment_data),
                'avg_total_orders': segment_data['total_orders'].mean(),
                'avg_total_spent': segment_data['total_spent'].mean(),
                'avg_order_value': segment_data['avg_order_value'].mean(),
                'customer_ids': segment_data['user_id'].tolist()
            }
        
        return segments
    
    async def get_product_recommendations(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get personalized product recommendations for a user"""
        try:
            # Get user's order history
            orders = await self.orders_collection.find({"user_id": user_id}).to_list(length=None)
            if not orders:
                return []
            
            # Get all products
            products = await self.products_collection.find({}).to_list(length=None)
            
            # Convert to pandas DataFrames
            orders_df = pd.DataFrame(orders)
            products_df = pd.DataFrame(products)
            
            # Get user's favorite categories
            user_categories = orders_df['items'].explode()['category'].value_counts().head(3).index.tolist()
            
            # Get similar products
            similar_products = products_df[
                (products_df['category'].isin(user_categories)) &
                (~products_df['_id'].isin(orders_df['items'].explode()['product_id'].unique()))
            ]
            
            # Calculate recommendation scores
            recommendations = []
            for _, product in similar_products.iterrows():
                score = 0
                
                # Category match
                if product['category'] in user_categories:
                    score += 2
                
                # Price range match
                user_avg_price = orders_df['items'].explode()['price'].mean()
                if abs(product['price'] - user_avg_price) / user_avg_price < 0.2:
                    score += 1
                
                # Popularity
                product_orders = len(orders_df[orders_df['items'].apply(lambda x: any(item['product_id'] == product['_id'] for item in x))])
                score += product_orders * 0.5
                
                recommendations.append({
                    'product_id': product['_id'],
                    'name': product['name'],
                    'category': product['category'],
                    'price': product['price'],
                    'score': score
                })
            
            # Sort by score and return top recommendations
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            return [] 