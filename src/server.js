// Import required packages
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { connectDB } from './db.js';

// Load environment variables from .env file
dotenv.config();

// Create Express application
const app = express();

// Middleware
// Enable Cross-Origin Resource Sharing (CORS)
app.use(cors());
// Parse JSON bodies (as sent by API clients)
app.use(express.json());
// Parse URL-encoded bodies
app.use(express.urlencoded({ extended: true }));

// Define routes
// Test route to verify API is working
app.get('/api/test', (req, res) => {
  res.json({ message: 'API working' });
});

// Get port from environment variables or use 5000 as default
const PORT = process.env.PORT || 5000;

// Start the server
const startServer = async () => {
  try {
    // Connect to MongoDB
    await connectDB();
    
    // Start listening for requests
    app.listen(PORT, () => {
      console.log(`Server is running on port ${PORT}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
};

// Initialize the server
startServer(); 