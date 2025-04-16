import mongoose, { Document, Schema } from 'mongoose';

export interface ISupplier extends Document {
  name: string;
  email: string;
  phone: string;
  address: {
    street: string;
    city: string;
    state: string;
    zipCode: string;
    country: string;
  };
  products: mongoose.Types.ObjectId[];
  isActive: boolean;
  rating: number;
  createdAt: Date;
  updatedAt: Date;
}

const supplierSchema = new Schema<ISupplier>(
  {
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
      type: Schema.Types.ObjectId,
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
  },
  {
    timestamps: true,
  }
);

// Indexes
supplierSchema.index({ name: 'text' });
supplierSchema.index({ email: 1 }, { unique: true });
supplierSchema.index({ isActive: 1 });
supplierSchema.index({ rating: 1 });

// Method to calculate average rating
supplierSchema.methods.calculateRating = async function(): Promise<number> {
  const products = await mongoose.model('Product').find({ 'supplier.id': this._id });
  if (products.length === 0) return 0;
  
  const totalRating = products.reduce((sum, product) => sum + (product.rating || 0), 0);
  return totalRating / products.length;
};

export const Supplier = mongoose.model<ISupplier>('Supplier', supplierSchema); 