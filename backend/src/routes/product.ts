import express from 'express';
import {
  getProducts,
  getProductById,
  createProduct,
  updateProduct,
  deleteProduct
} from '../controllers/product';

const router = express.Router();

// Get all products
router.get('/', getProducts);

// Get product by ID
router.get('/:id', getProductById);

// Create new product (protected route)
router.post('/', createProduct);

// Update product (protected route)
router.put('/:id', updateProduct);

// Delete product (protected route)
router.delete('/:id', deleteProduct);

export default router; 