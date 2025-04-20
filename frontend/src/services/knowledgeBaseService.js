import { api } from './api';

export const knowledgeBaseService = {
  // Article endpoints
  getArticles: () => api.get('/knowledge-base/articles'),
  getArticle: (id) => api.get(`/knowledge-base/articles/${id}`),
  createArticle: (data) => api.post('/knowledge-base/articles', data),
  updateArticle: (id, data) => api.put(`/knowledge-base/articles/${id}`, data),
  deleteArticle: (id) => api.delete(`/knowledge-base/articles/${id}`),
  searchArticles: (query) => api.get(`/knowledge-base/articles/search?query=${query}`),
  getPopularArticles: () => api.get('/knowledge-base/articles/popular'),
  voteArticle: (id, isHelpful) => api.post(`/knowledge-base/articles/${id}/vote`, { is_helpful: isHelpful }),
  getStats: () => api.get('/knowledge-base/stats'),

  // Category endpoints
  getCategories: () => api.get('/knowledge-base/categories'),
  createCategory: (data) => api.post('/knowledge-base/categories', data),
  updateCategory: (id, data) => api.put(`/knowledge-base/categories/${id}`, data),
  deleteCategory: (id) => api.delete(`/knowledge-base/categories/${id}`),

  // Tag endpoints
  getTags: () => api.get('/knowledge-base/tags'),
  createTag: (data) => api.post('/knowledge-base/tags', data),
  updateTag: (id, data) => api.put(`/knowledge-base/tags/${id}`, data),
  deleteTag: (id) => api.delete(`/knowledge-base/tags/${id}`),
}; 