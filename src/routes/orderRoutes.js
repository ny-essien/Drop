import express from 'express';
import {
    createOrder,
    getOrders,
    updateOrderStatus
} from '../controllers/orderController.js';

const router = express.Router();

// Order routes
router.post('/', createOrder);
router.get('/:userId', getOrders);
router.patch('/:orderId/status', updateOrderStatus);

export default router; 