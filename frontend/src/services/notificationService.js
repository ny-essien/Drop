import api from './api';

const notificationService = {
    /**
     * Get notifications with optional filtering
     * @param {Object} params - Filter parameters
     * @param {string} [params.type] - Filter by notification type
     * @param {string} [params.status] - Filter by notification status
     * @param {Date} [params.startDate] - Filter by start date
     * @param {Date} [params.endDate] - Filter by end date
     * @param {number} [params.limit=100] - Number of notifications to return
     * @param {number} [params.skip=0] - Number of notifications to skip
     * @returns {Promise<Array>} List of notifications
     */
    getNotifications: async (params = {}) => {
        const response = await api.get('/notifications', { params });
        return response.data;
    },

    /**
     * Get a specific notification by ID
     * @param {string} notificationId - The ID of the notification
     * @returns {Promise<Object>} The notification
     */
    getNotification: async (notificationId) => {
        const response = await api.get(`/notifications/${notificationId}`);
        return response.data;
    },

    /**
     * Create a new notification
     * @param {Object} notification - The notification data
     * @returns {Promise<Object>} The created notification
     */
    createNotification: async (notification) => {
        const response = await api.post('/notifications', notification);
        return response.data;
    },

    /**
     * Update notification status
     * @param {string} notificationId - The ID of the notification
     * @param {string} status - The new status
     * @param {string} [error] - Error message if any
     * @returns {Promise<Object>} The updated notification
     */
    updateNotificationStatus: async (notificationId, status, error) => {
        const response = await api.put(`/notifications/${notificationId}/status`, {
            status,
            error
        });
        return response.data;
    },

    /**
     * Delete a notification
     * @param {string} notificationId - The ID of the notification
     * @returns {Promise<Object>} Success status
     */
    deleteNotification: async (notificationId) => {
        const response = await api.delete(`/notifications/${notificationId}`);
        return response.data;
    },

    /**
     * Get notification statistics
     * @returns {Promise<Object>} Notification statistics
     */
    getNotificationStats: async () => {
        const response = await api.get('/notifications/stats/summary');
        return response.data;
    },

    /**
     * Send order confirmation notification
     * @param {string} orderId - The ID of the order
     * @returns {Promise<Object>} The result of the notification
     */
    sendOrderConfirmation: async (orderId) => {
        const response = await api.post(`/notifications/orders/${orderId}/confirm`);
        return response.data;
    },

    /**
     * Notify warehouse about new order
     * @param {string} orderId - The ID of the order
     * @returns {Promise<Object>} The result of the notification
     */
    notifyWarehouse: async (orderId) => {
        const response = await api.post(`/notifications/orders/${orderId}/notify-warehouse`);
        return response.data;
    },

    /**
     * Send order status update notification
     * @param {string} orderId - The ID of the order
     * @returns {Promise<Object>} The result of the notification
     */
    sendStatusUpdate: async (orderId) => {
        const response = await api.post(`/notifications/orders/${orderId}/status-update`);
        return response.data;
    },

    /**
     * Send order cancellation notice
     * @param {string} orderId - The ID of the order
     * @returns {Promise<Object>} The result of the notification
     */
    sendCancellationNotice: async (orderId) => {
        const response = await api.post(`/notifications/orders/${orderId}/cancel`);
        return response.data;
    },

    /**
     * Send low stock alert
     * @param {string} productId - The ID of the product
     * @returns {Promise<Object>} The result of the notification
     */
    sendLowStockAlert: async (productId) => {
        const response = await api.post(`/notifications/products/${productId}/low-stock`);
        return response.data;
    }
};

export default notificationService; 