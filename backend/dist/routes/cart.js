"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const auth_1 = require("../middleware/auth");
const cart_1 = require("../controllers/cart");
const router = (0, express_1.Router)();
// Apply auth middleware to all routes
router.use(auth_1.auth);
// Cart routes
router.get('/', async (req, res) => {
    await (0, cart_1.getCart)(req, res);
});
router.post('/', async (req, res) => {
    await (0, cart_1.addToCart)(req, res);
});
router.put('/:productId', async (req, res) => {
    await (0, cart_1.updateCartItem)(req, res);
});
router.delete('/:productId', async (req, res) => {
    await (0, cart_1.removeFromCart)(req, res);
});
router.delete('/', async (req, res) => {
    await (0, cart_1.clearCart)(req, res);
});
exports.default = router;
