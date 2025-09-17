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
  const canvasRef = useRef(null);

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
        // Set up video element with proper event handling
        if (videoRef.current) {
          const video = videoRef.current;
          
          // Set up event handlers before setting srcObject
          video.onloadedmetadata = () => {
            console.log('✅ Video metadata loaded:', {
              readyState: video.readyState,
              videoWidth: video.videoWidth,
              videoHeight: video.videoHeight
            });
            
            video.play().then(() => {
              console.log('✅ Video playing successfully');
              // Only set camera as active after video is actually playing
              setCameraActive(true);
              setError(null);
            }).catch(err => {
              console.error('Video play failed:', err);
              setError('📷 Failed to start video preview. Camera may still work for capture.');
            });
          };
          
          video.onloadeddata = () => {
            console.log('✅ Video data loaded - ready for capture');
          };
          
          video.onerror = (err) => {
            console.error('Video element error:', err);
            setError('📷 Video display error. Please try again.');
          };
          
          video.oncanplay = () => {
            console.log('✅ Video can start playing');
          };
          
          // Set the stream
          video.srcObject = result.stream;
        }
        
        setCameraStream(result.stream);
        // Don't set cameraActive here - wait for video to be ready
        console.log('✅ Camera stream obtained successfully');
        
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
    console.log('🔍 Starting photo capture process...');
    
    if (!videoRef.current) {
      setError('Video element not found');
      return;
    }
    
    if (!cameraStream) {
      setError('Camera stream not available');
      return;
    }

    const video = videoRef.current;
    
    // Check if video is ready immediately
    console.log('🔍 Pre-capture video state:', {
      readyState: video.readyState,
      videoWidth: video.videoWidth,
      videoHeight: video.videoHeight,
      paused: video.paused
    });

    try {
      setIsProcessing(true);
      setError(null);
      
      // Function to attempt capture
      const attemptCapture = () => {
        const result = capturePhoto(video, 0.8);
        
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
          console.error('📸 Photo capture failed:', result.error);
          setError(result.message || '📷 Failed to capture photo. Please try again.');
        }
        
        setIsProcessing(false);
      };
      
      // If video isn't ready, wait for it
      if (video.readyState < 2 || !video.videoWidth || !video.videoHeight) {
        console.log('⏳ Video not ready, waiting for loadeddata event...');
        
        const onVideoReady = () => {
          console.log('✅ Video ready for capture:', {
            readyState: video.readyState,
            videoWidth: video.videoWidth,
            videoHeight: video.videoHeight
          });
          video.removeEventListener('loadeddata', onVideoReady);
          video.removeEventListener('canplay', onVideoReady);
          attemptCapture();
        };
        
        video.addEventListener('loadeddata', onVideoReady);
        video.addEventListener('canplay', onVideoReady);
        
        // Fallback timeout
        setTimeout(() => {
          video.removeEventListener('loadeddata', onVideoReady);
          video.removeEventListener('canplay', onVideoReady);
          console.log('⏰ Timeout reached, attempting capture anyway...');
          attemptCapture();
        }, 3000);
        
      } else {
        // Video is ready, capture immediately
        attemptCapture();
      }
      
    } catch (err) {
      console.error('🚨 Unexpected capture error:', err);
      setError('📷 Failed to capture photo. Please try again or use GPS Check-in.');
      setIsProcessing(false);
    }
  }, [cameraStream]);

  const completeCheckIn = useCallback(async () => {
    if (!capturedImage) return;

    setIsProcessing(true);
    try {
      // Prepare data for face check-in API
      const checkinData = {
        employee_id: 'current_user', // This would come from auth context
        face_image: capturedImage,
        timestamp: new Date().toISOString(),
        device_info: navigator.userAgent
      };

      // Make actual API call to record face attendance
      const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const response = await fetch(`${API}/api/hrms/face-checkin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(checkinData)
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      // Set success state
      setCheckInComplete(true);
      setAttendanceId(`ATT_FACE_${Date.now()}`);
      setError(null);
      
      if (onCheckInComplete) {
        onCheckInComplete({
          success: true,
          method: 'face_checkin',
          timestamp: result.check_in_time || checkinData.timestamp,
          image: capturedImage,
          confidence: result.recognition_confidence
        });
      }
    } catch (error) {
      console.error('Face check-in error:', error);
      setError('Failed to record attendance. Please try again or use GPS check-in.');
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

      // Create attendance record with GPS data
      const attendanceData = {
        employee_id: 'current_user', // This would come from auth context
        check_in_time: new Date().toISOString(),
        method: 'gps',
        location: {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy
        },
        device_info: navigator.userAgent
      };

      // Make actual API call to record GPS attendance
      const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const response = await fetch(`${API}/api/hrms/gps-checkin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(attendanceData)
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      // Set success state
      setCheckInComplete(true);
      setAttendanceId(result.attendance_id || `ATT_${Date.now()}`);
      setError(null);
      
      if (onCheckInComplete) {
        onCheckInComplete({
          success: true,
          method: 'gps_checkin',
          timestamp: result.check_in_time || attendanceData.check_in_time,
          location: attendanceData.location,
          attendance_id: result.attendance_id
        });
      }
    } catch (error) {
      console.error('GPS check-in error:', error);
      if (error.code === 1) {
        setError('📍 Location access denied. Please enable location permissions or try manual check-in.');
      } else if (error.code === 2) {
        setError('📍 Location unavailable. Please check your GPS settings or try manual check-in.');
      } else if (error.code === 3) {
        setError('📍 Location request timed out. Please try again or use manual check-in.');
      } else {
        setError('📍 GPS check-in failed. Please try manual check-in or contact support.');
      }
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
        <h2 className="text-xl font-bold text-gray-900 mb-2">📷 Camera Check-In</h2>
        <p className="text-sm text-gray-600">Use your camera to capture attendance photo</p>
      </div>

      {/* Success State */}
      {checkInComplete && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-center">
          <div className="text-green-600 text-2xl mb-2">✅</div>
          <h3 className="text-lg font-semibold text-green-800 mb-1">Check-In Successful!</h3>
          <p className="text-green-700 text-sm mb-2">Attendance recorded successfully</p>
          {attendanceId && (
            <p className="text-green-600 text-xs">ID: {attendanceId}</p>
          )}
          <button
            onClick={() => {
              setCheckInComplete(false);
              setAttendanceId(null);
              setCapturedImage(null);
              setError(null);
            }}
            className="mt-3 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
          >
            New Check-In
          </button>
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm">{error}</p>
          <div className="mt-2 flex space-x-2">
            <button
              onClick={() => setError(null)}
              className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
            >
              🔄 Try Camera Again
            </button>
            <button
              onClick={completeGPSCheckIn}
              disabled={isProcessing}
              className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700 disabled:opacity-50"
            >
              📍 Use GPS Instead
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
              className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium text-lg"
            >
              {isProcessing ? 'Initializing Camera...' : '📷 Start Camera Check-In'}
            </button>
            
            <div className="text-gray-400 text-xs">Camera is the recommended method for attendance</div>
            
            <button
              onClick={completeGPSCheckIn}
              disabled={isProcessing}
              className="w-full bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 disabled:opacity-50 text-sm"
            >
              📍 Alternative: GPS Check-In
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
              controls={false}
              className="w-full"
              style={{ transform: 'scaleX(-1)', minHeight: '200px' }}
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