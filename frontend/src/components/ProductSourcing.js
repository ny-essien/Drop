import React, { useState, useEffect } from 'react';
import {
    Box,
    Container,
    Typography,
    Grid,
    TextField,
    Button,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
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
    CardActions
} from '@mui/material';
import productSourcingService from '../services/productSourcingService';

const ProductSourcing = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState(0);
    const [searchQuery, setSearchQuery] = useState('');
    const [suppliers, setSuppliers] = useState([]);
    const [selectedSupplier, setSelectedSupplier] = useState('');
    const [category, setCategory] = useState('');
    const [importLimit, setImportLimit] = useState(100);
    const [products, setProducts] = useState([]);
    const [priceComparisons, setPriceComparisons] = useState([]);
    const [variations, setVariations] = useState([]);

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
    };

    const handleSearchSuppliers = async () => {
        try {
            setLoading(true);
            setError(null);
            const result = await productSourcingService.searchSuppliers(searchQuery);
            setSuppliers(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleBulkImport = async () => {
        try {
            setLoading(true);
            setError(null);
            const result = await productSourcingService.bulkImportProducts(
                selectedSupplier,
                category,
                importLimit
            );
            setProducts(result.products);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleComparePrices = async (productId) => {
        try {
            setLoading(true);
            setError(null);
            const result = await productSourcingService.comparePrices(productId);
            setPriceComparisons(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleGetVariations = async (productId) => {
        try {
            setLoading(true);
            setError(null);
            const result = await productSourcingService.getProductVariations(productId);
            setVariations(result);
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
                    Product Sourcing
                </Typography>

                <Paper sx={{ p: 2, mb: 2 }}>
                    <Tabs value={activeTab} onChange={handleTabChange}>
                        <Tab label="Supplier Search" />
                        <Tab label="Bulk Import" />
                        <Tab label="Price Comparison" />
                        <Tab label="Product Variations" />
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
                            <Grid item xs={12} md={8}>
                                <TextField
                                    fullWidth
                                    label="Search Suppliers"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                />
                            </Grid>
                            <Grid item xs={12} md={4}>
                                <Button
                                    fullWidth
                                    variant="contained"
                                    onClick={handleSearchSuppliers}
                                >
                                    Search
                                </Button>
                            </Grid>
                        </Grid>

                        <TableContainer sx={{ mt: 2 }}>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Name</TableCell>
                                        <TableCell>Categories</TableCell>
                                        <TableCell>Rating</TableCell>
                                        <TableCell>Action</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {suppliers.map((supplier) => (
                                        <TableRow key={supplier._id}>
                                            <TableCell>{supplier.name}</TableCell>
                                            <TableCell>
                                                {supplier.product_categories.join(', ')}
                                            </TableCell>
                                            <TableCell>{supplier.rating}</TableCell>
                                            <TableCell>
                                                <Button
                                                    variant="outlined"
                                                    onClick={() => setSelectedSupplier(supplier._id)}
                                                >
                                                    Select
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>
                )}

                {activeTab === 1 && (
                    <Paper sx={{ p: 2 }}>
                        <Grid container spacing={2}>
                            <Grid item xs={12} md={4}>
                                <FormControl fullWidth>
                                    <InputLabel>Category</InputLabel>
                                    <Select
                                        value={category}
                                        onChange={(e) => setCategory(e.target.value)}
                                    >
                                        <MenuItem value="electronics">Electronics</MenuItem>
                                        <MenuItem value="clothing">Clothing</MenuItem>
                                        <MenuItem value="home">Home & Garden</MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={12} md={4}>
                                <TextField
                                    fullWidth
                                    type="number"
                                    label="Import Limit"
                                    value={importLimit}
                                    onChange={(e) => setImportLimit(parseInt(e.target.value))}
                                />
                            </Grid>
                            <Grid item xs={12} md={4}>
                                <Button
                                    fullWidth
                                    variant="contained"
                                    onClick={handleBulkImport}
                                >
                                    Import Products
                                </Button>
                            </Grid>
                        </Grid>

                        <Grid container spacing={2} sx={{ mt: 2 }}>
                            {products.map((product) => (
                                <Grid item xs={12} sm={6} md={4} key={product._id}>
                                    <Card>
                                        <CardContent>
                                            <Typography variant="h6">{product.name}</Typography>
                                            <Typography color="textSecondary">
                                                ${product.price}
                                            </Typography>
                                            <Typography variant="body2">
                                                {product.description}
                                            </Typography>
                                        </CardContent>
                                        <CardActions>
                                            <Button
                                                size="small"
                                                onClick={() => handleComparePrices(product._id)}
                                            >
                                                Compare Prices
                                            </Button>
                                            <Button
                                                size="small"
                                                onClick={() => handleGetVariations(product._id)}
                                            >
                                                View Variations
                                            </Button>
                                        </CardActions>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    </Paper>
                )}

                {activeTab === 2 && (
                    <Paper sx={{ p: 2 }}>
                        <TableContainer>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Supplier</TableCell>
                                        <TableCell>Price</TableCell>
                                        <TableCell>Shipping</TableCell>
                                        <TableCell>Total</TableCell>
                                        <TableCell>Stock</TableCell>
                                        <TableCell>Delivery</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {priceComparisons.map((comparison) => (
                                        <TableRow key={comparison.supplier_id}>
                                            <TableCell>{comparison.supplier_name}</TableCell>
                                            <TableCell>${comparison.price}</TableCell>
                                            <TableCell>${comparison.shipping_cost}</TableCell>
                                            <TableCell>
                                                ${comparison.price + comparison.shipping_cost}
                                            </TableCell>
                                            <TableCell>{comparison.stock_quantity}</TableCell>
                                            <TableCell>{comparison.estimated_delivery}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>
                )}

                {activeTab === 3 && (
                    <Paper sx={{ p: 2 }}>
                        <TableContainer>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Name</TableCell>
                                        <TableCell>Attributes</TableCell>
                                        <TableCell>Price</TableCell>
                                        <TableCell>Stock</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {variations.map((variation) => (
                                        <TableRow key={variation._id}>
                                            <TableCell>{variation.name}</TableCell>
                                            <TableCell>
                                                {Object.entries(variation.attributes)
                                                    .map(([key, value]) => `${key}: ${value}`)
                                                    .join(', ')}
                                            </TableCell>
                                            <TableCell>${variation.price}</TableCell>
                                            <TableCell>{variation.stock_quantity}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>
                )}
            </Box>
        </Container>
    );
};

export default ProductSourcing; 