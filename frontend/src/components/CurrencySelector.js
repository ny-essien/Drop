import React, { useState, useEffect } from 'react';
import {
    Box,
    IconButton,
    Menu,
    MenuItem,
    Typography,
    CircularProgress
} from '@mui/material';
import { Language as LanguageIcon } from '@mui/icons-material';
import currencyService from '../services/currencyService';
import currencyConverter from '../utils/currencyConverter';

const CurrencySelector = () => {
    const [anchorEl, setAnchorEl] = useState(null);
    const [currencies, setCurrencies] = useState([]);
    const [selectedCurrency, setSelectedCurrency] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadCurrencies();
    }, []);

    const loadCurrencies = async () => {
        try {
            const [currenciesResponse, defaultResponse] = await Promise.all([
                currencyService.getAllCurrencies(),
                currencyService.getDefaultCurrency()
            ]);
            setCurrencies(currenciesResponse.data);
            setSelectedCurrency(defaultResponse.data);
        } catch (error) {
            console.error('Failed to load currencies:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleCurrencySelect = async (currency) => {
        try {
            // Update user's currency preference in the backend
            await currencyService.setUserCurrency(currency.code);
            setSelectedCurrency(currency);
            handleClose();
            
            // Reload the page to update all prices
            window.location.reload();
        } catch (error) {
            console.error('Failed to update currency:', error);
        }
    };

    if (loading) {
        return (
            <Box display="flex" alignItems="center">
                <CircularProgress size={24} />
            </Box>
        );
    }

    return (
        <Box>
            <IconButton
                onClick={handleClick}
                color="inherit"
                aria-label="select currency"
            >
                <LanguageIcon />
                {selectedCurrency && (
                    <Typography variant="body2" sx={{ ml: 1 }}>
                        {selectedCurrency.code}
                    </Typography>
                )}
            </IconButton>
            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleClose}
            >
                {currencies.map((currency) => (
                    <MenuItem
                        key={currency.code}
                        onClick={() => handleCurrencySelect(currency)}
                        selected={selectedCurrency?.code === currency.code}
                    >
                        <Typography variant="body2">
                            {currency.name} ({currency.code})
                        </Typography>
                    </MenuItem>
                ))}
            </Menu>
        </Box>
    );
};

export default CurrencySelector; 