"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.connectDB = void 0;
const mongoose_1 = __importDefault(require("mongoose"));
const logger_1 = require("./logger");
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/dropship';
const connectDB = async () => {
    try {
        await mongoose_1.default.connect(MONGODB_URI, {
            maxPoolSize: 10,
            serverSelectionTimeoutMS: 5000,
            socketTimeoutMS: 45000,
        });
        logger_1.logger.info('MongoDB connected successfully');
    }
    catch (error) {
        logger_1.logger.error('MongoDB connection error:', error);
        process.exit(1);
    }
};
exports.connectDB = connectDB;
mongoose_1.default.connection.on('error', (err) => {
    logger_1.logger.error('MongoDB connection error:', err);
});
mongoose_1.default.connection.on('disconnected', () => {
    logger_1.logger.warn('MongoDB disconnected');
});
mongoose_1.default.connection.on('reconnected', () => {
    logger_1.logger.info('MongoDB reconnected');
});
process.on('SIGINT', async () => {
    try {
        await mongoose_1.default.connection.close();
        logger_1.logger.info('MongoDB connection closed through app termination');
        process.exit(0);
    }
    catch (err) {
        logger_1.logger.error('Error closing MongoDB connection:', err);
        process.exit(1);
    }
});
