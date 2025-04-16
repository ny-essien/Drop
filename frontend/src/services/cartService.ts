import axios from 'axios';

const API_URL = 'http://localhost:5000/api/cart';

export interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
  image: string;
}

export const getCart = async (): Promise<CartItem[]> => {
  const response = await axios.get(API_URL, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  });
  return response.data;
};

export const addToCart = async (productId: string, quantity: number = 1): Promise<CartItem> => {
  const response = await axios.post(
    API_URL,
    { productId, quantity },
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    }
  );
  return response.data;
};

export const updateCartItem = async (itemId: string, quantity: number): Promise<CartItem> => {
  const response = await axios.put(
    `${API_URL}/${itemId}`,
    { quantity },
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    }
  );
  return response.data;
};

export const removeFromCart = async (itemId: string): Promise<void> => {
  await axios.delete(`${API_URL}/${itemId}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  });
}; 