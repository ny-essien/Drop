import React, { useState, useEffect } from 'react';
import { knowledgeBaseService } from '../services/knowledgeBaseService';
import {
  Box,
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
  IconButton,
  TablePagination,
  Switch,
  FormControlLabel
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search';

const AdminKnowledgeBase = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [editDialog, setEditDialog] = useState(false);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: '',
    tags: [],
    is_active: true
  });
  const [categories, setCategories] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [stats, setStats] = useState({
    total_articles: 0,
    total_views: 0,
    total_votes: 0,
    categories: {}
  });

  useEffect(() => {
    fetchArticles();
    fetchCategories();
    fetchStats();
  }, [page, rowsPerPage]);

  const fetchArticles = async () => {
    try {
      const response = await knowledgeBaseService.getArticles();
      setArticles(response.data);
    } catch (err) {
      setError('Failed to load articles');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await knowledgeBaseService.getCategories();
      setCategories(response.data);
    } catch (err) {
      setError('Failed to load categories');
    }
  };

  const fetchStats = async () => {
    try {
      const response = await knowledgeBaseService.getStats();
      setStats(response.data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleSearch = async () => {
    try {
      const response = await knowledgeBaseService.searchArticles(searchQuery);
      setArticles(response.data);
    } catch (err) {
      setError('Failed to search articles');
    }
  };

  const handleCreateArticle = async () => {
    try {
      await knowledgeBaseService.createArticle(formData);
      setEditDialog(false);
      setFormData({ title: '', content: '', category: '', tags: [], is_active: true });
      fetchArticles();
      fetchStats();
    } catch (err) {
      setError('Failed to create article');
    }
  };

  const handleUpdateArticle = async () => {
    try {
      await knowledgeBaseService.updateArticle(selectedArticle.id, formData);
      setEditDialog(false);
      setSelectedArticle(null);
      setFormData({ title: '', content: '', category: '', tags: [], is_active: true });
      fetchArticles();
      fetchStats();
    } catch (err) {
      setError('Failed to update article');
    }
  };

  const handleDeleteArticle = async (articleId) => {
    try {
      await knowledgeBaseService.deleteArticle(articleId);
      fetchArticles();
      fetchStats();
    } catch (err) {
      setError('Failed to delete article');
    }
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getCategoryColor = (category) => {
    const colors = {
      'general': 'default',
      'orders': 'primary',
      'payments': 'success',
      'shipping': 'info',
      'returns': 'warning',
      'account': 'error'
    };
    return colors[category] || 'default';
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
        <Typography variant="h4">Knowledge Base Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {
            setSelectedArticle(null);
            setFormData({ title: '', content: '', category: '', tags: [], is_active: true });
            setEditDialog(true);
          }}
        >
          Add Article
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Total Articles</Typography>
            <Typography variant="h4">{stats.total_articles}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Total Views</Typography>
            <Typography variant="h4">{stats.total_views}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Total Votes</Typography>
            <Typography variant="h4">{stats.total_votes}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Categories</Typography>
            <Typography variant="h4">{Object.keys(stats.categories).length}</Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Search and Filter */}
      <Box mb={3}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Search Articles"
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
                {categories.map((category) => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      {/* Articles Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Views</TableCell>
              <TableCell>Votes</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {articles
              .filter(article => !selectedCategory || article.category === selectedCategory)
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((article) => (
                <TableRow key={article.id}>
                  <TableCell>{article.title}</TableCell>
                  <TableCell>
                    <Chip
                      label={article.category}
                      color={getCategoryColor(article.category)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{article.views}</TableCell>
                  <TableCell>{article.helpful_votes}</TableCell>
                  <TableCell>
                    <Chip
                      label={article.is_active ? 'Active' : 'Inactive'}
                      color={article.is_active ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => {
                        setSelectedArticle(article);
                        setFormData({
                          title: article.title,
                          content: article.content,
                          category: article.category,
                          tags: article.tags,
                          is_active: article.is_active
                        });
                        setEditDialog(true);
                      }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteArticle(article.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={articles.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>

      {/* Edit/Create Article Dialog */}
      <Dialog open={editDialog} onClose={() => setEditDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedArticle ? 'Edit Article' : 'Create New Article'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={6}
                label="Content"
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
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
                  {categories.map((category) => (
                    <MenuItem key={category} value={category}>
                      {category}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Tags"
                value={formData.tags.join(', ')}
                onChange={(e) => setFormData({ ...formData, tags: e.target.value.split(',').map(tag => tag.trim()) })}
                helperText="Separate tags with commas"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  />
                }
                label="Active"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(false)}>Cancel</Button>
          <Button
            onClick={selectedArticle ? handleUpdateArticle : handleCreateArticle}
            variant="contained"
          >
            {selectedArticle ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminKnowledgeBase; 