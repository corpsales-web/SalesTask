import React, { useState, useRef, useEffect, useCallback } from 'react';
import axios from 'axios';

const FaceCheckInComponent = ({ onCheckInComplete }) => {
  const [isCapturing, setIsCapturing] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [cameraStream, setCameraStream] = useState(null);
  const [facingMode, setFacingMode] = useState('user'); // 'user' for front camera, 'environment' for back
  const [deviceType, setDeviceType] = useState('unknown');
  const [browserType, setBrowserType] = useState('unknown');
  const [cameraPermissionStatus, setCameraPermissionStatus] = useState('unknown');
  const [availableDevices, setAvailableDevices] = useState([]);
  const [currentDeviceId, setCurrentDeviceId] = useState(null);
  const [isInitializing, setIsInitializing] = useState(false);
  const [supportedConstraints, setSupportedConstraints] = useState({});

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  // Enhanced device detection
  const detectDevice = useCallback(() => {
    const userAgent = navigator.userAgent;
    let device = 'unknown';
    let browser = 'unknown';

    // Device detection
    if (/iPad/i.test(userAgent)) device = 'ipad';
    else if (/iPhone/i.test(userAgent)) device = 'iphone';
    else if (/Android/i.test(userAgent) && /Mobile/i.test(userAgent)) device = 'android-mobile';
    else if (/Android/i.test(userAgent)) device = 'android-tablet';
    else if (/Macintosh/i.test(userAgent)) device = 'macbook';
    else if (/Windows/i.test(userAgent)) device = 'windows';
    else device = 'desktop';

    // Browser detection
    if (/Chrome/i.test(userAgent) && !/Edge/i.test(userAgent)) browser = 'chrome';
    else if (/Firefox/i.test(userAgent)) browser = 'firefox';
    else if (/Safari/i.test(userAgent) && !/Chrome/i.test(userAgent)) browser = 'safari';
    else if (/Edge/i.test(userAgent)) browser = 'edge';
    else browser = 'other';

    setDeviceType(device);
    setBrowserType(browser);
    
    return { device, browser };
  }, []);

  // Check camera permission status
  const checkCameraPermission = useCallback(async () => {
    try {
      if (!navigator.permissions) {
        setCameraPermissionStatus('unknown');
        return 'unknown';
      }

      const permission = await navigator.permissions.query({ name: 'camera' });
      setCameraPermissionStatus(permission.state);
      return permission.state;
    } catch (error) {
      console.warn('Could not check camera permission:', error);
      setCameraPermissionStatus('unknown');
      return 'unknown';
    }
  }, []);

  // Get available camera devices
  const getAvailableDevices = useCallback(async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
        console.warn('enumerateDevices not supported');
        return [];
      }

      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter(device => device.kind === 'videoinput');
      setAvailableDevices(videoDevices);
      return videoDevices;
    } catch (error) {
      console.warn('Could not enumerate devices:', error);
      setAvailableDevices([]);
      return [];
    }
  }, []);

  // Check supported constraints
  const checkSupportedConstraints = useCallback(() => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getSupportedConstraints) {
      setSupportedConstraints({});
      return {};
    }

    const constraints = navigator.mediaDevices.getSupportedConstraints();
    setSupportedConstraints(constraints);
    return constraints;
  }, []);

  // Enhanced initialization
  useEffect(() => {
    const initializeComponent = async () => {
      setIsInitializing(true);
      
      try {
        // Detect device and browser
        detectDevice();
        
        // Check permissions
        await checkCameraPermission();
        
        // Get available devices
        await getAvailableDevices();
        
        // Check supported constraints
        checkSupportedConstraints();
        
      } catch (error) {
        console.warn('Initialization error:', error);
      } finally {
        setIsInitializing(false);
      }
    };

    initializeComponent();
  }, [detectDevice, checkCameraPermission, getAvailableDevices, checkSupportedConstraints]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
      }
    };
  }, [cameraStream]);

  // Enhanced camera constraints based on device and browser
  const getOptimalConstraints = useCallback(() => {
    const baseConstraints = {
      video: {
        facingMode: facingMode,
        audio: false
      }
    };

    // Device-specific optimizations
    if (deviceType === 'iphone' || deviceType === 'ipad') {
      // iOS specific constraints
      baseConstraints.video = {
        ...baseConstraints.video,
        width: { min: 320, ideal: 640, max: 1280 },
        height: { min: 240, ideal: 480, max: 720 },
        frameRate: { ideal: 30, max: 30 },
        ...(currentDeviceId && { deviceId: { exact: currentDeviceId } })
      };
    } else if (deviceType.includes('android')) {
      // Android specific constraints
      baseConstraints.video = {
        ...baseConstraints.video,
        width: { min: 320, ideal: 720, max: 1280 },
        height: { min: 240, ideal: 540, max: 720 },
        frameRate: { ideal: 30, max: 30 },
        ...(currentDeviceId && { deviceId: { exact: currentDeviceId } })
      };
    } else if (deviceType === 'macbook') {
      // MacBook specific constraints
      baseConstraints.video = {
        ...baseConstraints.video,
        width: { min: 640, ideal: 1280, max: 1920 },
        height: { min: 480, ideal: 720, max: 1080 },
        frameRate: { ideal: 30, max: 60 },
        ...(currentDeviceId && { deviceId: { exact: currentDeviceId } })
      };
    } else {
      // Default desktop constraints
      baseConstraints.video = {
        ...baseConstraints.video,
        width: { min: 320, ideal: 1280, max: 1920 },
        height: { min: 240, ideal: 720, max: 1080 },
        frameRate: { ideal: 30, max: 60 },
        ...(currentDeviceId && { deviceId: { exact: currentDeviceId } })
      };
    }

    return baseConstraints;
  }, [facingMode, deviceType, currentDeviceId]);

  // Enhanced camera start with multiple fallbacks
  const startCamera = async () => {
    try {
      setError(null);
      setIsInitializing(true);
      
      // Check HTTPS requirement for some browsers
      if (browserType === 'chrome' && location.protocol !== 'https:' && location.hostname !== 'localhost') {
        throw new Error('Camera access requires HTTPS in Chrome browser');
      }

      // Stop existing stream if any
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
      if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        setCameraStream(null);
      }

      // Check if getUserMedia is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera access is not supported in this browser');
      }

      let stream = null;
      let lastError = null;

      // Try multiple constraint configurations
      const constraintsList = [
        getOptimalConstraints(),
        // Fallback 1: Basic constraints
        {
          video: {
            facingMode: facingMode,
            width: { ideal: 640 },
            height: { ideal: 480 }
          },
          audio: false
        },
        // Fallback 2: Minimal constraints
        {
          video: { facingMode: facingMode },
          audio: false
        },
        // Fallback 3: Any camera
        {
          video: true,
          audio: false
        }
      ];

      for (const constraints of constraintsList) {
        try {
          console.log('Trying constraints:', constraints);
          stream = await navigator.mediaDevices.getUserMedia(constraints);
          break;
        } catch (error) {
          console.warn('Constraint failed:', error);
          lastError = error;
          continue;
        }
      }

      if (!stream) {
        throw lastError || new Error('Could not access camera with any constraints');
      }

      // Store stream reference
      streamRef.current = stream;
      setCameraStream(stream);
      
      // Configure video element
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        
        // Handle different browsers
        if (browserType === 'safari' || deviceType.includes('iphone') || deviceType === 'ipad') {
          // iOS Safari specific handling
          videoRef.current.setAttribute('playsinline', true);
          videoRef.current.setAttribute('webkit-playsinline', true);
          videoRef.current.muted = true;
        }
        
        try {
          await videoRef.current.play();
        } catch (playError) {
          console.warn('Video play error:', playError);
          // Try to play with user interaction
          const playPromise = videoRef.current.play();
          if (playPromise !== undefined) {
            playPromise.catch(e => console.warn('Play promise rejected:', e));
          }
        }
      }

      setIsCapturing(true);

    } catch (error) {
      console.error('Error accessing camera:', error);
      
      // Provide specific error messages based on error type
      let errorMessage = 'Failed to access camera. ';
      
      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        errorMessage += 'Camera permission denied. Please allow camera access and try again.';
      } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
        errorMessage += 'No camera device found. Please check if a camera is connected.';
      } else if (error.name === 'NotSupportedError' || error.name === 'ConstraintNotSatisfiedError') {
        errorMessage += 'Camera settings not supported. Trying with different settings...';
        // Try again with minimal constraints
        setTimeout(() => {
          setFacingMode('user');
          startCamera();
        }, 1000);
        return;
      } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
        errorMessage += 'Camera is busy or not accessible. Please close other apps using the camera and try again.';
      } else if (error.message.includes('HTTPS')) {
        errorMessage += 'Camera access requires HTTPS connection for security. Please use HTTPS.';
      } else {
        errorMessage += error.message || 'Please check camera permissions and try again.';
      }
      
      setError(errorMessage);
    } finally {
      setIsInitializing(false);
    }
  };

  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      setCameraStream(null);
    }
    setIsCapturing(false);
  };

  const captureImage = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to blob
    canvas.toBlob((blob) => {
      setCapturedImage(blob);
      stopCamera();
    }, 'image/jpeg', 0.8);
  };

  const retakePhoto = () => {
    setCapturedImage(null);
    startCamera();
  };

  const switchCamera = async () => {
    const newFacingMode = facingMode === 'user' ? 'environment' : 'user';
    setFacingMode(newFacingMode);
    
    if (isCapturing) {
      stopCamera();
      // Small delay to ensure stream is properly stopped
      setTimeout(() => {
        startCamera();
      }, 100);
    }
  };

  const submitCheckIn = async () => {
    if (!capturedImage) {
      setError('Please capture an image first');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      // Create form data
      const formData = new FormData();
      formData.append('image', capturedImage, 'checkin.jpg');
      formData.append('timestamp', new Date().toISOString());

      // Submit check-in
      const response = await axios.post(
        `${API_BASE_URL}/api/hrms/face-checkin`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      // Success
      if (onCheckInComplete) {
        onCheckInComplete(response.data);
      }

      alert('Check-in successful!');
      setCapturedImage(null);

    } catch (error) {
      console.error('Error submitting check-in:', error);
      setError(error.response?.data?.detail || error.message || 'Check-in failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const getCurrentLocation = () => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          });
        },
        (error) => {
          reject(error);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000 // 5 minutes
        }
      );
    });
  };

  const isMobileDevice = () => {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  };

  return (
    <div className="face-checkin-component bg-white rounded-lg border border-gray-200 p-6">
      <div className="text-center mb-6">
        <h3 className="text-xl font-medium text-gray-900 mb-2">Face Check-In</h3>
        <p className="text-sm text-gray-600">
          Capture your photo to record attendance
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <span className="text-red-500 mr-2">⚠️</span>
            <span className="text-red-700">{error}</span>
          </div>
        </div>
      )}

      {/* Camera View */}
      {isCapturing && (
        <div className="mb-6">
          <div className="relative bg-black rounded-lg overflow-hidden">
            <video
              ref={videoRef}
              className="w-full h-64 object-cover"
              autoPlay
              playsInline
              muted
            />
            
            {/* Camera overlay */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-48 h-48 border-2 border-white rounded-full opacity-50"></div>
            </div>

            {/* Camera controls overlay */}
            <div className="absolute bottom-4 left-0 right-0 flex justify-center space-x-4">
              <button
                onClick={captureImage}
                className="w-16 h-16 bg-white rounded-full border-4 border-gray-300 hover:border-gray-400 transition-colors"
              >
                <div className="w-12 h-12 bg-gray-300 rounded-full mx-auto"></div>
              </button>
              
              {isMobileDevice() && (
                <button
                  onClick={switchCamera}
                  className="w-12 h-12 bg-white bg-opacity-80 rounded-full flex items-center justify-center text-gray-700 hover:bg-opacity-100 transition-all"
                >
                  🔄
                </button>
              )}
            </div>
          </div>

          <div className="mt-4 flex justify-center">
            <button
              onClick={stopCamera}
              className="px-4 py-2 text-sm bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Captured Image Preview */}
      {capturedImage && (
        <div className="mb-6">
          <div className="relative bg-gray-100 rounded-lg overflow-hidden">
            <img
              src={URL.createObjectURL(capturedImage)}
              alt="Captured"
              className="w-full h-64 object-cover"
            />
            
            {/* Preview overlay */}
            <div className="absolute bottom-4 left-0 right-0 flex justify-center space-x-3">
              <button
                onClick={retakePhoto}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
              >
                Retake
              </button>
              
              <button
                onClick={submitCheckIn}
                disabled={isProcessing}
                className={`px-4 py-2 rounded-md font-medium ${
                  isProcessing
                    ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                    : 'bg-green-600 text-white hover:bg-green-700'
                }`}
              >
                {isProcessing ? 'Processing...' : 'Submit Check-In'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Start Camera Button */}
      {!isCapturing && !capturedImage && (
        <div className="text-center">
          <button
            onClick={startCamera}
            className="inline-flex items-center px-6 py-3 border border-transparent rounded-lg shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <span className="text-2xl mr-2">📷</span>
            Start Camera
          </button>
          
          <p className="mt-2 text-xs text-gray-500">
            Make sure you're in a well-lit area for best results
          </p>
        </div>
      )}

      {/* Hidden canvas for image capture */}
      <canvas
        ref={canvasRef}
        className="hidden"
      />

      {/* Browser Compatibility Check */}
      {!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia ? (
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center">
            <span className="text-yellow-500 mr-2">⚠️</span>
            <span className="text-yellow-700">
              Camera access is not supported in this browser. Please use Chrome, Firefox, or Edge.
            </span>
          </div>
        </div>
      ) : null}

      {/* Instructions */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="text-sm font-medium text-blue-800 mb-2">Instructions:</h4>
        <ul className="text-xs text-blue-700 space-y-1">
          <li>• Position your face within the circular guide</li>
          <li>• Ensure good lighting on your face</li>
          <li>• Look directly at the camera</li>
          <li>• Remove sunglasses or face coverings</li>
          <li>• Stay still while capturing</li>
        </ul>
      </div>
    </div>
  );
};

export default FaceCheckInComponent;