import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import Shipping from '../Shipping';
import shippingService from '../../services/shippingService';

// Mock the shipping service
jest.mock('../../services/shippingService');

const mockCarriers = [
  { id: 'carrier1', name: 'Test Carrier 1', services: ['standard', 'express'] },
  { id: 'carrier2', name: 'Test Carrier 2', services: ['standard'] }
];

const mockTrackingInfo = {
  status: 'in_transit',
  location: 'Test City',
  estimated_delivery: '2024-03-20'
};

const mockShippingHistory = [
  { status: 'created', timestamp: '2024-03-18T10:00:00Z' },
  { status: 'in_transit', timestamp: '2024-03-19T10:00:00Z' }
];

describe('Shipping Component', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();

    // Setup default mock implementations
    shippingService.getAvailableCarriers.mockResolvedValue(mockCarriers);
    shippingService.trackShipment.mockResolvedValue(mockTrackingInfo);
    shippingService.getShippingHistory.mockResolvedValue(mockShippingHistory);
    shippingService.getShippingStatus.mockResolvedValue({ current_status: 'pending' });
  });

  test('renders shipping tabs', () => {
    render(<Shipping />);
    expect(screen.getByText('Create Label')).toBeInTheDocument();
    expect(screen.getByText('Track Shipment')).toBeInTheDocument();
    expect(screen.getByText('Manage Status')).toBeInTheDocument();
    expect(screen.getByText('Shipping History')).toBeInTheDocument();
  });

  test('loads carriers when creating label', async () => {
    render(<Shipping />);
    
    const orderIdInput = screen.getByLabelText(/order id/i);
    fireEvent.change(orderIdInput, { target: { value: 'test123' } });
    
    await waitFor(() => {
      expect(shippingService.getAvailableCarriers).toHaveBeenCalledWith('test123');
    });

    expect(screen.getByText('Test Carrier 1')).toBeInTheDocument();
    expect(screen.getByText('Test Carrier 2')).toBeInTheDocument();
  });

  test('creates shipping label', async () => {
    shippingService.createShippingLabel.mockResolvedValue({
      tracking_number: 'TRACK123',
      label_url: 'http://test.com/label'
    });

    render(<Shipping />);
    
    // Fill in the form
    fireEvent.change(screen.getByLabelText(/order id/i), { 
      target: { value: 'test123' } 
    });
    
    await waitFor(() => {
      const carrierSelect = screen.getByLabelText(/carrier/i);
      fireEvent.change(carrierSelect, { target: { value: 'carrier1' } });
    });

    fireEvent.change(screen.getByLabelText(/service level/i), {
      target: { value: 'standard' }
    });

    // Submit the form
    fireEvent.click(screen.getByText('Create Label'));

    await waitFor(() => {
      expect(shippingService.createShippingLabel).toHaveBeenCalledWith(
        'test123',
        'carrier1',
        'standard'
      );
    });
  });

  test('tracks shipment', async () => {
    render(<Shipping />);
    
    // Switch to tracking tab
    fireEvent.click(screen.getByText('Track Shipment'));
    
    const trackingInput = screen.getByLabelText(/tracking number/i);
    fireEvent.change(trackingInput, { target: { value: 'TRACK123' } });
    
    fireEvent.click(screen.getByText('Track'));

    await waitFor(() => {
      expect(shippingService.trackShipment).toHaveBeenCalledWith('TRACK123');
      expect(screen.getByText('in_transit')).toBeInTheDocument();
      expect(screen.getByText('Test City')).toBeInTheDocument();
    });
  });

  test('displays shipping history', async () => {
    render(<Shipping />);
    
    // Switch to history tab
    fireEvent.click(screen.getByText('Shipping History'));
    
    const orderIdInput = screen.getByLabelText(/order id/i);
    fireEvent.change(orderIdInput, { target: { value: 'test123' } });
    
    fireEvent.click(screen.getByText('Get History'));

    await waitFor(() => {
      expect(shippingService.getShippingHistory).toHaveBeenCalledWith('test123');
      expect(screen.getByText('created')).toBeInTheDocument();
      expect(screen.getByText('in_transit')).toBeInTheDocument();
    });
  });

  test('updates shipping status', async () => {
    shippingService.updateShippingStatus.mockResolvedValue({
      current_status: 'delivered'
    });

    render(<Shipping />);
    
    // Switch to manage status tab
    fireEvent.click(screen.getByText('Manage Status'));
    
    const orderIdInput = screen.getByLabelText(/order id/i);
    fireEvent.change(orderIdInput, { target: { value: 'test123' } });
    
    const statusSelect = screen.getByLabelText(/new status/i);
    fireEvent.change(statusSelect, { target: { value: 'delivered' } });
    
    fireEvent.click(screen.getByText('Update Status'));

    await waitFor(() => {
      expect(shippingService.updateShippingStatus).toHaveBeenCalledWith(
        'test123',
        'delivered'
      );
    });
  });

  test('handles errors gracefully', async () => {
    shippingService.getAvailableCarriers.mockRejectedValue(
      new Error('Failed to fetch carriers')
    );

    render(<Shipping />);
    
    const orderIdInput = screen.getByLabelText(/order id/i);
    fireEvent.change(orderIdInput, { target: { value: 'test123' } });

    await waitFor(() => {
      expect(screen.getByText(/failed to fetch carriers/i)).toBeInTheDocument();
    });
  });

  test('cancels shipment', async () => {
    shippingService.cancelShipment.mockResolvedValue({
      success: true,
      cancellation_id: 'CANCEL123'
    });

    render(<Shipping />);
    
    // Switch to manage status tab
    fireEvent.click(screen.getByText('Manage Status'));
    
    const orderIdInput = screen.getByLabelText(/order id/i);
    fireEvent.change(orderIdInput, { target: { value: 'test123' } });
    
    fireEvent.click(screen.getByText('Cancel Shipment'));

    await waitFor(() => {
      expect(shippingService.cancelShipment).toHaveBeenCalledWith('test123');
      expect(screen.getByText(/shipment cancelled/i)).toBeInTheDocument();
    });
  });
}); 