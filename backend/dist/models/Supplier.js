"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.Supplier = void 0;
const mongoose_1 = __importStar(require("mongoose"));
const supplierSchema = new mongoose_1.Schema({
    name: {
        type: String,
        required: [true, 'Supplier name is required'],
        trim: true,
        maxlength: [100, 'Supplier name cannot exceed 100 characters'],
    },
    email: {
        type: String,
        required: [true, 'Email is required'],
        unique: true,
        lowercase: true,
        trim: true,
        match: [/^\S+@\S+\.\S+$/, 'Please enter a valid email'],
    },
    phone: {
        type: String,
        required: [true, 'Phone number is required'],
        trim: true,
    },
    address: {
        street: {
            type: String,
            required: [true, 'Street address is required'],
            trim: true,
        },
        city: {
            type: String,
            required: [true, 'City is required'],
            trim: true,
        },
        state: {
            type: String,
            required: [true, 'State is required'],
            trim: true,
        },
        zipCode: {
            type: String,
            required: [true, 'ZIP code is required'],
            trim: true,
        },
        country: {
            type: String,
            required: [true, 'Country is required'],
            trim: true,
        },
    },
    products: [{
            type: mongoose_1.Schema.Types.ObjectId,
            ref: 'Product',
        }],
    isActive: {
        type: Boolean,
        default: true,
    },
    rating: {
        type: Number,
        min: [0, 'Rating cannot be less than 0'],
        max: [5, 'Rating cannot be more than 5'],
        default: 0,
    },
}, {
    timestamps: true,
});
// Indexes
supplierSchema.index({ name: 'text' });
supplierSchema.index({ email: 1 }, { unique: true });
supplierSchema.index({ isActive: 1 });
supplierSchema.index({ rating: 1 });
// Method to calculate average rating
supplierSchema.methods.calculateRating = async function () {
    const products = await mongoose_1.default.model('Product').find({ 'supplier.id': this._id });
    if (products.length === 0)
        return 0;
    const totalRating = products.reduce((sum, product) => sum + (product.rating || 0), 0);
    return totalRating / products.length;
};
exports.Supplier = mongoose_1.default.model('Supplier', supplierSchema);
