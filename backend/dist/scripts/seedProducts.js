"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const mongoose_1 = __importDefault(require("mongoose"));
const Product_1 = __importDefault(require("../models/Product"));
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config();
const sampleProducts = [
    {
        name: "Wireless Earbuds",
        description: "High-quality wireless earbuds with noise cancellation",
        price: 99.99,
        image: "https://images.unsplash.com/photo-1606220588911-5117e04b71d0?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        stock: 50,
        category: "Electronics"
    },
    {
        name: "Smart Watch",
        description: "Feature-rich smartwatch with health tracking",
        price: 199.99,
        image: "https://images.unsplash.com/photo-1546868871-7041f2a55e12?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        stock: 30,
        category: "Electronics"
    },
    {
        name: "Laptop Backpack",
        description: "Durable backpack with laptop compartment",
        price: 49.99,
        image: "https://images.unsplash.com/photo-1553062413-3a9c8d9c1e7e?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        stock: 100,
        category: "Accessories"
    },
    {
        name: "Coffee Maker",
        description: "Automatic coffee maker with timer",
        price: 79.99,
        image: "https://images.unsplash.com/photo-1589003077984-894e1332f995?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        stock: 25,
        category: "Home"
    }
];
const seedProducts = async () => {
    try {
        const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/dropshipping';
        await mongoose_1.default.connect(MONGODB_URI);
        console.log('Connected to MongoDB');
        // Clear existing products
        await Product_1.default.deleteMany({});
        console.log('Cleared existing products');
        // Insert sample products
        await Product_1.default.insertMany(sampleProducts);
        console.log('Added sample products');
        // Disconnect from MongoDB
        await mongoose_1.default.disconnect();
        console.log('Disconnected from MongoDB');
    }
    catch (error) {
        console.error('Error seeding products:', error);
        process.exit(1);
    }
};
seedProducts();
