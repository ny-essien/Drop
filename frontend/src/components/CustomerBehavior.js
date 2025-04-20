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
    Divider
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
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar
} from 'recharts';
import {
    Person,
    ShoppingCart,
    Favorite,
    Category,
    TrendingUp,
    TrendingDown,
    Star,
    AccessTime
} from '@mui/icons-material';
import analyticsService from '../services/analyticsService';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658'];

const CustomerBehavior = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [customers, setCustomers] = useState([]);
    const [selectedCustomer, setSelectedCustomer] = useState(null);
    const [timeRange, setTimeRange] = useState('30d');
    const [activeTab, setActiveTab] = useState(0);
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        fetchCustomerAnalytics();
    }, [timeRange]);

    const fetchCustomerAnalytics = async () => {
        try {
            setLoading(true);
            const response = await analyticsService.getCustomerAnalytics();
            setCustomers(response.data);
            if (response.data.length > 0) {
                setSelectedCustomer(response.data[0]);
            }
            setError(null);
        } catch (err) {
            setError('Failed to fetch customer analytics');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const filteredCustomers = customers.filter(customer =>
        customer.name.toLowerCase().includes(searchQuery.toLowerCase())
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
                <Typography variant="h4">Customer Behavior Analysis</Typography>
                <Box display="flex" gap={2}>
                    <TextField
                        label="Search Customers"
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
                {/* Customer List */}
                <Grid item xs={12} md={4}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Customers
                            </Typography>
                            <List>
                                {filteredCustomers.map((customer) => (
                                    <React.Fragment key={customer.id}>
                                        <ListItem
                                            button
                                            selected={selectedCustomer?.id === customer.id}
                                            onClick={() => setSelectedCustomer(customer)}
                                        >
                                            <ListItemAvatar>
                                                <Avatar>
                                                    <Person />
                                                </Avatar>
                                            </ListItemAvatar>
                                            <ListItemText
                                                primary={customer.name}
                                                secondary={
                                                    <Box display="flex" alignItems="center" gap={1}>
                                                        <Typography variant="body2">
                                                            ${customer.total_spent.toFixed(2)}
                                                        </Typography>
                                                        <Typography variant="body2" color="textSecondary">
                                                            • {customer.total_orders} orders
                                                        </Typography>
                                                    </Box>
                                                }
                                            />
                                            <Chip
                                                label={customer.segment}
                                                size="small"
                                                color={
                                                    customer.segment === 'VIP' ? 'primary' :
                                                    customer.segment === 'Regular' ? 'success' :
                                                    'default'
                                                }
                                            />
                                        </ListItem>
                                        <Divider />
                                    </React.Fragment>
                                ))}
                            </List>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Customer Details */}
                <Grid item xs={12} md={8}>
                    {selectedCustomer && (
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    {selectedCustomer.name}
                                </Typography>
                                <Tabs
                                    value={activeTab}
                                    onChange={(e, newValue) => setActiveTab(newValue)}
                                    sx={{ mb: 3 }}
                                >
                                    <Tab label="Overview" />
                                    <Tab label="Purchase History" />
                                    <Tab label="Behavior" />
                                    <Tab label="Preferences" />
                                </Tabs>

                                {activeTab === 0 && (
                                    <Grid container spacing={2}>
                                        <Grid item xs={12} md={4}>
                                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                                <Typography variant="subtitle2" color="textSecondary">
                                                    Total Spent
                                                </Typography>
                                                <Typography variant="h4">
                                                    ${selectedCustomer.total_spent.toFixed(2)}
                                                </Typography>
                                                <Box display="flex" alignItems="center" justifyContent="center">
                                                    <ShoppingCart color="primary" />
                                                    <Typography variant="body2" color="textSecondary">
                                                        {selectedCustomer.total_orders} orders
                                                    </Typography>
                                                </Box>
                                            </Paper>
                                        </Grid>
                                        <Grid item xs={12} md={4}>
                                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                                <Typography variant="subtitle2" color="textSecondary">
                                                    Average Order Value
                                                </Typography>
                                                <Typography variant="h4">
                                                    ${selectedCustomer.average_order_value.toFixed(2)}
                                                </Typography>
                                                <Box display="flex" alignItems="center" justifyContent="center">
                                                    {selectedCustomer.growth > 0 ? (
                                                        <TrendingUp color="success" />
                                                    ) : (
                                                        <TrendingDown color="error" />
                                                    )}
                                                    <Typography
                                                        variant="body2"
                                                        color={selectedCustomer.growth > 0 ? 'success.main' : 'error.main'}
                                                    >
                                                        {Math.abs(selectedCustomer.growth).toFixed(1)}%
                                                    </Typography>
                                                </Box>
                                            </Paper>
                                        </Grid>
                                        <Grid item xs={12} md={4}>
                                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                                <Typography variant="subtitle2" color="textSecondary">
                                                    Purchase Frequency
                                                </Typography>
                                                <Typography variant="h4">
                                                    {selectedCustomer.purchase_frequency.toFixed(1)}
                                                </Typography>
                                                <Box display="flex" alignItems="center" justifyContent="center">
                                                    <AccessTime color="primary" />
                                                    <Typography variant="body2" color="textSecondary">
                                                        orders/month
                                                    </Typography>
                                                </Box>
                                            </Paper>
                                        </Grid>
                                    </Grid>
                                )}

                                {activeTab === 1 && (
                                    <Box>
                                        <Typography variant="subtitle1" gutterBottom>
                                            Purchase History
                                        </Typography>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <LineChart data={selectedCustomer.purchase_history}>
                                                <CartesianGrid strokeDasharray="3 3" />
                                                <XAxis dataKey="date" />
                                                <YAxis />
                                                <Tooltip />
                                                <Legend />
                                                <Line
                                                    type="monotone"
                                                    dataKey="amount"
                                                    stroke="#8884d8"
                                                    name="Amount"
                                                />
                                                <Line
                                                    type="monotone"
                                                    dataKey="items"
                                                    stroke="#82ca9d"
                                                    name="Items"
                                                />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </Box>
                                )}

                                {activeTab === 2 && (
                                    <Box>
                                        <Typography variant="subtitle1" gutterBottom>
                                            Customer Behavior
                                        </Typography>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <RadarChart data={selectedCustomer.behavior_metrics}>
                                                <PolarGrid />
                                                <PolarAngleAxis dataKey="metric" />
                                                <PolarRadiusAxis />
                                                <Radar
                                                    name="Score"
                                                    dataKey="value"
                                                    stroke="#8884d8"
                                                    fill="#8884d8"
                                                    fillOpacity={0.6}
                                                />
                                            </RadarChart>
                                        </ResponsiveContainer>
                                    </Box>
                                )}

                                {activeTab === 3 && (
                                    <Box>
                                        <Typography variant="subtitle1" gutterBottom>
                                            Category Preferences
                                        </Typography>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <PieChart>
                                                <Pie
                                                    data={selectedCustomer.category_preferences}
                                                    cx="50%"
                                                    cy="50%"
                                                    labelLine={false}
                                                    outerRadius={80}
                                                    fill="#8884d8"
                                                    dataKey="value"
                                                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                                >
                                                    {selectedCustomer.category_preferences.map((entry, index) => (
                                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                    ))}
                                                </Pie>
                                                <Tooltip />
                                            </PieChart>
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

export default CustomerBehavior; 