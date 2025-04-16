"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const product_1 = require("../controllers/product");
const router = (0, express_1.Router)();
router.get('/', async (req, res) => {
    await (0, product_1.getProducts)(req, res);
});
router.get('/:id', async (req, res) => {
    await (0, product_1.getProductById)(req, res);
});
router.post('/', async (req, res) => {
    await (0, product_1.createProduct)(req, res);
});
router.put('/:id', async (req, res) => {
    await (0, product_1.updateProduct)(req, res);
});
router.delete('/:id', async (req, res) => {
    await (0, product_1.deleteProduct)(req, res);
});
exports.default = router;
