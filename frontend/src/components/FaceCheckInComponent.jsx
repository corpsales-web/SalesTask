import React, { useState, useRef, useCallback } from 'react';

const FaceCheckInComponent = ({ onCheckInComplete }) => {
  const [cameraActive, setCameraActive] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [cameraStream, setCameraStream] = useState(null);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const startCamera = useCallback(async () => {
    setError(null);
    try {
      // Stop any existing stream
      if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
      }

      // Simple, reliable camera constraints
      const constraints = {
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        },
        audio: false
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play();
        };
      }
      
      setCameraStream(stream);
      setCameraActive(true);
      setError(null);
      
    } catch (err) {
      console.error('Camera access error:', err);
      setError('Camera access failed. Please ensure camera permissions are granted.');
      setCameraActive(false);
      
      // Provide working alternatives
      setTimeout(() => {
        if (onCheckInComplete) {
          // Offer GPS check-in as working alternative
          const useGPS = window.confirm('Camera not available. Would you like to use GPS check-in instead?');
          if (useGPS) {
            completeGPSCheckIn();
          }
        }
      }, 1000);
    }
  }, [cameraStream, onCheckInComplete]);

  const stopCamera = useCallback(() => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      setCameraStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
    setError(null);
  }, [cameraStream]);

  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to data URL
    const imageDataUrl = canvas.toDataURL('image/jpeg', 0.8);
    setCapturedImage(imageDataUrl);

    // Stop camera after capture
    stopCamera();
  }, [stopCamera]);

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
    try {
      // Get location
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 10000,
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
          <button
            onClick={startCamera}
            disabled={isProcessing}
            className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
          >
            {isProcessing ? 'Processing...' : '📷 Start Camera'}
          </button>
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
              onClick={capturePhoto}
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