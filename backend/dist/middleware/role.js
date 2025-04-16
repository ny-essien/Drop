"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.requireRole = void 0;
const requireRole = (roles) => {
    return (req, res, next) => {
        const { role } = req.user;
        if (!roles.includes(role)) {
            return res.status(403).json({ message: 'Access denied' });
        }
        next();
    };
};
exports.requireRole = requireRole;
