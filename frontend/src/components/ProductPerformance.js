import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Grid,
    Typography,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    CircularProgress,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    Paper,
    Tabs,
    Tab,
    TextField,
    Button
} from '@mui/material';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    LineChart,
    Line,
    PieChart,
    Pie,
    Cell
} from 'recharts';
import { TrendingUp, TrendingDown, Star, ShoppingCart, Return } from '@mui/icons-material';
import analyticsService from '../services/analyticsService';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658'];

const ProductPerformance = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [products, setProducts] = useState([]);
    const [selectedProduct, setSelectedProduct] = useState(null);
    const [timeRange, setTimeRange] = useState('30d');
    const [activeTab, setActiveTab] = useState(0);
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        fetchProductAnalytics();
    }, [timeRange]);

    const fetchProductAnalytics = async () => {
        try {
            setLoading(true);
            const response = await analyticsService.getProductAnalytics();
            setProducts(response.data);
            if (response.data.length > 0) {
                setSelectedProduct(response.data[0]);
            }
            setError(null);
        } catch (err) {
            setError('Failed to fetch product analytics');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const filteredProducts = products.filter(product =>
        product.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4">Product Performance</Typography>
                <Box display="flex" gap={2}>
                    <TextField
                        label="Search Products"
                        variant="outlined"
                        size="small"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                    <FormControl sx={{ minWidth: 120 }}>
                        <InputLabel>Time Range</InputLabel>
                        <Select
                            value={timeRange}
                            onChange={(e) => setTimeRange(e.target.value)}
                            label="Time Range"
                        >
                            <MenuItem value="7d">Last 7 Days</MenuItem>
                            <MenuItem value="30d">Last 30 Days</MenuItem>
                            <MenuItem value="90d">Last 90 Days</MenuItem>
                        </Select>
                    </FormControl>
                </Box>
            </Box>

            {error && (
                <Typography color="error" mb={2}>
                    {error}
                </Typography>
            )}

            <Grid container spacing={3}>
                {/* Product Selection */}
                <Grid item xs={12} md={4}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Products
                            </Typography>
                            <TableContainer>
                                <Table>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Product</TableCell>
                                            <TableCell align="right">Sales</TableCell>
                                            <TableCell align="right">Growth</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {filteredProducts.map((product) => (
                                            <TableRow
                                                key={product.id}
                                                hover
                                                selected={selectedProduct?.id === product.id}
                                                onClick={() => setSelectedProduct(product)}
                                                sx={{ cursor: 'pointer' }}
                                            >
                                                <TableCell>{product.name}</TableCell>
                                                <TableCell align="right">
                                                    ${product.total_sales.toFixed(2)}
                                                </TableCell>
                                                <TableCell align="right">
                                                    <Box display="flex" alignItems="center" justifyContent="flex-end">
                                                        {product.growth > 0 ? (
                                                            <TrendingUp color="success" fontSize="small" />
                                                        ) : (
                                                            <TrendingDown color="error" fontSize="small" />
                                                        )}
                                                        <Typography
                                                            variant="body2"
                                                            color={product.growth > 0 ? 'success.main' : 'error.main'}
                                                        >
                                                            {Math.abs(product.growth).toFixed(1)}%
                                                        </Typography>
                                                    </Box>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Product Details */}
                <Grid item xs={12} md={8}>
                    {selectedProduct && (
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    {selectedProduct.name}
                                </Typography>
                                <Tabs
                                    value={activeTab}
                                    onChange={(e, newValue) => setActiveTab(newValue)}
                                    sx={{ mb: 3 }}
                                >
                                    <Tab label="Overview" />
                                    <Tab label="Sales" />
                                    <Tab label="Reviews" />
                                    <Tab label="Inventory" />
                                </Tabs>

                                {activeTab === 0 && (
                                    <Grid container spacing={2}>
                                        <Grid item xs={12} md={4}>
                                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                                <Typography variant="subtitle2" color="textSecondary">
                                                    Total Sales
                                                </Typography>
                                                <Typography variant="h4">
                                                    ${selectedProduct.total_sales.toFixed(2)}
                                                </Typography>
                                                <Box display="flex" alignItems="center" justifyContent="center">
                                                    {selectedProduct.growth > 0 ? (
                                                        <TrendingUp color="success" />
                                                    ) : (
                                                        <TrendingDown color="error" />
                                                    )}
                                                    <Typography
                                                        variant="body2"
                                                        color={selectedProduct.growth > 0 ? 'success.main' : 'error.main'}
                                                    >
                                                        {Math.abs(selectedProduct.growth).toFixed(1)}%
                                                    </Typography>
                                                </Box>
                                            </Paper>
                                        </Grid>
                                        <Grid item xs={12} md={4}>
                                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                                <Typography variant="subtitle2" color="textSecondary">
                                                    Average Rating
                                                </Typography>
                                                <Typography variant="h4">
                                                    {selectedProduct.average_rating.toFixed(1)}
                                                </Typography>
                                                <Box display="flex" alignItems="center" justifyContent="center">
                                                    <Star color="warning" />
                                                    <Typography variant="body2" color="textSecondary">
                                                        ({selectedProduct.total_reviews} reviews)
                                                    </Typography>
                                                </Box>
                                            </Paper>
                                        </Grid>
                                        <Grid item xs={12} md={4}>
                                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                                <Typography variant="subtitle2" color="textSecondary">
                                                    Conversion Rate
                                                </Typography>
                                                <Typography variant="h4">
                                                    {(selectedProduct.conversion_rate * 100).toFixed(1)}%
                                                </Typography>
                                                <Box display="flex" alignItems="center" justifyContent="center">
                                                    <ShoppingCart color="primary" />
                                                    <Typography variant="body2" color="textSecondary">
                                                        {selectedProduct.total_views} views
                                                    </Typography>
                                                </Box>
                                            </Paper>
                                        </Grid>
                                    </Grid>
                                )}

                                {activeTab === 1 && (
                                    <Box>
                                        <Typography variant="subtitle1" gutterBottom>
                                            Sales Trend
                                        </Typography>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <LineChart data={selectedProduct.sales_trend}>
                                                <CartesianGrid strokeDasharray="3 3" />
                                                <XAxis dataKey="date" />
                                                <YAxis />
                                                <Tooltip />
                                                <Legend />
                                                <Line
                                                    type="monotone"
                                                    dataKey="sales"
                                                    stroke="#8884d8"
                                                    name="Sales"
                                                />
                                                <Line
                                                    type="monotone"
                                                    dataKey="units"
                                                    stroke="#82ca9d"
                                                    name="Units"
                                                />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </Box>
                                )}

                                {activeTab === 2 && (
                                    <Box>
                                        <Typography variant="subtitle1" gutterBottom>
                                            Review Distribution
                                        </Typography>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <PieChart>
                                                <Pie
                                                    data={selectedProduct.rating_distribution}
                                                    cx="50%"
                                                    cy="50%"
                                                    labelLine={false}
                                                    outerRadius={80}
                                                    fill="#8884d8"
                                                    dataKey="value"
                                                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                                >
                                                    {selectedProduct.rating_distribution.map((entry, index) => (
                                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                    ))}
                                                </Pie>
                                                <Tooltip />
                                            </PieChart>
                                        </ResponsiveContainer>
                                    </Box>
                                )}

                                {activeTab === 3 && (
                                    <Box>
                                        <Typography variant="subtitle1" gutterBottom>
                                            Inventory Metrics
                                        </Typography>
                                        <Grid container spacing={2}>
                                            <Grid item xs={12} md={6}>
                                                <Paper sx={{ p: 2 }}>
                                                    <Typography variant="subtitle2" color="textSecondary">
                                                        Stock Level
                                                    </Typography>
                                                    <Typography variant="h4">
                                                        {selectedProduct.current_stock}
                                                    </Typography>
                                                    <Typography variant="body2" color="textSecondary">
                                                        {selectedProduct.stock_status}
                                                    </Typography>
                                                </Paper>
                                            </Grid>
                                            <Grid item xs={12} md={6}>
                                                <Paper sx={{ p: 2 }}>
                                                    <Typography variant="subtitle2" color="textSecondary">
                                                        Stock Turnover
                                                    </Typography>
                                                    <Typography variant="h4">
                                                        {selectedProduct.stock_turnover.toFixed(2)}
                                                    </Typography>
                                                    <Typography variant="body2" color="textSecondary">
                                                        Days to sell out: {selectedProduct.days_to_sell_out}
                                                    </Typography>
                                                </Paper>
                                            </Grid>
                                        </Grid>
                                    </Box>
                                )}
                            </CardContent>
                        </Card>
                    )}
                </Grid>
            </Grid>
        </Box>
    );
};

export default ProductPerformance; 