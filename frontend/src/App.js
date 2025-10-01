/* eslint-disable */
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
import { Activity, Users, Target, CheckCircle, Package, UserCheck, Brain, Settings, Plus, Upload, Camera, Phone, MessageCircle, Mail, Image, FileText, Edit, MessageSquare, Star, MapPin, Calendar, Clock, DollarSign, TrendingUp, UserPlus, Download, Share, Heart, MoreHorizontal, Filter, Search, Bell, X, Mic, MicOff, Volume2, VolumeX, Play, Pause, RotateCcw, Send, Sparkles, Zap, RefreshCw, AlertCircle, CheckCircle2, Info, Globe, Smartphone, Monitor, Tablet, BookOpen } from 'lucide-react';
import './styles/responsive.css';
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
import EnhancedFileUploadHeader from './components/EnhancedFileUploadHeader';
import Aavana2Assistant from './components/Aavana2Assistant';
import GoalsManagementSystem from './components/GoalsManagementSystem';
import ComprehensiveDigitalMarketingManager from './components/ComprehensiveDigitalMarketingManager';
import notificationManager from './utils/notificationManager';
import FloatingChatbot from './components/FloatingChatbot';
import axios from 'axios';
import { useToast } from './hooks/use-toast';
import { toast } from './hooks/use-toast';
import indianCitiesStates from './data/indianCitiesStates';
import { TabProvider } from './contexts/TabContext';
import TabNavigation from './components/TabNavigation'; 
import TabContent from './components/TabContent';
import OpsSmoke from './components/OpsSmoke';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const App = () => {
  if (typeof window !== 'undefined' && window.location && window.location.pathname === '/ops/smoke') {
    return <OpsSmoke />
  }

  const [loading, setLoading] = useState(true);
  const [dashboardStats, setDashboardStats] = useState({ totalLeads: 0, activeLeads: 0, conversion_rate: 0, totalRevenue: 0, pendingTasks: 0 });
  const [leads, setLeads] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [leadActionType, setLeadActionType] = useState(null);
  const [showFileUploadModal, setShowFileUploadModal] = useState(false);
  const [showVoiceSTTModal, setShowVoiceSTTModal] = useState(false);
  const [showLeadActionsPanel, setShowLeadActionsPanel] = useState(false);
  const [showAddLeadModal, setShowAddLeadModal] = useState(false);
  const [showAddTaskModal, setShowAddTaskModal] = useState(false);
  const [showBulkUploadModal, setShowBulkUploadModal] = useState(false);
  const [activeAdminPanel, setActiveAdminPanel] = useState('overview');
  const [currentUser, setCurrentUser] = useState(null);
  const [aiInsights, setAiInsights] = useState([]);
  const [showGoalsModal, setShowGoalsModal] = useState(false);
  const [showMarketingModal, setShowMarketingModal] = useState(false);
  const [showNotificationPanel, setShowNotificationPanel] = useState(false);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => { initializeApp(); }, []);

  const initializeApp = async () => {
    setLoading(true);
    try {
      await Promise.all([ fetchDashboardStats(), fetchLeads(), fetchTasks(), checkAuthentication() ]);
    } catch (error) {
      console.error('App initialization error:', error);
    } finally { setLoading(false); }
  };

  // API Functions
  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/api/dashboard/stats`);
      setDashboardStats(response.data);
    } catch (error) {
      console.error('Dashboard stats error:', error);
    }
  };

  const fetchLeads = async () => {
    try {
      const response = await axios.get(`${API}/api/leads`);
      const data = response.data;
      if (Array.isArray(data.items)) setLeads(data.items); else if (Array.isArray(data)) setLeads(data); else setLeads([]);
    } catch (error) {
      console.error('Leads fetch error:', error);
      setLeads([]);
    }
  };

  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API}/api/tasks`);
      const data = response.data;
      if (Array.isArray(data.items)) setTasks(data.items); else if (Array.isArray(data)) setTasks(data); else setTasks([]);
    } catch (error) {
      console.error('Tasks fetch error:', error);
      setTasks([]);
    }
  };

  const markNotificationAsRead = (notificationId) => {
    setNotifications(prev => prev.map(n => n.id === notificationId ? { ...n, read: true } : n));
  };
  const markAllNotificationsAsRead = () => { setNotifications(prev => prev.map(n => ({ ...n, read: true }))); };
  const getUnreadNotificationCount = () => notifications.filter(n => !n.read).length;
  const addNotification = (title, message, type = 'info') => {
    const newNotification = { id: Date.now().toString(), title, message, type, timestamp: new Date().toISOString(), read: false };
    setNotifications(prev => [newNotification, ...prev]);
  };

  const checkAuthentication = () => {
    const token = localStorage.getItem('auth_token');
    const user = localStorage.getItem('current_user');
    if (token && user) setCurrentUser(JSON.parse(user));
  };

  const handleActionComplete = (result) => {
    setShowLeadActionsPanel(false);
    if (result.success) fetchLeads();
  };

  // Lead Management Functions
  const createLead = async (leadData) => {
    try {
      const response = await axios.post(`${API}/api/leads`, leadData);
      const lead = response.data?.lead || response.data;
      setLeads(prev => [...prev, lead]);
      setShowAddLeadModal(false);
      setNewLead({ name: '', phone: '', email: '', budget: '', space_size: '', location: '', source: '', category: '', notes: '' });
      toast({ title: 'Success', description: 'Lead created successfully' });
    } catch (error) {
      console.error('Create lead error:', error);
      toast({ title: 'Error', description: 'Failed to create lead' });
    }
  };

  const updateLead = async (leadId, updates) => {
    try {
      const response = await axios.put(`${API}/api/leads/${leadId}`, updates);
      const lead = response.data?.lead || response.data;
      setLeads(prev => prev.map(l => l.id === leadId ? lead : l));
      toast({ title: 'Success', description: 'Lead updated successfully' });
    } catch (error) {
      console.error('Update lead error:', error);
      toast({ title: 'Error', description: 'Failed to update lead' });
    }
  };

  // Task Management Functions
  const createTask = async (taskData) => {
    try {
      const response = await axios.post(`${API}/api/tasks`, taskData);
      const task = response.data?.task || response.data;
      setTasks(prev => [...prev, task]);
      setShowAddTaskModal(false);
      setNewTask({ title: '', description: '', assignee: '', priority: 'Medium', due_date: '', category: 'General' });
      toast({ title: 'Success', description: 'Task created successfully' });
    } catch (error) {
      console.error('Create task error:', error);
      toast({ title: 'Error', description: 'Failed to create task' });
    }
  };

  const updateTaskStatus = async (taskId, status) => {
    try {
      const response = await axios.put(`${API}/api/tasks/${taskId}/status`, { status });
      const task = response.data?.task || response.data;
      setTasks(prev => prev.map(t => t.id === taskId ? task : t));
      toast({ title: 'Success', description: 'Task status updated' });
    } catch (error) {
      console.error('Update task status error:', error);
      toast({ title: 'Error', description: 'Failed to update task status' });
    }
  };

  return (
    <TabProvider>
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-100">
        {/* Early Smoke route is handled above */}
        <header className="bg-white shadow-lg border-b-2 border-emerald-200">
          <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8">
            <div className="flex justify-between items-center py-2 sm:py-4">
              <div className="flex items-center space-x-2 sm:space-x-4">
                <div className="flex items-center">
                  <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-emerald-600 to-green-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-sm sm:text-lg">A</span>
                  </div>
                  <h1 className="ml-2 sm:ml-3 text-lg sm:text-2xl font-bold text-gray-900 hidden xs:block">Aavana Greens CRM</h1>
                  <h1 className="ml-2 text-sm font-bold text-gray-900 xs:hidden">Aavana</h1>
                </div>
              </div>

              <div className="flex items-center space-x-1 sm:space-x-4">
                <div className="flex items-center space-x-1 sm:space-x-2">
                  <button onClick={() => setShowGoalsModal(true)} className="bg-green-600 text-white px-2 py-1 sm:px-4 sm:py-2 rounded-lg hover:bg-green-700 flex items-center text-xs sm:text-sm">
                    <Target className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                    <span className="hidden sm:inline">Goals</span>
                  </button>
                  <button onClick={() => setShowMarketingModal(true)} className="bg-orange-600 text-white px-2 py-1 sm:px-4 sm:py-2 rounded-lg hover:bg-orange-700 flex items-center text-xs sm:text-sm">
                    <TrendingUp className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                    <span className="hidden sm:inline">Marketing</span>
                  </button>
                  <button onClick={() => setShowNotificationPanel(!showNotificationPanel)} className="relative bg-gray-100 text-gray-700 p-1 sm:p-2 rounded-lg hover:bg-gray-200">
                    <Bell className="h-4 w-4 sm:h-5 sm:w-5" />
                    {getUnreadNotificationCount() > 0 && (
                      <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 sm:h-5 sm:w-5 flex items-center justify-center text-[10px] sm:text-xs">{getUnreadNotificationCount()}</span>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="space-y-6">
            <TabNavigation />
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
                leadActionType={leadActionType}
                setShowLeadActionsPanel={setShowLeadActionsPanel}
                setSelectedLead={setSelectedLead}
                setLeadActionType={setLeadActionType}
                onActionComplete={handleActionComplete}
              />
            )}
          </div>
        </main>

        <FloatingChatbot />
        <GoalsManagementSystem isOpen={showGoalsModal} onClose={() => setShowGoalsModal(false)} />
        <ComprehensiveDigitalMarketingManager isOpen={showMarketingModal} onClose={() => setShowMarketingModal(false)} />
      </div>
    </TabProvider>
  );
};

export default App;