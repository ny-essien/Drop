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
const mongoose_1 = __importStar(require("mongoose"));
const productSchema = new mongoose_1.Schema({
    name: {
        type: String,
        required: [true, 'Product name is required'],
        trim: true,
        maxlength: [100, 'Product name cannot exceed 100 characters'],
    },
    description: {
        type: String,
        required: [true, 'Product description is required'],
        trim: true,
    },
    price: {
        type: Number,
        required: [true, 'Product price is required'],
        min: [0, 'Price cannot be negative'],
    },
    category: {
        type: String,
        required: [true, 'Product category is required'],
        trim: true,
    },
    images: [{
            type: String,
            required: [true, 'At least one product image is required'],
        }],
    stock: {
        type: Number,
        required: [true, 'Product stock is required'],
        min: [0, 'Stock cannot be negative'],
        default: 0,
    },
    supplier: {
        id: {
            type: mongoose_1.Schema.Types.ObjectId,
            required: [true, 'Supplier ID is required'],
            ref: 'Supplier',
        },
        name: {
            type: String,
            required: [true, 'Supplier name is required'],
            trim: true,
        },
    },
    attributes: {
        type: Map,
        of: mongoose_1.Schema.Types.Mixed,
    },
    isActive: {
        type: Boolean,
        default: true,
    },
}, {
    timestamps: true,
});
// Indexes
productSchema.index({ name: 'text', description: 'text' });
productSchema.index({ category: 1 });
productSchema.index({ price: 1 });
productSchema.index({ 'supplier.id': 1 });
productSchema.index({ isActive: 1 });
// Virtual for formatted price
productSchema.virtual('formattedPrice').get(function () {
    return `$${this.price.toFixed(2)}`;
});
// Method to check if product is in stock
productSchema.methods.isInStock = function () {
    return this.stock > 0;
};
// Method to update stock
productSchema.methods.updateStock = async function (quantity) {
    if (this.stock + quantity < 0) {
        return false;
    }
    this.stock += quantity;
    await this.save();
    return true;
};
const Product = mongoose_1.default.model('Product', productSchema);
exports.default = Product;
