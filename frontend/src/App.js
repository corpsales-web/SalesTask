import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
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
import axios from 'axios';
import { useToast } from './hooks/use-toast';
import { toast } from './hooks/use-toast';
import indianCitiesStates from './data/indianCitiesStates';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const App = () => {
  // Force re-render approach with direct DOM manipulation
  const [activeTab, setActiveTab] = useState("dashboard");
  const [forceUpdate, setForceUpdate] = useState(0);
  
  // Force update function
  const handleTabChange = (newTab) => {
    console.log(`Changing tab from ${activeTab} to ${newTab}`);
    setActiveTab(newTab);
    setForceUpdate(prev => prev + 1);
    // Also update URL hash for backup
    window.location.hash = newTab;
    // Force component re-render
    setTimeout(() => setForceUpdate(prev => prev + 1), 100);
  };
  
  const [dashboardStats, setDashboardStats] = useState({
    totalLeads: 26,
    activeLeads: 18,
    conversion_rate: 75,
    totalRevenue: 125000,
    pendingTasks: 12
  });

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
                <Button variant="outline" size="sm" className="flex items-center">
                  📎 Upload
                </Button>
                <Button variant="outline" size="sm" className="flex items-center">
                  🎤 Voice
                </Button>
                <Button variant="outline" size="sm" className="flex items-center">
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
        {/* Simple Tab Navigation */}
        <div className="space-y-6">
          <div className="grid w-full grid-cols-8 bg-white shadow-sm border border-emerald-100 text-xs rounded-lg overflow-hidden">
            <button 
              onClick={() => handleTabChange("dashboard")}
              className={`p-3 flex items-center justify-center transition-colors ${activeTab === "dashboard" ? "bg-emerald-100 text-emerald-700 font-bold" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <Activity className="h-3 w-3 mr-1" />
              Dashboard
            </button>
            <button 
              onClick={() => setActiveTab("leads")}
              className={`p-3 flex items-center justify-center transition-colors ${activeTab === "leads" ? "bg-emerald-100 text-emerald-700" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <Users className="h-3 w-3 mr-1" />
              Leads
            </button>
            <button 
              onClick={() => setActiveTab("pipeline")}
              className={`p-3 flex items-center justify-center transition-colors ${activeTab === "pipeline" ? "bg-emerald-100 text-emerald-700" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <Target className="h-3 w-3 mr-1" />
              Pipeline
            </button>
            <button 
              onClick={() => setActiveTab("tasks")}
              className={`p-3 flex items-center justify-center transition-colors ${activeTab === "tasks" ? "bg-emerald-100 text-emerald-700" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <CheckCircle className="h-3 w-3 mr-1" />
              Tasks
            </button>
            <button 
              onClick={() => setActiveTab("erp")}
              className={`p-3 flex items-center justify-center transition-colors ${activeTab === "erp" ? "bg-emerald-100 text-emerald-700" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <Package className="h-3 w-3 mr-1" />
              ERP
            </button>
            <button 
              onClick={() => handleTabChange("hrms")}
              className={`p-3 flex items-center justify-center transition-colors ${activeTab === "hrms" ? "bg-emerald-100 text-emerald-700 font-bold" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <UserCheck className="h-3 w-3 mr-1" />
              HRMS
            </button>
            <button 
              onClick={() => setActiveTab("ai")}
              className={`p-3 flex items-center justify-center transition-colors ${activeTab === "ai" ? "bg-emerald-100 text-emerald-700" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <Brain className="h-3 w-3 mr-1" />
              AI
            </button>
            <button 
              onClick={() => setActiveTab("admin")}
              className={`p-3 flex items-center justify-center transition-colors ${activeTab === "admin" ? "bg-emerald-100 text-emerald-700" : "text-gray-600 hover:bg-gray-50"}`}
            >
              <Settings className="h-3 w-3 mr-1" />
              Admin
            </button>
          </div>

          {/* Direct Conditional Content Rendering */}
          <div key={renderKey}>
          
          {/* Debug Info */}
          <div className="mb-4 p-2 bg-yellow-100 rounded text-sm">
            <strong>Debug:</strong> Current activeTab = "{activeTab}" | Hash = "{window.location.hash}"
          </div>
          
          {/* Dashboard Content */}
          {activeTab === "dashboard" && (
            <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="bg-white shadow-lg border-emerald-100">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Total Leads</CardTitle>
                  <Users className="h-4 w-4 text-emerald-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-900">{dashboardStats.totalLeads}</div>
                </CardContent>
              </Card>

              <Card className="bg-white shadow-lg border-emerald-100">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Active Leads</CardTitle>
                  <Target className="h-4 w-4 text-blue-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-900">{dashboardStats.activeLeads}</div>
                </CardContent>
              </Card>

              <Card className="bg-white shadow-lg border-emerald-100">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Conversion Rate</CardTitle>
                  <TrendingUp className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-900">{dashboardStats.conversion_rate}%</div>
                  <Progress value={dashboardStats.conversion_rate} className="mt-2" />
                </CardContent>
              </Card>

              <Card className="bg-white shadow-lg border-emerald-100">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Pending Tasks</CardTitle>
                  <Clock className="h-4 w-4 text-orange-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-900">{dashboardStats.pendingTasks}</div>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-white shadow-lg">
                <CardHeader>
                  <CardTitle className="text-gray-900">Recent Leads</CardTitle>
                  <CardDescription>Latest lead inquiries</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback>RK</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <p className="text-sm font-medium">Rajesh Kumar</p>
                        <p className="text-xs text-gray-500">Interested in 3BHK villa</p>
                      </div>
                      <Badge className="bg-green-100 text-green-800">Hot</Badge>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback>PS</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <p className="text-sm font-medium">Priya Sharma</p>
                        <p className="text-xs text-gray-500">Looking for 2BHK apartment</p>
                      </div>
                      <Badge className="bg-yellow-100 text-yellow-800">Warm</Badge>
                    </div>
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
                      <span className="text-sm font-medium">8</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">In Progress</span>
                      <span className="text-sm font-medium">12</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Qualified</span>
                      <span className="text-sm font-medium">6</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            </div>
          )}

          {/* HRMS Content */}
          {activeTab === "hrms" && (
            <div className="space-y-6">
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">Employee Management</h2>
                    <p className="text-gray-600">Manage employee attendance and records</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
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
              </div>
            </div>
          )}

          {/* Other Tabs */}
          {activeTab === "leads" && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Lead Management</h2>
              <p className="text-gray-600">Manage your leads and prospects</p>
            </div>
          )}

          {activeTab === "tasks" && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Task Management</h2>
              <p className="text-gray-600">Track and manage your tasks</p>
            </div>
          )}

          {activeTab === "erp" && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Business Management & Operations</h2>
              <p className="text-gray-600">Manage projects and operations</p>
            </div>
          )}

          {activeTab === "pipeline" && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Sales Pipeline</h2>
              <p className="text-gray-600">Track your sales pipeline</p>
            </div>
          )}

          {activeTab === "ai" && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">AI Assistant</h2>
              <p className="text-gray-600">AI-powered insights and automation</p>
            </div>
          )}

          {activeTab === "admin" && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Super Admin Panel</h2>
              <p className="text-gray-600">System administration and settings</p>
              <div className="mt-6">
                <NotificationSystem showTestingPanel={true} />
              </div>
            </div>
          )}

          </div>
        </div>
      </main>
    </div>
  );
};

export default App;