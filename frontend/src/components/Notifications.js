import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    IconButton,
    Chip,
    Paper,
    Divider,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    MenuItem,
    Grid
} from '@mui/material';
import {
    Email as EmailIcon,
    LocalShipping as ShippingIcon,
    Cancel as CancelIcon,
    Warning as WarningIcon,
    CheckCircle as CheckCircleIcon,
    Delete as DeleteIcon,
    Refresh as RefreshIcon
} from '@mui/icons-material';
import { format } from 'date-fns';
import notificationService from '../services/notificationService';

const NotificationList = () => {
    const [notifications, setNotifications] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedNotification, setSelectedNotification] = useState(null);
    const [openDialog, setOpenDialog] = useState(false);
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        fetchNotifications();
    }, [filter]);

    const fetchNotifications = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await notificationService.getNotifications({
                type: filter === 'all' ? undefined : filter
            });
            setNotifications(response);
            setLoading(false);
        } catch (err) {
            setError('Failed to fetch notifications');
            setLoading(false);
        }
    };

    const handleNotificationClick = (notification) => {
        setSelectedNotification(notification);
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setSelectedNotification(null);
    };

    const handleDeleteNotification = async (notificationId) => {
        try {
            await notificationService.deleteNotification(notificationId);
            fetchNotifications();
        } catch (err) {
            setError('Failed to delete notification');
        }
    };

    const handleRetryNotification = async (notification) => {
        try {
            // Retry the specific notification type
            switch (notification.type) {
                case 'order_confirmation':
                    await notificationService.sendOrderConfirmation(notification.metadata.order_id);
                    break;
                case 'warehouse':
                    await notificationService.notifyWarehouse(notification.metadata.order_id);
                    break;
                case 'status_update':
                    await notificationService.sendStatusUpdate(notification.metadata.order_id);
                    break;
                case 'cancellation':
                    await notificationService.sendCancellationNotice(notification.metadata.order_id);
                    break;
                case 'low_stock':
                    await notificationService.sendLowStockAlert(notification.metadata.product_id);
                    break;
                default:
                    throw new Error('Unknown notification type');
            }
            handleCloseDialog();
            fetchNotifications();
        } catch (err) {
            setError('Failed to retry notification');
        }
    };

    const getNotificationIcon = (type) => {
        switch (type) {
            case 'order_confirmation':
                return <EmailIcon color="primary" />;
            case 'warehouse':
                return <ShippingIcon color="action" />;
            case 'cancellation':
                return <CancelIcon color="error" />;
            case 'low_stock':
                return <WarningIcon color="warning" />;
            case 'status_update':
                return <CheckCircleIcon color="success" />;
            default:
                return <EmailIcon />;
        }
    };

    const getNotificationStatus = (status) => {
        switch (status) {
            case 'sent':
                return <Chip label="Sent" color="success" size="small" />;
            case 'failed':
                return <Chip label="Failed" color="error" size="small" />;
            case 'pending':
                return <Chip label="Pending" color="warning" size="small" />;
            default:
                return <Chip label={status} size="small" />;
        }
    };

    const filteredNotifications = notifications.filter(notification => {
        if (filter === 'all') return true;
        return notification.type === filter;
    });

    return (
        <Box sx={{ p: 3 }}>
            <Grid container spacing={2} alignItems="center" sx={{ mb: 3 }}>
                <Grid item xs>
                    <Typography variant="h5" component="h1">
                        Notifications
                    </Typography>
                </Grid>
                <Grid item>
                    <TextField
                        select
                        label="Filter"
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        size="small"
                        sx={{ minWidth: 150 }}
                    >
                        <MenuItem value="all">All</MenuItem>
                        <MenuItem value="order_confirmation">Order Confirmations</MenuItem>
                        <MenuItem value="warehouse">Warehouse</MenuItem>
                        <MenuItem value="cancellation">Cancellations</MenuItem>
                        <MenuItem value="low_stock">Low Stock</MenuItem>
                        <MenuItem value="status_update">Status Updates</MenuItem>
                    </TextField>
                </Grid>
                <Grid item>
                    <IconButton onClick={fetchNotifications} disabled={loading}>
                        <RefreshIcon />
                    </IconButton>
                </Grid>
            </Grid>

            {error && (
                <Typography color="error" sx={{ mb: 2 }}>
                    {error}
                </Typography>
            )}

            <Paper elevation={2}>
                <List>
                    {loading ? (
                        <ListItem>
                            <ListItemText primary="Loading notifications..." />
                        </ListItem>
                    ) : filteredNotifications.length === 0 ? (
                        <ListItem>
                            <ListItemText primary="No notifications found" />
                        </ListItem>
                    ) : (
                        filteredNotifications.map((notification) => (
                            <React.Fragment key={notification.id}>
                                <ListItem
                                    button
                                    onClick={() => handleNotificationClick(notification)}
                                    secondaryAction={
                                        <IconButton
                                            edge="end"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleDeleteNotification(notification.id);
                                            }}
                                        >
                                            <DeleteIcon />
                                        </IconButton>
                                    }
                                >
                                    <ListItemIcon>
                                        {getNotificationIcon(notification.type)}
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={notification.title}
                                        secondary={
                                            <>
                                                {format(new Date(notification.createdAt), 'PPp')}
                                                <br />
                                                {getNotificationStatus(notification.status)}
                                            </>
                                        }
                                    />
                                </ListItem>
                                <Divider />
                            </React.Fragment>
                        ))
                    )}
                </List>
            </Paper>

            <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
                {selectedNotification && (
                    <>
                        <DialogTitle>
                            {selectedNotification.title}
                            <Typography variant="subtitle2" color="text.secondary">
                                {format(new Date(selectedNotification.createdAt), 'PPp')}
                            </Typography>
                        </DialogTitle>
                        <DialogContent>
                            <Typography paragraph>
                                {selectedNotification.message}
                            </Typography>
                            <Typography variant="subtitle2" color="text.secondary">
                                Status: {getNotificationStatus(selectedNotification.status)}
                            </Typography>
                            {selectedNotification.error && (
                                <Typography color="error" sx={{ mt: 2 }}>
                                    Error: {selectedNotification.error}
                                </Typography>
                            )}
                        </DialogContent>
                        <DialogActions>
                            <Button onClick={handleCloseDialog}>Close</Button>
                            {selectedNotification.status === 'failed' && (
                                <Button
                                    variant="contained"
                                    color="primary"
                                    onClick={() => handleRetryNotification(selectedNotification)}
                                >
                                    Retry
                                </Button>
                            )}
                        </DialogActions>
                    </>
                )}
            </Dialog>
        </Box>
    );
};

export default NotificationList; 