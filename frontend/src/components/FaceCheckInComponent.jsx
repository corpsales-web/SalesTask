import React, { useState, useRef, useCallback } from 'react';
import { initializeCamera, capturePhoto, stopCameraStream, checkCameraAvailability, getDeviceInfo } from '../utils/cameraUtils';

const FaceCheckInComponent = ({ onCheckInComplete }) => {
  const [cameraActive, setCameraActive] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [cameraStream, setCameraStream] = useState(null);
  const [checkInComplete, setCheckInComplete] = useState(false);
  const [attendanceId, setAttendanceId] = useState(null);
  
  const videoRef = useRef(null);

  const startCamera = useCallback(async () => {
    setError(null);
    setIsProcessing(true);
    
    try {
      // Stop any existing stream
      if (cameraStream) {
        stopCameraStream(cameraStream);
        setCameraStream(null);
      }

      // Initialize camera with comprehensive error handling
      const result = await initializeCamera({
        video: {
          width: { ideal: 640, max: 1280 },
          height: { ideal: 480, max: 720 },
          facingMode: 'user'
        }
      });

      if (result.success) {
        // Set up video element
        if (videoRef.current) {
          videoRef.current.srcObject = result.stream;
          videoRef.current.onloadedmetadata = () => {
            videoRef.current.play().catch(err => {
              console.error('Video play failed:', err);
              setError('📷 Failed to start video preview. Camera may still work for capture.');
            });
          };
        }
        
        setCameraStream(result.stream);
        setCameraActive(true);
        setError(null);
        console.log('✅ Camera initialized successfully');
        
      } else {
        // Handle camera initialization failure
        setError(result.message);
        setCameraActive(false);
        
        // Log device info for debugging
        const deviceInfo = await getDeviceInfo();
        console.log('Camera initialization failed. Device info:', deviceInfo);
      }
      
    } catch (err) {
      console.error('Unexpected camera error:', err);
      setError('📷 Unexpected camera error. Please try GPS Check-in instead.');
      setCameraActive(false);
    } finally {
      setIsProcessing(false);
    }
  }, [cameraStream]);

  const stopCamera = useCallback(() => {
    if (cameraStream) {
      stopCameraStream(cameraStream);
      setCameraStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
    setError(null);
  }, [cameraStream]);

  const handleCapturePhoto = useCallback(() => {
    if (!videoRef.current || !cameraStream) {
      setError('Camera not ready for capture');
      return;
    }

    try {
      setIsProcessing(true);
      
      // Use the comprehensive capture utility
      const result = capturePhoto(videoRef.current, 0.8);
      
      if (result.success) {
        setCapturedImage(result.dataURL);
        console.log('✅ Photo captured successfully:', result.dimensions);
        
        // Stop camera after successful capture
        if (cameraStream) {
          stopCameraStream(cameraStream);
        }
        setCameraStream(null);
        setCameraActive(false);
        setError(null);
        
      } else {
        setError(result.message);
        console.error('Photo capture failed:', result.error);
      }
      
    } catch (err) {
      console.error('Unexpected capture error:', err);
      setError('📷 Failed to capture photo. Please try again or use GPS Check-in.');
    } finally {
      setIsProcessing(false);
    }
  }, [cameraStream]);

  const completeCheckIn = useCallback(async () => {
    if (!capturedImage) return;

    setIsProcessing(true);
    try {
      // Simulate attendance recording
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      if (onCheckInComplete) {
        onCheckInComplete({
          success: true,
          method: 'face_checkin',
          timestamp: new Date().toISOString(),
          image: capturedImage
        });
      }
    } catch (error) {
      setError('Failed to record attendance. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  }, [capturedImage, onCheckInComplete]);

  const completeGPSCheckIn = useCallback(async () => {
    setIsProcessing(true);
    setError(null);
    
    try {
      // Get location with proper error handling
      const position = await new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
          reject(new Error('Geolocation not supported'));
          return;
        }
        
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 15000,
          maximumAge: 60000
        });
      });

      // Simulate attendance recording with GPS
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (onCheckInComplete) {
        onCheckInComplete({
          success: true,
          method: 'gps_checkin',
          timestamp: new Date().toISOString(),
          location: {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          }
        });
      }
    } catch (error) {
      setError('GPS check-in failed. Please try manual check-in.');
    } finally {
      setIsProcessing(false);
    }
  }, [onCheckInComplete]);

  const retryCapture = useCallback(() => {
    setCapturedImage(null);
    setError(null);
    startCamera();
  }, [startCamera]);

  return (
    <div className="face-checkin-component bg-white rounded-lg border border-gray-200 p-6 max-w-md mx-auto">
      <div className="text-center mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2">📷 Face Check-In</h2>
        <p className="text-sm text-gray-600">Capture your photo to record attendance</p>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm">{error}</p>
          <div className="mt-2 flex space-x-2">
            <button
              onClick={completeGPSCheckIn}
              disabled={isProcessing}
              className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-50"
            >
              📍 Use GPS Instead
            </button>
            <button
              onClick={() => setError(null)}
              className="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {!cameraActive && !capturedImage && !error && (
        <div className="text-center">
          <div className="mb-4 p-6 border-2 border-dashed border-gray-300 rounded-lg">
            <div className="text-4xl mb-2">📸</div>
            <p className="text-gray-600">Ready to capture your photo</p>
          </div>
          <div className="space-y-3">
            <button
              onClick={startCamera}
              disabled={isProcessing}
              className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
            >
              {isProcessing ? 'Processing...' : '📷 Start Camera'}
            </button>
            
            <div className="text-gray-500 text-sm">or</div>
            
            <button
              onClick={completeGPSCheckIn}
              disabled={isProcessing}
              className="w-full bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium"
            >
              📍 GPS Check-In Instead
            </button>
          </div>
        </div>
      )}

      {cameraActive && (
        <div className="text-center">
          <div className="mb-4 bg-black rounded-lg overflow-hidden">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full"
              style={{ transform: 'scaleX(-1)' }}
            />
          </div>
          <div className="flex space-x-2">
            <button
              onClick={handleCapturePhoto}
              className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 font-medium"
            >
              📸 Capture
            </button>
            <button
              onClick={stopCamera}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {capturedImage && (
        <div className="text-center">
          <div className="mb-4">
            <img
              src={capturedImage}
              alt="Captured"
              className="w-full rounded-lg border"
            />
          </div>
          <div className="flex space-x-2">
            <button
              onClick={completeCheckIn}
              disabled={isProcessing}
              className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium"
            >
              {isProcessing ? 'Recording...' : '✅ Complete Check-In'}
            </button>
            <button
              onClick={retryCapture}
              disabled={isProcessing}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              🔄 Retake
            </button>
          </div>
        </div>
      )}

      <canvas ref={canvasRef} className="hidden" />
      
      {/* Alternative GPS Check-In */}
      {!cameraActive && !capturedImage && !isProcessing && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <button
            onClick={completeGPSCheckIn}
            className="w-full bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 font-medium"
          >
            📍 GPS Check-In Instead
          </button>
        </div>
      )}
    </div>
  );
};

export default FaceCheckInComponent;