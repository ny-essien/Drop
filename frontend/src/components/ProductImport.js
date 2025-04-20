import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import AddIcon from '@mui/icons-material/Add';

const ProductImport = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [importSource, setImportSource] = useState('');
  const [supplierId, setSupplierId] = useState('');
  const [suppliers, setSuppliers] = useState([]);
  const [importData, setImportData] = useState('');
  const [previewData, setPreviewData] = useState(null);
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);
  const { user } = useAuth();

  const handleImport = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const data = JSON.parse(importData);
      const response = await api.post(`/products/import/${importSource}`, {
        supplier_id: supplierId,
        data
      });

      setSuccess('Products imported successfully');
      setImportData('');
      setPreviewData(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to import products');
    } finally {
      setLoading(false);
    }
  };

  const handleBulkImport = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const data = JSON.parse(importData);
      const response = await api.post(`/products/import/bulk/${importSource}`, {
        supplier_id: supplierId,
        data
      });

      setSuccess('Products imported successfully');
      setImportData('');
      setPreviewData(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to import products');
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = () => {
    try {
      const data = JSON.parse(importData);
      setPreviewData(data);
      setPreviewDialogOpen(true);
    } catch (err) {
      setError('Invalid JSON data');
    }
  };

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Import Products
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Import Source</InputLabel>
                <Select
                  value={importSource}
                  onChange={(e) => setImportSource(e.target.value)}
                  label="Import Source"
                >
                  <MenuItem value="aliexpress">AliExpress</MenuItem>
                  <MenuItem value="amazon">Amazon</MenuItem>
                  <MenuItem value="ebay">eBay</MenuItem>
                  <MenuItem value="custom">Custom</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Supplier</InputLabel>
                <Select
                  value={supplierId}
                  onChange={(e) => setSupplierId(e.target.value)}
                  label="Supplier"
                >
                  {suppliers.map((supplier) => (
                    <MenuItem key={supplier.id} value={supplier.id}>
                      {supplier.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={10}
                label="Import Data (JSON)"
                value={importData}
                onChange={(e) => setImportData(e.target.value)}
                variant="outlined"
              />
            </Grid>
          </Grid>

          <Box mt={3} display="flex" gap={2}>
            <Button
              variant="contained"
              startIcon={<CloudUploadIcon />}
              onClick={handleImport}
              disabled={loading || !importData || !importSource || !supplierId}
            >
              Import Single
            </Button>
            <Button
              variant="contained"
              startIcon={<CloudUploadIcon />}
              onClick={handleBulkImport}
              disabled={loading || !importData || !importSource || !supplierId}
            >
              Bulk Import
            </Button>
            <Button
              variant="outlined"
              onClick={handlePreview}
              disabled={!importData}
            >
              Preview
            </Button>
          </Box>
        </CardContent>
      </Card>

      {loading && (
        <Box display="flex" justifyContent="center" my={3}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {success}
        </Alert>
      )}

      <Dialog
        open={previewDialogOpen}
        onClose={() => setPreviewDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Import Preview</DialogTitle>
        <DialogContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Price</TableCell>
                  <TableCell>Stock</TableCell>
                  <TableCell>Supplier Price</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {previewData?.map((item, index) => (
                  <TableRow key={index}>
                    <TableCell>{item.name}</TableCell>
                    <TableCell>${item.price}</TableCell>
                    <TableCell>{item.stock}</TableCell>
                    <TableCell>${item.supplier_price}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProductImport; 