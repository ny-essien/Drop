import React, { useState, useEffect } from 'react';
import {
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    FormControl,
    Grid,
    IconButton,
    InputLabel,
    MenuItem,
    Paper,
    Select,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Typography,
    Pagination,
    Tooltip
} from '@mui/material';
import {
    Assignment as AssignmentIcon,
    Close as CloseIcon,
    Search as SearchIcon,
    Send as SendIcon,
    FilterList as FilterIcon
} from '@mui/icons-material';
import supportService from '../services/supportService';
import { useAuth } from '../contexts/AuthContext';

const AdminSupportTickets = () => {
    const { user } = useAuth();
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [selectedTicket, setSelectedTicket] = useState(null);
    const [newMessage, setNewMessage] = useState('');
    const [stats, setStats] = useState(null);
    const [filters, setFilters] = useState({
        status: '',
        priority: '',
        category: '',
        search: ''
    });

    useEffect(() => {
        fetchTickets();
        fetchStats();
    }, [page, filters]);

    const fetchTickets = async () => {
        try {
            setLoading(true);
            const params = {
                page,
                ...filters
            };
            const response = await supportService.getAdminTickets(params);
            setTickets(response.data.tickets);
            setTotalPages(response.data.totalPages);
            setError(null);
        } catch (err) {
            setError('Failed to fetch tickets');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            const response = await supportService.getTicketStats();
            setStats(response.data);
        } catch (err) {
            console.error('Failed to fetch stats:', err);
        }
    };

    const handleAddMessage = async () => {
        if (!selectedTicket || !newMessage.trim()) return;
        try {
            await supportService.addMessage(selectedTicket._id, newMessage);
            const updatedTicket = await supportService.getTicket(selectedTicket._id);
            setSelectedTicket(updatedTicket.data);
            setNewMessage('');
            fetchTickets();
        } catch (err) {
            setError('Failed to add message');
            console.error(err);
        }
    };

    const handleUpdateStatus = async (ticketId, status) => {
        try {
            await supportService.updateTicketStatus(ticketId, status);
            if (selectedTicket && selectedTicket._id === ticketId) {
                const updatedTicket = await supportService.getTicket(ticketId);
                setSelectedTicket(updatedTicket.data);
            }
            fetchTickets();
        } catch (err) {
            setError('Failed to update status');
            console.error(err);
        }
    };

    const handleAssignTicket = async (ticketId) => {
        try {
            await supportService.assignTicket(ticketId, user._id);
            if (selectedTicket && selectedTicket._id === ticketId) {
                const updatedTicket = await supportService.getTicket(ticketId);
                setSelectedTicket(updatedTicket.data);
            }
            fetchTickets();
        } catch (err) {
            setError('Failed to assign ticket');
            console.error(err);
        }
    };

    const handleCloseTicket = async (ticketId) => {
        try {
            await supportService.closeTicket(ticketId);
            if (selectedTicket && selectedTicket._id === ticketId) {
                const updatedTicket = await supportService.getTicket(ticketId);
                setSelectedTicket(updatedTicket.data);
            }
            fetchTickets();
        } catch (err) {
            setError('Failed to close ticket');
            console.error(err);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'open': return 'primary';
            case 'in_progress': return 'warning';
            case 'resolved': return 'success';
            case 'closed': return 'error';
            default: return 'default';
        }
    };

    const getPriorityColor = (priority) => {
        switch (priority) {
            case 'low': return 'success';
            case 'medium': return 'warning';
            case 'high': return 'error';
            default: return 'default';
        }
    };

    if (loading) {
        return <Typography>Loading...</Typography>;
    }

    return (
        <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4">Support Tickets</Typography>
                {stats && (
                    <Box display="flex" gap={2}>
                        <Chip label={`Total: ${stats.total}`} color="primary" />
                        <Chip label={`Open: ${stats.open}`} color="warning" />
                        <Chip label={`In Progress: ${stats.in_progress}`} color="info" />
                        <Chip label={`Resolved: ${stats.resolved}`} color="success" />
                    </Box>
                )}
            </Box>

            {error && (
                <Typography color="error" mb={2}>
                    {error}
                </Typography>
            )}

            {/* Filters */}
            <Paper sx={{ p: 2, mb: 2 }}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} sm={6} md={3}>
                        <FormControl fullWidth>
                            <InputLabel>Status</InputLabel>
                            <Select
                                value={filters.status}
                                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                                label="Status"
                            >
                                <MenuItem value="">All</MenuItem>
                                <MenuItem value="open">Open</MenuItem>
                                <MenuItem value="in_progress">In Progress</MenuItem>
                                <MenuItem value="resolved">Resolved</MenuItem>
                                <MenuItem value="closed">Closed</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <FormControl fullWidth>
                            <InputLabel>Priority</InputLabel>
                            <Select
                                value={filters.priority}
                                onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
                                label="Priority"
                            >
                                <MenuItem value="">All</MenuItem>
                                <MenuItem value="low">Low</MenuItem>
                                <MenuItem value="medium">Medium</MenuItem>
                                <MenuItem value="high">High</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <FormControl fullWidth>
                            <InputLabel>Category</InputLabel>
                            <Select
                                value={filters.category}
                                onChange={(e) => setFilters({ ...filters, category: e.target.value })}
                                label="Category"
                            >
                                <MenuItem value="">All</MenuItem>
                                <MenuItem value="general">General</MenuItem>
                                <MenuItem value="technical">Technical</MenuItem>
                                <MenuItem value="billing">Billing</MenuItem>
                                <MenuItem value="order">Order</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <TextField
                            fullWidth
                            label="Search"
                            value={filters.search}
                            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                            InputProps={{
                                endAdornment: <SearchIcon />
                            }}
                        />
                    </Grid>
                </Grid>
            </Paper>

            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Subject</TableCell>
                            <TableCell>User</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Priority</TableCell>
                            <TableCell>Category</TableCell>
                            <TableCell>Assigned To</TableCell>
                            <TableCell>Last Updated</TableCell>
                            <TableCell>Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {tickets.map((ticket) => (
                            <TableRow key={ticket._id}>
                                <TableCell>{ticket.subject}</TableCell>
                                <TableCell>{ticket.user_id?.name || 'N/A'}</TableCell>
                                <TableCell>
                                    <Chip
                                        label={ticket.status}
                                        color={getStatusColor(ticket.status)}
                                        size="small"
                                    />
                                </TableCell>
                                <TableCell>
                                    <Chip
                                        label={ticket.priority}
                                        color={getPriorityColor(ticket.priority)}
                                        size="small"
                                    />
                                </TableCell>
                                <TableCell>{ticket.category}</TableCell>
                                <TableCell>
                                    {ticket.assigned_to?.name || 'Unassigned'}
                                </TableCell>
                                <TableCell>{new Date(ticket.updatedAt).toLocaleString()}</TableCell>
                                <TableCell>
                                    <Box display="flex" gap={1}>
                                        <Tooltip title="View Ticket">
                                            <IconButton
                                                size="small"
                                                onClick={() => setSelectedTicket(ticket)}
                                            >
                                                <SearchIcon />
                                            </IconButton>
                                        </Tooltip>
                                        {!ticket.assigned_to && (
                                            <Tooltip title="Assign to Me">
                                                <IconButton
                                                    size="small"
                                                    onClick={() => handleAssignTicket(ticket._id)}
                                                >
                                                    <AssignmentIcon />
                                                </IconButton>
                                            </Tooltip>
                                        )}
                                        {ticket.status !== 'closed' && (
                                            <Tooltip title="Close Ticket">
                                                <IconButton
                                                    size="small"
                                                    onClick={() => handleCloseTicket(ticket._id)}
                                                >
                                                    <CloseIcon />
                                                </IconButton>
                                            </Tooltip>
                                        )}
                                    </Box>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

            <Box display="flex" justifyContent="center" mt={3}>
                <Pagination
                    count={totalPages}
                    page={page}
                    onChange={(e, value) => setPage(value)}
                />
            </Box>

            {/* Ticket Details Dialog */}
            <Dialog
                open={!!selectedTicket}
                onClose={() => setSelectedTicket(null)}
                maxWidth="md"
                fullWidth
            >
                {selectedTicket && (
                    <>
                        <DialogTitle>
                            <Typography variant="h6">{selectedTicket.subject}</Typography>
                            <Box display="flex" gap={1} mt={1}>
                                <Chip
                                    label={selectedTicket.status}
                                    color={getStatusColor(selectedTicket.status)}
                                />
                                <Chip
                                    label={selectedTicket.priority}
                                    color={getPriorityColor(selectedTicket.priority)}
                                />
                            </Box>
                        </DialogTitle>
                        <DialogContent>
                            <Box mb={3}>
                                <Typography variant="subtitle2" color="textSecondary">
                                    Created by: {selectedTicket.user_id?.name || 'Unknown User'} | 
                                    Created: {new Date(selectedTicket.createdAt).toLocaleString()}
                                </Typography>
                                {selectedTicket.assigned_to && (
                                    <Typography variant="subtitle2" color="textSecondary">
                                        Assigned to: {selectedTicket.assigned_to.name}
                                    </Typography>
                                )}
                            </Box>
                            {selectedTicket.messages.map((message, index) => (
                                <Card key={index} sx={{ mb: 2 }}>
                                    <CardContent>
                                        <Box display="flex" justifyContent="space-between" mb={1}>
                                            <Typography variant="subtitle2">
                                                {message.sender === user._id ? 'You' : message.sender.name}
                                            </Typography>
                                            <Typography variant="caption" color="textSecondary">
                                                {new Date(message.timestamp).toLocaleString()}
                                            </Typography>
                                        </Box>
                                        <Typography>{message.content}</Typography>
                                    </CardContent>
                                </Card>
                            ))}
                            <Box mt={2}>
                                <TextField
                                    fullWidth
                                    multiline
                                    rows={3}
                                    value={newMessage}
                                    onChange={(e) => setNewMessage(e.target.value)}
                                    placeholder="Type your message..."
                                    variant="outlined"
                                />
                            </Box>
                        </DialogContent>
                        <DialogActions>
                            <Box display="flex" justifyContent="space-between" width="100%">
                                <Box>
                                    {selectedTicket.status !== 'closed' && (
                                        <>
                                            <Button
                                                onClick={() => handleUpdateStatus(selectedTicket._id, 'in_progress')}
                                                color="warning"
                                            >
                                                Mark In Progress
                                            </Button>
                                            <Button
                                                onClick={() => handleUpdateStatus(selectedTicket._id, 'resolved')}
                                                color="success"
                                            >
                                                Mark Resolved
                                            </Button>
                                            <Button
                                                onClick={() => handleCloseTicket(selectedTicket._id)}
                                                color="error"
                                            >
                                                Close Ticket
                                            </Button>
                                        </>
                                    )}
                                </Box>
                                <Box>
                                    <Button onClick={() => setSelectedTicket(null)}>Close</Button>
                                    <Button
                                        onClick={handleAddMessage}
                                        variant="contained"
                                        color="primary"
                                        startIcon={<SendIcon />}
                                    >
                                        Send
                                    </Button>
                                </Box>
                            </Box>
                        </DialogActions>
                    </>
                )}
            </Dialog>
        </Box>
    );
};

export default AdminSupportTickets; 