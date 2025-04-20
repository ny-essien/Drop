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
    Grid,
    IconButton,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Typography,
    Pagination
} from '@mui/material';
import { Add as AddIcon, Send as SendIcon } from '@mui/icons-material';
import supportService from '../services/supportService';
import { useAuth } from '../contexts/AuthContext';

const SupportTickets = () => {
    const { user } = useAuth();
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [selectedTicket, setSelectedTicket] = useState(null);
    const [newMessage, setNewMessage] = useState('');
    const [openNewTicket, setOpenNewTicket] = useState(false);
    const [newTicket, setNewTicket] = useState({
        subject: '',
        message: '',
        priority: 'medium',
        category: 'general'
    });

    useEffect(() => {
        fetchTickets();
    }, [page]);

    const fetchTickets = async () => {
        try {
            setLoading(true);
            const response = await supportService.getUserTickets({ page });
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

    const handleCreateTicket = async () => {
        try {
            await supportService.createTicket(newTicket);
            setOpenNewTicket(false);
            setNewTicket({
                subject: '',
                message: '',
                priority: 'medium',
                category: 'general'
            });
            fetchTickets();
        } catch (err) {
            setError('Failed to create ticket');
            console.error(err);
        }
    };

    const handleAddMessage = async () => {
        if (!selectedTicket || !newMessage.trim()) return;
        try {
            await supportService.addMessage(selectedTicket._id, newMessage);
            const updatedTicket = await supportService.getTicket(selectedTicket._id);
            setSelectedTicket(updatedTicket.data);
            setNewMessage('');
        } catch (err) {
            setError('Failed to add message');
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
                <Button
                    variant="contained"
                    color="primary"
                    startIcon={<AddIcon />}
                    onClick={() => setOpenNewTicket(true)}
                >
                    New Ticket
                </Button>
            </Box>

            {error && (
                <Typography color="error" mb={2}>
                    {error}
                </Typography>
            )}

            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Subject</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Priority</TableCell>
                            <TableCell>Category</TableCell>
                            <TableCell>Last Updated</TableCell>
                            <TableCell>Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {tickets.map((ticket) => (
                            <TableRow key={ticket._id}>
                                <TableCell>{ticket.subject}</TableCell>
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
                                <TableCell>{new Date(ticket.updatedAt).toLocaleString()}</TableCell>
                                <TableCell>
                                    <Button
                                        size="small"
                                        onClick={() => setSelectedTicket(ticket)}
                                    >
                                        View
                                    </Button>
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

            {/* New Ticket Dialog */}
            <Dialog open={openNewTicket} onClose={() => setOpenNewTicket(false)}>
                <DialogTitle>Create New Ticket</DialogTitle>
                <DialogContent>
                    <TextField
                        fullWidth
                        label="Subject"
                        value={newTicket.subject}
                        onChange={(e) => setNewTicket({ ...newTicket, subject: e.target.value })}
                        margin="normal"
                    />
                    <TextField
                        fullWidth
                        label="Message"
                        value={newTicket.message}
                        onChange={(e) => setNewTicket({ ...newTicket, message: e.target.value })}
                        margin="normal"
                        multiline
                        rows={4}
                    />
                    <TextField
                        fullWidth
                        select
                        label="Priority"
                        value={newTicket.priority}
                        onChange={(e) => setNewTicket({ ...newTicket, priority: e.target.value })}
                        margin="normal"
                        SelectProps={{
                            native: true
                        }}
                    >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                    </TextField>
                    <TextField
                        fullWidth
                        select
                        label="Category"
                        value={newTicket.category}
                        onChange={(e) => setNewTicket({ ...newTicket, category: e.target.value })}
                        margin="normal"
                        SelectProps={{
                            native: true
                        }}
                    >
                        <option value="general">General</option>
                        <option value="technical">Technical</option>
                        <option value="billing">Billing</option>
                        <option value="order">Order</option>
                    </TextField>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenNewTicket(false)}>Cancel</Button>
                    <Button onClick={handleCreateTicket} color="primary">
                        Create
                    </Button>
                </DialogActions>
            </Dialog>

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
                                    Created: {new Date(selectedTicket.createdAt).toLocaleString()}
                                </Typography>
                            </Box>
                            {selectedTicket.messages.map((message, index) => (
                                <Card key={index} sx={{ mb: 2 }}>
                                    <CardContent>
                                        <Box display="flex" justifyContent="space-between" mb={1}>
                                            <Typography variant="subtitle2">
                                                {message.sender === user._id ? 'You' : 'Support'}
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
                            <Button onClick={() => setSelectedTicket(null)}>Close</Button>
                            <Button
                                onClick={handleAddMessage}
                                variant="contained"
                                color="primary"
                                startIcon={<SendIcon />}
                            >
                                Send
                            </Button>
                        </DialogActions>
                    </>
                )}
            </Dialog>
        </Box>
    );
};

export default SupportTickets; 