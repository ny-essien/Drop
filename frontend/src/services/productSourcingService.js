import api from './api';

const productSourcingService = {
    // Search suppliers
    searchSuppliers: async (query, filters = {}) => {
        try {
            const response = await api.get('/api/suppliers/search', {
                params: { query, ...filters }
            });
            return response.data;
        } catch (error) {
            console.error('Error searching suppliers:', error);
            throw error;
        }
    },

    // Compare prices
    comparePrices: async (productId) => {
        try {
            const response = await api.get(`/api/products/${productId}/price-comparison`);
            return response.data;
        } catch (error) {
            console.error('Error comparing prices:', error);
            throw error;
        }
    },

    // Bulk import products
    bulkImportProducts: async (supplierId, category, limit = 100) => {
        try {
            const response = await api.post('/api/products/bulk-import', {
                supplierId,
                category,
                limit
            });
            return response.data;
        } catch (error) {
            console.error('Error bulk importing products:', error);
            throw error;
        }
    },

    // Get product variations
    getProductVariations: async (productId) => {
        try {
            const response = await api.get(`/api/products/${productId}/variations`);
            return response.data;
        } catch (error) {
            console.error('Error getting product variations:', error);
            throw error;
        }
    },

    // Create product variation
    createProductVariation: async (productId, variationData) => {
        try {
            const response = await api.post(`/api/products/${productId}/variations`, variationData);
            return response.data;
        } catch (error) {
            console.error('Error creating product variation:', error);
            throw error;
        }
    },

    // Advanced product search
    searchProducts: async (query, filters = {}) => {
        try {
            const response = await api.get('/api/products/search', {
                params: { query, ...filters }
            });
            return response.data;
        } catch (error) {
            console.error('Error searching products:', error);
            throw error;
        }
    }
};

export default productSourcingService; 