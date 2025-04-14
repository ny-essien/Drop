// Import mongoose for MongoDB interaction
import mongoose from 'mongoose';

// Function to connect to MongoDB
export const connectDB = async () => {
  try {
    // Get the connection URI from environment variables
    const uri = process.env.MONGODB_URI;
    
    // Connect to MongoDB using the URI
    // useNewUrlParser and useUnifiedTopology are no longer needed in newer versions
    // as they are now default options
    const conn = await mongoose.connect(uri);
    
    console.log(`MongoDB Connected: ${conn.connection.host}`);
  } catch (error) {
    // Log any connection errors
    console.error(`Error connecting to MongoDB: ${error.message}`);
    process.exit(1); // Exit process with failure
  }
}; 