import shippingService from '../shippingService';
import api from '../api';

jest.mock('../api');

describe('Shipping Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('getAvailableCarriers fetches carriers for an order', async () => {
    const mockCarriers = [
      { id: 'carrier1', name: 'Test Carrier 1' },
      { id: 'carrier2', name: 'Test Carrier 2' }
    ];
    api.get.mockResolvedValue({ data: mockCarriers });

    const result = await shippingService.getAvailableCarriers('test123');
    
    expect(api.get).toHaveBeenCalledWith('/orders/test123/carriers');
    expect(result).toEqual(mockCarriers);
  });

  test('createShippingLabel creates a label for an order', async () => {
    const mockLabel = {
      tracking_number: 'TRACK123',
      label_url: 'http://test.com/label'
    };
    api.post.mockResolvedValue({ data: mockLabel });

    const result = await shippingService.createShippingLabel(
      'test123',
      'carrier1',
      'standard'
    );
    
    expect(api.post).toHaveBeenCalledWith('/orders/test123/labels', {
      carrier_id: 'carrier1',
      service_level: 'standard'
    });
    expect(result).toEqual(mockLabel);
  });

  test('trackShipment retrieves tracking information', async () => {
    const mockTracking = {
      status: 'in_transit',
      location: 'Test City',
      estimated_delivery: '2024-03-20'
    };
    api.get.mockResolvedValue({ data: mockTracking });

    const result = await shippingService.trackShipment('TRACK123');
    
    expect(api.get).toHaveBeenCalledWith('/tracking/TRACK123');
    expect(result).toEqual(mockTracking);
  });

  test('getShippingStatus retrieves status for an order', async () => {
    const mockStatus = { current_status: 'in_transit' };
    api.get.mockResolvedValue({ data: mockStatus });

    const result = await shippingService.getShippingStatus('test123');
    
    expect(api.get).toHaveBeenCalledWith('/orders/test123/status');
    expect(result).toEqual(mockStatus);
  });

  test('updateShippingStatus updates status for an order', async () => {
    const mockResponse = { current_status: 'delivered' };
    api.put.mockResolvedValue({ data: mockResponse });

    const result = await shippingService.updateShippingStatus('test123', 'delivered');
    
    expect(api.put).toHaveBeenCalledWith('/orders/test123/status', {
      status: 'delivered'
    });
    expect(result).toEqual(mockResponse);
  });

  test('getShippingHistory retrieves history for an order', async () => {
    const mockHistory = [
      { status: 'created', timestamp: '2024-03-18T10:00:00Z' },
      { status: 'in_transit', timestamp: '2024-03-19T10:00:00Z' }
    ];
    api.get.mockResolvedValue({ data: mockHistory });

    const result = await shippingService.getShippingHistory('test123');
    
    expect(api.get).toHaveBeenCalledWith('/orders/test123/history');
    expect(result).toEqual(mockHistory);
  });

  test('cancelShipment cancels a shipment', async () => {
    const mockResponse = {
      success: true,
      cancellation_id: 'CANCEL123'
    };
    api.post.mockResolvedValue({ data: mockResponse });

    const result = await shippingService.cancelShipment('test123');
    
    expect(api.post).toHaveBeenCalledWith('/orders/test123/cancel');
    expect(result).toEqual(mockResponse);
  });

  test('handles API errors gracefully', async () => {
    const errorMessage = 'Network Error';
    api.get.mockRejectedValue(new Error(errorMessage));

    await expect(shippingService.getAvailableCarriers('test123'))
      .rejects
      .toThrow(errorMessage);
  });

  test('handles empty responses', async () => {
    api.get.mockResolvedValue({ data: null });

    const result = await shippingService.getShippingStatus('test123');
    expect(result).toBeNull();
  });
}); 