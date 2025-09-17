import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Upload, Camera, FolderPlus, Image, Trash2, Download, Eye, Tag, Filter, Search, Grid, List, ArrowUp } from 'lucide-react';

const ProjectGalleryManager = () => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [filterCategory, setFilterCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [uploadMode, setUploadMode] = useState(null); // 'file', 'camera', or null
  const [isUploading, setIsUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  // Initialize with sample projects and images
  useEffect(() => {
    const sampleProjects = [
      {
        id: '1',
        name: 'Green Building Complex - Phase 1',
        description: 'Sustainable residential complex with 50 units',
        createdAt: '2024-01-15',
        imageCount: 15,
        status: 'in_progress',
        location: 'Mumbai, Maharashtra',
        images: [
          {
            id: '1',
            filename: 'construction_progress_001.jpg',
            category: 'progress',
            description: 'Foundation work completion',
            uploadDate: '2024-01-20',
            tags: ['foundation', 'construction', 'progress'],
            aiCategory: 'construction_progress',
            confidence: 0.95
          },
          {
            id: '2', 
            filename: 'landscape_design_001.jpg',
            category: 'design',
            description: 'Landscape architecture plan',
            uploadDate: '2024-01-22',
            tags: ['landscape', 'design', 'garden'],
            aiCategory: 'landscape_design',
            confidence: 0.88
          },
          {
            id: '3',
            filename: 'before_site_001.jpg', 
            category: 'before',
            description: 'Site condition before construction',
            uploadDate: '2024-01-18',
            tags: ['before', 'site', 'raw'],
            aiCategory: 'site_before',
            confidence: 0.92
          }
        ]
      },
      {
        id: '2',
        name: 'Eco-Friendly Office Campus',
        description: 'LEED certified office complex with solar panels',
        createdAt: '2024-02-01',
        imageCount: 22,
        status: 'completed',
        location: 'Pune, Maharashtra',
        images: [
          {
            id: '4',
            filename: 'solar_installation_001.jpg',
            category: 'solar',
            description: 'Solar panel installation on rooftop',
            uploadDate: '2024-02-10',
            tags: ['solar', 'renewable', 'rooftop'],
            aiCategory: 'renewable_energy',
            confidence: 0.97
          },
          {
            id: '5',
            filename: 'interior_sustainable_001.jpg',
            category: 'interior',
            description: 'Sustainable interior design features',
            uploadDate: '2024-02-15',
            tags: ['interior', 'sustainable', 'design'],
            aiCategory: 'interior_design',
            confidence: 0.91
          }
        ]
      },
      {
        id: '3',
        name: 'Urban Vertical Garden',
        description: 'Vertical gardening system for urban spaces',
        createdAt: '2024-03-01', 
        imageCount: 8,
        status: 'planning',
        location: 'Bangalore, Karnataka',
        images: [
          {
            id: '6',
            filename: 'vertical_garden_design.jpg',
            category: 'design',
            description: 'Vertical garden concept design',
            uploadDate: '2024-03-05',
            tags: ['vertical', 'garden', 'urban'],
            aiCategory: 'garden_design',
            confidence: 0.89
          }
        ]
      }
    ];
    
    setProjects(sampleProjects);
    setSelectedProject(sampleProjects[0]);
  }, []);

  // AI-powered image classification simulation
  const classifyImage = async (file) => {
    // Simulate AI processing delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const filename = file.name.toLowerCase();
    let category = 'general';
    let confidence = 0.75;
    let tags = [];

    // Simple keyword-based classification (in real app, this would be AI)
    if (filename.includes('before') || filename.includes('site')) {
      category = 'site_before';
      tags = ['before', 'site', 'raw'];
      confidence = 0.92;
    } else if (filename.includes('progress') || filename.includes('construction')) {
      category = 'construction_progress';
      tags = ['progress', 'construction', 'building'];
      confidence = 0.95;
    } else if (filename.includes('after') || filename.includes('complete')) {
      category = 'site_after';
      tags = ['after', 'completed', 'finished'];
      confidence = 0.93;
    } else if (filename.includes('landscape') || filename.includes('garden')) {
      category = 'landscape_design';
      tags = ['landscape', 'garden', 'green'];
      confidence = 0.88;
    } else if (filename.includes('interior') || filename.includes('inside')) {
      category = 'interior_design';
      tags = ['interior', 'design', 'indoor'];
      confidence = 0.91;
    } else if (filename.includes('solar') || filename.includes('panel')) {
      category = 'renewable_energy';
      tags = ['solar', 'renewable', 'energy'];
      confidence = 0.97;
    }

    return { category, confidence, tags };
  };

  // Handle file uploads
  const handleFileUpload = async (files) => {
    if (!selectedProject || !files.length) return;
    
    setIsUploading(true);
    
    try {
      for (const file of files) {
        // Classify image using AI
        const classification = await classifyImage(file);
        
        // Simulate file upload
        const newImage = {
          id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
          filename: file.name,
          category: classification.category === 'general' ? 'misc' : classification.category.split('_')[0],
          description: `Auto-uploaded: ${file.name}`,
          uploadDate: new Date().toISOString().split('T')[0],
          tags: classification.tags,
          aiCategory: classification.category,
          confidence: classification.confidence,
          file: file,
          url: URL.createObjectURL(file)
        };

        // Add to selected project
        setProjects(prev => prev.map(project => 
          project.id === selectedProject.id 
            ? { 
                ...project, 
                images: [...project.images, newImage],
                imageCount: project.imageCount + 1
              }
            : project
        ));

        // Update selected project
        setSelectedProject(prev => ({
          ...prev,
          images: [...prev.images, newImage],
          imageCount: prev.imageCount + 1
        }));
      }
      
      console.log('✅ Images uploaded and classified successfully');
    } catch (error) {
      console.error('❌ Error uploading images:', error);
    } finally {
      setIsUploading(false);
      setUploadMode(null);
    }
  };

  // Handle drag and drop
  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files).filter(file => 
      file.type.startsWith('image/')
    );
    if (files.length > 0) {
      handleFileUpload(files);
    }
  };

  // Filter images based on category and search
  const filteredImages = selectedProject?.images?.filter(image => {
    const matchesCategory = filterCategory === 'all' || image.category === filterCategory;
    const matchesSearch = searchTerm === '' || 
      image.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
      image.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      image.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    return matchesCategory && matchesSearch;
  }) || [];

  // Get unique categories from all images
  const categories = ['all', ...new Set(selectedProject?.images?.map(img => img.category) || [])];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Project Gallery Manager</h2>
          <p className="text-gray-600">AI-powered image organization and management</p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            onClick={() => setUploadMode('file')}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Upload className="h-4 w-4 mr-2" />
            Upload Files
          </Button>
          <Button
            onClick={() => setUploadMode('camera')}
            className="bg-green-600 hover:bg-green-700"
          >
            <Camera className="h-4 w-4 mr-2" />
            Take Photo
          </Button>
          <Button
            onClick={() => {
              const newProject = {
                id: Date.now().toString(),
                name: `New Project ${projects.length + 1}`,
                description: 'New project description',
                createdAt: new Date().toISOString().split('T')[0],
                imageCount: 0,
                status: 'planning',
                location: 'Location TBD',
                images: []
              };
              setProjects([...projects, newProject]);
              setSelectedProject(newProject);
            }}
            variant="outline"
          >
            <FolderPlus className="h-4 w-4 mr-2" />
            New Project
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Project List */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Projects</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {projects.map(project => (
                <div
                  key={project.id}
                  onClick={() => setSelectedProject(project)}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedProject?.id === project.id 
                      ? 'bg-blue-50 border-blue-200' 
                      : 'hover:bg-gray-50 border-gray-200'
                  }`}
                >
                  <h4 className="font-medium text-sm">{project.name}</h4>
                  <p className="text-xs text-gray-600 mt-1">{project.imageCount} images</p>
                  <div className="flex items-center justify-between mt-2">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      project.status === 'completed' ? 'bg-green-100 text-green-700' :
                      project.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {project.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Image Gallery */}
        <div className="lg:col-span-3">
          {selectedProject && (
            <Card>
              <CardHeader>
                <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
                  <div>
                    <CardTitle>{selectedProject.name}</CardTitle>
                    <p className="text-sm text-gray-600 mt-1">{selectedProject.description}</p>
                    <p className="text-xs text-gray-500 mt-1">📍 {selectedProject.location}</p>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {/* Search */}
                    <div className="relative">
                      <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Search images..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    {/* Category Filter */}
                    <select
                      value={filterCategory}
                      onChange={(e) => setFilterCategory(e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      {categories.map(category => (
                        <option key={category} value={category}>
                          {category === 'all' ? 'All Categories' : category.charAt(0).toUpperCase() + category.slice(1)}
                        </option>
                      ))}
                    </select>

                    {/* View Mode Toggle */}
                    <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden">
                      <button
                        onClick={() => setViewMode('grid')}
                        className={`p-2 transition-colors ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-50'}`}
                        title="Grid View"
                      >
                        <Grid className="h-4 w-4" />
                      </button>
                      <div className="w-px bg-gray-300"></div>
                      <button
                        onClick={() => setViewMode('list')}
                        className={`p-2 transition-colors ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-50'}`}
                        title="List View"
                      >
                        <List className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                {/* Upload Area */}
                {uploadMode && (
                  <div 
                    className={`mb-6 p-8 border-2 border-dashed rounded-lg text-center transition-colors ${
                      dragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-300 bg-gray-50'
                    }`}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}  
                    onDrop={handleDrop}
                  >
                    {isUploading ? (
                      <div>
                        <ArrowUp className="h-8 w-8 text-blue-600 mx-auto mb-2 animate-bounce" />
                        <p className="text-blue-600 font-medium">Processing and classifying images...</p>
                        <p className="text-sm text-gray-600">AI is analyzing and organizing your images</p>
                      </div>
                    ) : (
                      <div>
                        {uploadMode === 'file' ? (
                          <>
                            <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                            <p className="text-gray-600 mb-2">Drag and drop images here, or click to browse</p>
                            <Button 
                              onClick={() => fileInputRef.current?.click()}
                              variant="outline"
                            >
                              Select Files
                            </Button>
                            <input
                              ref={fileInputRef}
                              type="file"
                              multiple
                              accept="image/*"
                              className="hidden"
                              onChange={(e) => handleFileUpload(Array.from(e.target.files))}
                            />
                          </>
                        ) : (
                          <>
                            <Camera className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                            <p className="text-gray-600 mb-2">Take a photo using your device camera</p>
                            <Button 
                              onClick={() => cameraInputRef.current?.click()}
                              variant="outline"
                            >
                              Open Camera
                            </Button>
                            <input
                              ref={cameraInputRef}
                              type="file"
                              accept="image/*"
                              capture="environment"
                              className="hidden"
                              onChange={(e) => handleFileUpload(Array.from(e.target.files))}
                            />
                          </>
                        )}
                        <Button 
                          onClick={() => setUploadMode(null)}
                          variant="ghost"
                          className="ml-2"
                        >
                          Cancel
                        </Button>
                      </div>
                    )}
                  </div>
                )}

                {/* Images Display */}
                {filteredImages.length === 0 ? (
                  <div className="text-center py-12">
                    <Image className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-600 mb-2">No Images Found</h3>
                    <p className="text-gray-500 mb-4">
                      {searchTerm || filterCategory !== 'all' 
                        ? 'No images match your current filters.' 
                        : 'Start by uploading some images to this project.'}
                    </p>
                    <Button onClick={() => setUploadMode('file')}>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload Images
                    </Button>
                  </div>
                ) : (
                  <div className={viewMode === 'grid' 
                    ? 'grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4' 
                    : 'space-y-4'
                  }>
                    {filteredImages.map(image => (
                      <div key={image.id} className={`border rounded-lg overflow-hidden hover:shadow-md transition-shadow ${
                        viewMode === 'list' ? 'flex items-center p-4' : 'bg-white'
                      }`}>
                        {viewMode === 'grid' ? (
                          <>
                            <div className="aspect-square bg-gray-100 flex items-center justify-center">
                              {image.url ? (
                                <img 
                                  src={image.url} 
                                  alt={image.filename}
                                  className="w-full h-full object-cover"
                                />
                              ) : (
                                <Image className="h-8 w-8 text-gray-400" />
                              )}
                            </div>
                            <div className="p-3">
                              <h4 className="font-medium text-sm truncate">{image.filename}</h4>
                              <p className="text-xs text-gray-600 mt-1 line-clamp-2">{image.description}</p>
                              <div className="flex items-center justify-between mt-2">
                                <span className={`text-xs px-2 py-1 rounded-full ${
                                  image.category === 'progress' ? 'bg-blue-100 text-blue-700' :
                                  image.category === 'before' ? 'bg-gray-100 text-gray-700' :
                                  image.category === 'design' ? 'bg-purple-100 text-purple-700' :
                                  image.category === 'solar' ? 'bg-yellow-100 text-yellow-700' :
                                  image.category === 'interior' ? 'bg-indigo-100 text-indigo-700' :
                                  'bg-green-100 text-green-700'
                                }`}>
                                  {image.category}
                                </span>
                                <div className="flex items-center space-x-1">
                                  <span className="text-xs text-blue-600 font-medium">
                                    🤖 AI: {Math.round(image.confidence * 100)}%
                                  </span>
                                </div>
                              </div>
                              <div className="mt-2">
                                <span className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded border border-blue-200">
                                  {image.aiCategory.replace('_', ' ')}
                                </span>
                              </div>
                              <div className="flex flex-wrap gap-1 mt-2">
                                {image.tags.slice(0, 2).map(tag => (
                                  <span key={tag} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                                    {tag}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </>
                        ) : (
                          <>
                            <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center mr-4">
                              {image.url ? (
                                <img 
                                  src={image.url} 
                                  alt={image.filename}
                                  className="w-full h-full object-cover rounded-lg"
                                />
                              ) : (
                                <Image className="h-6 w-6 text-gray-400" />
                              )}
                            </div>
                            <div className="flex-1">
                              <h4 className="font-medium">{image.filename}</h4>
                              <p className="text-sm text-gray-600 mt-1">{image.description}</p>
                              <div className="flex items-center space-x-2 mt-2">
                                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                                  {image.category}
                                </span>
                                <span className="text-xs text-gray-500">
                                  AI Confidence: {Math.round(image.confidence * 100)}%
                                </span>
                                <span className="text-xs text-gray-500">
                                  {image.uploadDate}
                                </span>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Button size="sm" variant="ghost">
                                <Eye className="h-4 w-4" />
                              </Button>
                              <Button size="sm" variant="ghost">
                                <Download className="h-4 w-4" />
                              </Button>
                              <Button size="sm" variant="ghost" className="text-red-600 hover:text-red-700">
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProjectGalleryManager;