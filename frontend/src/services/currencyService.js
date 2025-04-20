import api from './api';

const currencyService = {
    // Get all currencies
    getAllCurrencies: () => api.get('/currencies'),

    // Get default currency
    getDefaultCurrency: () => api.get('/currencies/default'),

    // Get currency by code
    getCurrencyByCode: (code) => api.get(`/currencies/${code}`),

    // Update exchange rates
    updateExchangeRates: () => api.post('/currencies/update-rates'),

    // Convert amount between currencies
    convertAmount: (amount, fromCurrency, toCurrency) => 
        api.post('/currencies/convert', { amount, fromCurrency, toCurrency }),

    // Set default currency
    setDefaultCurrency: (code) => api.post(`/currencies/${code}/set-default`),

    // Add new currency
    addCurrency: (currencyData) => api.post('/currencies', currencyData),

    // Update currency
    updateCurrency: (code, updateData) => api.put(`/currencies/${code}`, updateData),

    // Delete currency
    deleteCurrency: (code) => api.delete(`/currencies/${code}`),

    // Get user's preferred currency
    getUserCurrency: () => api.get('/currencies/user/preference'),

    // Set user's preferred currency
    setUserCurrency: (currencyCode) => api.post('/currencies/user/preference', { currencyCode }),

    // Subscribe to exchange rate updates
    subscribeToUpdates: (callback) => {
        const eventSource = new EventSource('/api/currencies/updates');
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            callback(data);
        };

        eventSource.onerror = (error) => {
            console.error('EventSource failed:', error);
            eventSource.close();
        };

        return () => eventSource.close();
    },

    // Get historical exchange rates
    getHistoricalRates: (currencyCode, startDate, endDate) =>
        api.get(`/currencies/${currencyCode}/history`, {
            params: { startDate, endDate }
        }),

    // Get exchange rate trends
    getRateTrends: (currencyCode, period = '7d') =>
        api.get(`/currencies/${currencyCode}/trends`, {
            params: { period }
        })
};

export default currencyService; 