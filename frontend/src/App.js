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
// Import new tab system
import { TabProvider } from './contexts/TabContext';
import TabNavigation from './components/TabNavigation'; 
import TabContent from './components/TabContent';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const App = () => {
  // Core State Management
  const [loading, setLoading] = useState(true);
  
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
      setCurrentUser(JSON.parse(user));
    }
  };

  // Legacy function - now handled by TabContext
  const showContent = (tabName) => {
    console.log(`🔄 LEGACY TAB SWITCH: ${tabName} - Now handled by TabContext`);
  };

  // Action completion handler for lead actions
  const handleActionComplete = (result) => {
    console.log('Action completed:', result);
    setShowLeadActionsPanel(false);
    // Refresh data if needed
    if (result.success) {
      fetchLeads();
    }
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
    setCurrentUser(null);
    toast({ title: "Success", description: "Logged out successfully" });
  };

  // Legacy content rendering - replaced by TabContent component
  const renderContent = () => {
    console.log(`🎯 LEGACY RENDER - Now handled by TabContent component`);
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Content now handled by TabContent component</p>
      </div>
    );
  };

  return (
    <TabProvider>
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
                  <button
                    onClick={() => setShowFileUploadModal(true)}
                    className="bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 flex items-center"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Upload
                  </button>
                  <button
                    onClick={() => setShowVoiceModal(true)}
                    className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 flex items-center"
                  >
                    <Mic className="h-4 w-4 mr-2" />
                    Voice
                  </button>
                  <button
                    onClick={() => setShowCheckInModal(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center"
                  >
                    <Camera className="h-4 w-4 mr-2" />
                    Check-In
                  </button>
                  <button className="relative bg-gray-100 text-gray-700 p-2 rounded-lg hover:bg-gray-200">
                    <Bell className="h-5 w-5" />
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      3
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="space-y-6">
            {/* New Tab Navigation */}
            <TabNavigation />

            {/* Content Area - New Tab System */}
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
                <span className="ml-2 text-gray-600">Loading...</span>
              </div>
            ) : (
              <TabContent
                dashboardStats={dashboardStats}
                leads={leads}
                tasks={tasks}
                showLeadActionsPanel={showLeadActionsPanel}
                selectedLead={selectedLead}
                setShowLeadActionsPanel={setShowLeadActionsPanel}
                onActionComplete={handleActionComplete}
              />
            )}
          </div>
        </main>

        {/* Modals and other components would go here */}
      </div>
    </TabProvider>
  );
};

export default App;
