import { Request, Response } from 'express';
import Cart from '../models/cart';
import Product from '../models/product';

export const getCart = async (req: Request, res: Response) => {
  try {
    const cart = await Cart.findOne({ userId: req.user?.userId }).populate('items.product');
    
    if (!cart) {
      return res.status(200).json({ items: [] });
    }

    const cartItems = cart.items.map(item => ({
      id: item._id.toString(),
      name: (item.product as any).name,
      price: (item.product as any).price,
      quantity: item.quantity,
      image: (item.product as any).image
    }));

    res.status(200).json(cartItems);
  } catch (error) {
    res.status(500).json({ message: 'Error fetching cart' });
  }
};

export const addToCart = async (req: Request, res: Response) => {
  try {
    const { productId, quantity } = req.body;
    const userId = req.user?.userId;

    if (!userId) {
      return res.status(401).json({ message: 'Authentication required' });
    }

    const product = await Product.findById(productId);
    if (!product) {
      return res.status(404).json({ message: 'Product not found' });
    }

    let cart = await Cart.findOne({ userId });
    
    if (!cart) {
      cart = new Cart({
        userId,
        items: [{ product: productId, quantity }]
      });
    } else {
      const existingItem = cart.items.find(item => 
        item.product.toString() === productId
      );

      if (existingItem) {
        existingItem.quantity += quantity;
      } else {
        cart.items.push({ product: productId, quantity });
      }
    }

    await cart.save();
    
    const updatedCart = await Cart.findById(cart._id).populate('items.product');
    const addedItem = updatedCart?.items.find(item => 
      item.product._id.toString() === productId
    );

    if (!addedItem) {
      return res.status(500).json({ message: 'Error adding item to cart' });
    }

    res.status(201).json({
      id: addedItem._id.toString(),
      name: (addedItem.product as any).name,
      price: (addedItem.product as any).price,
      quantity: addedItem.quantity,
      image: (addedItem.product as any).image
    });
  } catch (error) {
    res.status(500).json({ message: 'Error adding to cart' });
  }
};

export const updateCartItem = async (req: Request, res: Response) => {
  try {
    const { itemId } = req.params;
    const { quantity } = req.body;
    const userId = req.user?.userId;

    if (!userId) {
      return res.status(401).json({ message: 'Authentication required' });
    }

    const cart = await Cart.findOne({ userId });
    if (!cart) {
      return res.status(404).json({ message: 'Cart not found' });
    }

    const item = cart.items.id(itemId);
    if (!item) {
      return res.status(404).json({ message: 'Item not found in cart' });
    }

    item.quantity = quantity;
    await cart.save();

    const updatedCart = await Cart.findById(cart._id).populate('items.product');
    const updatedItem = updatedCart?.items.id(itemId);

    if (!updatedItem) {
      return res.status(500).json({ message: 'Error updating cart item' });
    }

    res.status(200).json({
      id: updatedItem._id.toString(),
      name: (updatedItem.product as any).name,
      price: (updatedItem.product as any).price,
      quantity: updatedItem.quantity,
      image: (updatedItem.product as any).image
    });
  } catch (error) {
    res.status(500).json({ message: 'Error updating cart item' });
  }
};

export const removeFromCart = async (req: Request, res: Response) => {
  try {
    const { itemId } = req.params;
    const userId = req.user?.userId;

    if (!userId) {
      return res.status(401).json({ message: 'Authentication required' });
    }

    const cart = await Cart.findOne({ userId });
    if (!cart) {
      return res.status(404).json({ message: 'Cart not found' });
    }

    const item = cart.items.id(itemId);
    if (!item) {
      return res.status(404).json({ message: 'Item not found in cart' });
    }

    item.remove();
    await cart.save();

    res.status(200).json({ message: 'Item removed from cart' });
  } catch (error) {
    res.status(500).json({ message: 'Error removing item from cart' });
  }
}; 