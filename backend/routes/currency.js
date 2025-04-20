const express = require('express');
const router = express.Router();
const currencyService = require('../services/currencyService');
const { checkAuth, checkAdmin } = require('../middleware/auth');

// Get all currencies
router.get('/', async (req, res) => {
    try {
        const currencies = await currencyService.getAllCurrencies();
        res.json(currencies);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Get default currency
router.get('/default', async (req, res) => {
    try {
        const currency = await currencyService.getDefaultCurrency();
        res.json(currency);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Get currency by code
router.get('/:code', async (req, res) => {
    try {
        const currency = await currencyService.getCurrencyByCode(req.params.code);
        if (!currency) {
            return res.status(404).json({ message: 'Currency not found' });
        }
        res.json(currency);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Update exchange rates (admin only)
router.post('/update-rates', checkAuth, checkAdmin, async (req, res) => {
    try {
        const result = await currencyService.updateExchangeRates();
        res.json(result);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Convert amount between currencies
router.post('/convert', async (req, res) => {
    try {
        const { amount, fromCurrency, toCurrency } = req.body;
        const convertedAmount = await currencyService.convertAmount(amount, fromCurrency, toCurrency);
        res.json({ convertedAmount });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Set default currency (admin only)
router.post('/:code/set-default', checkAuth, checkAdmin, async (req, res) => {
    try {
        const currency = await currencyService.setDefaultCurrency(req.params.code);
        res.json(currency);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Add new currency (admin only)
router.post('/', checkAuth, checkAdmin, async (req, res) => {
    try {
        const currency = await currencyService.addCurrency(req.body);
        res.status(201).json(currency);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Update currency (admin only)
router.put('/:code', checkAuth, checkAdmin, async (req, res) => {
    try {
        const currency = await currencyService.updateCurrency(req.params.code, req.body);
        res.json(currency);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Delete currency (admin only)
router.delete('/:code', checkAuth, checkAdmin, async (req, res) => {
    try {
        const currency = await currencyService.deleteCurrency(req.params.code);
        res.json(currency);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Get user's preferred currency
router.get('/user/preference', checkAuth, async (req, res) => {
    try {
        const currency = await currencyService.getUserCurrency(req.user.id);
        res.json(currency);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Set user's preferred currency
router.post('/user/preference', checkAuth, async (req, res) => {
    try {
        const { currencyCode } = req.body;
        const currency = await currencyService.setUserCurrency(req.user.id, currencyCode);
        res.json(currency);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Get historical exchange rates
router.get('/:code/history', async (req, res) => {
    try {
        const { startDate, endDate } = req.query;
        const rates = await currencyService.getHistoricalRates(req.params.code, startDate, endDate);
        res.json(rates);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Get exchange rate trends
router.get('/:code/trends', async (req, res) => {
    try {
        const { period } = req.query;
        const trends = await currencyService.getRateTrends(req.params.code, period);
        res.json(trends);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// SSE endpoint for real-time updates
router.get('/updates', (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    const sendUpdate = async () => {
        try {
            const rates = await currencyService.getLatestRates();
            res.write(`data: ${JSON.stringify(rates)}\n\n`);
        } catch (error) {
            console.error('Error sending update:', error);
        }
    };

    // Send initial update
    sendUpdate();

    // Set up interval for updates
    const interval = setInterval(sendUpdate, 60000); // Update every minute

    // Clean up on client disconnect
    req.on('close', () => {
        clearInterval(interval);
    });
});

module.exports = router; 