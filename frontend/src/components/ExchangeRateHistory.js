import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    CircularProgress
} from '@mui/material';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';
import currencyService from '../services/currencyService';
import currencyConverter from '../utils/currencyConverter';

const ExchangeRateHistory = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedCurrency, setSelectedCurrency] = useState('');
    const [period, setPeriod] = useState('7d');
    const [historicalData, setHistoricalData] = useState([]);
    const [trendData, setTrendData] = useState([]);

    useEffect(() => {
        loadCurrencies();
    }, []);

    useEffect(() => {
        if (selectedCurrency) {
            loadHistoricalData();
            loadTrendData();
        }
    }, [selectedCurrency, period]);

    const loadCurrencies = async () => {
        try {
            const response = await currencyService.getAllCurrencies();
            if (response.data.length > 0) {
                setSelectedCurrency(response.data[0].code);
            }
        } catch (error) {
            setError('Failed to load currencies');
        }
    };

    const loadHistoricalData = async () => {
        try {
            setLoading(true);
            const endDate = new Date();
            const startDate = new Date();
            startDate.setDate(startDate.getDate() - 30); // Last 30 days

            const response = await currencyService.getHistoricalRates(
                selectedCurrency,
                startDate.toISOString(),
                endDate.toISOString()
            );
            setHistoricalData(response.data);
        } catch (error) {
            setError('Failed to load historical data');
        } finally {
            setLoading(false);
        }
    };

    const loadTrendData = async () => {
        try {
            const response = await currencyService.getRateTrends(selectedCurrency, period);
            setTrendData(response.data);
        } catch (error) {
            setError('Failed to load trend data');
        }
    };

    const handleCurrencyChange = (event) => {
        setSelectedCurrency(event.target.value);
    };

    const handlePeriodChange = (event) => {
        setPeriod(event.target.value);
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h5">Exchange Rate History</Typography>
                <Box display="flex" gap={2}>
                    <FormControl sx={{ minWidth: 120 }}>
                        <InputLabel>Currency</InputLabel>
                        <Select
                            value={selectedCurrency}
                            onChange={handleCurrencyChange}
                            label="Currency"
                        >
                            {currencyConverter.currencies.map((currency) => (
                                <MenuItem key={currency.code} value={currency.code}>
                                    {currency.name} ({currency.code})
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <FormControl sx={{ minWidth: 120 }}>
                        <InputLabel>Period</InputLabel>
                        <Select
                            value={period}
                            onChange={handlePeriodChange}
                            label="Period"
                        >
                            <MenuItem value="1d">Last 24 Hours</MenuItem>
                            <MenuItem value="7d">Last 7 Days</MenuItem>
                            <MenuItem value="30d">Last 30 Days</MenuItem>
                            <MenuItem value="90d">Last 90 Days</MenuItem>
                        </Select>
                    </FormControl>
                </Box>
            </Box>

            <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                    Historical Exchange Rates
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={historicalData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line
                            type="monotone"
                            dataKey="rate"
                            stroke="#8884d8"
                            name="Exchange Rate"
                        />
                    </LineChart>
                </ResponsiveContainer>
            </Paper>

            <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                    Exchange Rate Trends
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={trendData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="timestamp" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line
                            type="monotone"
                            dataKey="rate"
                            stroke="#82ca9d"
                            name="Current Rate"
                        />
                        <Line
                            type="monotone"
                            dataKey="average"
                            stroke="#ffc658"
                            name="Average Rate"
                        />
                    </LineChart>
                </ResponsiveContainer>
            </Paper>
        </Box>
    );
};

export default ExchangeRateHistory; 