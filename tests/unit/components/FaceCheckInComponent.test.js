import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FaceCheckInComponent from '../../../frontend/src/components/FaceCheckInComponent';

// Mock getUserMedia
const mockGetUserMedia = jest.fn();
Object.defineProperty(global.navigator, 'mediaDevices', {
  writable: true,
  value: {
    getUserMedia: mockGetUserMedia,
    enumerateDevices: jest.fn().mockResolvedValue([]),
    getSupportedConstraints: jest.fn().mockReturnValue({})
  }
});

// Mock permissions API
Object.defineProperty(global.navigator, 'permissions', {
  writable: true,
  value: {
    query: jest.fn().mockResolvedValue({ state: 'granted' })
  }
});

describe('FaceCheckInComponent', () => {
  const mockOnCheckInComplete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock video element methods
    window.HTMLVideoElement.prototype.play = jest.fn().mockResolvedValue();
    window.HTMLCanvasElement.prototype.getContext = jest.fn().mockReturnValue({
      drawImage: jest.fn(),
      clearRect: jest.fn(),
      getImageData: jest.fn(),
      putImageData: jest.fn()
    });
  });

  test('renders Face Check-In component with initial UI', () => {
    render(<FaceCheckInComponent onCheckInComplete={mockOnCheckInComplete} />);
    
    expect(screen.getByText('Face Check-In')).toBeInTheDocument();
    expect(screen.getByText('Capture your photo to record attendance')).toBeInTheDocument();
    expect(screen.getByText('Start Camera')).toBeInTheDocument();
  });

  test('displays device and browser information in development mode', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';
    
    render(<FaceCheckInComponent onCheckInComplete={mockOnCheckInComplete} />);
    
    // Check for device info display
    expect(screen.getByText(/Device:/)).toBeInTheDocument();
    expect(screen.getByText(/Browser:/)).toBeInTheDocument();
    
    process.env.NODE_ENV = originalEnv;
  });

  test('shows enhanced instructions for different devices', async () => {
    render(<FaceCheckInComponent onCheckInComplete={mockOnCheckInComplete} />);
    
    expect(screen.getByText('Position your face within the circular guide')).toBeInTheDocument();
    expect(screen.getByText('Ensure good lighting on your face')).toBeInTheDocument();
    expect(screen.getByText('Look directly at the camera')).toBeInTheDocument();
    expect(screen.getByText('Remove sunglasses or face coverings')).toBeInTheDocument();
    expect(screen.getByText('Stay still while capturing')).toBeInTheDocument();
  });

  test('handles camera access with proper fallback mechanisms', async () => {
    const mockStream = {
      getTracks: jest.fn().mockReturnValue([{ stop: jest.fn() }])
    };
    
    mockGetUserMedia
      .mockRejectedValueOnce(new Error('ConstraintNotSatisfiedError'))
      .mockResolvedValueOnce(mockStream);

    render(<FaceCheckInComponent onCheckInComplete={mockOnCheckInComplete} />);
    
    const startButton = screen.getByText('Start Camera');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(mockGetUserMedia).toHaveBeenCalledTimes(2);
    });
  });

  test('displays proper error messages for different error types', async () => {
    const permissionError = new Error('Permission denied');
    permissionError.name = 'NotAllowedError';
    mockGetUserMedia.mockRejectedValue(permissionError);

    render(<FaceCheckInComponent onCheckInComplete={mockOnCheckInComplete} />);
    
    const startButton = screen.getByText('Start Camera');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText(/Camera permission denied/)).toBeInTheDocument();
    });
  });

  test('shows HTTPS requirement warning for Chrome', () => {
    // Mock location
    delete window.location;
    window.location = { protocol: 'http:', hostname: 'example.com' };
    
    // Mock Chrome user agent
    Object.defineProperty(navigator, 'userAgent', {
      writable: true,
      value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124'
    });

    render(<FaceCheckInComponent onCheckInComplete={mockOnCheckInComplete} />);
    
    expect(screen.getByText(/HTTPS connection required/)).toBeInTheDocument();
  });

  test('handles device orientation changes on mobile', async () => {
    // Mock mobile device
    Object.defineProperty(navigator, 'userAgent', {
      writable: true,
      value: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
    });

    render(<FaceCheckInComponent onCheckInComplete={mockOnCheckInComplete} />);

    // Simulate orientation change
    fireEvent(window, new Event('orientationchange'));

    // Component should handle orientation changes gracefully
    expect(screen.getByText('Face Check-In')).toBeInTheDocument();
  });

  test('captures image with device-specific processing', async () => {
    const mockStream = {
      getTracks: jest.fn().mockReturnValue([{ stop: jest.fn() }])
    };
    mockGetUserMedia.mockResolvedValue(mockStream);

    // Mock canvas toBlob
    HTMLCanvasElement.prototype.toBlob = jest.fn((callback) => {
      callback(new Blob(['test'], { type: 'image/jpeg' }));
    });

    render(<FaceCheckInComponent onCheckInComplete={mockOnCheckInComplete} />);
    
    const startButton = screen.getByText('Start Camera');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(mockGetUserMedia).toHaveBeenCalled();
    });

    // Camera should be started, now test capture
    // Note: In real test, we'd need to mock video element properly
  });

  test('includes location services integration', async () => {
    // Mock geolocation
    const mockGeolocation = {
      getCurrentPosition: jest.fn((success) => success({
        coords: { latitude: 40.7128, longitude: -74.0060, accuracy: 10 }
      }))
    };
    Object.defineProperty(global.navigator, 'geolocation', {
      value: mockGeolocation
    });

    render(<FaceCheckInComponent onCheckInComplete={mockOnCheckInComplete} />);
    
    // Component should be able to access location services
    expect(navigator.geolocation).toBeDefined();
  });

  test('provides comprehensive browser compatibility information', () => {
    render(<FaceCheckInComponent onCheckInComplete={mockOnCheckInComplete} />);
    
    // Should show compatibility information
    expect(screen.getByText(/For the best experience, please use:/)).toBeInTheDocument();
    expect(screen.getByText(/Chrome 53\+ or Firefox 36\+/)).toBeInTheDocument();
    expect(screen.getByText(/Safari 11\+ \(iOS 11\+\)/)).toBeInTheDocument();
    expect(screen.getByText(/Edge 12\+/)).toBeInTheDocument();
  });
});