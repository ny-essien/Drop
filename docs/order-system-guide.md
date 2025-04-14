# Order System Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Database Model](#database-model)
4. [API Endpoints](#api-endpoints)
5. [Implementation Details](#implementation-details)
6. [Testing the API](#testing-the-api)

## Introduction

This guide explains the implementation of an order system for a dropshipping application. The system allows users to create orders from their shopping carts, view their order history, and update order statuses. It integrates with the existing product and cart modules.

## Project Structure

The order system consists of the following files:

```
src/
├── models/
│   └── Order.js             # Order database model
├── controllers/
│   └── orderController.js   # Order business logic
├── routes/
│   └── orderRoutes.js       # API route definitions
└── server.js                # Main application file
```

## Database Model

The Order model (`src/models/Order.js`) defines the structure of order documents in MongoDB:

```javascript
// Order Item Schema (nested)
const orderItemSchema = new mongoose.Schema({
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

// Main Order Schema
const orderSchema = new mongoose.Schema({
    userId: {
        type: String,
        required: [true, 'User ID is required']
    },
    items: {
        type: [orderItemSchema],
        required: [true, 'Order items are required']
    },
    totalPrice: {
        type: Number,
        required: [true, 'Total price is required'],
        min: [0, 'Total price cannot be negative']
    },
    status: {
        type: String,
        enum: ['pending', 'processing', 'shipped', 'delivered', 'cancelled'],
        default: 'pending'
    }
}, {
    timestamps: true
});
```

Key features of the model:
- Nested schema for order items
- Reference to Product model
- Required field validation
- Status enumeration
- Automatic timestamps

## API Endpoints

The system provides the following RESTful endpoints:

1. **Create Order**
   - Method: POST
   - URL: `/api/orders`
   - Body: `{ userId }`
   - Response: Created order object

2. **Get User's Orders**
   - Method: GET
   - URL: `/api/orders/:userId`
   - Response: Array of orders

3. **Update Order Status**
   - Method: PATCH
   - URL: `/api/orders/:orderId/status`
   - Body: `{ status }`
   - Response: Updated order object

## Implementation Details

### 1. Order Controller (`src/controllers/orderController.js`)

The controller contains three main functions:

```javascript
// Create Order
export const createOrder = async (req, res) => {
    // Implementation details...
};

// Get Orders
export const getOrders = async (req, res) => {
    // Implementation details...
};

// Update Order Status
export const updateOrderStatus = async (req, res) => {
    // Implementation details...
};
```

### 2. Routes Configuration (`src/routes/orderRoutes.js`)

The routes file maps HTTP methods to controller functions:

```javascript
import express from 'express';
import {
    createOrder,
    getOrders,
    updateOrderStatus
} from '../controllers/orderController.js';

const router = express.Router();

router.post('/', createOrder);
router.get('/:userId', getOrders);
router.patch('/:orderId/status', updateOrderStatus);

export default router;
```

### 3. Server Configuration (`src/server.js`)

The main server file includes the order routes:

```javascript
import orderRoutes from './routes/orderRoutes.js';

// ... other imports and setup ...

app.use('/api/orders', orderRoutes);
```

## Testing the API

You can test the API using tools like Postman or cURL. Here are example requests:

1. **Create Order**
```bash
curl -X POST http://localhost:5000/api/orders \
-H "Content-Type: application/json" \
-d '{
    "userId": "user123"
}'
```

2. **Get User's Orders**
```bash
curl http://localhost:5000/api/orders/user123
```

3. **Update Order Status**
```bash
curl -X PATCH http://localhost:5000/api/orders/order123/status \
-H "Content-Type: application/json" \
-d '{
    "status": "processing"
}'
```

## Error Handling

The API includes comprehensive error handling:
- 400 Bad Request: Invalid input data or status
- 404 Not Found: Order or cart not found
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
   - Status enumeration
   - Custom validation messages

4. **Performance**
   - Efficient database queries
   - Proper indexing (MongoDB)
   - Sorting by creation date

5. **Security**
   - Input validation
   - Error handling
   - Data sanitization

## Future Enhancements

1. **Order Processing**
   - Payment processing
   - Email notifications
   - Order tracking

2. **Additional Features**
   - Order cancellation
   - Refund processing
   - Order history export

3. **Performance**
   - Caching
   - Batch operations
   - Optimized queries

4. **Integration**
   - Shipping providers
   - Payment gateways
   - Inventory management 