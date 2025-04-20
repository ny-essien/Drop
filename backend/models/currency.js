const mongoose = require('mongoose');

const currencySchema = new mongoose.Schema({
    code: {
        type: String,
        required: true,
        unique: true,
        uppercase: true
    },
    name: {
        type: String,
        required: true
    },
    symbol: {
        type: String,
        required: true
    },
    exchange_rate: {
        type: Number,
        required: true,
        default: 1
    },
    is_default: {
        type: Boolean,
        default: false
    },
    last_updated: {
        type: Date,
        default: Date.now
    },
    status: {
        type: String,
        enum: ['active', 'inactive'],
        default: 'active'
    }
}, {
    timestamps: true
});

// Ensure only one default currency exists
currencySchema.pre('save', async function(next) {
    if (this.is_default) {
        await this.constructor.updateMany(
            { _id: { $ne: this._id } },
            { is_default: false }
        );
    }
    next();
});

module.exports = mongoose.model('Currency', currencySchema); 