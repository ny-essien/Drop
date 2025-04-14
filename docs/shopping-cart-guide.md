# Shopping Cart Module Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Database Model](#database-model)
4. [API Endpoints](#api-endpoints)
5. [Implementation Details](#implementation-details)
6. [Testing the API](#testing-the-api)

## Introduction

This guide explains the implementation of a shopping cart module for a MERN (MongoDB, Express.js, React.js, Node.js) stack application. The module provides a complete API for managing shopping carts, including adding items, updating quantities, removing items, and checkout functionality.

## Project Structure

The shopping cart module consists of the following files:

```
src/
├── models/
│   └── Cart.js              # Cart database model
├── controllers/
│   └── cartController.js    # Cart business logic
├── routes/
│   └── cartRoutes.js        # API route definitions
└── server.js                # Main application file
```

## Database Model

The Cart model (`src/models/Cart.js`) defines the structure of cart documents in MongoDB:

```javascript
// Cart Item Schema (nested)
const cartItemSchema = new mongoose.Schema({
    productId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Product',
        required: [true, 'Product ID is required']
    },
    quantity: {
        type: Number,
        required: [true, 'Quantity is required'],
        min: [1, 'Quantity must be at least 1']
    }
});

// Main Cart Schema
const cartSchema = new mongoose.Schema({
    userId: {
        type: String,
        required: [true, 'User ID is required']
    },
    items: {
        type: [cartItemSchema],
        default: []
    },
    totalPrice: {
        type: Number,
        default: 0
    }
}, {
    timestamps: true
});
```

Key features of the model:
- Nested schema for cart items
- Reference to Product model
- Automatic total price calculation
- Required field validation
- Quantity validation
- Automatic timestamps

## API Endpoints

The module provides the following RESTful endpoints:

1. **Add Item to Cart**
   - Method: POST
   - URL: `/api/cart/add`
   - Body: `{ userId, productId, quantity }`
   - Response: Updated cart object

2. **Get User's Cart**
   - Method: GET
   - URL: `/api/cart/:userId`
   - Response: Cart object

3. **Update Cart Item**
   - Method: PUT
   - URL: `/api/cart/update`
   - Body: `{ userId, productId, quantity }`
   - Response: Updated cart object

4. **Remove Item from Cart**
   - Method: DELETE
   - URL: `/api/cart/remove/:userId/:productId`
   - Response: Updated cart object

5. **Checkout Cart**
   - Method: POST
   - URL: `/api/cart/checkout`
   - Body: `{ userId }`
   - Response: Success message and empty cart

## Implementation Details

### 1. Cart Controller (`src/controllers/cartController.js`)

The controller contains five main functions and a helper function:

```javascript
// Helper function to calculate total price
const calculateTotalPrice = async (items) => {
    let total = 0;
    for (const item of items) {
        const product = await Product.findById(item.productId);
        if (product) {
            total += product.price * item.quantity;
        }
    }
    return total;
};

// Add to Cart
export const addToCart = async (req, res) => {
    // Implementation details...
};

// Get Cart
export const getCart = async (req, res) => {
    // Implementation details...
};

// Update Cart Item
export const updateCartItem = async (req, res) => {
    // Implementation details...
};

// Remove from Cart
export const removeFromCart = async (req, res) => {
    // Implementation details...
};

// Checkout Cart
export const checkoutCart = async (req, res) => {
    // Implementation details...
};
```

### 2. Routes Configuration (`src/routes/cartRoutes.js`)

The routes file maps HTTP methods to controller functions:

```javascript
import express from 'express';
import {
    addToCart,
    getCart,
    updateCartItem,
    removeFromCart,
    checkoutCart
} from '../controllers/cartController.js';

const router = express.Router();

router.post('/add', addToCart);
router.get('/:userId', getCart);
router.put('/update', updateCartItem);
router.delete('/remove/:userId/:productId', removeFromCart);
router.post('/checkout', checkoutCart);

export default router;
```

### 3. Server Configuration (`src/server.js`)

The main server file includes the cart routes:

```javascript
import cartRoutes from './routes/cartRoutes.js';

// ... other imports and setup ...

app.use('/api/cart', cartRoutes);
```

## Testing the API

You can test the API using tools like Postman or cURL. Here are example requests:

1. **Add Item to Cart**
```bash
curl -X POST http://localhost:5000/api/cart/add \
-H "Content-Type: application/json" \
-d '{
    "userId": "user123",
    "productId": "product123",
    "quantity": 2
}'
```

2. **Get Cart**
```bash
curl http://localhost:5000/api/cart/user123
```

3. **Update Cart Item**
```bash
curl -X PUT http://localhost:5000/api/cart/update \
-H "Content-Type: application/json" \
-d '{
    "userId": "user123",
    "productId": "product123",
    "quantity": 3
}'
```

4. **Remove Item**
```bash
curl -X DELETE http://localhost:5000/api/cart/remove/user123/product123
```

5. **Checkout**
```bash
curl -X POST http://localhost:5000/api/cart/checkout \
-H "Content-Type: application/json" \
-d '{
    "userId": "user123"
}'
```

## Error Handling

The API includes comprehensive error handling:
- 400 Bad Request: Invalid input data
- 404 Not Found: Cart or item not found
- 500 Server Error: Internal server errors

All responses follow a consistent format:
```javascript
{
    "success": boolean,
    "data": object | array | null,
    "error": string | null,
    "message": string | null
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

4. **Performance**
   - Efficient database queries
   - Automatic total price calculation
   - Proper indexing (MongoDB)

5. **Security**
   - Input validation
   - Error handling
   - Data sanitization

## Future Enhancements

1. **Authentication**
   - Add user authentication
   - Secure routes
   - Session management

2. **Order Processing**
   - Create order records
   - Process payments
   - Update product stock

3. **Additional Features**
   - Cart expiration
   - Save for later
   - Multiple shipping addresses
   - Discount codes

4. **Performance**
   - Caching
   - Batch operations
   - Optimized queries 