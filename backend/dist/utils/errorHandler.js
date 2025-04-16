"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.errorHandler = exports.catchAsync = exports.AppError = void 0;
class AppError extends Error {
    constructor(message, statusCode) {
        super(message);
        this.statusCode = statusCode;
        this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
        Error.captureStackTrace(this, this.constructor);
    }
}
exports.AppError = AppError;
const catchAsync = (fn) => {
    return (req, res, next) => {
        Promise.resolve(fn(req, res, next)).catch(next);
    };
};
exports.catchAsync = catchAsync;
const errorHandler = (err, _req, res, _next) => {
    if (err instanceof AppError) {
        return res.status(err.statusCode).json({
            status: err.status,
            error: err.message
        });
    }
    return res.status(500).json({
        status: 'error',
        error: 'Something went wrong'
    });
};
exports.errorHandler = errorHandler;
