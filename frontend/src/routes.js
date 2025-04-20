import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { PrivateRoute } from './components/PrivateRoute';
import { AdminRoute } from './components/AdminRoute';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import Products from './components/Products';
import Cart from './components/Cart';
import Orders from './components/Orders';
import SupportTicket from './components/SupportTicket';
import FAQ from './components/FAQ';
import KnowledgeBase from './components/KnowledgeBase';
import AdminDashboard from './components/AdminDashboard';
import AdminProducts from './components/AdminProducts';
import AdminOrders from './components/AdminOrders';
import AdminUsers from './components/AdminUsers';
import AdminSupport from './components/AdminSupport';
import AdminFAQ from './components/AdminFAQ';
import AdminKnowledgeBase from './components/AdminKnowledgeBase';

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/faq" element={<FAQ />} />
      <Route path="/knowledge-base" element={<KnowledgeBase />} />

      {/* Protected Routes */}
      <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
      <Route path="/products" element={<PrivateRoute><Products /></PrivateRoute>} />
      <Route path="/cart" element={<PrivateRoute><Cart /></PrivateRoute>} />
      <Route path="/orders" element={<PrivateRoute><Orders /></PrivateRoute>} />
      <Route path="/support" element={<PrivateRoute><SupportTicket /></PrivateRoute>} />

      {/* Admin Routes */}
      <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
      <Route path="/admin/products" element={<AdminRoute><AdminProducts /></AdminRoute>} />
      <Route path="/admin/orders" element={<AdminRoute><AdminOrders /></AdminRoute>} />
      <Route path="/admin/users" element={<AdminRoute><AdminUsers /></AdminRoute>} />
      <Route path="/admin/support" element={<AdminRoute><AdminSupport /></AdminRoute>} />
      <Route path="/admin/faq" element={<AdminRoute><AdminFAQ /></AdminRoute>} />
      <Route path="/admin/knowledge-base" element={<AdminRoute><AdminKnowledgeBase /></AdminRoute>} />
    </Routes>
  );
};

export default AppRoutes; 