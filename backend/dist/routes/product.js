"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const product_1 = require("../controllers/product");
const router = (0, express_1.Router)();
// Get all products
router.get('/', async (req, res) => {
    await (0, product_1.getProducts)(req, res);
});
// Get product by ID
router.get('/:id', async (req, res) => {
    await (0, product_1.getProductById)(req, res);
});
// Create new product (protected route)
router.post('/', async (req, res) => {
    await (0, product_1.createProduct)(req, res);
});
// Update product (protected route)
router.put('/:id', async (req, res) => {
    await (0, product_1.updateProduct)(req, res);
});
// Delete product (protected route)
router.delete('/:id', async (req, res) => {
    await (0, product_1.deleteProduct)(req, res);
});
exports.default = router;
