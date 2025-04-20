import api from './api';

const shippingService = {
    // Get available carriers for an order
    getAvailableCarriers: async (orderId) => {
        try {
            const response = await api.get(`/api/shipping/orders/${orderId}/carriers`);
            return response.data;
        } catch (error) {
            console.error('Error getting available carriers:', error);
            throw error;
        }
    },

    // Create shipping label
    createShippingLabel: async (orderId, carrierId, serviceLevel) => {
        try {
            const response = await api.post(`/api/shipping/orders/${orderId}/labels`, {
                carrierId,
                serviceLevel
            });
            return response.data;
        } catch (error) {
            console.error('Error creating shipping label:', error);
            throw error;
        }
    },

    // Track shipment
    trackShipment: async (trackingNumber) => {
        try {
            const response = await api.get(`/api/shipping/tracking/${trackingNumber}`);
            return response.data;
        } catch (error) {
            console.error('Error tracking shipment:', error);
            throw error;
        }
    },

    // Get shipping status
    getShippingStatus: async (orderId) => {
        try {
            const response = await api.get(`/api/shipping/orders/${orderId}/status`);
            return response.data;
        } catch (error) {
            console.error('Error getting shipping status:', error);
            throw error;
        }
    },

    // Update shipping status
    updateShippingStatus: async (orderId, status) => {
        try {
            const response = await api.put(`/api/shipping/orders/${orderId}/status`, {
                status
            });
            return response.data;
        } catch (error) {
            console.error('Error updating shipping status:', error);
            throw error;
        }
    },

    // Get shipping history
    getShippingHistory: async (orderId) => {
        try {
            const response = await api.get(`/api/shipping/orders/${orderId}/history`);
            return response.data;
        } catch (error) {
            console.error('Error getting shipping history:', error);
            throw error;
        }
    },

    // Cancel shipment
    cancelShipment: async (orderId) => {
        try {
            const response = await api.post(`/api/shipping/orders/${orderId}/cancel`);
            return response.data;
        } catch (error) {
            console.error('Error canceling shipment:', error);
            throw error;
        }
    }
};

export default shippingService; 