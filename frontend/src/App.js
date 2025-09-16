import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Badge } from './components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Label } from './components/ui/label';
import { Textarea } from './components/ui/textarea';
import { Progress } from './components/ui/progress';
import { Avatar, AvatarFallback, AvatarImage } from './components/ui/avatar';
import { Separator } from './components/ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Activity, Users, Target, CheckCircle, Package, UserCheck, Brain, Settings, Plus, Upload, Camera, Phone, MessageCircle, Mail, Image, FileText, Edit, MessageSquare, Star, MapPin, Calendar, Clock, DollarSign, TrendingUp, UserPlus, Download, Share, Heart, MoreHorizontal, Filter, Search, Bell, X, Mic, MicOff, Volume2, VolumeX, Play, Pause, RotateCcw, Send, Sparkles, Zap, RefreshCw, AlertCircle, CheckCircle2, Info, Globe, Smartphone, Monitor, Tablet } from 'lucide-react';
import FileUploadComponent from './components/FileUploadComponent';
import LeadActionsPanel from './components/LeadActionsPanel';
import VoiceSTTComponent from './components/VoiceSTTComponent';
import RoleManagementPanel from './components/RoleManagementPanel';
import NotificationSystem from './components/NotificationSystem';
import FaceCheckInComponent from './components/FaceCheckInComponent';
import BulkExcelUploadComponent from './components/BulkExcelUploadComponent';
import DigitalMarketingDashboard from './components/DigitalMarketingDashboard';
import LeadRoutingPanel from './components/LeadRoutingPanel';
import WorkflowAuthoringPanel from './components/WorkflowAuthoringPanel';
import CameraComponent from './components/CameraComponent';
import axios from 'axios';
import { useToast } from './hooks/use-toast';
import { toast } from './hooks/use-toast';
import indianCitiesStates from './data/indianCitiesStates';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const App = () => {
  // Core State Management
  const [currentView, setCurrentView] = useState("dashboard");
  const [loading, setLoading] = useState(false);
  
  // Data States
  const [dashboardStats, setDashboardStats] = useState({
    totalLeads: 0,
    activeLeads: 0,
    conversion_rate: 0,
    totalRevenue: 0,
    pendingTasks: 0
  });
  const [leads, setLeads] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  
  // UI States
  const [selectedLead, setSelectedLead] = useState(null);
  const [showFileUploadModal, setShowFileUploadModal] = useState(false);
  const [showVoiceSTTModal, setShowVoiceSTTModal] = useState(false);
  const [showFaceCheckInModal, setShowFaceCheckInModal] = useState(false);
  const [showLeadActionsPanel, setShowLeadActionsPanel] = useState(false);
  const [showAddLeadModal, setShowAddLeadModal] = useState(false);
  const [showAddTaskModal, setShowAddTaskModal] = useState(false);
  const [showBulkUploadModal, setShowBulkUploadModal] = useState(false);
  
  // Admin States
  const [activeAdminPanel, setActiveAdminPanel] = useState('overview');
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // AI States
  const [aiInsights, setAiInsights] = useState([]);
  const [showAavana2, setShowAavana2] = useState(false);
  const [aavana2Language, setAavana2Language] = useState('en');
  const [aavana2Messages, setAavana2Messages] = useState([]);

  // Form States
  const [newLead, setNewLead] = useState({
    name: '', phone: '', email: '', budget: '', space_size: '', location: '', source: '', category: '', notes: ''
  });
  const [newTask, setNewTask] = useState({
    title: '', description: '', assignee: '', priority: 'Medium', due_date: '', category: 'General'
  });

  // Initialize data on component mount
  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchDashboardStats(),
        fetchLeads(),
        fetchTasks(),
        checkAuthentication()
      ]);
    } catch (error) {
      console.error('App initialization error:', error);
    } finally {
      setLoading(false);
    }
  };

  // API Functions
  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/api/dashboard/stats`);
      setDashboardStats(response.data);
    } catch (error) {
      console.error('Dashboard stats error:', error);
      // Fallback data
      setDashboardStats({
        totalLeads: 26,
        activeLeads: 18,
        conversion_rate: 75,
        totalRevenue: 125000,
        pendingTasks: 12
      });
    }
  };

  const fetchLeads = async () => {
    try {
      const response = await axios.get(`${API}/api/leads`);
      setLeads(response.data);
    } catch (error) {
      console.error('Leads fetch error:', error);
      // Fallback demo data
      setLeads([
        {
          id: '1',
          name: 'Rajesh Kumar',
          phone: '9876543210',
          email: 'rajesh@example.com',
          budget: 5000000,
          space_size: '3 BHK',
          location: 'Mumbai, Maharashtra',
          source: 'Website',
          category: 'Hot',
          status: 'New',
          notes: 'Interested in premium villa projects',
          created_at: new Date().toISOString()
        },
        {
          id: '2',
          name: 'Priya Sharma',
          phone: '9876543211',
          email: 'priya@example.com',
          budget: 3500000,
          space_size: '2 BHK',
          location: 'Pune, Maharashtra',
          source: 'Referral',
          category: 'Warm',
          status: 'Contacted',
          notes: 'Looking for apartment near IT hub',
          created_at: new Date().toISOString()
        },
        {
          id: '3',
          name: 'Amit Patel',
          phone: '9876543212',
          email: 'amit@example.com',
          budget: 7500000,
          space_size: '4 BHK',
          location: 'Bangalore, Karnataka',
          source: 'Social Media',
          category: 'Hot',
          status: 'Qualified',
          notes: 'Corporate executive, ready to invest',
          created_at: new Date().toISOString()
        }
      ]);
    }
  };

  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API}/api/tasks`);
      setTasks(response.data);
    } catch (error) {
      console.error('Tasks fetch error:', error);
      // Fallback demo data
      setTasks([
        {
          id: '1',
          title: 'Follow up with Rajesh Kumar',
          description: 'Schedule site visit for premium villa',
          assignee: 'Sales Team',
          priority: 'High',
          status: 'Pending',
          due_date: '2024-01-15',
          category: 'Sales',
          created_at: new Date().toISOString()
        },
        {
          id: '2',
          title: 'Prepare proposal for Priya Sharma',
          description: 'Create customized apartment proposal',
          assignee: 'Marketing Team',
          priority: 'Medium',
          status: 'In Progress',
          due_date: '2024-01-12',
          category: 'Marketing',
          created_at: new Date().toISOString()
        }
      ]);
    }
  };

  const checkAuthentication = () => {
    const token = localStorage.getItem('auth_token');
    const user = localStorage.getItem('current_user');
    if (token && user) {
      setIsAuthenticated(true);
      setCurrentUser(JSON.parse(user));
    }
  };

  // Tab switching function
  const showContent = (tabName) => {
    console.log(`Switching to tab: ${tabName}`);
    setCurrentView(tabName);
  };

  // Lead Management Functions
  const createLead = async (leadData) => {
    try {
      const response = await axios.post(`${API}/api/leads`, leadData);
      setLeads(prev => [...prev, response.data]);
      setShowAddLeadModal(false);
      setNewLead({ name: '', phone: '', email: '', budget: '', space_size: '', location: '', source: '', category: '', notes: '' });
      toast({ title: "Success", description: "Lead created successfully" });
    } catch (error) {
      console.error('Create lead error:', error);
      toast({ title: "Error", description: "Failed to create lead" });
    }
  };

  const updateLead = async (leadId, updates) => {
    try {
      const response = await axios.put(`${API}/api/leads/${leadId}`, updates);
      setLeads(prev => prev.map(lead => lead.id === leadId ? response.data : lead));
      toast({ title: "Success", description: "Lead updated successfully" });
    } catch (error) {
      console.error('Update lead error:', error);
      toast({ title: "Error", description: "Failed to update lead" });
    }
  };

  // Task Management Functions
  const createTask = async (taskData) => {
    try {
      const response = await axios.post(`${API}/api/tasks`, taskData);
      setTasks(prev => [...prev, response.data]);
      setShowAddTaskModal(false);
      setNewTask({ title: '', description: '', assignee: '', priority: 'Medium', due_date: '', category: 'General' });
      toast({ title: "Success", description: "Task created successfully" });
    } catch (error) {
      console.error('Create task error:', error);
      toast({ title: "Error", description: "Failed to create task" });
    }
  };

  const updateTaskStatus = async (taskId, status) => {
    try {
      const response = await axios.put(`${API}/api/tasks/${taskId}/status`, { status });
      setTasks(prev => prev.map(task => task.id === taskId ? { ...task, status } : task));
      toast({ title: "Success", description: "Task status updated" });
    } catch (error) {
      console.error('Update task status error:', error);
      toast({ title: "Error", description: "Failed to update task status" });
    }
  };

  // Authentication Functions
  const handleLogin = async (credentials) => {
    try {
      const response = await axios.post(`${API}/api/auth/login`, credentials);
      const { access_token, user } = response.data;
      localStorage.setItem('auth_token', access_token);
      localStorage.setItem('current_user', JSON.stringify(user));
      setIsAuthenticated(true);
      setCurrentUser(user);
      toast({ title: "Success", description: "Logged in successfully" });
    } catch (error) {
      console.error('Login error:', error);
      toast({ title: "Error", description: "Login failed" });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('current_user');
    setIsAuthenticated(false);
    setCurrentUser(null);
    toast({ title: "Success", description: "Logged out successfully" });
  };

  // Content Rendering Function
  const renderContent = () => {
    switch(currentView) {
      case 'dashboard':
        return (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="bg-white shadow-lg border-emerald-100 hover:shadow-xl transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Total Leads</CardTitle>
                  <Users className="h-4 w-4 text-emerald-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-900">{dashboardStats.totalLeads}</div>
                  <p className="text-xs text-gray-500 mt-1">Active pipeline</p>
                </CardContent>
              </Card>

              <Card className="bg-white shadow-lg border-emerald-100 hover:shadow-xl transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Active Leads</CardTitle>
                  <Target className="h-4 w-4 text-blue-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-900">{dashboardStats.activeLeads}</div>
                  <p className="text-xs text-gray-500 mt-1">In progress</p>
                </CardContent>
              </Card>

              <Card className="bg-white shadow-lg border-emerald-100 hover:shadow-xl transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Conversion Rate</CardTitle>
                  <TrendingUp className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-900">{dashboardStats.conversion_rate}%</div>
                  <Progress value={dashboardStats.conversion_rate} className="mt-2" />
                </CardContent>
              </Card>

              <Card className="bg-white shadow-lg border-emerald-100 hover:shadow-xl transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Pending Tasks</CardTitle>
                  <Clock className="h-4 w-4 text-orange-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-900">{dashboardStats.pendingTasks}</div>
                  <p className="text-xs text-gray-500 mt-1">Requires attention</p>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-white shadow-lg">
                <CardHeader>
                  <CardTitle className="text-gray-900">Recent Leads</CardTitle>
                  <CardDescription>Latest lead inquiries</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {leads.slice(0, 3).map((lead) => (
                      <div key={lead.id} className="flex items-center space-x-3">
                        <Avatar className="h-8 w-8">
                          <AvatarFallback>{lead.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <p className="text-sm font-medium">{lead.name}</p>
                          <p className="text-xs text-gray-500">{lead.space_size} in {lead.location}</p>
                        </div>
                        <Badge className={`${
                          lead.category === 'Hot' ? 'bg-red-100 text-red-800' :
                          lead.category === 'Warm' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {lead.category}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white shadow-lg">
                <CardHeader>
                  <CardTitle className="text-gray-900">Pipeline Overview</CardTitle>
                  <CardDescription>Leads by stage</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">New Leads</span>
                      <span className="text-sm font-medium">{leads.filter(l => l.status === 'New').length}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Contacted</span>
                      <span className="text-sm font-medium">{leads.filter(l => l.status === 'Contacted').length}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Qualified</span>
                      <span className="text-sm font-medium">{leads.filter(l => l.status === 'Qualified').length}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        );

      case 'leads':
        return (
          <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Lead Management</h2>
                <p className="text-gray-600">Manage your leads and prospects</p>
              </div>
              <div className="flex space-x-2">
                <Button
                  onClick={() => setShowBulkUploadModal(true)}
                  variant="outline"
                  className="flex items-center"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Bulk Upload
                </Button>
                <Button
                  onClick={() => setShowAddLeadModal(true)}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white flex items-center"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Lead
                </Button>
              </div>
            </div>

            {/* Lead Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {leads.map((lead) => (
                <Card key={lead.id} className="bg-white shadow-lg hover:shadow-xl transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">{lead.name}</CardTitle>
                        <CardDescription>{lead.phone} • {lead.email}</CardDescription>
                      </div>
                      <Badge className={`${
                        lead.category === 'Hot' ? 'bg-red-100 text-red-800' :
                        lead.category === 'Warm' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {lead.category}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 mb-4">
                      <p className="text-sm"><strong>Budget:</strong> ₹{(lead.budget / 100000).toFixed(1)}L</p>
                      <p className="text-sm"><strong>Requirement:</strong> {lead.space_size}</p>
                      <p className="text-sm"><strong>Location:</strong> {lead.location}</p>
                      <p className="text-sm"><strong>Source:</strong> {lead.source}</p>
                    </div>
                    
                    {/* Lead Action Buttons */}
                    <div className="grid grid-cols-3 gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs"
                        onClick={() => window.open(`tel:${lead.phone}`)}
                      >
                        <Phone className="h-3 w-3 mr-1" />
                        Call
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs"
                        onClick={() => window.open(`https://wa.me/${lead.phone.replace(/\D/g, '')}`)}
                      >
                        <MessageCircle className="h-3 w-3 mr-1" />
                        WhatsApp
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs"
                        onClick={() => window.open(`mailto:${lead.email}`)}
                      >
                        <Mail className="h-3 w-3 mr-1" />
                        Email
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs"
                        onClick={() => {
                          setSelectedLead(lead);
                          setShowLeadActionsPanel(true);
                        }}
                      >
                        <Camera className="h-3 w-3 mr-1" />
                        Images
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs"
                      >
                        <FileText className="h-3 w-3 mr-1" />
                        Catalogue
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs"
                        onClick={() => {
                          setSelectedLead(lead);
                          // Open edit modal
                        }}
                      >
                        <Edit className="h-3 w-3 mr-1" />
                        Edit
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {leads.length === 0 && (
              <div className="text-center py-12">
                <Users className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No leads yet</h3>
                <p className="text-gray-600 mb-4">Get started by adding your first lead</p>
                <Button onClick={() => setShowAddLeadModal(true)} className="bg-emerald-600 hover:bg-emerald-700">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Lead
                </Button>
              </div>
            )}
          </div>
        );

      case 'tasks':
        return (
          <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Task Management</h2>
                <p className="text-gray-600">Track and manage your tasks</p>
              </div>
              <div className="flex space-x-2">
                <Button
                  onClick={() => setShowVoiceSTTModal(true)}
                  variant="outline"
                  className="flex items-center"
                >
                  <Mic className="h-4 w-4 mr-2" />
                  Voice Task
                </Button>
                <Button
                  onClick={() => setShowAddTaskModal(true)}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white flex items-center"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Task
                </Button>
              </div>
            </div>

            {/* Task Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {tasks.map((task) => (
                <Card key={task.id} className="bg-white shadow-lg hover:shadow-xl transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">{task.title}</CardTitle>
                        <CardDescription>{task.description}</CardDescription>
                      </div>
                      <Badge className={`${
                        task.priority === 'High' ? 'bg-red-100 text-red-800' :
                        task.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {task.priority}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 mb-4">
                      <p className="text-sm"><strong>Assignee:</strong> {task.assignee}</p>
                      <p className="text-sm"><strong>Due Date:</strong> {new Date(task.due_date).toLocaleDateString()}</p>
                      <p className="text-sm"><strong>Category:</strong> {task.category}</p>
                      <p className="text-sm"><strong>Status:</strong> 
                        <Badge className={`ml-2 ${
                          task.status === 'Completed' ? 'bg-green-100 text-green-800' :
                          task.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {task.status}
                        </Badge>
                      </p>
                    </div>
                    
                    {/* Task Action Buttons */}
                    <div className="flex space-x-2">
                      {task.status === 'Pending' && (
                        <Button
                          size="sm"
                          className="bg-blue-600 hover:bg-blue-700 text-white"
                          onClick={() => updateTaskStatus(task.id, 'In Progress')}
                        >
                          Start
                        </Button>
                      )}
                      {task.status === 'In Progress' && (
                        <Button
                          size="sm"
                          className="bg-green-600 hover:bg-green-700 text-white"
                          onClick={() => updateTaskStatus(task.id, 'Completed')}
                        >
                          Complete
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          // Open edit modal
                        }}
                      >
                        <Edit className="h-3 w-3 mr-1" />
                        Edit
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {tasks.length === 0 && (
              <div className="text-center py-12">
                <CheckCircle className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks yet</h3>
                <p className="text-gray-600 mb-4">Get started by adding your first task</p>
                <Button onClick={() => setShowAddTaskModal(true)} className="bg-emerald-600 hover:bg-emerald-700">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Task
                </Button>
              </div>
            )}
          </div>
        );

      case 'erp':
        return (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Business Management & Operations</h2>
                <p className="text-gray-600">Manage projects, files, and operations</p>
              </div>
            </div>

            {/* ERP Features */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* File Upload */}
              <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-blue-700">
                    <Upload className="h-5 w-5" />
                    File Upload
                  </CardTitle>
                  <CardDescription>Upload and manage project files</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button 
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                    onClick={() => setShowFileUploadModal(true)}
                  >
                    Upload Files
                  </Button>
                </CardContent>
              </Card>

              {/* Project Gallery */}
              <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-green-700">
                    <Image className="h-5 w-5" />
                    Project Gallery
                  </CardTitle>
                  <CardDescription>Manage project images and media</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" className="w-full border-green-200 text-green-700 hover:bg-green-50">
                    View Gallery
                  </Button>
                </CardContent>
              </Card>

              {/* Product Catalog */}
              <Card className="bg-gradient-to-br from-purple-50 to-violet-50 border-purple-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-purple-700">
                    <Package className="h-5 w-5" />
                    Product Catalog
                  </CardTitle>
                  <CardDescription>Manage product listings and catalogs</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" className="w-full border-purple-200 text-purple-700 hover:bg-purple-50">
                    Manage Catalog
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* File Upload Component Integration */}
            <FileUploadComponent />
          </div>
        );

      case 'pipeline':
        return (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Sales Pipeline</h2>
                <p className="text-gray-600">Track your sales pipeline and conversion funnel</p>
              </div>
            </div>

            {/* Pipeline Stages */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {['New', 'Contacted', 'Qualified', 'Closed'].map((stage, index) => {
                const stageLeads = leads.filter(lead => 
                  stage === 'New' ? lead.status === 'New' :
                  stage === 'Contacted' ? lead.status === 'Contacted' :
                  stage === 'Qualified' ? lead.status === 'Qualified' :
                  lead.status === 'Closed'
                );
                
                return (
                  <Card key={stage} className="bg-white shadow-lg">
                    <CardHeader>
                      <CardTitle className="text-center">{stage}</CardTitle>
                      <CardDescription className="text-center">{stageLeads.length} leads</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {stageLeads.slice(0, 3).map((lead) => (
                          <div key={lead.id} className="p-3 bg-gray-50 rounded-lg">
                            <p className="font-medium text-sm">{lead.name}</p>
                            <p className="text-xs text-gray-600">₹{(lead.budget / 100000).toFixed(1)}L</p>
                          </div>
                        ))}
                        {stageLeads.length > 3 && (
                          <p className="text-xs text-center text-gray-500">
                            +{stageLeads.length - 3} more
                          </p>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Pipeline Analytics */}
            <Card className="bg-white shadow-lg">
              <CardHeader>
                <CardTitle>Pipeline Analytics</CardTitle>
                <CardDescription>Conversion rates and performance metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-emerald-600">{dashboardStats.conversion_rate}%</p>
                    <p className="text-sm text-gray-600">Conversion Rate</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">₹{(dashboardStats.totalRevenue / 100000).toFixed(1)}L</p>
                    <p className="text-sm text-gray-600">Total Revenue</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">{leads.length}</p>
                    <p className="text-sm text-gray-600">Total Leads</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        );

      case 'hrms':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Employee Management</h2>
                <p className="text-gray-600">Manage employee attendance and records</p>
              </div>
            </div>

            {/* HRMS Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-blue-700">
                    <UserCheck className="h-5 w-5" />
                    Face Check-in
                  </CardTitle>
                  <CardDescription>Face recognition + GPS tracking</CardDescription>
                </CardHeader>
                <CardContent>
                  <FaceCheckInComponent />
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-green-700">
                    <Calendar className="h-5 w-5" />
                    Leave Management
                  </CardTitle>
                  <CardDescription>Apply and track leave requests</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button className="w-full bg-green-600 hover:bg-green-700 text-white">
                    Apply Leave
                  </Button>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-purple-50 to-violet-50 border-purple-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-purple-700">
                    <Clock className="h-5 w-5" />
                    Attendance
                  </CardTitle>
                  <CardDescription>View attendance history</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" className="w-full border-purple-200 text-purple-700 hover:bg-purple-50">
                    View History
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Employee List */}
            <Card className="bg-white shadow-lg">
              <CardHeader>
                <CardTitle>Employee Directory</CardTitle>
                <CardDescription>Manage employee information and access</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <UserCheck className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Employee Directory</h3>
                  <p className="text-gray-600">Employee management features available with admin access</p>
                </div>
              </CardContent>
            </Card>
          </div>
        );

      case 'ai':
        return (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">AI Assistant</h2>
                <p className="text-gray-600">AI-powered insights and automation</p>
              </div>
              <div className="flex space-x-2">
                <Button
                  onClick={() => setShowAavana2(!showAavana2)}
                  className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white"
                >
                  <Brain className="h-4 w-4 mr-2" />
                  {showAavana2 ? 'Close AI Chat' : 'Open AI Chat'}
                </Button>
              </div>
            </div>

            {/* AI Feature Tabs */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <Button
                variant={activeAdminPanel === 'insights' ? 'default' : 'outline'}
                onClick={() => setActiveAdminPanel('insights')}
                className="flex items-center justify-center"
              >
                <Brain className="h-4 w-4 mr-2" />
                AI Insights
              </Button>
              <Button
                variant={activeAdminPanel === 'workflows' ? 'default' : 'outline'}
                onClick={() => setActiveAdminPanel('workflows')}
                className="flex items-center justify-center"
              >
                <Zap className="h-4 w-4 mr-2" />
                Workflows
              </Button>
              <Button
                variant={activeAdminPanel === 'routing' ? 'default' : 'outline'}
                onClick={() => setActiveAdminPanel('routing')}
                className="flex items-center justify-center"
              >
                <MapPin className="h-4 w-4 mr-2" />
                Lead Routing
              </Button>
              <Button
                variant={activeAdminPanel === 'marketing' ? 'default' : 'outline'}
                onClick={() => setActiveAdminPanel('marketing')}
                className="flex items-center justify-center"
              >
                <Target className="h-4 w-4 mr-2" />
                Digital Marketing
              </Button>
            </div>

            {/* AI Content */}
            {activeAdminPanel === 'insights' && (
              <div className="space-y-6">
                {/* AI Features */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <Card className="bg-gradient-to-br from-purple-50 to-violet-50 border-purple-200">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-purple-700">
                        <Brain className="h-5 w-5" />
                        Lead Scoring
                      </CardTitle>
                      <CardDescription>AI-powered lead qualification</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <Button variant="outline" className="w-full border-purple-200 text-purple-700 hover:bg-purple-50">
                        Analyze Leads
                      </Button>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-blue-700">
                        <TrendingUp className="h-5 w-5" />
                        Sales Insights
                      </CardTitle>
                      <CardDescription>Predictive analytics and trends</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <Button variant="outline" className="w-full border-blue-200 text-blue-700 hover:bg-blue-50">
                        View Insights
                      </Button>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-green-700">
                        <MessageSquare className="h-5 w-5" />
                        Auto Responses
                      </CardTitle>
                      <CardDescription>Automated customer communication</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <Button variant="outline" className="w-full border-green-200 text-green-700 hover:bg-green-50">
                        Configure
                      </Button>
                    </CardContent>
                  </Card>
                </div>

                {/* AI Insights Display */}
                <Card className="bg-white shadow-lg">
                  <CardHeader>
                    <CardTitle>AI Insights Dashboard</CardTitle>
                    <CardDescription>Real-time AI analysis and recommendations</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="p-4 bg-purple-50 rounded-lg">
                        <h4 className="font-medium text-purple-900 mb-2">Lead Quality Score</h4>
                        <p className="text-2xl font-bold text-purple-700">8.7/10</p>
                        <p className="text-sm text-purple-600">Above average quality leads this month</p>
                      </div>
                      <div className="p-4 bg-blue-50 rounded-lg">
                        <h4 className="font-medium text-blue-900 mb-2">Conversion Prediction</h4>
                        <p className="text-2xl font-bold text-blue-700">74%</p>
                        <p className="text-sm text-blue-600">Expected conversion rate for current pipeline</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {activeAdminPanel === 'workflows' && <WorkflowAuthoringPanel />}
            {activeAdminPanel === 'routing' && <LeadRoutingPanel />}
            {activeAdminPanel === 'marketing' && <DigitalMarketingDashboard />}
          </div>
        );

      case 'admin':
        return (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Super Admin Panel</h2>
                <p className="text-gray-600">System administration and settings</p>
              </div>
            </div>

            {/* Admin Navigation */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <Button
                variant={activeAdminPanel === 'overview' ? 'default' : 'outline'}
                onClick={() => setActiveAdminPanel('overview')}
                className="flex items-center justify-center"
              >
                <Settings className="h-4 w-4 mr-2" />
                Overview
              </Button>
              <Button
                variant={activeAdminPanel === 'users' ? 'default' : 'outline'}
                onClick={() => setActiveAdminPanel('users')}
                className="flex items-center justify-center"
              >
                <Users className="h-4 w-4 mr-2" />
                User Management
              </Button>
              <Button
                variant={activeAdminPanel === 'roles' ? 'default' : 'outline'}
                onClick={() => setActiveAdminPanel('roles')}
                className="flex items-center justify-center"
              >
                <UserCheck className="h-4 w-4 mr-2" />
                Role Management
              </Button>
              <Button
                variant={activeAdminPanel === 'notifications' ? 'default' : 'outline'}
                onClick={() => setActiveAdminPanel('notifications')}
                className="flex items-center justify-center"
              >
                <Bell className="h-4 w-4 mr-2" />
                Notifications
              </Button>
            </div>

            {/* Admin Content */}
            {activeAdminPanel === 'overview' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <Card className="bg-white shadow-lg">
                  <CardHeader>
                    <CardTitle>System Status</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Database</span>
                        <Badge className="bg-green-100 text-green-800">Online</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span>API</span>
                        <Badge className="bg-green-100 text-green-800">Healthy</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span>Storage</span>
                        <Badge className="bg-green-100 text-green-800">Available</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-white shadow-lg">
                  <CardHeader>
                    <CardTitle>Quick Stats</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <p><strong>Total Users:</strong> {users.length}</p>
                      <p><strong>Active Sessions:</strong> 1</p>
                      <p><strong>Storage Used:</strong> 2.3 GB</p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-white shadow-lg">
                  <CardHeader>
                    <CardTitle>Recent Activity</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm">
                      <p>• User admin logged in</p>
                      <p>• New lead created</p>
                      <p>• Task completed</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {activeAdminPanel === 'users' && (
              <Card className="bg-white shadow-lg">
                <CardHeader>
                  <CardTitle>User Management</CardTitle>
                  <CardDescription>Manage system users and permissions</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8">
                    <Users className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">User Management</h3>
                    <p className="text-gray-600 mb-4">Advanced user management features</p>
                    <Button className="bg-emerald-600 hover:bg-emerald-700">
                      <Plus className="h-4 w-4 mr-2" />
                      Add User
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {activeAdminPanel === 'roles' && (
              <RoleManagementPanel />
            )}

            {activeAdminPanel === 'notifications' && (
              <Card className="bg-white shadow-lg">
                <CardHeader>
                  <CardTitle>Notification System</CardTitle>
                  <CardDescription>Configure and test notification channels</CardDescription>
                </CardHeader>
                <CardContent>
                  <NotificationSystem showTestingPanel={true} />
                </CardContent>
              </Card>
            )}
          </div>
        );

      default:
        return (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Content Not Found</h2>
            <p className="text-gray-600">The requested content could not be found.</p>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-100">
      {/* Header */}
      <header className="bg-white shadow-lg border-b-2 border-emerald-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-gradient-to-br from-emerald-600 to-green-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">A</span>
                </div>
                <h1 className="ml-3 text-2xl font-bold text-gray-900">Aavana Greens CRM</h1>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="flex items-center"
                  onClick={() => setShowFileUploadModal(true)}
                >
                  📎 Upload
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="flex items-center"
                  onClick={() => setShowVoiceSTTModal(true)}
                >
                  🎤 Voice
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="flex items-center"
                  onClick={() => setShowFaceCheckInModal(true)}
                >
                  📷 Check-In
                </Button>
                <div className="relative">
                  <NotificationSystem showTestingPanel={false} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Tab Navigation */}
          <div className="grid w-full grid-cols-8 bg-white shadow-sm border border-emerald-100 text-xs rounded-lg overflow-hidden">
            <button 
              onClick={() => showContent("dashboard")}
              className={`p-3 flex items-center justify-center transition-colors ${currentView === "dashboard" ? "bg-emerald-100 text-emerald-700 font-bold" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <Activity className="h-3 w-3 mr-1" />
              Dashboard
            </button>
            <button 
              onClick={() => showContent("leads")}
              className={`p-3 flex items-center justify-center transition-colors ${currentView === "leads" ? "bg-emerald-100 text-emerald-700 font-bold" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <Users className="h-3 w-3 mr-1" />
              Leads
            </button>
            <button 
              onClick={() => showContent("pipeline")}
              className={`p-3 flex items-center justify-center transition-colors ${currentView === "pipeline" ? "bg-emerald-100 text-emerald-700 font-bold" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <Target className="h-3 w-3 mr-1" />
              Pipeline
            </button>
            <button 
              onClick={() => showContent("tasks")}
              className={`p-3 flex items-center justify-center transition-colors ${currentView === "tasks" ? "bg-emerald-100 text-emerald-700 font-bold" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <CheckCircle className="h-3 w-3 mr-1" />
              Tasks
            </button>
            <button 
              onClick={() => showContent("erp")}
              className={`p-3 flex items-center justify-center transition-colors ${currentView === "erp" ? "bg-emerald-100 text-emerald-700 font-bold" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <Package className="h-3 w-3 mr-1" />
              ERP
            </button>
            <button 
              onClick={() => showContent("hrms")}
              className={`p-3 flex items-center justify-center transition-colors ${currentView === "hrms" ? "bg-emerald-100 text-emerald-700 font-bold" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <UserCheck className="h-3 w-3 mr-1" />
              HRMS
            </button>
            <button 
              onClick={() => showContent("ai")}
              className={`p-3 flex items-center justify-center transition-colors ${currentView === "ai" ? "bg-emerald-100 text-emerald-700 font-bold" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <Brain className="h-3 w-3 mr-1" />
              AI
            </button>
            <button 
              onClick={() => showContent("admin")}
              className={`p-3 flex items-center justify-center transition-colors ${currentView === "admin" ? "bg-emerald-100 text-emerald-700 font-bold" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <Settings className="h-3 w-3 mr-1" />
              Admin
            </button>
          </div>

          {/* Content Area */}
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
              <span className="ml-2 text-gray-600">Loading...</span>
            </div>
          ) : (
            renderContent()
          )}
        </div>
      </main>

      {/* Modals */}
      {showFileUploadModal && (
        <Dialog open={showFileUploadModal} onOpenChange={setShowFileUploadModal}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>File Upload</DialogTitle>
              <DialogDescription>Upload files to the system</DialogDescription>
            </DialogHeader>
            <FileUploadComponent />
          </DialogContent>
        </Dialog>
      )}

      {showVoiceSTTModal && (
        <Dialog open={showVoiceSTTModal} onOpenChange={setShowVoiceSTTModal}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Voice Task Creator</DialogTitle>
              <DialogDescription>Create tasks using voice commands</DialogDescription>
            </DialogHeader>
            <VoiceSTTComponent onTaskCreated={(task) => {
              createTask(task);
              setShowVoiceSTTModal(false);
            }} />
          </DialogContent>
        </Dialog>
      )}

      {showFaceCheckInModal && (
        <Dialog open={showFaceCheckInModal} onOpenChange={setShowFaceCheckInModal}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Face Check-In</DialogTitle>
              <DialogDescription>Employee attendance via face recognition</DialogDescription>
            </DialogHeader>
            <FaceCheckInComponent />
          </DialogContent>
        </Dialog>
      )}

      {showLeadActionsPanel && selectedLead && (
        <Dialog open={showLeadActionsPanel} onOpenChange={setShowLeadActionsPanel}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Lead Actions - {selectedLead.name}</DialogTitle>
              <DialogDescription>Perform actions for this lead</DialogDescription>
            </DialogHeader>
            <LeadActionsPanel 
              lead={selectedLead} 
              onClose={() => setShowLeadActionsPanel(false)}
            />
          </DialogContent>
        </Dialog>
      )}

      {showAddLeadModal && (
        <Dialog open={showAddLeadModal} onOpenChange={setShowAddLeadModal}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Add New Lead</DialogTitle>
              <DialogDescription>Create a new lead in the system</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Name</Label>
                  <Input 
                    value={newLead.name}
                    onChange={(e) => setNewLead({...newLead, name: e.target.value})}
                    placeholder="Full name"
                  />
                </div>
                <div>
                  <Label>Phone</Label>
                  <Input 
                    value={newLead.phone}
                    onChange={(e) => setNewLead({...newLead, phone: e.target.value})}
                    placeholder="Phone number"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Email</Label>
                  <Input 
                    value={newLead.email}
                    onChange={(e) => setNewLead({...newLead, email: e.target.value})}
                    placeholder="Email address"
                  />
                </div>
                <div>
                  <Label>Budget</Label>
                  <Input 
                    type="number"
                    value={newLead.budget}
                    onChange={(e) => setNewLead({...newLead, budget: e.target.value})}
                    placeholder="Budget in ₹"
                  />
                </div>
              </div>
              <div>
                <Label>Requirements</Label>
                <Input 
                  value={newLead.space_size}
                  onChange={(e) => setNewLead({...newLead, space_size: e.target.value})}
                  placeholder="e.g., 3 BHK, 2000 sq ft"
                />
              </div>
              <div>
                <Label>Location</Label>
                <Input 
                  value={newLead.location}
                  onChange={(e) => setNewLead({...newLead, location: e.target.value})}
                  placeholder="Preferred location"
                />
              </div>
              <div>
                <Label>Notes</Label>
                <Textarea 
                  value={newLead.notes}
                  onChange={(e) => setNewLead({...newLead, notes: e.target.value})}
                  placeholder="Additional notes"
                />
              </div>
              <div className="flex space-x-2">
                <Button 
                  onClick={() => createLead(newLead)}
                  className="bg-emerald-600 hover:bg-emerald-700"
                >
                  Create Lead
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => setShowAddLeadModal(false)}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {showAddTaskModal && (
        <Dialog open={showAddTaskModal} onOpenChange={setShowAddTaskModal}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Add New Task</DialogTitle>
              <DialogDescription>Create a new task in the system</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Title</Label>
                <Input 
                  value={newTask.title}
                  onChange={(e) => setNewTask({...newTask, title: e.target.value})}
                  placeholder="Task title"
                />
              </div>
              <div>
                <Label>Description</Label>
                <Textarea 
                  value={newTask.description}
                  onChange={(e) => setNewTask({...newTask, description: e.target.value})}
                  placeholder="Task description"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Assignee</Label>
                  <Input 
                    value={newTask.assignee}
                    onChange={(e) => setNewTask({...newTask, assignee: e.target.value})}
                    placeholder="Assign to"
                  />
                </div>
                <div>
                  <Label>Priority</Label>
                  <Select value={newTask.priority} onValueChange={(value) => setNewTask({...newTask, priority: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Low">Low</SelectItem>
                      <SelectItem value="Medium">Medium</SelectItem>
                      <SelectItem value="High">High</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label>Due Date</Label>
                <Input 
                  type="date"
                  value={newTask.due_date}
                  onChange={(e) => setNewTask({...newTask, due_date: e.target.value})}
                />
              </div>
              <div className="flex space-x-2">
                <Button 
                  onClick={() => createTask(newTask)}
                  className="bg-emerald-600 hover:bg-emerald-700"
                >
                  Create Task
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => setShowAddTaskModal(false)}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {showBulkUploadModal && (
        <Dialog open={showBulkUploadModal} onOpenChange={setShowBulkUploadModal}>
          <DialogContent className="max-w-4xl">
            <DialogHeader>
              <DialogTitle>Bulk Lead Upload</DialogTitle>
              <DialogDescription>Upload multiple leads via Excel/CSV</DialogDescription>
            </DialogHeader>
            <BulkExcelUploadComponent onComplete={() => {
              setShowBulkUploadModal(false);
              fetchLeads(); // Refresh leads after bulk upload
            }} />
          </DialogContent>
        </Dialog>
      )}

      {/* Aavana 2.0 Floating Chat */}
      {showAavana2 && (
        <div className="fixed bottom-20 right-20 w-96 h-[500px] bg-white border-2 border-emerald-200 rounded-lg shadow-2xl z-[60] flex flex-col">
          <div className="bg-gradient-to-r from-emerald-600 to-green-600 text-white p-4 rounded-t-lg">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-bold text-lg flex items-center">
                  <Brain className="h-5 w-5 mr-2" />
                  Aavana 2.0
                </h3>
                <p className="text-xs opacity-90">Multilingual AI Assistant</p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/10"
                onClick={() => setShowAavana2(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div className="flex-1 p-4 overflow-y-auto">
            <div className="text-center text-gray-600">
              <Brain className="h-12 w-12 mx-auto mb-3 text-emerald-600" />
              <p>AI Assistant Ready</p>
              <p className="text-sm">Ask me anything about your CRM!</p>
            </div>
          </div>
          <div className="p-4 border-t">
            <div className="flex space-x-2">
              <Input placeholder="Type your message..." className="flex-1" />
              <Button className="bg-emerald-600 hover:bg-emerald-700">
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;