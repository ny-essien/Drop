"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createOrder = exports.getOrderById = exports.getOrders = void 0;
const Order_1 = __importDefault(require("../models/Order"));
const Cart_1 = __importDefault(require("../models/Cart"));
const getOrders = async (req, res) => {
    try {
        const orders = await Order_1.default.find({ user: req.user?.userId })
            .populate('items.product')
            .sort({ createdAt: -1 });
        res.json(orders);
    }
    catch (error) {
        res.status(500).json({ message: 'Error fetching orders', error });
    }
};
exports.getOrders = getOrders;
const getOrderById = async (req, res) => {
    try {
        const { id } = req.params;
        const order = await Order_1.default.findById(id).populate('items.product');
        if (!order) {
            return res.status(404).json({ message: 'Order not found' });
        }
        return res.json(order);
    }
    catch (error) {
        return res.status(500).json({ message: 'Error fetching order', error });
    }
};
exports.getOrderById = getOrderById;
const createOrder = async (req, res) => {
    try {
        const { userId } = req.user;
        const cart = await Cart_1.default.findOne({ user: userId }).populate('items.product');
        if (!cart || cart.items.length === 0) {
            return res.status(400).json({ message: 'Cart is empty' });
        }
        // Calculate total from cart items
        const total = cart.items.reduce((sum, item) => {
            return sum + (item.product.price * item.quantity);
        }, 0);
        const order = new Order_1.default({
            user: userId,
            items: cart.items.map(item => ({
                product: item.product._id,
                quantity: item.quantity,
                price: item.product.price
            })),
            total,
            status: 'pending'
        });
        await order.save();
        // Clear the cart
        cart.items = [];
        await cart.save();
        return res.status(201).json(order);
    }
    catch (error) {
        return res.status(500).json({ message: 'Error creating order', error });
    }
};
exports.createOrder = createOrder;
