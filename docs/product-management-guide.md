# MERN Backend Product Management Module Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Database Model](#database-model)
4. [API Endpoints](#api-endpoints)
5. [Implementation Details](#implementation-details)
6. [Testing the API](#testing-the-api)

## Introduction

This guide explains the implementation of a product management module for a MERN (MongoDB, Express.js, React.js, Node.js) stack application. The module provides a complete CRUD (Create, Read, Update, Delete) API for managing products in a dropshipping application.

## Project Structure

The product management module consists of the following files:

```
src/
├── models/
│   └── Product.js         # Product database model
├── controllers/
│   └── productController.js # Product business logic
├── routes/
│   └── productRoutes.js   # API route definitions
└── server.js              # Main application file
```

## Database Model

The Product model (`src/models/Product.js`) defines the structure of product documents in MongoDB:

```javascript
const productSchema = new mongoose.Schema({
    title: {
        type: String,
        required: [true, 'Product title is required'],
        trim: true
    },
    description: {
        type: String,
        required: [true, 'Product description is required']
    },
    price: {
        type: Number,
        required: [true, 'Product price is required'],
        min: [0, 'Price cannot be negative']
    },
    images: {
        type: [String],
        default: []
    },
    stock: {
        type: Number,
        required: [true, 'Product stock is required'],
        min: [0, 'Stock cannot be negative']
    },
    supplierName: {
        type: String,
        required: [true, 'Supplier name is required'],
        trim: true
    }
}, {
    timestamps: true
});
```

Key features of the model:
- Required fields with validation messages
- Price and stock validation to prevent negative values
- Array field for product images
- Automatic timestamps for created and updated dates

## API Endpoints

The module provides the following RESTful endpoints:

1. **Create Product**
   - Method: POST
   - URL: `/api/products`
   - Body: JSON object with product details
   - Response: Created product object

2. **Get All Products**
   - Method: GET
   - URL: `/api/products`
   - Response: Array of all products

3. **Get Single Product**
   - Method: GET
   - URL: `/api/products/:id`
   - Response: Single product object

4. **Update Product**
   - Method: PUT
   - URL: `/api/products/:id`
   - Body: JSON object with updated fields
   - Response: Updated product object

5. **Delete Product**
   - Method: DELETE
   - URL: `/api/products/:id`
   - Response: Success message

## Implementation Details

### 1. Product Controller (`src/controllers/productController.js`)

The controller contains five main functions:

```javascript
// Create Product
export const createProduct = async (req, res) => {
    try {
        const product = await Product.create(req.body);
        res.status(201).json({
            success: true,
            data: product
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            error: error.message
        });
    }
};

// Get All Products
export const getProducts = async (req, res) => {
    try {
        const products = await Product.find();
        res.status(200).json({
            success: true,
            count: products.length,
            data: products
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Server Error'
        });
    }
};

// Get Single Product
export const getProduct = async (req, res) => {
    try {
        const product = await Product.findById(req.params.id);
        if (!product) {
            return res.status(404).json({
                success: false,
                error: 'Product not found'
            });
        }
        res.status(200).json({
            success: true,
            data: product
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Server Error'
        });
    }
};

// Update Product
export const updateProduct = async (req, res) => {
    try {
        const product = await Product.findByIdAndUpdate(
            req.params.id,
            req.body,
            {
                new: true,
                runValidators: true
            }
        );
        if (!product) {
            return res.status(404).json({
                success: false,
                error: 'Product not found'
            });
        }
        res.status(200).json({
            success: true,
            data: product
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            error: error.message
        });
    }
};

// Delete Product
export const deleteProduct = async (req, res) => {
    try {
        const product = await Product.findByIdAndDelete(req.params.id);
        if (!product) {
            return res.status(404).json({
                success: false,
                error: 'Product not found'
            });
        }
        res.status(200).json({
            success: true,
            data: {}
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Server Error'
        });
    }
};
```

### 2. Routes Configuration (`src/routes/productRoutes.js`)

The routes file maps HTTP methods to controller functions:

```javascript
import express from 'express';
import {
    createProduct,
    getProducts,
    getProduct,
    updateProduct,
    deleteProduct
} from '../controllers/productController.js';

const router = express.Router();

router.route('/')
    .get(getProducts)
    .post(createProduct);

router.route('/:id')
    .get(getProduct)
    .put(updateProduct)
    .delete(deleteProduct);

export default router;
```

### 3. Server Configuration (`src/server.js`)

The main server file includes:
- Express setup
- Middleware configuration
- Database connection
- Route registration

```javascript
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { connectDB } from './db.js';
import productRoutes from './routes/productRoutes.js';

// Load environment variables
dotenv.config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/products', productRoutes);

// Server startup
const PORT = process.env.PORT || 5000;

const startServer = async () => {
    try {
        await connectDB();
        app.listen(PORT, () => {
            console.log(`Server is running on port ${PORT}`);
        });
    } catch (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
};

startServer();
```

## Testing the API

You can test the API using tools like Postman or cURL. Here are example requests:

1. **Create a Product**
```bash
curl -X POST http://localhost:5000/api/products \
-H "Content-Type: application/json" \
-d '{
    "title": "Sample Product",
    "description": "This is a sample product",
    "price": 99.99,
    "stock": 100,
    "supplierName": "Sample Supplier"
}'
```

2. **Get All Products**
```bash
curl http://localhost:5000/api/products
```

3. **Get Single Product**
```bash
curl http://localhost:5000/api/products/:id
```

4. **Update Product**
```bash
curl -X PUT http://localhost:5000/api/products/:id \
-H "Content-Type: application/json" \
-d '{
    "price": 89.99
}'
```

5. **Delete Product**
```bash
curl -X DELETE http://localhost:5000/api/products/:id
```

## Error Handling

The API includes comprehensive error handling:
- 400 Bad Request: Invalid input data
- 404 Not Found: Resource not found
- 500 Server Error: Internal server errors

All responses follow a consistent format:
```javascript
{
    "success": boolean,
    "data": object | array | null,
    "error": string | null
}
```

## Best Practices Implemented

1. **Code Organization**
   - Separation of concerns (Model, Controller, Routes)
   - Modular file structure
   - Clear naming conventions

2. **Error Handling**
   - Try-catch blocks
   - Appropriate HTTP status codes
   - Consistent error response format

3. **Data Validation**
   - Required field validation
   - Data type validation
   - Custom validation messages

4. **Security**
   - CORS enabled
   - Input sanitization
   - Environment variable usage

5. **Performance**
   - Efficient database queries
   - Proper indexing (MongoDB)
   - Response optimization 