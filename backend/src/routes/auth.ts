import express from 'express';
import { 
  signup, 
  login, 
  logout, 
  verifyEmail,
  forgotPassword,
  resetPassword,
  updateProfile
} from '../controllers/auth';
import { auth } from '../middleware/auth';

const router = express.Router();

// Public routes
router.post('/register', signup);
router.post('/login', login);
router.get('/verify-email/:token', verifyEmail);
router.post('/forgot-password', forgotPassword);
router.post('/reset-password/:token', resetPassword);

// Protected routes
router.post('/logout', auth, logout);
router.put('/profile', auth, updateProfile);

export default router; 