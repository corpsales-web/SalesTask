import React, { useState, useCallback, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

const FileUploadComponent = ({ projectId, onUploadComplete, maxFiles = 10, acceptedTypes = {} }) => {
  const [uploads, setUploads] = useState({});
  const [uploadProgress, setUploadProgress] = useState({});
  const [completedUploads, setCompletedUploads] = useState([]);
  const [errors, setErrors] = useState({});
  const [showCameraCapture, setShowCameraCapture] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);
  
  const abortControllers = useRef({});
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  // Camera functionality
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 1280 }, 
          height: { ideal: 720 },
          facingMode: 'environment' // Use back camera if available
        } 
      });
      setCameraStream(stream);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setShowCameraCapture(true);
    } catch (error) {
      console.error('Error accessing camera:', error);
      setErrors(prev => ({ ...prev, camera: 'Failed to access camera. Please check permissions.' }));
    }
  };

  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      setCameraStream(null);
    }
    setShowCameraCapture(false);
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0);
      
      canvas.toBlob(async (blob) => {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `camera-capture-${timestamp}.jpg`;
        const file = new File([blob], filename, { type: 'image/jpeg' });
        
        // Upload the captured photo
        await uploadFile(file);
        stopCamera();
      }, 'image/jpeg', 0.8);
    }
  };

  const defaultAcceptedTypes = {
    'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'],
    'video/*': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'],
    'application/pdf': ['.pdf'],
    'text/*': ['.txt', '.csv', '.json'],
    'application/zip': ['.zip'],
    'application/x-zip-compressed': ['.zip']
  };

  const onDrop = useCallback(async (acceptedFiles, rejectedFiles) => {
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      const newErrors = {};
      rejectedFiles.forEach(rejection => {
        const filename = rejection.file.name;
        newErrors[filename] = rejection.errors.map(err => err.message).join(', ');
      });
      setErrors(prev => ({ ...prev, ...newErrors }));
    }

    // Process accepted files
    for (const file of acceptedFiles) {
      await uploadFile(file);
    }
  }, [projectId]);

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragReject
  } = useDropzone({
    onDrop,
    accept: Object.keys(acceptedTypes).length > 0 ? acceptedTypes : defaultAcceptedTypes,
    maxSize: 500 * 1024 * 1024, // 500MB
    maxFiles: maxFiles,
    multiple: true
  });

  const uploadFile = async (file) => {
    const fileId = `${Date.now()}-${file.name}`;
    
    try {
      // Create abort controller for this upload
      abortControllers.current[fileId] = new AbortController();

      // Initialize upload state
      setUploads(prev => ({
        ...prev,
        [fileId]: {
          file,
          status: 'uploading',
          startTime: Date.now()
        }
      }));

      setUploadProgress(prev => ({
        ...prev,
        [fileId]: {
          loaded: 0,
          total: file.size,
          percentage: 0
        }
      }));

      // Create form data
      const formData = new FormData();
      formData.append('file', file);
      if (projectId) {
        formData.append('project_id', projectId);
      }

      // Get auth token
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      // Upload file
      const response = await axios.post(
        `${API_BASE_URL}/api/upload/file`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          },
          signal: abortControllers.current[fileId].signal,
          onUploadProgress: (progressEvent) => {
            const progress = {
              loaded: progressEvent.loaded,
              total: progressEvent.total,
              percentage: Math.round((progressEvent.loaded / progressEvent.total) * 100)
            };
            
            setUploadProgress(prev => ({
              ...prev,
              [fileId]: progress
            }));
          }
        }
      );

      // Upload successful
      setUploads(prev => ({
        ...prev,
        [fileId]: {
          ...prev[fileId],
          status: 'completed',
          result: response.data
        }
      }));

      setCompletedUploads(prev => [...prev, response.data]);

      if (onUploadComplete) {
        onUploadComplete(response.data);
      }

    } catch (error) {
      if (error.name === 'AbortError' || error.message === 'canceled') {
        // Upload was cancelled
        setUploads(prev => ({
          ...prev,
          [fileId]: {
            ...prev[fileId],
            status: 'cancelled'
          }
        }));
      } else {
        // Upload failed
        setUploads(prev => ({
          ...prev,
          [fileId]: {
            ...prev[fileId],
            status: 'failed',
            error: error.response?.data?.detail || error.message
          }
        }));

        setErrors(prev => ({
          ...prev,
          [file.name]: error.response?.data?.detail || error.message
        }));
      }
    } finally {
      // Cleanup
      delete abortControllers.current[fileId];
    }
  };

  const cancelUpload = (fileId) => {
    if (abortControllers.current[fileId]) {
      abortControllers.current[fileId].abort();
    }
  };

  const removeUpload = (fileId) => {
    setUploads(prev => {
      const newUploads = { ...prev };
      delete newUploads[fileId];
      return newUploads;
    });
    
    setUploadProgress(prev => {
      const newProgress = { ...prev };
      delete newProgress[fileId];
      return newProgress;
    });
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getUploadSpeed = (fileId) => {
    const upload = uploads[fileId];
    const progress = uploadProgress[fileId];
    
    if (!upload || !progress || progress.loaded === 0) return '0 B/s';
    
    const timeElapsed = (Date.now() - upload.startTime) / 1000;
    const speed = progress.loaded / timeElapsed;
    return formatFileSize(speed) + '/s';
  };

  const getTimeRemaining = (fileId) => {
    const progress = uploadProgress[fileId];
    const upload = uploads[fileId];
    
    if (!progress || !upload || progress.percentage === 0) return 'Calculating...';
    
    const remainingBytes = progress.total - progress.loaded;
    const timeElapsed = (Date.now() - upload.startTime) / 1000;
    const speed = progress.loaded / timeElapsed;
    
    if (speed === 0) return 'Unknown';
    
    const remainingTime = remainingBytes / speed;
    
    if (remainingTime < 60) return `${Math.round(remainingTime)}s`;
    if (remainingTime < 3600) return `${Math.round(remainingTime / 60)}m`;
    return `${Math.round(remainingTime / 3600)}h`;
  };

  return (
    <div className="file-upload-component">
      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`
          drop-zone border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${isDragReject ? 'border-red-500 bg-red-50' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-4">
          <div className="text-6xl">
            {isDragActive ? '📁' : '📎'}
          </div>
          
          <div>
            <p className="text-lg font-medium text-gray-700">
              {isDragActive ? 'Drop files here...' : 'Drag & drop files here, or click to select'}
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Max file size: 500MB • Max files: {maxFiles}
            </p>
          </div>
        </div>
      </div>

      {/* Upload Progress */}
      {Object.keys(uploads).length > 0 && (
        <div className="mt-6 space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Upload Progress</h3>
          
          {Object.entries(uploads).map(([fileId, upload]) => {
            const progress = uploadProgress[fileId] || { percentage: 0 };
            
            return (
              <div key={fileId} className="border rounded-lg p-4 bg-white shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">
                      {upload.file.type.startsWith('image/') ? '🖼️' :
                       upload.file.type.startsWith('video/') ? '🎥' :
                       upload.file.type === 'application/pdf' ? '📄' :
                       upload.file.type.includes('zip') ? '🗜️' : '📁'}
                    </div>
                    
                    <div>
                      <p className="font-medium text-gray-900">{upload.file.name}</p>
                      <p className="text-sm text-gray-500">{formatFileSize(upload.file.size)}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {upload.status === 'uploading' && (
                      <button
                        onClick={() => cancelUpload(fileId)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Cancel
                      </button>
                    )}
                    
                    {upload.status !== 'uploading' && (
                      <button
                        onClick={() => removeUpload(fileId)}
                        className="text-gray-400 hover:text-gray-600 text-sm"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                </div>

                {/* Progress Bar */}
                {upload.status === 'uploading' && (
                  <div className="space-y-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${progress.percentage}%` }}
                      />
                    </div>
                    
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>{progress.percentage}%</span>
                      <span>{getUploadSpeed(fileId)}</span>
                      <span>ETA: {getTimeRemaining(fileId)}</span>
                    </div>
                  </div>
                )}

                {/* Status Messages */}
                {upload.status === 'completed' && (
                  <div className="flex items-center text-green-600 text-sm">
                    <span className="mr-2">✅</span>
                    Upload completed successfully
                  </div>
                )}

                {upload.status === 'failed' && (
                  <div className="flex items-center text-red-600 text-sm">
                    <span className="mr-2">❌</span>
                    {upload.error || 'Upload failed'}
                  </div>
                )}

                {upload.status === 'cancelled' && (
                  <div className="flex items-center text-gray-600 text-sm">
                    <span className="mr-2">⏹️</span>
                    Upload cancelled
                  </div>
                )}

                {/* Thumbnails for images */}
                {upload.status === 'completed' && upload.result?.thumbnails && (
                  <div className="mt-3">
                    <p className="text-xs text-gray-500 mb-2">Thumbnails:</p>
                    <div className="flex space-x-2">
                      {Object.entries(upload.result.thumbnails).map(([size, url]) => (
                        <img
                          key={size}
                          src={url}
                          alt={`${size} thumbnail`}
                          className="w-16 h-16 object-cover rounded border"
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Error Messages */}
      {Object.keys(errors).length > 0 && (
        <div className="mt-4 space-y-2">
          {Object.entries(errors).map(([filename, error]) => (
            <div key={filename} className="flex items-center text-red-600 text-sm bg-red-50 p-2 rounded">
              <span className="mr-2">⚠️</span>
              <span className="font-medium">{filename}:</span>
              <span className="ml-1">{error}</span>
            </div>
          ))}
        </div>
      )}

      {/* Completed Uploads Summary */}
      {completedUploads.length > 0 && (
        <div className="mt-6 p-4 bg-green-50 rounded-lg">
          <h3 className="text-lg font-medium text-green-800 mb-2">
            ✅ {completedUploads.length} file{completedUploads.length !== 1 ? 's' : ''} uploaded successfully
          </h3>
          <div className="space-y-1">
            {completedUploads.map((upload, index) => (
              <div key={index} className="text-sm text-green-700">
                📎 {upload.original_filename} ({formatFileSize(upload.file_size)})
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUploadComponent;