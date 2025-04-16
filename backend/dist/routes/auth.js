"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const auth_1 = require("../middleware/auth");
const auth_2 = require("../controllers/auth");
const router = (0, express_1.Router)();
// Auth routes
router.post('/register', async (req, res) => {
    await (0, auth_2.signup)(req, res);
});
router.post('/login', async (req, res) => {
    await (0, auth_2.login)(req, res);
});
router.get('/verify-email/:token', async (req, res) => {
    await (0, auth_2.verifyEmail)(req, res);
});
router.post('/forgot-password', async (req, res) => {
    await (0, auth_2.forgotPassword)(req, res);
});
router.post('/reset-password/:token', async (req, res) => {
    await (0, auth_2.resetPassword)(req, res);
});
router.post('/logout', auth_1.auth, async (req, res) => {
    await (0, auth_2.logout)(req, res);
});
router.put('/profile', auth_1.auth, async (req, res) => {
    await (0, auth_2.updateProfile)(req, res);
});
exports.default = router;
