import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    IconButton,
    Snackbar,
    Alert,
    CircularProgress
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import currencyService from '../../services/currencyService';

const CurrencyManagement = () => {
    const [currencies, setCurrencies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [openDialog, setOpenDialog] = useState(false);
    const [selectedCurrency, setSelectedCurrency] = useState(null);
    const [formData, setFormData] = useState({
        code: '',
        name: '',
        symbol: '',
        exchange_rate: 1,
        is_default: false
    });
    const [snackbar, setSnackbar] = useState({
        open: false,
        message: '',
        severity: 'success'
    });

    useEffect(() => {
        fetchCurrencies();
    }, []);

    const fetchCurrencies = async () => {
        try {
            setLoading(true);
            const response = await currencyService.getAllCurrencies();
            setCurrencies(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to fetch currencies');
            setSnackbar({
                open: true,
                message: 'Failed to fetch currencies',
                severity: 'error'
            });
        } finally {
            setLoading(false);
        }
    };

    const handleOpenDialog = (currency = null) => {
        if (currency) {
            setSelectedCurrency(currency);
            setFormData({
                code: currency.code,
                name: currency.name,
                symbol: currency.symbol,
                exchange_rate: currency.exchange_rate,
                is_default: currency.is_default
            });
        } else {
            setSelectedCurrency(null);
            setFormData({
                code: '',
                name: '',
                symbol: '',
                exchange_rate: 1,
                is_default: false
            });
        }
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setSelectedCurrency(null);
        setFormData({
            code: '',
            name: '',
            symbol: '',
            exchange_rate: 1,
            is_default: false
        });
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async () => {
        try {
            if (selectedCurrency) {
                await currencyService.updateCurrency(selectedCurrency.code, formData);
                setSnackbar({
                    open: true,
                    message: 'Currency updated successfully',
                    severity: 'success'
                });
            } else {
                await currencyService.addCurrency(formData);
                setSnackbar({
                    open: true,
                    message: 'Currency added successfully',
                    severity: 'success'
                });
            }
            fetchCurrencies();
            handleCloseDialog();
        } catch (err) {
            setSnackbar({
                open: true,
                message: err.response?.data?.message || 'Operation failed',
                severity: 'error'
            });
        }
    };

    const handleDelete = async (code) => {
        if (window.confirm('Are you sure you want to delete this currency?')) {
            try {
                await currencyService.deleteCurrency(code);
                setSnackbar({
                    open: true,
                    message: 'Currency deleted successfully',
                    severity: 'success'
                });
                fetchCurrencies();
            } catch (err) {
                setSnackbar({
                    open: true,
                    message: err.response?.data?.message || 'Failed to delete currency',
                    severity: 'error'
                });
            }
        }
    };

    const handleSetDefault = async (code) => {
        try {
            await currencyService.setDefaultCurrency(code);
            setSnackbar({
                open: true,
                message: 'Default currency updated successfully',
                severity: 'success'
            });
            fetchCurrencies();
        } catch (err) {
            setSnackbar({
                open: true,
                message: err.response?.data?.message || 'Failed to set default currency',
                severity: 'error'
            });
        }
    };

    const handleUpdateRates = async () => {
        try {
            await currencyService.updateExchangeRates();
            setSnackbar({
                open: true,
                message: 'Exchange rates updated successfully',
                severity: 'success'
            });
            fetchCurrencies();
        } catch (err) {
            setSnackbar({
                open: true,
                message: err.response?.data?.message || 'Failed to update exchange rates',
                severity: 'error'
            });
        }
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
                <Typography variant="h5">Currency Management</Typography>
                <Box>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={() => handleOpenDialog()}
                        sx={{ mr: 2 }}
                    >
                        Add Currency
                    </Button>
                    <Button
                        variant="outlined"
                        startIcon={<RefreshIcon />}
                        onClick={handleUpdateRates}
                    >
                        Update Rates
                    </Button>
                </Box>
            </Box>

            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Code</TableCell>
                            <TableCell>Name</TableCell>
                            <TableCell>Symbol</TableCell>
                            <TableCell>Exchange Rate</TableCell>
                            <TableCell>Default</TableCell>
                            <TableCell>Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {currencies.map((currency) => (
                            <TableRow key={currency.code}>
                                <TableCell>{currency.code}</TableCell>
                                <TableCell>{currency.name}</TableCell>
                                <TableCell>{currency.symbol}</TableCell>
                                <TableCell>{currency.exchange_rate}</TableCell>
                                <TableCell>
                                    {currency.is_default ? (
                                        <Typography color="primary">Default</Typography>
                                    ) : (
                                        <Button
                                            size="small"
                                            onClick={() => handleSetDefault(currency.code)}
                                        >
                                            Set Default
                                        </Button>
                                    )}
                                </TableCell>
                                <TableCell>
                                    <IconButton
                                        size="small"
                                        onClick={() => handleOpenDialog(currency)}
                                    >
                                        <EditIcon />
                                    </IconButton>
                                    <IconButton
                                        size="small"
                                        onClick={() => handleDelete(currency.code)}
                                        disabled={currency.is_default}
                                    >
                                        <DeleteIcon />
                                    </IconButton>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

            <Dialog open={openDialog} onClose={handleCloseDialog}>
                <DialogTitle>
                    {selectedCurrency ? 'Edit Currency' : 'Add New Currency'}
                </DialogTitle>
                <DialogContent>
                    <Box sx={{ pt: 2 }}>
                        <TextField
                            fullWidth
                            label="Code"
                            name="code"
                            value={formData.code}
                            onChange={handleInputChange}
                            margin="normal"
                            disabled={!!selectedCurrency}
                        />
                        <TextField
                            fullWidth
                            label="Name"
                            name="name"
                            value={formData.name}
                            onChange={handleInputChange}
                            margin="normal"
                        />
                        <TextField
                            fullWidth
                            label="Symbol"
                            name="symbol"
                            value={formData.symbol}
                            onChange={handleInputChange}
                            margin="normal"
                        />
                        <TextField
                            fullWidth
                            label="Exchange Rate"
                            name="exchange_rate"
                            type="number"
                            value={formData.exchange_rate}
                            onChange={handleInputChange}
                            margin="normal"
                        />
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>Cancel</Button>
                    <Button onClick={handleSubmit} variant="contained" color="primary">
                        {selectedCurrency ? 'Update' : 'Add'}
                    </Button>
                </DialogActions>
            </Dialog>

            <Snackbar
                open={snackbar.open}
                autoHideDuration={6000}
                onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
            >
                <Alert
                    onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
                    severity={snackbar.severity}
                >
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Box>
    );
};

export default CurrencyManagement; 