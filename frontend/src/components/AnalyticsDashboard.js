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
    DatePicker,
    Button,
    CircularProgress,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    Tabs,
    Tab,
    TextField,
    IconButton,
    Tooltip
} from '@mui/material';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartsTooltip,
    Legend,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    LineChart,
    Line,
    AreaChart,
    Area,
    ScatterChart,
    Scatter
} from 'recharts';
import { DateRange, Download, Refresh, TrendingUp, TrendingDown, Equalizer } from '@mui/icons-material';
import analyticsService from '../services/analyticsService';
import { useAuth } from '../contexts/AuthContext';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658'];

const AnalyticsDashboard = () => {
    const { user } = useAuth();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [timeRange, setTimeRange] = useState('7d');
    const [startDate, setStartDate] = useState(new Date(Date.now() - 7 * 24 * 60 * 60 * 1000));
    const [endDate, setEndDate] = useState(new Date());
    const [salesData, setSalesData] = useState(null);
    const [productData, setProductData] = useState(null);
    const [customerData, setCustomerData] = useState(null);
    const [supplierData, setSupplierData] = useState(null);
    const [financialData, setFinancialData] = useState(null);
    const [activeTab, setActiveTab] = useState(0);
    const [exportFormat, setExportFormat] = useState('csv');
    const [autoRefresh, setAutoRefresh] = useState(false);

    useEffect(() => {
        fetchAnalytics();
        if (autoRefresh) {
            const interval = setInterval(fetchAnalytics, 300000); // Refresh every 5 minutes
            return () => clearInterval(interval);
        }
    }, [timeRange, startDate, endDate, autoRefresh]);

    const fetchAnalytics = async () => {
        try {
            setLoading(true);
            const [sales, financial, products, customers, suppliers] = await Promise.all([
                analyticsService.getSalesAnalytics(startDate, endDate),
                analyticsService.getFinancialReports(startDate, endDate),
                analyticsService.getProductAnalytics(),
                analyticsService.getCustomerAnalytics(),
                analyticsService.getSupplierAnalytics()
            ]);

            setSalesData(sales.data);
            setFinancialData(financial.data[0]);
            setProductData(products.data);
            setCustomerData(customers.data);
            setSupplierData(suppliers.data);
            setError(null);
        } catch (err) {
            setError('Failed to fetch analytics data');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleTimeRangeChange = (event) => {
        const range = event.target.value;
        setTimeRange(range);
        
        const now = new Date();
        switch (range) {
            case '7d':
                setStartDate(new Date(now - 7 * 24 * 60 * 60 * 1000));
                break;
            case '30d':
                setStartDate(new Date(now - 30 * 24 * 60 * 60 * 1000));
                break;
            case '90d':
                setStartDate(new Date(now - 90 * 24 * 60 * 60 * 1000));
                break;
            case 'custom':
                break;
        }
        setEndDate(now);
    };

    const handleExport = async () => {
        try {
            const data = {
                sales: salesData,
                financial: financialData,
                products: productData,
                customers: customerData,
                suppliers: supplierData
            };
            
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `analytics-${new Date().toISOString()}.${exportFormat}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (err) {
            console.error('Failed to export data:', err);
        }
    };

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
                <Typography variant="h4">Analytics Dashboard</Typography>
                <Box display="flex" gap={2} alignItems="center">
                    <FormControl sx={{ minWidth: 120 }}>
                        <InputLabel>Time Range</InputLabel>
                        <Select
                            value={timeRange}
                            onChange={handleTimeRangeChange}
                            label="Time Range"
                        >
                            <MenuItem value="7d">Last 7 Days</MenuItem>
                            <MenuItem value="30d">Last 30 Days</MenuItem>
                            <MenuItem value="90d">Last 90 Days</MenuItem>
                            <MenuItem value="custom">Custom Range</MenuItem>
                        </Select>
                    </FormControl>
                    {timeRange === 'custom' && (
                        <>
                            <DatePicker
                                label="Start Date"
                                value={startDate}
                                onChange={setStartDate}
                                renderInput={(params) => <TextField {...params} />}
                            />
                            <DatePicker
                                label="End Date"
                                value={endDate}
                                onChange={setEndDate}
                                renderInput={(params) => <TextField {...params} />}
                            />
                        </>
                    )}
                    <Tooltip title="Refresh Data">
                        <IconButton onClick={fetchAnalytics}>
                            <Refresh />
                        </IconButton>
                    </Tooltip>
                    <Tooltip title="Auto Refresh">
                        <IconButton 
                            onClick={() => setAutoRefresh(!autoRefresh)}
                            color={autoRefresh ? 'primary' : 'default'}
                        >
                            <Equalizer />
                        </IconButton>
                    </Tooltip>
                    <FormControl sx={{ minWidth: 120 }}>
                        <InputLabel>Export Format</InputLabel>
                        <Select
                            value={exportFormat}
                            onChange={(e) => setExportFormat(e.target.value)}
                            label="Export Format"
                        >
                            <MenuItem value="csv">CSV</MenuItem>
                            <MenuItem value="json">JSON</MenuItem>
                            <MenuItem value="excel">Excel</MenuItem>
                        </Select>
                    </FormControl>
                    <Button
                        variant="contained"
                        startIcon={<Download />}
                        onClick={handleExport}
                    >
                        Export
                    </Button>
                </Box>
            </Box>

            {error && (
                <Typography color="error" mb={2}>
                    {error}
                </Typography>
            )}

            <Tabs
                value={activeTab}
                onChange={(e, newValue) => setActiveTab(newValue)}
                sx={{ mb: 3 }}
            >
                <Tab label="Overview" />
                <Tab label="Products" />
                <Tab label="Customers" />
                <Tab label="Suppliers" />
                <Tab label="Financial" />
            </Tabs>

            {activeTab === 0 && (
                <Grid container spacing={3}>
                    {/* Sales Overview */}
                    <Grid item xs={12} md={6}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Sales Overview
                                </Typography>
                                <ResponsiveContainer width="100%" height={300}>
                                    <AreaChart data={salesData}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="date" />
                                        <YAxis />
                                        <RechartsTooltip />
                                        <Legend />
                                        <Area
                                            type="monotone"
                                            dataKey="total_sales"
                                            stroke="#8884d8"
                                            fill="#8884d8"
                                            name="Total Sales"
                                        />
                                        <Area
                                            type="monotone"
                                            dataKey="total_orders"
                                            stroke="#82ca9d"
                                            fill="#82ca9d"
                                            name="Total Orders"
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </Grid>

                    {/* Sales by Category */}
                    <Grid item xs={12} md={6}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Sales by Category
                                </Typography>
                                <ResponsiveContainer width="100%" height={300}>
                                    <PieChart>
                                        <Pie
                                            data={Object.entries(salesData?.sales_by_category || {}).map(([name, value]) => ({
                                                name,
                                                value
                                            }))}
                                            cx="50%"
                                            cy="50%"
                                            labelLine={false}
                                            outerRadius={80}
                                            fill="#8884d8"
                                            dataKey="value"
                                            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                        >
                                            {Object.entries(salesData?.sales_by_category || {}).map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <RechartsTooltip />
                                    </PieChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </Grid>

                    {/* Key Metrics */}
                    <Grid item xs={12}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Key Metrics
                                </Typography>
                                <Grid container spacing={2}>
                                    <Grid item xs={12} md={3}>
                                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                                            <Typography variant="subtitle2" color="textSecondary">
                                                Total Revenue
                                            </Typography>
                                            <Typography variant="h4">
                                                ${financialData?.total_revenue.toFixed(2)}
                                            </Typography>
                                            <Box display="flex" alignItems="center" justifyContent="center">
                                                <TrendingUp color="success" />
                                                <Typography variant="body2" color="success.main">
                                                    +12.5%
                                                </Typography>
                                            </Box>
                                        </Paper>
                                    </Grid>
                                    <Grid item xs={12} md={3}>
                                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                                            <Typography variant="subtitle2" color="textSecondary">
                                                Gross Profit
                                            </Typography>
                                            <Typography variant="h4">
                                                ${financialData?.gross_profit.toFixed(2)}
                                            </Typography>
                                            <Box display="flex" alignItems="center" justifyContent="center">
                                                <TrendingUp color="success" />
                                                <Typography variant="body2" color="success.main">
                                                    +8.3%
                                                </Typography>
                                            </Box>
                                        </Paper>
                                    </Grid>
                                    <Grid item xs={12} md={3}>
                                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                                            <Typography variant="subtitle2" color="textSecondary">
                                                Net Profit
                                            </Typography>
                                            <Typography variant="h4">
                                                ${financialData?.net_profit.toFixed(2)}
                                            </Typography>
                                            <Box display="flex" alignItems="center" justifyContent="center">
                                                <TrendingDown color="error" />
                                                <Typography variant="body2" color="error.main">
                                                    -2.1%
                                                </Typography>
                                            </Box>
                                        </Paper>
                                    </Grid>
                                    <Grid item xs={12} md={3}>
                                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                                            <Typography variant="subtitle2" color="textSecondary">
                                                Profit Margin
                                            </Typography>
                                            <Typography variant="h4">
                                                {(financialData?.profit_margin * 100).toFixed(1)}%
                                            </Typography>
                                            <Box display="flex" alignItems="center" justifyContent="center">
                                                <TrendingDown color="error" />
                                                <Typography variant="body2" color="error.main">
                                                    -1.2%
                                                </Typography>
                                            </Box>
                                        </Paper>
                                    </Grid>
                                </Grid>
                            </CardContent>
                        </Card>
                    </Grid>

                    {/* Top Selling Products */}
                    <Grid item xs={12}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Top Selling Products
                                </Typography>
                                <TableContainer>
                                    <Table>
                                        <TableHead>
                                            <TableRow>
                                                <TableCell>Product</TableCell>
                                                <TableCell align="right">Total Sales</TableCell>
                                                <TableCell align="right">Units Sold</TableCell>
                                                <TableCell align="right">Revenue</TableCell>
                                                <TableCell align="right">Growth</TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {salesData?.top_selling_products.map((product) => (
                                                <TableRow key={product.product_id}>
                                                    <TableCell>{product.name}</TableCell>
                                                    <TableCell align="right">
                                                        ${product.total_sales.toFixed(2)}
                                                    </TableCell>
                                                    <TableCell align="right">
                                                        {product.units_sold}
                                                    </TableCell>
                                                    <TableCell align="right">
                                                        ${(product.total_sales * product.units_sold).toFixed(2)}
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

                    {/* Sales by Channel */}
                    <Grid item xs={12} md={6}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Sales by Channel
                                </Typography>
                                <ResponsiveContainer width="100%" height={300}>
                                    <BarChart data={Object.entries(financialData?.sales_by_channel || {}).map(([name, value]) => ({
                                        name,
                                        value
                                    }))}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="name" />
                                        <YAxis />
                                        <RechartsTooltip />
                                        <Bar dataKey="value" fill="#8884d8" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </Grid>

                    {/* Expenses by Category */}
                    <Grid item xs={12} md={6}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Expenses by Category
                                </Typography>
                                <ResponsiveContainer width="100%" height={300}>
                                    <PieChart>
                                        <Pie
                                            data={Object.entries(financialData?.expenses_by_category || {}).map(([name, value]) => ({
                                                name,
                                                value
                                            }))}
                                            cx="50%"
                                            cy="50%"
                                            labelLine={false}
                                            outerRadius={80}
                                            fill="#8884d8"
                                            dataKey="value"
                                            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                        >
                                            {Object.entries(financialData?.expenses_by_category || {}).map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <RechartsTooltip />
                                    </PieChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            )}

            {activeTab === 1 && (
                <Grid container spacing={3}>
                    {/* Product Performance */}
                    <Grid item xs={12}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Product Performance
                                </Typography>
                                <ResponsiveContainer width="100%" height={400}>
                                    <ScatterChart>
                                        <CartesianGrid />
                                        <XAxis type="number" dataKey="conversion_rate" name="Conversion Rate" />
                                        <YAxis type="number" dataKey="profit_margin" name="Profit Margin" />
                                        <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} />
                                        <Scatter
                                            data={productData?.map(p => ({
                                                conversion_rate: p.conversion_rate,
                                                profit_margin: p.profit_margin,
                                                name: p.name
                                            }))}
                                            fill="#8884d8"
                                        />
                                    </ScatterChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            )}

            {activeTab === 2 && (
                <Grid container spacing={3}>
                    {/* Customer Segmentation */}
                    <Grid item xs={12}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Customer Segmentation
                                </Typography>
                                <ResponsiveContainer width="100%" height={400}>
                                    <ScatterChart>
                                        <CartesianGrid />
                                        <XAxis type="number" dataKey="purchase_frequency" name="Purchase Frequency" />
                                        <YAxis type="number" dataKey="customer_lifetime_value" name="Customer Value" />
                                        <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} />
                                        <Scatter
                                            data={customerData?.map(c => ({
                                                purchase_frequency: c.purchase_frequency,
                                                customer_lifetime_value: c.customer_lifetime_value,
                                                name: c.customer_id
                                            }))}
                                            fill="#8884d8"
                                        />
                                    </ScatterChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            )}

            {activeTab === 3 && (
                <Grid container spacing={3}>
                    {/* Supplier Performance */}
                    <Grid item xs={12}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Supplier Performance
                                </Typography>
                                <ResponsiveContainer width="100%" height={400}>
                                    <ScatterChart>
                                        <CartesianGrid />
                                        <XAxis type="number" dataKey="on_time_delivery_rate" name="On-time Delivery" />
                                        <YAxis type="number" dataKey="profit_margin" name="Profit Margin" />
                                        <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} />
                                        <Scatter
                                            data={supplierData?.map(s => ({
                                                on_time_delivery_rate: s.on_time_delivery_rate,
                                                profit_margin: s.profit_margin,
                                                name: s.supplier_id
                                            }))}
                                            fill="#8884d8"
                                        />
                                    </ScatterChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            )}

            {activeTab === 4 && (
                <Grid container spacing={3}>
                    {/* Financial Trends */}
                    <Grid item xs={12}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Financial Trends
                                </Typography>
                                <ResponsiveContainer width="100%" height={400}>
                                    <LineChart data={financialData?.trends}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="date" />
                                        <YAxis />
                                        <RechartsTooltip />
                                        <Legend />
                                        <Line
                                            type="monotone"
                                            dataKey="revenue"
                                            stroke="#8884d8"
                                            name="Revenue"
                                        />
                                        <Line
                                            type="monotone"
                                            dataKey="expenses"
                                            stroke="#ff7300"
                                            name="Expenses"
                                        />
                                        <Line
                                            type="monotone"
                                            dataKey="profit"
                                            stroke="#82ca9d"
                                            name="Profit"
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            )}
        </Box>
    );
};

export default AnalyticsDashboard; 