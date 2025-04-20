import api from './api';

const analyticsService = {
    // Sales Analytics
    getSalesAnalytics: (startDate, endDate) => 
        api.get('/analytics/sales', { params: { start_date: startDate, end_date: endDate } }),
    generateSalesAnalytics: (startDate, endDate) => 
        api.post('/analytics/sales/generate', null, { params: { start_date: startDate, end_date: endDate } }),

    // Product Analytics
    getProductAnalytics: (productId) => 
        api.get(`/analytics/products/${productId}`),
    generateProductAnalytics: (productId) => 
        api.post(`/analytics/products/${productId}/generate`),

    // Customer Analytics
    getCustomerAnalytics: (customerId) => 
        api.get(`/analytics/customers/${customerId}`),
    generateCustomerAnalytics: (customerId) => 
        api.post(`/analytics/customers/${customerId}/generate`),

    // Supplier Analytics
    getSupplierAnalytics: (supplierId) => 
        api.get(`/analytics/suppliers/${supplierId}`),
    generateSupplierAnalytics: (supplierId) => 
        api.post(`/analytics/suppliers/${supplierId}/generate`),

    // Financial Reports
    getFinancialReports: (startDate, endDate) => 
        api.get('/analytics/financial', { params: { start_date: startDate, end_date: endDate } }),
    generateFinancialReport: (startDate, endDate) => 
        api.post('/analytics/financial/generate', null, { params: { start_date: startDate, end_date: endDate } })
};

export default analyticsService; 