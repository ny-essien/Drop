"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.logout = exports.updateProfile = exports.resetPassword = exports.forgotPassword = exports.login = exports.verifyEmail = exports.signup = void 0;
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const crypto_1 = __importDefault(require("crypto"));
const User_1 = __importDefault(require("../models/User"));
const email_1 = require("../utils/email");
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
const signup = async (req, res) => {
    try {
        const { username, email, password } = req.body;
        // Check if user already exists
        const existingUser = await User_1.default.findOne({ $or: [{ email }, { username }] });
        if (existingUser) {
            return res.status(400).json({ message: 'User already exists' });
        }
        // Generate verification token
        const verificationToken = crypto_1.default.randomBytes(20).toString('hex');
        // Create new user
        const user = new User_1.default({
            username,
            email,
            password,
            verificationToken
        });
        await user.save();
        // Send verification email
        await (0, email_1.sendVerificationEmail)(user.email, verificationToken);
        // Generate JWT token
        const token = jsonwebtoken_1.default.sign({ userId: user._id }, JWT_SECRET, { expiresIn: '24h' });
        return res.status(201).json({
            message: 'User created successfully. Please check your email to verify your account.',
            token,
            user: {
                id: user._id,
                username: user.username,
                email: user.email,
                isVerified: user.isVerified
            }
        });
    }
    catch (error) {
        return res.status(500).json({ message: 'Error creating user', error });
    }
};
exports.signup = signup;
const verifyEmail = async (req, res) => {
    try {
        const { token } = req.params;
        const user = await User_1.default.findOne({ verificationToken: token });
        if (!user) {
            return res.status(400).json({ message: 'Invalid verification token' });
        }
        user.isVerified = true;
        user.verificationToken = undefined;
        await user.save();
        return res.json({ message: 'Email verified successfully' });
    }
    catch (error) {
        return res.status(500).json({ message: 'Error verifying email', error });
    }
};
exports.verifyEmail = verifyEmail;
const login = async (req, res) => {
    try {
        const { email, password } = req.body;
        // Find user by email
        const user = await User_1.default.findOne({ email });
        if (!user) {
            return res.status(401).json({ message: 'Invalid credentials' });
        }
        // Check if email is verified
        if (!user.isVerified) {
            return res.status(401).json({ message: 'Please verify your email first' });
        }
        // Check password
        const isMatch = await user.comparePassword(password);
        if (!isMatch) {
            return res.status(401).json({ message: 'Invalid credentials' });
        }
        // Generate JWT token
        const token = jsonwebtoken_1.default.sign({ userId: user._id }, JWT_SECRET, { expiresIn: '24h' });
        return res.json({
            message: 'Login successful',
            token,
            user: {
                id: user._id,
                username: user.username,
                email: user.email,
                isVerified: user.isVerified,
                role: user.role
            }
        });
    }
    catch (error) {
        return res.status(500).json({ message: 'Error logging in', error });
    }
};
exports.login = login;
const forgotPassword = async (req, res) => {
    try {
        const { email } = req.body;
        const user = await User_1.default.findOne({ email });
        if (!user) {
            return res.status(404).json({ message: 'User not found' });
        }
        const resetToken = await user.generatePasswordResetToken();
        await (0, email_1.sendPasswordResetEmail)(user.email, resetToken);
        return res.json({ message: 'Password reset email sent' });
    }
    catch (error) {
        return res.status(500).json({ message: 'Error sending password reset email', error });
    }
};
exports.forgotPassword = forgotPassword;
const resetPassword = async (req, res) => {
    try {
        const { token } = req.params;
        const { password } = req.body;
        const hashedToken = crypto_1.default
            .createHash('sha256')
            .update(token)
            .digest('hex');
        const user = await User_1.default.findOne({
            resetPasswordToken: hashedToken,
            resetPasswordExpires: { $gt: Date.now() }
        });
        if (!user) {
            return res.status(400).json({ message: 'Invalid or expired token' });
        }
        user.password = password;
        user.resetPasswordToken = undefined;
        user.resetPasswordExpires = undefined;
        await user.save();
        return res.json({ message: 'Password reset successful' });
    }
    catch (error) {
        return res.status(500).json({ message: 'Error resetting password', error });
    }
};
exports.resetPassword = resetPassword;
const updateProfile = async (req, res) => {
    try {
        const { userId } = req.user;
        const { firstName, lastName, phone, address } = req.body;
        const user = await User_1.default.findById(userId);
        if (!user) {
            return res.status(404).json({ message: 'User not found' });
        }
        user.profile = {
            firstName,
            lastName,
            phone,
            address
        };
        await user.save();
        return res.json({
            message: 'Profile updated successfully',
            profile: user.profile
        });
    }
    catch (error) {
        return res.status(500).json({ message: 'Error updating profile', error });
    }
};
exports.updateProfile = updateProfile;
const logout = (req, res) => {
    res.json({ message: 'Logout successful' });
};
exports.logout = logout;
