"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.clearCart = exports.removeFromCart = exports.updateCartItem = exports.addToCart = exports.getCart = void 0;
const Cart_1 = __importDefault(require("../models/Cart"));
const Product_1 = __importDefault(require("../models/Product"));
const getCart = async (req, res) => {
    try {
        const { userId } = req.user;
        const cart = await Cart_1.default.findOne({ user: userId }).populate('items.product');
        if (!cart) {
            return res.json({ items: [] });
        }
        return res.json(cart);
    }
    catch (error) {
        return res.status(500).json({ error: 'Error fetching cart' });
    }
};
exports.getCart = getCart;
const addToCart = async (req, res) => {
    try {
        const { userId } = req.user;
        const { productId, quantity } = req.body;
        const product = await Product_1.default.findById(productId);
        if (!product) {
            return res.status(404).json({ error: 'Product not found' });
        }
        let cart = await Cart_1.default.findOne({ user: userId });
        if (!cart) {
            cart = new Cart_1.default({ user: userId, items: [] });
        }
        const existingItem = cart.items.find(item => item.product.toString() === productId);
        if (existingItem) {
            existingItem.quantity += quantity;
        }
        else {
            cart.items.push({ product: productId, quantity });
        }
        await cart.save();
        return res.json(cart);
    }
    catch (error) {
        return res.status(500).json({ error: 'Error adding to cart' });
    }
};
exports.addToCart = addToCart;
const updateCartItem = async (req, res) => {
    try {
        const { userId } = req.user;
        const { productId } = req.params;
        const { quantity } = req.body;
        const cart = await Cart_1.default.findOne({ user: userId });
        if (!cart) {
            return res.status(404).json({ error: 'Cart not found' });
        }
        const item = cart.items.find(item => item.product.toString() === productId);
        if (!item) {
            return res.status(404).json({ error: 'Item not found in cart' });
        }
        item.quantity = quantity;
        await cart.save();
        return res.json(cart);
    }
    catch (error) {
        return res.status(500).json({ error: 'Error updating cart' });
    }
};
exports.updateCartItem = updateCartItem;
const removeFromCart = async (req, res) => {
    try {
        const { userId } = req.user;
        const { productId } = req.params;
        const cart = await Cart_1.default.findOne({ user: userId });
        if (!cart) {
            return res.status(404).json({ error: 'Cart not found' });
        }
        cart.items = cart.items.filter(item => item.product.toString() !== productId);
        await cart.save();
        return res.json(cart);
    }
    catch (error) {
        return res.status(500).json({ error: 'Error removing from cart' });
    }
};
exports.removeFromCart = removeFromCart;
const clearCart = async (req, res) => {
    try {
        const { userId } = req.user;
        const cart = await Cart_1.default.findOne({ user: userId });
        if (!cart) {
            return res.status(404).json({ error: 'Cart not found' });
        }
        cart.items = [];
        await cart.save();
        return res.json(cart);
    }
    catch (error) {
        return res.status(500).json({ error: 'Error clearing cart' });
    }
};
exports.clearCart = clearCart;
