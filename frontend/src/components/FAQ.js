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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Chip
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search';

const FAQ = () => {
  const [faqs, setFaqs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [editDialog, setEditDialog] = useState(false);
  const [selectedFaq, setSelectedFaq] = useState(null);
  const [formData, setFormData] = useState({
    question: '',
    answer: '',
    category: '',
    is_active: true
  });
  const { user } = useAuth();

  useEffect(() => {
    fetchFaqs();
  }, []);

  const fetchFaqs = async () => {
    try {
      const response = await api.get('/faqs');
      setFaqs(response.data);
    } catch (err) {
      setError('Failed to load FAQs');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    try {
      const response = await api.get(`/faqs/search?query=${searchQuery}`);
      setFaqs(response.data);
    } catch (err) {
      setError('Failed to search FAQs');
    }
  };

  const handleCreateFaq = async () => {
    try {
      await api.post('/admin/faqs', formData);
      setEditDialog(false);
      setFormData({ question: '', answer: '', category: '', is_active: true });
      fetchFaqs();
    } catch (err) {
      setError('Failed to create FAQ');
    }
  };

  const handleUpdateFaq = async () => {
    try {
      await api.put(`/admin/faqs/${selectedFaq.id}`, formData);
      setEditDialog(false);
      setSelectedFaq(null);
      setFormData({ question: '', answer: '', category: '', is_active: true });
      fetchFaqs();
    } catch (err) {
      setError('Failed to update FAQ');
    }
  };

  const handleDeleteFaq = async (faqId) => {
    try {
      await api.delete(`/admin/faqs/${faqId}`);
      fetchFaqs();
    } catch (err) {
      setError('Failed to delete FAQ');
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'general': return 'default';
      case 'orders': return 'primary';
      case 'payments': return 'success';
      case 'shipping': return 'info';
      case 'returns': return 'warning';
      case 'account': return 'error';
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
        <Typography variant="h4">Frequently Asked Questions</Typography>
        {user?.is_admin && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {
              setSelectedFaq(null);
              setFormData({ question: '', answer: '', category: '', is_active: true });
              setEditDialog(true);
            }}
          >
            Add FAQ
          </Button>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Box mb={3}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Search FAQs"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                endAdornment: (
                  <IconButton onClick={handleSearch}>
                    <SearchIcon />
                  </IconButton>
                )
              }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                label="Category"
              >
                <MenuItem value="">All Categories</MenuItem>
                <MenuItem value="general">General</MenuItem>
                <MenuItem value="orders">Orders</MenuItem>
                <MenuItem value="payments">Payments</MenuItem>
                <MenuItem value="shipping">Shipping</MenuItem>
                <MenuItem value="returns">Returns</MenuItem>
                <MenuItem value="account">Account</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      {faqs
        .filter(faq => !selectedCategory || faq.category === selectedCategory)
        .map((faq) => (
          <Accordion key={faq.id}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box display="flex" justifyContent="space-between" alignItems="center" width="100%">
                <Typography>{faq.question}</Typography>
                <Box>
                  <Chip
                    label={faq.category}
                    color={getCategoryColor(faq.category)}
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  {user?.is_admin && (
                    <>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedFaq(faq);
                          setFormData({
                            question: faq.question,
                            answer: faq.answer,
                            category: faq.category,
                            is_active: faq.is_active
                          });
                          setEditDialog(true);
                        }}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteFaq(faq.id);
                        }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </>
                  )}
                </Box>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>{faq.answer}</Typography>
            </AccordionDetails>
          </Accordion>
        ))}

      {/* Edit/Create FAQ Dialog */}
      <Dialog open={editDialog} onClose={() => setEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {selectedFaq ? 'Edit FAQ' : 'Create New FAQ'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Question"
                value={formData.question}
                onChange={(e) => setFormData({ ...formData, question: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Answer"
                value={formData.answer}
                onChange={(e) => setFormData({ ...formData, answer: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  label="Category"
                >
                  <MenuItem value="general">General</MenuItem>
                  <MenuItem value="orders">Orders</MenuItem>
                  <MenuItem value="payments">Payments</MenuItem>
                  <MenuItem value="shipping">Shipping</MenuItem>
                  <MenuItem value="returns">Returns</MenuItem>
                  <MenuItem value="account">Account</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(false)}>Cancel</Button>
          <Button
            onClick={selectedFaq ? handleUpdateFaq : handleCreateFaq}
            variant="contained"
          >
            {selectedFaq ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FAQ; 