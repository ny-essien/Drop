"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const auth_1 = require("../middleware/auth");
const orders_1 = require("../controllers/orders");
const router = (0, express_1.Router)();
// Apply auth middleware to all routes
router.use(auth_1.auth);
// Order routes
router.get('/', async (req, res) => {
    await (0, orders_1.getOrders)(req, res);
});
router.get('/:id', async (req, res) => {
    await (0, orders_1.getOrderById)(req, res);
});
router.post('/', async (req, res) => {
    await (0, orders_1.createOrder)(req, res);
});
exports.default = router;
