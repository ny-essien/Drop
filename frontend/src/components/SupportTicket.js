import React, { useState, useEffect } from 'react';
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
  Paper,
  Chip,
  IconButton
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SendIcon from '@mui/icons-material/Send';
import CloseIcon from '@mui/icons-material/Close';

const SupportTicket = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [newTicketDialog, setNewTicketDialog] = useState(false);
  const [responseDialog, setResponseDialog] = useState(false);
  const [formData, setFormData] = useState({
    subject: '',
    description: '',
    priority: 1
  });
  const [responseText, setResponseText] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = async () => {
    try {
      const response = await api.get('/support/tickets');
      setTickets(response.data);
    } catch (err) {
      setError('Failed to load tickets');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTicket = async () => {
    try {
      await api.post('/support/tickets', formData);
      setNewTicketDialog(false);
      setFormData({ subject: '', description: '', priority: 1 });
      fetchTickets();
    } catch (err) {
      setError('Failed to create ticket');
    }
  };

  const handleAddResponse = async () => {
    try {
      await api.post(`/support/tickets/${selectedTicket.id}/responses`, {
        message: responseText
      });
      setResponseDialog(false);
      setResponseText('');
      fetchTickets();
    } catch (err) {
      setError('Failed to add response');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'open': return 'error';
      case 'in_progress': return 'warning';
      case 'resolved': return 'success';
      case 'closed': return 'default';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 1: return 'success';
      case 2: return 'warning';
      case 3: return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Support Tickets</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setNewTicketDialog(true)}
        >
          New Ticket
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Subject</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tickets.map((ticket) => (
              <TableRow key={ticket.id}>
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
                    label={`Priority ${ticket.priority}`}
                    color={getPriorityColor(ticket.priority)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {new Date(ticket.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <Button
                    size="small"
                    onClick={() => {
                      setSelectedTicket(ticket);
                      setResponseDialog(true);
                    }}
                  >
                    View/Respond
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* New Ticket Dialog */}
      <Dialog open={newTicketDialog} onClose={() => setNewTicketDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Ticket</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Subject"
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  label="Priority"
                >
                  <MenuItem value={1}>Low</MenuItem>
                  <MenuItem value={2}>Medium</MenuItem>
                  <MenuItem value={3}>High</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewTicketDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateTicket} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Response Dialog */}
      <Dialog open={responseDialog} onClose={() => setResponseDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Ticket: {selectedTicket?.subject}
          <IconButton
            onClick={() => setResponseDialog(false)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {selectedTicket && (
            <>
              <Typography variant="subtitle1" gutterBottom>
                Description:
              </Typography>
              <Typography paragraph>{selectedTicket.description}</Typography>
              
              <Typography variant="subtitle1" gutterBottom>
                Responses:
              </Typography>
              {selectedTicket.responses?.map((response) => (
                <Card key={response.id} sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="body2" color="text.secondary">
                      {response.is_admin ? 'Admin' : 'You'} - {new Date(response.created_at).toLocaleString()}
                    </Typography>
                    <Typography>{response.message}</Typography>
                  </CardContent>
                </Card>
              ))}
              
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Your Response"
                value={responseText}
                onChange={(e) => setResponseText(e.target.value)}
                sx={{ mt: 2 }}
              />
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResponseDialog(false)}>Cancel</Button>
          <Button
            onClick={handleAddResponse}
            variant="contained"
            startIcon={<SendIcon />}
            disabled={!responseText}
          >
            Send Response
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SupportTicket; 