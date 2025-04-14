import express from 'express';
import {
    addToCart,
    getCart,
    updateCartItem,
    removeFromCart,
    checkoutCart
} from '../controllers/cartController.js';

const router = express.Router();

// Cart routes
router.post('/add', addToCart);
router.get('/:userId', getCart);
router.put('/update', updateCartItem);
router.delete('/remove/:userId/:productId', removeFromCart);
router.post('/checkout', checkoutCart);

export default router; 