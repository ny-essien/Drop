import React, { useState, useEffect } from 'react';
import {
    Box,
    Container,
    Typography,
    Grid,
    Paper,
    Button,
    CircularProgress,
    Alert,
    Tabs,
    Tab,
    Card,
    CardContent,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from '@mui/material';
import mlService from '../services/mlService';
import { useSelector } from 'react-redux';

const MLDashboard = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState(0);
    const [productId, setProductId] = useState('');
    const [priceOptimization, setPriceOptimization] = useState(null);
    const [demandForecast, setDemandForecast] = useState(null);
    const [customerSegments, setCustomerSegments] = useState(null);
    const [recommendations, setRecommendations] = useState([]);
    const { user } = useSelector((state) => state.auth);

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
    };

    const handleTrainPriceModel = async () => {
        try {
            setLoading(true);
            setError(null);
            const result = await mlService.trainPriceOptimizationModel();
            setError(`Model trained successfully with score: ${result.score}`);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleOptimizePrice = async () => {
        try {
            setLoading(true);
            setError(null);
            const result = await mlService.optimizePrice(productId);
            setPriceOptimization(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleTrainDemandModel = async () => {
        try {
            setLoading(true);
            setError(null);
            const result = await mlService.trainDemandForecastingModel();
            setError(`Model trained successfully with score: ${result.score}`);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleForecastDemand = async () => {
        try {
            setLoading(true);
            setError(null);
            const result = await mlService.forecastDemand(productId);
            setDemandForecast(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleGetSegments = async () => {
        try {
            setLoading(true);
            setError(null);
            const result = await mlService.getCustomerSegments();
            setCustomerSegments(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const loadRecommendations = async () => {
            if (user) {
                try {
                    const result = await mlService.getProductRecommendations(user.id);
                    setRecommendations(result);
                } catch (err) {
                    console.error('Error loading recommendations:', err);
                }
            }
        };
        loadRecommendations();
    }, [user]);

    return (
        <Container maxWidth="lg">
            <Box sx={{ my: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Machine Learning Dashboard
                </Typography>

                <Paper sx={{ p: 2, mb: 2 }}>
                    <Tabs value={activeTab} onChange={handleTabChange}>
                        <Tab label="Price Optimization" />
                        <Tab label="Demand Forecasting" />
                        <Tab label="Customer Segmentation" />
                        <Tab label="Recommendations" />
                    </Tabs>
                </Paper>

                {error && (
                    <Alert severity={error.includes('successfully') ? 'success' : 'error'} sx={{ mb: 2 }}>
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
                            <Grid item xs={12}>
                                <Button
                                    variant="contained"
                                    onClick={handleTrainPriceModel}
                                    sx={{ mb: 2 }}
                                >
                                    Train Price Optimization Model
                                </Button>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    fullWidth
                                    label="Product ID"
                                    value={productId}
                                    onChange={(e) => setProductId(e.target.value)}
                                />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Button
                                    fullWidth
                                    variant="contained"
                                    onClick={handleOptimizePrice}
                                >
                                    Optimize Price
                                </Button>
                            </Grid>
                        </Grid>

                        {priceOptimization && (
                            <Card sx={{ mt: 2 }}>
                                <CardContent>
                                    <Typography variant="h6">Price Optimization Results</Typography>
                                    <Typography>Current Price: ${priceOptimization.current_price}</Typography>
                                    <Typography>Optimal Price: ${priceOptimization.optimal_price}</Typography>
                                    <Typography>
                                        Predicted Revenue Increase: {priceOptimization.predicted_revenue_increase.toFixed(2)}%
                                    </Typography>
                                    <Typography>
                                        Profit Margin: {priceOptimization.profit_margin ? (priceOptimization.profit_margin * 100).toFixed(2) : 'N/A'}%
                                    </Typography>

                                    <Typography variant="subtitle1" sx={{ mt: 2 }}>
                                        Price Suggestions:
                                    </Typography>
                                    <TableContainer>
                                        <Table>
                                            <TableHead>
                                                <TableRow>
                                                    <TableCell>Price</TableCell>
                                                    <TableCell>Predicted Revenue</TableCell>
                                                    <TableCell>Profit Margin</TableCell>
                                                </TableRow>
                                            </TableHead>
                                            <TableBody>
                                                {priceOptimization.price_suggestions.map((suggestion, index) => (
                                                    <TableRow key={index}>
                                                        <TableCell>${suggestion.price.toFixed(2)}</TableCell>
                                                        <TableCell>${suggestion.predicted_revenue.toFixed(2)}</TableCell>
                                                        <TableCell>
                                                            {suggestion.profit_margin ? (suggestion.profit_margin * 100).toFixed(2) : 'N/A'}%
                                                        </TableCell>
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

                {activeTab === 1 && (
                    <Paper sx={{ p: 2 }}>
                        <Grid container spacing={2}>
                            <Grid item xs={12}>
                                <Button
                                    variant="contained"
                                    onClick={handleTrainDemandModel}
                                    sx={{ mb: 2 }}
                                >
                                    Train Demand Forecasting Model
                                </Button>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    fullWidth
                                    label="Product ID"
                                    value={productId}
                                    onChange={(e) => setProductId(e.target.value)}
                                />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Button
                                    fullWidth
                                    variant="contained"
                                    onClick={handleForecastDemand}
                                >
                                    Forecast Demand
                                </Button>
                            </Grid>
                        </Grid>

                        {demandForecast && (
                            <Card sx={{ mt: 2 }}>
                                <CardContent>
                                    <Typography variant="h6">Demand Forecast</Typography>
                                    <Typography>
                                        Total Predicted Sales: {demandForecast.total_predicted_sales}
                                    </Typography>
                                    <Typography>
                                        Average Daily Sales: {demandForecast.average_daily_sales}
                                    </Typography>

                                    <Box sx={{ height: 400, mt: 2 }}>
                                        <ResponsiveContainer width="100%" height="100%">
                                            <LineChart
                                                data={demandForecast.forecast}
                                                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                                            >
                                                <CartesianGrid strokeDasharray="3 3" />
                                                <XAxis dataKey="date" />
                                                <YAxis />
                                                <Tooltip />
                                                <Legend />
                                                <Line
                                                    type="monotone"
                                                    dataKey="predicted_sales"
                                                    stroke="#8884d8"
                                                    name="Predicted Sales"
                                                />
                                                <Line
                                                    type="monotone"
                                                    dataKey="confidence_interval.lower"
                                                    stroke="#82ca9d"
                                                    name="Lower Bound"
                                                    strokeDasharray="5 5"
                                                />
                                                <Line
                                                    type="monotone"
                                                    dataKey="confidence_interval.upper"
                                                    stroke="#82ca9d"
                                                    name="Upper Bound"
                                                    strokeDasharray="5 5"
                                                />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </Box>
                                </CardContent>
                            </Card>
                        )}
                    </Paper>
                )}

                {activeTab === 2 && (
                    <Paper sx={{ p: 2 }}>
                        <Button
                            variant="contained"
                            onClick={handleGetSegments}
                            sx={{ mb: 2 }}
                        >
                            Get Customer Segments
                        </Button>

                        {customerSegments && (
                            <Grid container spacing={2}>
                                {Object.entries(customerSegments).map(([segment, data]) => (
                                    <Grid item xs={12} md={6} key={segment}>
                                        <Card>
                                            <CardContent>
                                                <Typography variant="h6">{segment}</Typography>
                                                <Typography>Count: {data.count}</Typography>
                                                <Typography>
                                                    Avg. Total Orders: {data.avg_total_orders.toFixed(2)}
                                                </Typography>
                                                <Typography>
                                                    Avg. Total Spent: ${data.avg_total_spent.toFixed(2)}
                                                </Typography>
                                                <Typography>
                                                    Avg. Order Value: ${data.avg_order_value.toFixed(2)}
                                                </Typography>
                                            </CardContent>
                                        </Card>
                                    </Grid>
                                ))}
                            </Grid>
                        )}
                    </Paper>
                )}

                {activeTab === 3 && (
                    <Paper sx={{ p: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            Personalized Product Recommendations
                        </Typography>

                        {recommendations.length > 0 ? (
                            <TableContainer>
                                <Table>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Product</TableCell>
                                            <TableCell>Category</TableCell>
                                            <TableCell>Price</TableCell>
                                            <TableCell>Score</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {recommendations.map((recommendation) => (
                                            <TableRow key={recommendation.product_id}>
                                                <TableCell>{recommendation.name}</TableCell>
                                                <TableCell>{recommendation.category}</TableCell>
                                                <TableCell>${recommendation.price}</TableCell>
                                                <TableCell>{recommendation.score.toFixed(2)}</TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        ) : (
                            <Typography>No recommendations available.</Typography>
                        )}
                    </Paper>
                )}
            </Box>
        </Container>
    );
};

export default MLDashboard; 