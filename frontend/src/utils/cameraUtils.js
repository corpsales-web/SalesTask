/**
 * Camera Utility Functions
 * Comprehensive camera handling for containerized and production environments
 */

/**
 * Check if camera devices are available
 */
export const checkCameraAvailability = async () => {
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
      return { available: false, reason: 'NO_MEDIA_DEVICES_API' };
    }

    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoDevices = devices.filter(device => device.kind === 'videoinput');
    
    if (videoDevices.length === 0) {
      return { available: false, reason: 'NO_CAMERA_DEVICES' };
    }

    return { available: true, devices: videoDevices };
  } catch (error) {
    console.error('Camera availability check failed:', error);
    return { available: false, reason: 'ENUMERATION_FAILED', error };
  }
};

/**
 * Initialize camera with proper error handling
 */
export const initializeCamera = async (constraints = {}) => {
  try {
    // Check availability first
    const availability = await checkCameraAvailability();
    if (!availability.available) {
      throw new Error(getErrorMessage(availability.reason));
    }

    // Default constraints for reliable camera access
    const defaultConstraints = {
      video: {
        width: { ideal: 640, max: 1280 },
        height: { ideal: 480, max: 720 },
        facingMode: 'user',
        frameRate: { ideal: 30, max: 30 }
      },
      audio: false
    };

    const finalConstraints = { ...defaultConstraints, ...constraints };
    
    const stream = await navigator.mediaDevices.getUserMedia(finalConstraints);
    
    return {
      success: true,
      stream,
      message: 'Camera initialized successfully'
    };

  } catch (error) {
    console.error('Camera initialization failed:', error);
    
    return {
      success: false,
      error: error.name || 'UNKNOWN_ERROR',
      message: getErrorMessage(error.name || 'UNKNOWN_ERROR'),
      fallbackOptions: getFallbackOptions(error.name)
    };
  }
};

/**
 * Capture photo from video stream
 */
export const capturePhoto = (videoElement, quality = 0.8) => {
  try {
    if (!videoElement || videoElement.readyState !== 4) {
      throw new Error('Video element not ready');
    }

    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    
    // Set canvas dimensions to match video
    canvas.width = videoElement.videoWidth || 640;
    canvas.height = videoElement.videoHeight || 480;
    
    // Draw current video frame to canvas
    context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
    
    // Convert to blob
    const dataURL = canvas.toDataURL('image/jpeg', quality);
    
    return {
      success: true,
      dataURL,
      blob: dataURLToBlob(dataURL),
      dimensions: { width: canvas.width, height: canvas.height }
    };

  } catch (error) {
    console.error('Photo capture failed:', error);
    return {
      success: false,
      error: error.message,
      message: 'Failed to capture photo. Please try again.'
    };
  }
};

/**
 * Stop camera stream properly
 */
export const stopCameraStream = (stream) => {
  try {
    if (stream && stream.getTracks) {
      stream.getTracks().forEach(track => {
        track.stop();
        console.log(`Stopped ${track.kind} track:`, track.label);
      });
      return true;
    }
    return false;
  } catch (error) {
    console.error('Error stopping camera stream:', error);
    return false;
  }
};

/**
 * Get user-friendly error messages
 */
const getErrorMessage = (errorType) => {
  const messages = {
    'NO_MEDIA_DEVICES_API': '📷 Camera API not available in this browser. Please use a modern browser with camera support.',
    'NO_CAMERA_DEVICES': '📷 No camera devices found on this system. This is common in containerized or server environments.',
    'ENUMERATION_FAILED': '📷 Unable to detect camera devices. Camera access may be restricted.',
    'NotAllowedError': '📷 Camera access denied. Please allow camera permissions in your browser settings.',
    'NotFoundError': '📷 No camera device found. Please ensure a camera is connected and accessible.',
    'NotReadableError': '📷 Camera is already in use by another application. Please close other apps using the camera.',
    'OverconstrainedError': '📷 Camera settings not supported. Trying with basic settings.',
    'SecurityError': '📷 Camera access blocked due to security restrictions. Please enable camera permissions.',
    'AbortError': '📷 Camera initialization was interrupted. Please try again.',
    'UNKNOWN_ERROR': '📷 Camera initialization failed due to an unknown error.'
  };

  return messages[errorType] || messages['UNKNOWN_ERROR'];
};

/**
 * Get fallback options based on error type
 */
const getFallbackOptions = (errorType) => {
  const fallbacks = {
    'NO_CAMERA_DEVICES': [
      { type: 'GPS', label: 'Use GPS Location Instead', description: 'Use your location for check-in' },
      { type: 'MANUAL', label: 'Manual Entry', description: 'Enter details manually' }
    ],
    'NotAllowedError': [
      { type: 'PERMISSIONS', label: 'Enable Camera Permissions', description: 'Check browser settings' },
      { type: 'GPS', label: 'Use GPS Instead', description: 'Alternative check-in method' }
    ],
    'NotFoundError': [
      { type: 'GPS', label: 'Use GPS Location Instead', description: 'Use your location for check-in' }
    ],
    'NotReadableError': [
      { type: 'RETRY', label: 'Try Again', description: 'Close other camera apps and retry' },
      { type: 'GPS', label: 'Use GPS Instead', description: 'Alternative method' }
    ]
  };

  return fallbacks[errorType] || fallbacks['NO_CAMERA_DEVICES'];
};

/**
 * Convert data URL to Blob
 */
const dataURLToBlob = (dataURL) => {
  const arr = dataURL.split(',');
  const mime = arr[0].match(/:(.*?);/)[1];
  const bstr = atob(arr[1]);
  let n = bstr.length;
  const u8arr = new Uint8Array(n);
  
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n);
  }
  
  return new Blob([u8arr], { type: mime });
};

/**
 * Check if current environment supports camera
 */
export const isEnvironmentSupported = () => {
  const isHttps = window.location.protocol === 'https:' || window.location.hostname === 'localhost';
  const hasMediaDevices = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  
  return {
    https: isHttps,
    mediaDevices: hasMediaDevices,
    supported: isHttps && hasMediaDevices,
    issues: [
      ...(!isHttps ? ['Camera requires HTTPS or localhost'] : []),
      ...(!hasMediaDevices ? ['Browser does not support camera access'] : [])
    ]
  };
};

/**
 * Get device information for debugging
 */
export const getDeviceInfo = async () => {
  try {
    const environment = isEnvironmentSupported();
    const availability = await checkCameraAvailability();
    
    return {
      userAgent: navigator.userAgent,
      environment,
      availability,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    return {
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
};