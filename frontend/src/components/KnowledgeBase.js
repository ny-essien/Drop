import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { knowledgeBaseService } from '../services/knowledgeBaseService';
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
  Chip,
  Rating,
  Divider,
  Paper,
  InputAdornment
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import ThumbDownIcon from '@mui/icons-material/ThumbDown';
import VisibilityIcon from '@mui/icons-material/Visibility';

const KnowledgeBase = () => {
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
  const [popularArticles, setPopularArticles] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    fetchArticles();
    fetchCategories();
    fetchPopularArticles();
  }, []);

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

  const fetchPopularArticles = async () => {
    try {
      const response = await knowledgeBaseService.getPopularArticles();
      setPopularArticles(response.data);
    } catch (err) {
      console.error('Failed to load popular articles:', err);
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
    } catch (err) {
      setError('Failed to update article');
    }
  };

  const handleDeleteArticle = async (articleId) => {
    try {
      await knowledgeBaseService.deleteArticle(articleId);
      fetchArticles();
    } catch (err) {
      setError('Failed to delete article');
    }
  };

  const handleVote = async (articleId, isHelpful) => {
    try {
      await knowledgeBaseService.voteArticle(articleId, isHelpful);
      fetchArticles();
    } catch (err) {
      setError('Failed to submit vote');
    }
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
      <Grid container spacing={3}>
        {/* Main Content */}
        <Grid item xs={12} md={9}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h4">Knowledge Base</Typography>
            {user?.is_admin && (
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
                  label="Search Articles"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={handleSearch}>
                          <SearchIcon />
                        </IconButton>
                      </InputAdornment>
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

          {articles
            .filter(article => !selectedCategory || article.category === selectedCategory)
            .map((article) => (
              <Accordion key={article.id}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" width="100%">
                    <Typography>{article.title}</Typography>
                    <Box>
                      <Chip
                        label={article.category}
                        color={getCategoryColor(article.category)}
                        size="small"
                        sx={{ mr: 1 }}
                      />
                      {user?.is_admin && (
                        <>
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
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
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteArticle(article.id);
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
                  <Typography paragraph>{article.content}</Typography>
                  <Box display="flex" alignItems="center" gap={2} mt={2}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <VisibilityIcon fontSize="small" />
                      <Typography variant="body2">{article.views}</Typography>
                    </Box>
                    <Box display="flex" alignItems="center" gap={1}>
                      <ThumbUpIcon fontSize="small" />
                      <Typography variant="body2">{article.helpful_votes}</Typography>
                    </Box>
                    <Box display="flex" gap={1}>
                      <IconButton size="small" onClick={() => handleVote(article.id, true)}>
                        <ThumbUpIcon />
                      </IconButton>
                      <IconButton size="small" onClick={() => handleVote(article.id, false)}>
                        <ThumbDownIcon />
                      </IconButton>
                    </Box>
                  </Box>
                </AccordionDetails>
              </Accordion>
            ))}
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Popular Articles
            </Typography>
            {popularArticles.map((article) => (
              <Box key={article.id} mb={2}>
                <Typography variant="subtitle2">{article.title}</Typography>
                <Box display="flex" alignItems="center" gap={1}>
                  <VisibilityIcon fontSize="small" />
                  <Typography variant="body2">{article.views} views</Typography>
                </Box>
              </Box>
            ))}
          </Paper>

          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Categories
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {categories.map((category) => (
                <Chip
                  key={category}
                  label={category}
                  color={getCategoryColor(category)}
                  onClick={() => setSelectedCategory(category)}
                  sx={{ mb: 1 }}
                />
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>

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

export default KnowledgeBase; 