import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Divider,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import PaymentIcon from '@mui/icons-material/Payment';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

const OrderDetails = () => {
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { orderId } = useParams();
  const { user } = useAuth();

  useEffect(() => {
    fetchOrderDetails();
    // Poll for status updates every 30 seconds
    const interval = setInterval(fetchOrderStatus, 30000);
    return () => clearInterval(interval);
  }, [orderId]);

  const fetchOrderDetails = async () => {
    try {
      const response = await api.get(`/cart/orders/${orderId}`);
      setOrder(response.data);
    } catch (err) {
      setError('Failed to load order details');
    } finally {
      setLoading(false);
    }
  };

  const fetchOrderStatus = async () => {
    try {
      const response = await api.get(`/cart/orders/${orderId}/status`);
      if (order) {
        setOrder(prev => ({
          ...prev,
          status: response.data.status,
          payment_status: response.data.payment_status,
          tracking_number: response.data.tracking_number
        }));
      }
    } catch (err) {
      console.error('Failed to fetch order status:', err);
    }
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'warning';
      case 'processing':
        return 'info';
      case 'shipped':
        return 'success';
      case 'delivered':
        return 'success';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const getPaymentStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'warning';
      case 'paid':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Order Details
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Order Items
              </Typography>
              {order.items.map((item) => (
                <Box key={item.product_id} sx={{ mb: 2 }}>
                  <Grid container alignItems="center" spacing={2}>
                    <Grid item xs={12} sm={3}>
                      <img
                        src={item.image_url}
                        alt={item.name}
                        style={{ width: '100%', height: 'auto' }}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle1">{item.name}</Typography>
                      <Typography color="textSecondary">
                        Quantity: {item.quantity}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={3}>
                      <Typography variant="subtitle1" align="right">
                        ${(item.price * item.quantity).toFixed(2)}
                      </Typography>
                    </Grid>
                  </Grid>
                  <Divider sx={{ my: 2 }} />
                </Box>
              ))}
              <Box display="flex" justifyContent="space-between" mt={2}>
                <Typography variant="h6">Total</Typography>
                <Typography variant="h6">${order.total_amount.toFixed(2)}</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Order Status
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Chip
                  icon={<LocalShippingIcon />}
                  label={`Order Status: ${order.status}`}
                  color={getStatusColor(order.status)}
                  sx={{ mb: 1 }}
                />
                <Chip
                  icon={<PaymentIcon />}
                  label={`Payment Status: ${order.payment_status}`}
                  color={getPaymentStatusColor(order.payment_status)}
                />
              </Box>
              {order.tracking_number && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2">Tracking Number</Typography>
                  <Typography>{order.tracking_number}</Typography>
                </Box>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Shipping Address
              </Typography>
              <Typography>{order.shipping_address.name}</Typography>
              <Typography>{order.shipping_address.street}</Typography>
              <Typography>
                {order.shipping_address.city}, {order.shipping_address.state}{' '}
                {order.shipping_address.zip}
              </Typography>
              <Typography>{order.shipping_address.country}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default OrderDetails; 