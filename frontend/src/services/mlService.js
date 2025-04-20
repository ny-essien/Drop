import api from './api';

const mlService = {
    // Price Optimization
    trainPriceOptimizationModel: async () => {
        try {
            const response = await api.post('/api/ml/train/price-optimization');
            return response.data;
        } catch (error) {
            console.error('Error training price optimization model:', error);
            throw error;
        }
    },

    optimizePrice: async (productId) => {
        try {
            const response = await api.get(`/api/ml/products/${productId}/optimize-price`);
            return response.data;
        } catch (error) {
            console.error('Error optimizing price:', error);
            throw error;
        }
    },

    // Demand Forecasting
    trainDemandForecastingModel: async () => {
        try {
            const response = await api.post('/api/ml/train/demand-forecasting');
            return response.data;
        } catch (error) {
            console.error('Error training demand forecasting model:', error);
            throw error;
        }
    },

    forecastDemand: async (productId, days = 30) => {
        try {
            const response = await api.get(`/api/ml/products/${productId}/forecast`, {
                params: { days }
            });
            return response.data;
        } catch (error) {
            console.error('Error forecasting demand:', error);
            throw error;
        }
    },

    // Customer Segmentation
    getCustomerSegments: async () => {
        try {
            const response = await api.get('/api/ml/customers/segments');
            return response.data;
        } catch (error) {
            console.error('Error getting customer segments:', error);
            throw error;
        }
    },

    // Product Recommendations
    getProductRecommendations: async (userId, limit = 5) => {
        try {
            const response = await api.get(`/api/ml/users/${userId}/recommendations`, {
                params: { limit }
            });
            return response.data;
        } catch (error) {
            console.error('Error getting product recommendations:', error);
            throw error;
        }
    }
};

export default mlService; 