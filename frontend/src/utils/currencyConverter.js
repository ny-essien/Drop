import currencyService from '../services/currencyService';

class CurrencyConverter {
    constructor() {
        this.currencies = [];
        this.defaultCurrency = null;
        this.loadCurrencies();
    }

    async loadCurrencies() {
        try {
            const [currenciesResponse, defaultResponse] = await Promise.all([
                currencyService.getAllCurrencies(),
                currencyService.getDefaultCurrency()
            ]);
            this.currencies = currenciesResponse.data;
            this.defaultCurrency = defaultResponse.data;
        } catch (error) {
            console.error('Failed to load currencies:', error);
        }
    }

    async convertPrice(price, fromCurrency, toCurrency) {
        try {
            if (fromCurrency === toCurrency) return price;
            
            const response = await currencyService.convertAmount(price, fromCurrency, toCurrency);
            return response.data.convertedAmount;
        } catch (error) {
            console.error('Failed to convert price:', error);
            return price;
        }
    }

    formatPrice(price, currencyCode) {
        const currency = this.currencies.find(c => c.code === currencyCode) || this.defaultCurrency;
        if (!currency) return price.toString();

        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currencyCode,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(price);
    }

    getCurrencySymbol(currencyCode) {
        const currency = this.currencies.find(c => c.code === currencyCode) || this.defaultCurrency;
        return currency ? currency.symbol : '$';
    }

    async getExchangeRate(fromCurrency, toCurrency) {
        try {
            if (fromCurrency === toCurrency) return 1;
            
            const from = this.currencies.find(c => c.code === fromCurrency);
            const to = this.currencies.find(c => c.code === toCurrency);
            
            if (!from || !to) return 1;
            
            return to.exchange_rate / from.exchange_rate;
        } catch (error) {
            console.error('Failed to get exchange rate:', error);
            return 1;
        }
    }
}

export default new CurrencyConverter(); 