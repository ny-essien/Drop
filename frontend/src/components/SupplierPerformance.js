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
    Button,
    Avatar,
    List,
    ListItem,
    ListItemAvatar,
    ListItemText,
    Divider,
    Rating
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
    Cell,
    AreaChart,
    Area
} from 'recharts';
import {
    Store,
    LocalShipping,
    TrendingUp,
    TrendingDown,
    Star,
    AccessTime,
    Warning
} from '@mui/icons-material';
import analyticsService from '../services/analyticsService';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658'];

const SupplierPerformance = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [suppliers, setSuppliers] = useState([]);
    const [selectedSupplier, setSelectedSupplier] = useState(null);
    const [timeRange, setTimeRange] = useState('30d');
    const [activeTab, setActiveTab] = useState(0);
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        fetchSupplierAnalytics();
    }, [timeRange]);

    const fetchSupplierAnalytics = async () => {
        try {
            setLoading(true);
            const response = await analyticsService.getSupplierAnalytics();
            setSuppliers(response.data);
            if (response.data.length > 0) {
                setSelectedSupplier(response.data[0]);
            }
            setError(null);
        } catch (err) {
            setError('Failed to fetch supplier analytics');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const filteredSuppliers = suppliers.filter(supplier =>
        supplier.name.toLowerCase().includes(searchQuery.toLowerCase())
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
                <Typography variant="h4">Supplier Performance</Typography>
                <Box display="flex" gap={2}>
                    <TextField
                        label="Search Suppliers"
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
                {/* Supplier List */}
                <Grid item xs={12} md={4}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Suppliers
                            </Typography>
                            <List>
                                {filteredSuppliers.map((supplier) => (
                                    <React.Fragment key={supplier.id}>
                                        <ListItem
                                            button
                                            selected={selectedSupplier?.id === supplier.id}
                                            onClick={() => setSelectedSupplier(supplier)}
                                        >
                                            <ListItemAvatar>
                                                <Avatar>
                                                    <Store />
                                                </Avatar>
                                            </ListItemAvatar>
                                            <ListItemText
                                                primary={supplier.name}
                                                secondary={
                                                    <Box display="flex" alignItems="center" gap={1}>
                                                        <Typography variant="body2">
                                                            ${supplier.total_sales.toFixed(2)}
                                                        </Typography>
                                                        <Typography variant="body2" color="textSecondary">
                                                            • {supplier.total_products} products
                                                        </Typography>
                                                    </Box>
                                                }
                                            />
                                            <Box display="flex" alignItems="center" gap={1}>
                                                <Rating
                                                    value={supplier.rating}
                                                    precision={0.5}
                                                    readOnly
                                                    size="small"
                                                />
                                                <Chip
                                                    label={supplier.status}
                                                    size="small"
                                                    color={
                                                        supplier.status === 'Active' ? 'success' :
                                                        supplier.status === 'Warning' ? 'warning' :
                                                        'error'
                                                    }
                                                />
                                            </Box>
                                        </ListItem>
                                        <Divider />
                                    </React.Fragment>
                                ))}
                            </List>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Supplier Details */}
                <Grid item xs={12} md={8}>
                    {selectedSupplier && (
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    {selectedSupplier.name}
                                </Typography>
                                <Tabs
                                    value={activeTab}
                                    onChange={(e, newValue) => setActiveTab(newValue)}
                                    sx={{ mb: 3 }}
                                >
                                    <Tab label="Overview" />
                                    <Tab label="Performance" />
                                    <Tab label="Products" />
                                    <Tab label="Delivery" />
                                </Tabs>

                                {activeTab === 0 && (
                                    <Grid container spacing={2}>
                                        <Grid item xs={12} md={4}>
                                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                                <Typography variant="subtitle2" color="textSecondary">
                                                    Total Sales
                                                </Typography>
                                                <Typography variant="h4">
                                                    ${selectedSupplier.total_sales.toFixed(2)}
                                                </Typography>
                                                <Box display="flex" alignItems="center" justifyContent="center">
                                                    <Store color="primary" />
                                                    <Typography variant="body2" color="textSecondary">
                                                        {selectedSupplier.total_products} products
                                                    </Typography>
                                                </Box>
                                            </Paper>
                                        </Grid>
                                        <Grid item xs={12} md={4}>
                                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                                <Typography variant="subtitle2" color="textSecondary">
                                                    Average Rating
                                                </Typography>
                                                <Box display="flex" alignItems="center" justifyContent="center">
                                                    <Rating
                                                        value={selectedSupplier.rating}
                                                        precision={0.5}
                                                        readOnly
                                                    />
                                                </Box>
                                                <Typography variant="body2" color="textSecondary">
                                                    {selectedSupplier.total_reviews} reviews
                                                </Typography>
                                            </Paper>
                                        </Grid>
                                        <Grid item xs={12} md={4}>
                                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                                <Typography variant="subtitle2" color="textSecondary">
                                                    On-Time Delivery
                                                </Typography>
                                                <Typography variant="h4">
                                                    {selectedSupplier.on_time_delivery_rate}%
                                                </Typography>
                                                <Box display="flex" alignItems="center" justifyContent="center">
                                                    <LocalShipping color="primary" />
                                                    <Typography variant="body2" color="textSecondary">
                                                        {selectedSupplier.total_orders} orders
                                                    </Typography>
                                                </Box>
                                            </Paper>
                                        </Grid>
                                    </Grid>
                                )}

                                {activeTab === 1 && (
                                    <Box>
                                        <Typography variant="subtitle1" gutterBottom>
                                            Performance Metrics
                                        </Typography>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <AreaChart data={selectedSupplier.performance_metrics}>
                                                <CartesianGrid strokeDasharray="3 3" />
                                                <XAxis dataKey="date" />
                                                <YAxis />
                                                <Tooltip />
                                                <Legend />
                                                <Area
                                                    type="monotone"
                                                    dataKey="sales"
                                                    stroke="#8884d8"
                                                    fill="#8884d8"
                                                    fillOpacity={0.3}
                                                    name="Sales"
                                                />
                                                <Area
                                                    type="monotone"
                                                    dataKey="orders"
                                                    stroke="#82ca9d"
                                                    fill="#82ca9d"
                                                    fillOpacity={0.3}
                                                    name="Orders"
                                                />
                                            </AreaChart>
                                        </ResponsiveContainer>
                                    </Box>
                                )}

                                {activeTab === 2 && (
                                    <Box>
                                        <Typography variant="subtitle1" gutterBottom>
                                            Top Products
                                        </Typography>
                                        <TableContainer component={Paper}>
                                            <Table>
                                                <TableHead>
                                                    <TableRow>
                                                        <TableCell>Product</TableCell>
                                                        <TableCell align="right">Sales</TableCell>
                                                        <TableCell align="right">Units</TableCell>
                                                        <TableCell align="right">Rating</TableCell>
                                                    </TableRow>
                                                </TableHead>
                                                <TableBody>
                                                    {selectedSupplier.top_products.map((product) => (
                                                        <TableRow key={product.id}>
                                                            <TableCell>{product.name}</TableCell>
                                                            <TableCell align="right">
                                                                ${product.sales.toFixed(2)}
                                                            </TableCell>
                                                            <TableCell align="right">
                                                                {product.units}
                                                            </TableCell>
                                                            <TableCell align="right">
                                                                <Rating
                                                                    value={product.rating}
                                                                    precision={0.5}
                                                                    readOnly
                                                                    size="small"
                                                                />
                                                            </TableCell>
                                                        </TableRow>
                                                    ))}
                                                </TableBody>
                                            </Table>
                                        </TableContainer>
                                    </Box>
                                )}

                                {activeTab === 3 && (
                                    <Box>
                                        <Typography variant="subtitle1" gutterBottom>
                                            Delivery Performance
                                        </Typography>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <BarChart data={selectedSupplier.delivery_metrics}>
                                                <CartesianGrid strokeDasharray="3 3" />
                                                <XAxis dataKey="month" />
                                                <YAxis />
                                                <Tooltip />
                                                <Legend />
                                                <Bar
                                                    dataKey="on_time"
                                                    fill="#82ca9d"
                                                    name="On Time"
                                                />
                                                <Bar
                                                    dataKey="late"
                                                    fill="#ff8042"
                                                    name="Late"
                                                />
                                            </BarChart>
                                        </ResponsiveContainer>
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

export default SupplierPerformance; 