const express = require('express');
const router = express.Router();
const axios = require('axios');

// Python service base URL
const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:8000';

// Supplier product synchronization
router.post('/supplier/sync', async (req, res) => {
    try {
        const response = await axios.post(`${PYTHON_SERVICE_URL}/api/supplier/sync`, req.body);
        res.json(response.data);
    } catch (error) {
        console.error('Error syncing supplier products:', error);
        res.status(500).json({ message: 'Failed to sync supplier products' });
    }
});

// Order fulfillment
router.post('/order/fulfill', async (req, res) => {
    try {
        const response = await axios.post(`${PYTHON_SERVICE_URL}/api/order/fulfill`, req.body);
        res.json(response.data);
    } catch (error) {
        console.error('Error fulfilling order:', error);
        res.status(500).json({ message: 'Failed to fulfill order' });
    }
});

// Price monitoring
router.get('/price/monitor', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_SERVICE_URL}/api/price/monitor`);
        res.json(response.data);
    } catch (error) {
        console.error('Error monitoring prices:', error);
        res.status(500).json({ message: 'Failed to monitor prices' });
    }
});

// Stock level monitoring
router.get('/stock/monitor', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_SERVICE_URL}/api/stock/monitor`);
        res.json(response.data);
    } catch (error) {
        console.error('Error monitoring stock levels:', error);
        res.status(500).json({ message: 'Failed to monitor stock levels' });
    }
});

module.exports = router; 