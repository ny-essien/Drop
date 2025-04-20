import React, { useState, useEffect } from 'react';
import {
    Box,
    Container,
    Typography,
    Grid,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Button,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    CircularProgress,
    Alert,
    Tabs,
    Tab,
    Card,
    CardContent,
    CardActions,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField
} from '@mui/material';
import shippingService from '../services/shippingService';

const Shipping = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState(0);
    const [orderId, setOrderId] = useState('');
    const [carriers, setCarriers] = useState([]);
    const [selectedCarrier, setSelectedCarrier] = useState('');
    const [serviceLevel, setServiceLevel] = useState('');
    const [shippingStatus, setShippingStatus] = useState(null);
    const [shippingHistory, setShippingHistory] = useState([]);
    const [trackingNumber, setTrackingNumber] = useState('');
    const [trackingInfo, setTrackingInfo] = useState(null);
    const [labelDialogOpen, setLabelDialogOpen] = useState(false);
    const [newStatus, setNewStatus] = useState('');

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
    };

    const handleGetCarriers = async () => {
        try {
            setLoading(true);
            setError(null);
            const result = await shippingService.getAvailableCarriers(orderId);
            setCarriers(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateLabel = async () => {
        try {
            setLoading(true);
            setError(null);
            const result = await shippingService.createShippingLabel(
                orderId,
                selectedCarrier,
                serviceLevel
            );
            setShippingStatus(result);
            setLabelDialogOpen(false);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleTrackShipment = async () => {
        try {
            setLoading(true);
            setError(null);
            const result = await shippingService.trackShipment(trackingNumber);
            setTrackingInfo(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleGetStatus = async () => {
        try {
            setLoading(true);
            setError(null);
            const result = await shippingService.getShippingStatus(orderId);
            setShippingStatus(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateStatus = async () => {
        try {
            setLoading(true);
            setError(null);
            await shippingService.updateShippingStatus(orderId, newStatus);
            await handleGetStatus();
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleGetHistory = async () => {
        try {
            setLoading(true);
            setError(null);
            const result = await shippingService.getShippingHistory(orderId);
            setShippingHistory(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleCancelShipment = async () => {
        try {
            setLoading(true);
            setError(null);
            await shippingService.cancelShipment(orderId);
            await handleGetStatus();
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="lg">
            <Box sx={{ my: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Shipping Management
                </Typography>

                <Paper sx={{ p: 2, mb: 2 }}>
                    <Tabs value={activeTab} onChange={handleTabChange}>
                        <Tab label="Create Label" />
                        <Tab label="Track Shipment" />
                        <Tab label="Manage Status" />
                        <Tab label="Shipping History" />
                    </Tabs>
                </Paper>

                {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error}
                    </Alert>
                )}

                {loading && (
                    <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                        <CircularProgress />
                    </Box>
                )}

                {activeTab === 0 && (
                    <Paper sx={{ p: 2 }}>
                        <Grid container spacing={2}>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    fullWidth
                                    label="Order ID"
                                    value={orderId}
                                    onChange={(e) => setOrderId(e.target.value)}
                                />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Button
                                    fullWidth
                                    variant="contained"
                                    onClick={handleGetCarriers}
                                >
                                    Get Available Carriers
                                </Button>
                            </Grid>
                        </Grid>

                        {carriers.length > 0 && (
                            <TableContainer sx={{ mt: 2 }}>
                                <Table>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Carrier</TableCell>
                                            <TableCell>Service Level</TableCell>
                                            <TableCell>Estimated Delivery</TableCell>
                                            <TableCell>Action</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {carriers.map((carrier) => (
                                            <TableRow key={carrier.carrier_id}>
                                                <TableCell>{carrier.name}</TableCell>
                                                <TableCell>
                                                    <Select
                                                        value={serviceLevel}
                                                        onChange={(e) => setServiceLevel(e.target.value)}
                                                    >
                                                        {carrier.rates.map((rate) => (
                                                            <MenuItem
                                                                key={rate.service_level}
                                                                value={rate.service_level}
                                                            >
                                                                {rate.service_level} - ${rate.price}
                                                            </MenuItem>
                                                        ))}
                                                    </Select>
                                                </TableCell>
                                                <TableCell>{carrier.estimated_delivery}</TableCell>
                                                <TableCell>
                                                    <Button
                                                        variant="outlined"
                                                        onClick={() => {
                                                            setSelectedCarrier(carrier.carrier_id);
                                                            setLabelDialogOpen(true);
                                                        }}
                                                    >
                                                        Create Label
                                                    </Button>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        )}
                    </Paper>
                )}

                {activeTab === 1 && (
                    <Paper sx={{ p: 2 }}>
                        <Grid container spacing={2}>
                            <Grid item xs={12} md={8}>
                                <TextField
                                    fullWidth
                                    label="Tracking Number"
                                    value={trackingNumber}
                                    onChange={(e) => setTrackingNumber(e.target.value)}
                                />
                            </Grid>
                            <Grid item xs={12} md={4}>
                                <Button
                                    fullWidth
                                    variant="contained"
                                    onClick={handleTrackShipment}
                                >
                                    Track Shipment
                                </Button>
                            </Grid>
                        </Grid>

                        {trackingInfo && (
                            <Card sx={{ mt: 2 }}>
                                <CardContent>
                                    <Typography variant="h6">Tracking Information</Typography>
                                    <Typography>Status: {trackingInfo.status}</Typography>
                                    <Typography>
                                        Last Updated: {new Date(trackingInfo.last_updated).toLocaleString()}
                                    </Typography>
                                    <Typography variant="subtitle1" sx={{ mt: 2 }}>
                                        Tracking History:
                                    </Typography>
                                    <TableContainer>
                                        <Table>
                                            <TableHead>
                                                <TableRow>
                                                    <TableCell>Date</TableCell>
                                                    <TableCell>Status</TableCell>
                                                    <TableCell>Location</TableCell>
                                                </TableRow>
                                            </TableHead>
                                            <TableBody>
                                                {trackingInfo.tracking_history.map((event, index) => (
                                                    <TableRow key={index}>
                                                        <TableCell>
                                                            {new Date(event.timestamp).toLocaleString()}
                                                        </TableCell>
                                                        <TableCell>{event.status}</TableCell>
                                                        <TableCell>{event.location}</TableCell>
                                                    </TableRow>
                                                ))}
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                </CardContent>
                            </Card>
                        )}
                    </Paper>
                )}

                {activeTab === 2 && (
                    <Paper sx={{ p: 2 }}>
                        <Grid container spacing={2}>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    fullWidth
                                    label="Order ID"
                                    value={orderId}
                                    onChange={(e) => setOrderId(e.target.value)}
                                />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Button
                                    fullWidth
                                    variant="contained"
                                    onClick={handleGetStatus}
                                >
                                    Get Status
                                </Button>
                            </Grid>
                        </Grid>

                        {shippingStatus && (
                            <Grid container spacing={2} sx={{ mt: 2 }}>
                                <Grid item xs={12} md={6}>
                                    <Card>
                                        <CardContent>
                                            <Typography variant="h6">Current Status</Typography>
                                            <Typography>Status: {shippingStatus.status}</Typography>
                                            <Typography>
                                                Tracking Number: {shippingStatus.tracking_number}
                                            </Typography>
                                            <Typography>
                                                Last Updated: {new Date(shippingStatus.last_updated).toLocaleString()}
                                            </Typography>
                                        </CardContent>
                                    </Card>
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <Card>
                                        <CardContent>
                                            <Typography variant="h6">Update Status</Typography>
                                            <FormControl fullWidth sx={{ mt: 2 }}>
                                                <InputLabel>New Status</InputLabel>
                                                <Select
                                                    value={newStatus}
                                                    onChange={(e) => setNewStatus(e.target.value)}
                                                >
                                                    <MenuItem value="created">Created</MenuItem>
                                                    <MenuItem value="in_transit">In Transit</MenuItem>
                                                    <MenuItem value="out_for_delivery">Out for Delivery</MenuItem>
                                                    <MenuItem value="delivered">Delivered</MenuItem>
                                                    <MenuItem value="cancelled">Cancelled</MenuItem>
                                                </Select>
                                            </FormControl>
                                            <Button
                                                variant="contained"
                                                onClick={handleUpdateStatus}
                                                sx={{ mt: 2 }}
                                            >
                                                Update Status
                                            </Button>
                                            <Button
                                                variant="outlined"
                                                color="error"
                                                onClick={handleCancelShipment}
                                                sx={{ mt: 2, ml: 2 }}
                                            >
                                                Cancel Shipment
                                            </Button>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            </Grid>
                        )}
                    </Paper>
                )}

                {activeTab === 3 && (
                    <Paper sx={{ p: 2 }}>
                        <Grid container spacing={2}>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    fullWidth
                                    label="Order ID"
                                    value={orderId}
                                    onChange={(e) => setOrderId(e.target.value)}
                                />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Button
                                    fullWidth
                                    variant="contained"
                                    onClick={handleGetHistory}
                                >
                                    Get History
                                </Button>
                            </Grid>
                        </Grid>

                        {shippingHistory.length > 0 && (
                            <TableContainer sx={{ mt: 2 }}>
                                <Table>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Date</TableCell>
                                            <TableCell>Status</TableCell>
                                            <TableCell>Location</TableCell>
                                            <TableCell>Notes</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {shippingHistory.map((event, index) => (
                                            <TableRow key={index}>
                                                <TableCell>
                                                    {new Date(event.timestamp).toLocaleString()}
                                                </TableCell>
                                                <TableCell>{event.status}</TableCell>
                                                <TableCell>{event.location}</TableCell>
                                                <TableCell>{event.notes}</TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        )}
                    </Paper>
                )}

                <Dialog open={labelDialogOpen} onClose={() => setLabelDialogOpen(false)}>
                    <DialogTitle>Create Shipping Label</DialogTitle>
                    <DialogContent>
                        <Typography>
                            Are you sure you want to create a shipping label for order {orderId} with carrier {selectedCarrier}?
                        </Typography>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={() => setLabelDialogOpen(false)}>Cancel</Button>
                        <Button onClick={handleCreateLabel} variant="contained">
                            Create Label
                        </Button>
                    </DialogActions>
                </Dialog>
            </Box>
        </Container>
    );
};

export default Shipping; 