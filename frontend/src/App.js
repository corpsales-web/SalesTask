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
// Import responsive styles
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
// Import new tab system
import { TabProvider } from './contexts/TabContext';
import TabNavigation from './components/TabNavigation'; 
import TabContent from './components/TabContent';
import OpsSmoke from './components/OpsSmoke';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const App = () => {
  // Early smoke route handler without adding global routing
  if (typeof window !== 'undefined' && window.location && window.location.pathname === '/ops/smoke') {
    return <OpsSmoke />
  }

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
  const [leadActionType, setLeadActionType] = useState(null);
  const [showFileUploadModal, setShowFileUploadModal] = useState(false);
  const [showVoiceSTTModal, setShowVoiceSTTModal] = useState(false);
  const [showLeadActionsPanel, setShowLeadActionsPanel] = useState(false);
  const [showAddLeadModal, setShowAddLeadModal] = useState(false);
  const [showAddTaskModal, setShowAddTaskModal] = useState(false);
  const [showBulkUploadModal, setShowBulkUploadModal] = useState(false);
  
  // Admin States
  const [activeAdminPanel, setActiveAdminPanel] = useState('overview');
  const [currentUser, setCurrentUser] = useState(null);
  
  // AI States
  const [aiInsights, setAiInsights] = useState([]);
  
  // New Modal States
  const [showGoalsModal, setShowGoalsModal] = useState(false);
  const [showMarketingModal, setShowMarketingModal] = useState(false);
  const [showNotificationPanel, setShowNotificationPanel] = useState(false);
  
  // Notification State
  const [notifications, setNotifications] = useState([
    {
      id: '1',
      title: 'New Lead Assigned',
      message: 'TechCorp Solutions lead has been assigned to you',
      type: 'lead',
      timestamp: new Date(Date.now() - 300000).toISOString(), // 5 minutes ago
      read: false
    },
    {
      id: '2', 
      title: 'Deal Stage Updated',
      message: 'Green Building Complex deal moved to Contract stage',
      type: 'deal',
      timestamp: new Date(Date.now() - 1800000).toISOString(), // 30 minutes ago
      read: false
    },
    {
      id: '3',
      title: 'Task Due Soon',
      message: 'Site visit task is due in 2 hours',
      type: 'task',
      timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
      read: true
    }
  ]);

  // ... rest of file unchanged ...

  return (
    <TabProvider>
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-100">
        {/* Header - Fully Responsive */}
        <header className="bg-white shadow-lg border-b-2 border-emerald-200">
          <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8">
            <div className="flex justify-between items-center py-2 sm:py-4">
              <div className="flex items-center space-x-2 sm:space-x-4">
                <div className="flex items-center">
                  <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-emerald-600 to-green-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-sm sm:text-lg">A</span>
                  </div>
                  <h1 className="ml-2 sm:ml-3 text-lg sm:text-2xl font-bold text-gray-900 hidden xs:block">
                    Aavana Greens CRM
                  </h1>
                  <h1 className="ml-2 text-sm font-bold text-gray-900 xs:hidden">
                    Aavana
                  </h1>
                </div>
              </div>

              <div className="flex items-center space-x-1 sm:space-x-4">
                <div className="flex items-center space-x-1 sm:space-x-2">
                  <button
                    onClick={() => setShowGoalsModal(true)}
                    className="bg-green-600 text-white px-2 py-1 sm:px-4 sm:py-2 rounded-lg hover:bg-green-700 flex items-center text-xs sm:text-sm"
                  >
                    <Target className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                    <span className="hidden sm:inline">Goals</span>
                  </button>
                  <button
                    onClick={() => setShowMarketingModal(true)}
                    className="bg-orange-600 text-white px-2 py-1 sm:px-4 sm:py-2 rounded-lg hover:bg-orange-700 flex items-center text-xs sm:text-sm"
                  >
                    <TrendingUp className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                    <span className="hidden sm:inline">Marketing</span>
                  </button>
                  <button 
                    onClick={() => setShowNotificationPanel(!showNotificationPanel)}
                    className="relative bg-gray-100 text-gray-700 p-1 sm:p-2 rounded-lg hover:bg-gray-200"
                  >
                    <Bell className="h-4 w-4 sm:h-5 sm:w-5" />
                    {getUnreadNotificationCount() > 0 && (
                      <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 sm:h-5 sm:w-5 flex items-center justify-center text-[10px] sm:text-xs">
                        {getUnreadNotificationCount()}
                      </span>
                    )}
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
                leadActionType={leadActionType}
                setShowLeadActionsPanel={setShowLeadActionsPanel}
                setSelectedLead={setSelectedLead}
                setLeadActionType={setLeadActionType}
                onActionComplete={handleActionComplete}
              />
            )}
          </div>
        </main>

        {/* Floating Chatbot - Aavana 2.0 AI Assistant */}
        <FloatingChatbot />

        {/* Goals Management Modal */}
        <GoalsManagementSystem 
          isOpen={showGoalsModal}
          onClose={() => setShowGoalsModal(false)}
        />

        {/* Comprehensive Digital Marketing Manager Modal */}
        <ComprehensiveDigitalMarketingManager 
          isOpen={showMarketingModal}
          onClose={() => setShowMarketingModal(false)}
        />

        {/* Notification Panel */}
        {showNotificationPanel && (
          <div className="fixed top-16 right-4 w-80 bg-white rounded-lg shadow-lg border z-50">
            <div className="p-4 border-b">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Notifications</h3>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={markAllNotificationsAsRead}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    Mark all read
                  </button>
                  <button
                    onClick={() => setShowNotificationPanel(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>
            <div className="max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-4 text-center text-gray-500">
                  <Bell className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                  <p>No notifications</p>
                </div>
              ) : (
                notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`p-4 border-b cursor-pointer hover:bg-gray-50 ${
                      !notification.read ? 'bg-blue-50' : ''
                    }`}
                    onClick={() => markNotificationAsRead(notification.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h4 className="font-medium text-sm">{notification.title}</h4>
                          {!notification.read && (
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
                        <p className="text-xs text-gray-400 mt-2">
                          {new Date(notification.timestamp).toLocaleString()}
                        </p>
                      </div>
                      <div className="ml-2">
                        {notification.type === 'lead' && '🎯'}
                        {notification.type === 'deal' && '💼'}
                        {notification.type === 'task' && '✅'}
                        {notification.type === 'info' && 'ℹ️'}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
            {notifications.length > 0 && (
              <div className="p-3 border-t bg-gray-50">
                <button className="w-full text-sm text-blue-600 hover:text-blue-800 font-medium">
                  View All Notifications
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </TabProvider>
  );
};

export default App;