const Currency = require('../models/currency');
const axios = require('axios');
const User = require('../models/user');

class CurrencyService {
    // Get all currencies
    async getAllCurrencies() {
        return await Currency.find({ status: 'active' });
    }

    // Get default currency
    async getDefaultCurrency() {
        return await Currency.findOne({ is_default: true });
    }

    // Get currency by code
    async getCurrencyByCode(code) {
        return await Currency.findOne({ code: code.toUpperCase(), status: 'active' });
    }

    // Update exchange rates
    async updateExchangeRates() {
        try {
            const response = await axios.get('https://api.exchangerate-api.com/v4/latest/USD');
            const rates = response.data.rates;

            for (const [code, rate] of Object.entries(rates)) {
                await Currency.updateOne(
                    { code: code.toUpperCase() },
                    { 
                        exchange_rate: rate,
                        last_updated: new Date()
                    }
                );
            }

            return { success: true, message: 'Exchange rates updated successfully' };
        } catch (error) {
            console.error('Error updating exchange rates:', error);
            throw new Error('Failed to update exchange rates');
        }
    }

    // Convert amount between currencies
    async convertAmount(amount, fromCurrency, toCurrency) {
        const from = await this.getCurrencyByCode(fromCurrency);
        const to = await this.getCurrencyByCode(toCurrency);

        if (!from || !to) {
            throw new Error('Invalid currency code');
        }

        // Convert to USD first (base currency)
        const amountInUSD = amount / from.exchange_rate;
        // Convert to target currency
        return amountInUSD * to.exchange_rate;
    }

    // Set default currency
    async setDefaultCurrency(code) {
        const currency = await this.getCurrencyByCode(code);
        if (!currency) {
            throw new Error('Currency not found');
        }

        currency.is_default = true;
        await currency.save();
        return currency;
    }

    // Add new currency
    async addCurrency(currencyData) {
        const existingCurrency = await this.getCurrencyByCode(currencyData.code);
        if (existingCurrency) {
            throw new Error('Currency already exists');
        }

        const currency = new Currency({
            ...currencyData,
            code: currencyData.code.toUpperCase()
        });

        return await currency.save();
    }

    // Update currency
    async updateCurrency(code, updateData) {
        const currency = await this.getCurrencyByCode(code);
        if (!currency) {
            throw new Error('Currency not found');
        }

        Object.assign(currency, updateData);
        return await currency.save();
    }

    // Delete currency (soft delete)
    async deleteCurrency(code) {
        const currency = await this.getCurrencyByCode(code);
        if (!currency) {
            throw new Error('Currency not found');
        }

        currency.status = 'inactive';
        return await currency.save();
    }

    // Get user's preferred currency
    async getUserCurrency(userId) {
        const user = await User.findById(userId);
        if (!user) {
            throw new Error('User not found');
        }

        return await this.getCurrencyByCode(user.preferred_currency || 'USD');
    }

    // Set user's preferred currency
    async setUserCurrency(userId, currencyCode) {
        const user = await User.findById(userId);
        if (!user) {
            throw new Error('User not found');
        }

        const currency = await this.getCurrencyByCode(currencyCode);
        if (!currency) {
            throw new Error('Currency not found');
        }

        user.preferred_currency = currencyCode;
        await user.save();
        return currency;
    }

    // Get historical exchange rates
    async getHistoricalRates(currencyCode, startDate, endDate) {
        const currency = await this.getCurrencyByCode(currencyCode);
        if (!currency) {
            throw new Error('Currency not found');
        }

        // In a real application, you would fetch this from a historical rates database
        // For now, we'll generate some sample data
        const rates = [];
        const currentDate = new Date(startDate);
        const end = new Date(endDate);

        while (currentDate <= end) {
            rates.push({
                date: currentDate.toISOString(),
                rate: currency.exchange_rate * (0.95 + Math.random() * 0.1) // Simulate some variation
            });
            currentDate.setDate(currentDate.getDate() + 1);
        }

        return rates;
    }

    // Get exchange rate trends
    async getRateTrends(currencyCode, period = '7d') {
        const currency = await this.getCurrencyByCode(currencyCode);
        if (!currency) {
            throw new Error('Currency not found');
        }

        // Calculate the number of data points based on the period
        let points;
        switch (period) {
            case '1d':
                points = 24; // Hourly data for 24 hours
                break;
            case '7d':
                points = 7; // Daily data for 7 days
                break;
            case '30d':
                points = 30; // Daily data for 30 days
                break;
            case '90d':
                points = 90; // Daily data for 90 days
                break;
            default:
                points = 7;
        }

        // Generate trend data
        const trends = [];
        const baseRate = currency.exchange_rate;
        let sum = 0;

        for (let i = 0; i < points; i++) {
            const rate = baseRate * (0.95 + Math.random() * 0.1);
            sum += rate;
            trends.push({
                timestamp: new Date(Date.now() - (points - i) * 24 * 60 * 60 * 1000).toISOString(),
                rate: rate,
                average: sum / (i + 1)
            });
        }

        return trends;
    }

    // Get latest exchange rates
    async getLatestRates() {
        const currencies = await this.getAllCurrencies();
        return currencies.map(currency => ({
            code: currency.code,
            rate: currency.exchange_rate,
            last_updated: currency.last_updated
        }));
    }
}

module.exports = new CurrencyService(); 