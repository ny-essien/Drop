import { API_ENDPOINTS } from '../config/env';

// Types
export interface Product {
  _id: string;
  name: string;
  description: string;
  price: number;
  image_url: string;
  stock: number;
}

export interface CartItem {
  product: Product;
  quantity: number;
}

export interface Cart {
  items: CartItem[];
}

// API Functions
export const fetchProducts = async (skip = 0, limit = 10): Promise<Product[]> => {
  const response = await fetch(`${API_ENDPOINTS.products}?skip=${skip}&limit=${limit}`);
  if (!response.ok) throw new Error('Failed to fetch products');
  return response.json();
};

export const fetchProduct = async (id: string): Promise<Product> => {
  const response = await fetch(`${API_ENDPOINTS.products}/${id}`);
  if (!response.ok) throw new Error('Failed to fetch product');
  return response.json();
};

export const fetchCart = async (): Promise<Cart> => {
  const response = await fetch(API_ENDPOINTS.cart, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  if (!response.ok) throw new Error('Failed to fetch cart');
  return response.json();
};

export const addToCart = async (productId: string, quantity: number = 1): Promise<Cart> => {
  const response = await fetch(`${API_ENDPOINTS.cart}/items/${productId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify({ quantity })
  });
  if (!response.ok) throw new Error('Failed to add item to cart');
  return response.json();
};

export const updateCartItem = async (productId: string, quantity: number): Promise<Cart> => {
  const response = await fetch(`${API_ENDPOINTS.cart}/items/${productId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify({ quantity })
  });
  if (!response.ok) throw new Error('Failed to update cart item');
  return response.json();
};

export const removeFromCart = async (productId: string): Promise<Cart> => {
  const response = await fetch(`${API_ENDPOINTS.cart}/items/${productId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  if (!response.ok) throw new Error('Failed to remove item from cart');
  return response.json();
};

export const clearCart = async (): Promise<Cart> => {
  const response = await fetch(API_ENDPOINTS.cart, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  if (!response.ok) throw new Error('Failed to clear cart');
  return response.json();
}; 