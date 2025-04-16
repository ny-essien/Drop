export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export const API_ENDPOINTS = {
  products: `${API_BASE_URL}/products`,
  cart: `${API_BASE_URL}/cart`,
  auth: `${API_BASE_URL}/auth`,
  orders: `${API_BASE_URL}/orders`
}; 