import express from 'express';
import cors from 'cors';
import morgan from 'morgan';
import { connectDB } from './utils/db';
import { errorHandler } from './utils/errorHandler';
import { logger } from './utils/logger';

// Import routes
import authRoutes from './routes/auth';
import productRoutes from './routes/products';
import cartRoutes from './routes/cart';
import orderRoutes from './routes/orders';

const app = express();

// Connect to MongoDB
connectDB().catch((err) => {
  logger.error('Failed to connect to MongoDB', err);
  process.exit(1);
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/products', productRoutes);
app.use('/api/cart', cartRoutes);
app.use('/api/orders', orderRoutes);

// Error handling
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  errorHandler(err, req, res, next);
});

// 404 handler
app.use((_, res) => {
  res.status(404).json({ error: 'Not found' });
});

export default app; 