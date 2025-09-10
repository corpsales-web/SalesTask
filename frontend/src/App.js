import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Textarea } from "./components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Progress } from "./components/ui/progress";
import { Toaster } from "./components/ui/toaster";
import { useToast } from "./hooks/use-toast";
import { 
  Users, 
  TrendingUp, 
  DollarSign, 
  CheckCircle, 
  Clock, 
  Plus, 
  Phone, 
  Mail, 
  MapPin,
  Target,
  Calendar,
  Activity,
  Leaf,
  Mic,
  MicOff,
  Brain,
  Sparkles,
  Bot,
  Lightbulb,
  Zap,
  Edit,
  Trash2,
  Settings,
  Package,
  FileText,
  BarChart3,
  UserCheck,
  MessageSquare,
  Camera,
  Download,
  Upload,
  Archive,
  Clock2,
  AlertTriangle
} from "lucide-react";

// Import location and category data
import { 
  INDIAN_STATES, 
  CITIES_BY_STATE, 
  LEAD_CATEGORIES, 
  LEAD_SOURCES 
} from "./data/indianCitiesStates";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [leads, setLeads] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [selectedLead, setSelectedLead] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [voiceInput, setVoiceInput] = useState("");
  const [aiInsights, setAiInsights] = useState([]);
  const [generatedContent, setGeneratedContent] = useState("");
  
  // Location and Category Management
  const [customCategories, setCustomCategories] = useState([]);
  const [selectedState, setSelectedState] = useState("");
  const [selectedCity, setSelectedCity] = useState("");
  const [customLocation, setCustomLocation] = useState("");
  const [isCustomLocation, setIsCustomLocation] = useState(false);
  const [isCustomCategory, setIsCustomCategory] = useState(false);
  const [newCustomCategory, setNewCustomCategory] = useState("");
  
  // ERP & Business Management
  const [products, setProducts] = useState([]);
  const [inventoryAlerts, setInventoryAlerts] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [projects, setProjects] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [executiveDashboard, setExecutiveDashboard] = useState(null);
  
  // HRMS Data
  const [employees, setEmployees] = useState([]);
  const [attendanceData, setAttendanceData] = useState([]);
  const [payrollReport, setPayrollReport] = useState(null);
  
  const mediaRecorder = useRef(null);
  const { toast } = useToast();

  // Form states
  const [newLead, setNewLead] = useState({
    name: "",
    phone: "",
    email: "",
    budget: "",
    space_size: "",
    city: "",
    state: "",
    source: "",
    category: "",
    notes: "",
    tags: "",
    assigned_to: ""
  });

  // Category Management Functions
  const addCustomCategory = () => {
    if (newCustomCategory.trim() && !customCategories.includes(newCustomCategory.trim())) {
      setCustomCategories([...customCategories, newCustomCategory.trim()]);
      setNewCustomCategory("");
      toast({
        title: "Category Added",
        description: `"${newCustomCategory.trim()}" has been added to categories`
      });
    }
  };

  const deleteCustomCategory = (categoryToDelete) => {
    setCustomCategories(customCategories.filter(cat => cat !== categoryToDelete));
    toast({
      title: "Category Deleted",
      description: `"${categoryToDelete}" has been removed`
    });
  };

  // Location Management
  const handleLocationChange = () => {
    if (selectedState && selectedCity) {
      const location = `${selectedCity}, ${selectedState}`;
      setNewLead({...newLead, city: selectedCity, state: selectedState});
    }
  };

  useEffect(() => {
    handleLocationChange();
  }, [selectedState, selectedCity]);

  const [newTask, setNewTask] = useState({
    title: "",
    description: "",
    priority: "Medium",
    assigned_to: "",
    lead_id: "",
    due_date: ""
  });

  // Fetch data functions
  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setDashboardStats(response.data);
    } catch (error) {
      console.error("Error fetching dashboard stats:", error);
      toast({
        title: "Error",
        description: "Failed to fetch dashboard statistics",
        variant: "destructive"
      });
    }
  };

  const fetchLeads = async () => {
    try {
      const response = await axios.get(`${API}/leads`);
      setLeads(response.data);
    } catch (error) {
      console.error("Error fetching leads:", error);
      toast({
        title: "Error",
        description: "Failed to fetch leads",
        variant: "destructive"
      });
    }
  };

  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API}/tasks`);
      setTasks(response.data);
    } catch (error) {
      console.error("Error fetching tasks:", error);
      toast({
        title: "Error",
        description: "Failed to fetch tasks",
        variant: "destructive"
      });
    }
  };

  // ERP Data Fetching
  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API}/erp/products`);
      setProducts(response.data);
    } catch (error) {
      console.error("Error fetching products:", error);
    }
  };

  const fetchInventoryAlerts = async () => {
    try {
      const response = await axios.get(`${API}/erp/inventory-alerts`);
      setInventoryAlerts(response.data);
    } catch (error) {
      console.error("Error fetching inventory alerts:", error);
    }
  };

  const fetchInvoices = async () => {
    try {
      const response = await axios.get(`${API}/erp/invoices`);
      setInvoices(response.data);
    } catch (error) {
      console.error("Error fetching invoices:", error);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/erp/projects`);
      setProjects(response.data);
    } catch (error) {
      console.error("Error fetching projects:", error);
    }
  };

  const fetchExecutiveDashboard = async () => {
    try {
      const response = await axios.get(`${API}/analytics/executive-dashboard`);
      setExecutiveDashboard(response.data);
    } catch (error) {
      console.error("Error fetching executive dashboard:", error);
    }
  };

  // HRMS Data Fetching
  const fetchPayrollReport = async () => {
    try {
      const currentDate = new Date();
      const response = await axios.get(`${API}/hrms/payroll-report?month=${currentDate.getMonth() + 1}&year=${currentDate.getFullYear()}`);
      setPayrollReport(response.data);
    } catch (error) {
      console.error("Error fetching payroll report:", error);
    }
  };

  // Create lead function
  const createLead = async (e) => {
    e.preventDefault();
    try {
      const location = isCustomLocation ? 
        customLocation : 
        (selectedCity && selectedState ? `${selectedCity}, ${selectedState}` : "");
      
      const leadData = {
        ...newLead,
        location: location,
        budget: newLead.budget ? parseFloat(newLead.budget) : null,
        tags: newLead.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      };
      
      await axios.post(`${API}/leads`, leadData);
      toast({
        title: "Success",
        description: "Lead created successfully"
      });
      
      // Reset form
      setNewLead({
        name: "",
        phone: "",
        email: "",
        budget: "",
        space_size: "",
        city: "",
        state: "",
        source: "",
        category: "",
        notes: "",
        tags: "",
        assigned_to: ""
      });
      
      setSelectedState("");
      setSelectedCity("");
      setCustomLocation("");
      setIsCustomLocation(false);
      setIsCustomCategory(false);
      
      fetchLeads();
      fetchDashboardStats();
    } catch (error) {
      console.error("Error creating lead:", error);
      toast({
        title: "Error",
        description: "Failed to create lead",
        variant: "destructive"
      });
    }
  };

  // Update lead status
  const updateLeadStatus = async (leadId, newStatus) => {
    try {
      await axios.put(`${API}/leads/${leadId}`, { status: newStatus });
      toast({
        title: "Success",
        description: "Lead status updated successfully"
      });
      fetchLeads();
      fetchDashboardStats();
    } catch (error) {
      console.error("Error updating lead:", error);
      toast({
        title: "Error",
        description: "Failed to update lead status",
        variant: "destructive"
      });
    }
  };

  // Voice-to-Task functions
  const startVoiceRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      
      let audioChunks = [];
      
      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };
      
      mediaRecorder.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        // For demo purposes, we'll use a text input instead of actual speech recognition
        // In production, you would integrate with speech-to-text service
        setVoiceInput("Visit Mr. Sharma tomorrow 3 PM for balcony garden proposal");
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.current.start();
      setIsRecording(true);
      
      toast({
        title: "Recording Started",
        description: "Speak your task requirements..."
      });
      
    } catch (error) {
      console.error("Error accessing microphone:", error);
      toast({
        title: "Error",
        description: "Could not access microphone",
        variant: "destructive"
      });
    }
  };

  const stopVoiceRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      setIsRecording(false);
      
      toast({
        title: "Recording Stopped",
        description: "Processing your voice input..."
      });
    }
  };

  const processVoiceToTask = async () => {
    if (!voiceInput.trim()) return;
    
    try {
      const response = await axios.post(`${API}/ai/voice-to-task`, {
        voice_input: voiceInput,
        context: {
          user_role: "sales_manager",
          current_time: new Date().toISOString()
        }
      });
      
      toast({
        title: "✨ AI Task Created",
        description: `Task "${response.data.task_breakdown.title}" has been created successfully!`
      });
      
      // Clear voice input and refresh tasks
      setVoiceInput("");
      fetchTasks();
      
    } catch (error) {
      console.error("Error processing voice input:", error);
      toast({
        title: "Error",
        description: "Failed to process voice input",
        variant: "destructive"
      });
    }
  };

  // AI Insights function
  const generateAIInsights = async (type = "leads") => {
    try {
      const response = await axios.post(`${API}/ai/insights`, {
        type: type,
        timeframe: "current"
      });
      
      setAiInsights(response.data.insights);
      
      toast({
        title: "🧠 AI Insights Generated",
        description: "Fresh business insights are ready!"
      });
      
    } catch (error) {
      console.error("Error generating insights:", error);
      toast({
        title: "Error",
        description: "Failed to generate AI insights",
        variant: "destructive"
      });
    }
  };

  // AI Content Generation
  const generateContent = async (type = "social_post") => {
    try {
      const response = await axios.post(`${API}/ai/generate-content`, {
        type: type,
        topic: "Green building solutions and sustainable living",
        brand_context: "Aavana Greens - Your partner in sustainable green solutions",
        target_audience: "Homeowners and businesses interested in eco-friendly living"
      });
      
      setGeneratedContent(response.data.content);
      
      toast({
        title: "🎨 Content Generated",
        description: "AI has created marketing content for you!"
      });
      
    } catch (error) {
      console.error("Error generating content:", error);
      toast({
        title: "Error",
        description: "Failed to generate content",
        variant: "destructive"
      });
    }
  };
  const createTask = async (e) => {
    e.preventDefault();
    try {
      const taskData = {
        ...newTask,
        due_date: newTask.due_date ? new Date(newTask.due_date).toISOString() : null
      };
      
      await axios.post(`${API}/tasks`, taskData);
      toast({
        title: "Success",
        description: "Task created successfully"
      });
      
      setNewTask({
        title: "",
        description: "",
        priority: "Medium",
        assigned_to: "",
        lead_id: "",
        due_date: ""
      });
      
      fetchTasks();
    } catch (error) {
      console.error("Error creating task:", error);
      toast({
        title: "Error",
        description: "Failed to create task",
        variant: "destructive"
      });
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchDashboardStats(), fetchLeads(), fetchTasks()]);
      setLoading(false);
    };
    loadData();
  }, []);

  const getStatusColor = (status) => {
    const colors = {
      "New": "bg-blue-100 text-blue-800 border-blue-200",
      "Qualified": "bg-green-100 text-green-800 border-green-200",
      "Proposal": "bg-yellow-100 text-yellow-800 border-yellow-200",
      "Negotiation": "bg-orange-100 text-orange-800 border-orange-200",
      "Won": "bg-emerald-100 text-emerald-800 border-emerald-200",
      "Lost": "bg-red-100 text-red-800 border-red-200"
    };
    return colors[status] || "bg-gray-100 text-gray-800 border-gray-200";
  };

  const getPriorityColor = (priority) => {
    const colors = {
      "Low": "bg-gray-100 text-gray-800",
      "Medium": "bg-blue-100 text-blue-800",
      "High": "bg-orange-100 text-orange-800",
      "Urgent": "bg-red-100 text-red-800"
    };
    return colors[priority] || "bg-gray-100 text-gray-800";
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4"></div>
          <p className="text-emerald-700 font-medium">Loading Aavana Greens CRM...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-100">
      {/* Header */}
      <header className="bg-white shadow-lg border-b border-emerald-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="bg-emerald-600 p-2 rounded-lg">
                <Leaf className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Aavana Greens</h1>
                <p className="text-sm text-emerald-600 font-medium">CRM & Business Management</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-gray-500">Business Number</p>
                <p className="font-medium text-gray-900">8447475761</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-6 bg-white shadow-sm border border-emerald-100">
            <TabsTrigger value="dashboard" className="data-[state=active]:bg-emerald-100 data-[state=active]:text-emerald-700">
              <Activity className="h-4 w-4 mr-2" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="leads" className="data-[state=active]:bg-emerald-100 data-[state=active]:text-emerald-700">
              <Users className="h-4 w-4 mr-2" />
              Leads
            </TabsTrigger>
            <TabsTrigger value="pipeline" className="data-[state=active]:bg-emerald-100 data-[state=active]:text-emerald-700">
              <Target className="h-4 w-4 mr-2" />
              Pipeline
            </TabsTrigger>
            <TabsTrigger value="tasks" className="data-[state=active]:bg-emerald-100 data-[state=active]:text-emerald-700">
              <CheckCircle className="h-4 w-4 mr-2" />
              Tasks
            </TabsTrigger>
            <TabsTrigger value="ai" className="data-[state=active]:bg-emerald-100 data-[state=active]:text-emerald-700">
              <Brain className="h-4 w-4 mr-2" />
              AI Assistant
            </TabsTrigger>
            <TabsTrigger value="admin" className="data-[state=active]:bg-emerald-100 data-[state=active]:text-emerald-700">
              <Settings className="h-4 w-4 mr-2" />
              Admin Panel
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            {dashboardStats && (
              <>
                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <Card className="bg-white shadow-lg border-emerald-100 hover:shadow-xl transition-shadow">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium text-gray-600">Total Leads</CardTitle>
                      <Users className="h-4 w-4 text-emerald-600" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-gray-900">{dashboardStats.total_leads}</div>
                      <p className="text-xs text-emerald-600 mt-1">
                        +{dashboardStats.new_leads} new this period
                      </p>
                    </CardContent>
                  </Card>

                  <Card className="bg-white shadow-lg border-emerald-100 hover:shadow-xl transition-shadow">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium text-gray-600">Conversion Rate</CardTitle>
                      <TrendingUp className="h-4 w-4 text-emerald-600" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-gray-900">{dashboardStats.conversion_rate}%</div>
                      <Progress value={dashboardStats.conversion_rate} className="mt-2" />
                    </CardContent>
                  </Card>

                  <Card className="bg-white shadow-lg border-emerald-100 hover:shadow-xl transition-shadow">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium text-gray-600">Total Revenue</CardTitle>
                      <DollarSign className="h-4 w-4 text-emerald-600" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-gray-900">
                        ₹{dashboardStats.total_revenue.toLocaleString('en-IN')}
                      </div>
                      <p className="text-xs text-emerald-600 mt-1">
                        {dashboardStats.won_deals} deals closed
                      </p>
                    </CardContent>
                  </Card>

                  <Card className="bg-white shadow-lg border-emerald-100 hover:shadow-xl transition-shadow">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium text-gray-600">Pending Tasks</CardTitle>
                      <Clock className="h-4 w-4 text-emerald-600" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-gray-900">{dashboardStats.pending_tasks}</div>
                      <p className="text-xs text-emerald-600 mt-1">Action required</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Recent Activity */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card className="bg-white shadow-lg border-emerald-100">
                    <CardHeader>
                      <CardTitle className="text-gray-900">Recent Leads</CardTitle>
                      <CardDescription>Latest potential customers</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {leads.slice(0, 5).map((lead) => (
                          <div key={lead.id} className="flex items-center justify-between p-3 bg-emerald-50 rounded-lg">
                            <div>
                              <p className="font-medium text-gray-900">{lead.name}</p>
                              <p className="text-sm text-gray-600">{lead.location}</p>
                            </div>
                            <Badge className={getStatusColor(lead.status)}>{lead.status}</Badge>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-white shadow-lg border-emerald-100">
                    <CardHeader>
                      <CardTitle className="text-gray-900">Pipeline Overview</CardTitle>
                      <CardDescription>Leads by stage</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium text-gray-700">New</span>
                          <span className="text-sm font-bold text-blue-600">{dashboardStats.new_leads}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium text-gray-700">Qualified</span>
                          <span className="text-sm font-bold text-green-600">{dashboardStats.qualified_leads}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium text-gray-700">Won</span>
                          <span className="text-sm font-bold text-emerald-600">{dashboardStats.won_deals}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium text-gray-700">Lost</span>
                          <span className="text-sm font-bold text-red-600">{dashboardStats.lost_deals}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </>
            )}
          </TabsContent>

          {/* Leads Tab */}
          <TabsContent value="leads" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Lead Management</h2>
              <Dialog>
                <DialogTrigger asChild>
                  <Button className="bg-emerald-600 hover:bg-emerald-700 text-white">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Lead
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>Add New Lead</DialogTitle>
                    <DialogDescription>Create a new lead with comprehensive information</DialogDescription>
                  </DialogHeader>
                  <form onSubmit={createLead} className="space-y-4">
                    {/* Basic Information */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="name">Name *</Label>
                        <Input
                          id="name"
                          value={newLead.name}
                          onChange={(e) => setNewLead({...newLead, name: e.target.value})}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="phone">Phone *</Label>
                        <Input
                          id="phone"
                          value={newLead.phone}
                          onChange={(e) => setNewLead({...newLead, phone: e.target.value})}
                          required
                        />
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        value={newLead.email}
                        onChange={(e) => setNewLead({...newLead, email: e.target.value})}
                      />
                    </div>

                    {/* Lead Source */}
                    <div>
                      <Label htmlFor="source">Lead Source *</Label>
                      <Select value={newLead.source} onValueChange={(value) => setNewLead({...newLead, source: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select lead source" />
                        </SelectTrigger>
                        <SelectContent>
                          {LEAD_SOURCES.map((source) => (
                            <SelectItem key={source} value={source}>{source}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Client Category */}
                    <div>
                      <Label htmlFor="category">Client Category *</Label>
                      <div className="space-y-2">
                        <div className="flex gap-2">
                          <Select 
                            value={newLead.category} 
                            onValueChange={(value) => setNewLead({...newLead, category: value})}
                            disabled={isCustomCategory}
                          >
                            <SelectTrigger className="flex-1">
                              <SelectValue placeholder="Select client category" />
                            </SelectTrigger>
                            <SelectContent>
                              {LEAD_CATEGORIES.concat(customCategories).map((category) => (
                                <SelectItem key={category} value={category}>{category}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <Button 
                            type="button"
                            variant="outline" 
                            size="sm"
                            onClick={() => setIsCustomCategory(!isCustomCategory)}
                          >
                            {isCustomCategory ? "Select" : "Custom"}
                          </Button>
                        </div>
                        
                        {isCustomCategory && (
                          <div className="flex gap-2">
                            <Input
                              placeholder="Enter custom category"
                              value={newCustomCategory}
                              onChange={(e) => setNewCustomCategory(e.target.value)}
                              className="flex-1"
                            />
                            <Button 
                              type="button" 
                              size="sm" 
                              onClick={addCustomCategory}
                              className="bg-emerald-600 hover:bg-emerald-700"
                            >
                              Add
                            </Button>
                          </div>
                        )}
                        
                        {/* Custom Categories Management */}
                        {customCategories.length > 0 && (
                          <div className="bg-emerald-50 p-3 rounded-lg">
                            <Label className="text-sm font-medium text-emerald-800">Custom Categories:</Label>
                            <div className="flex flex-wrap gap-2 mt-2">
                              {customCategories.map((category) => (
                                <div key={category} className="flex items-center bg-white px-2 py-1 rounded border">
                                  <span className="text-sm">{category}</span>
                                  <Button
                                    type="button"
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => deleteCustomCategory(category)}
                                    className="ml-1 h-4 w-4 p-0 hover:bg-red-100"
                                  >
                                    <Trash2 className="h-3 w-3 text-red-600" />
                                  </Button>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Location Management */}
                    <div>
                      <Label>Location *</Label>
                      <div className="space-y-3">
                        <div className="flex gap-2">
                          <Button
                            type="button"
                            variant={!isCustomLocation ? "default" : "outline"}
                            size="sm"
                            onClick={() => setIsCustomLocation(false)}
                          >
                            Select from List
                          </Button>
                          <Button
                            type="button"
                            variant={isCustomLocation ? "default" : "outline"}
                            size="sm"
                            onClick={() => setIsCustomLocation(true)}
                          >
                            Enter Manually
                          </Button>
                        </div>

                        {!isCustomLocation ? (
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <Label htmlFor="state">State</Label>
                              <Select value={selectedState} onValueChange={setSelectedState}>
                                <SelectTrigger>
                                  <SelectValue placeholder="Select state" />
                                </SelectTrigger>
                                <SelectContent>
                                  {INDIAN_STATES.map((state) => (
                                    <SelectItem key={state} value={state}>{state}</SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            </div>
                            <div>
                              <Label htmlFor="city">City</Label>
                              <Select 
                                value={selectedCity} 
                                onValueChange={setSelectedCity}
                                disabled={!selectedState}
                              >
                                <SelectTrigger>
                                  <SelectValue placeholder="Select city" />
                                </SelectTrigger>
                                <SelectContent>
                                  {selectedState && CITIES_BY_STATE[selectedState]?.map((city) => (
                                    <SelectItem key={city} value={city}>{city}</SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            </div>
                          </div>
                        ) : (
                          <div>
                            <Label htmlFor="customLocation">Custom Location</Label>
                            <Input
                              id="customLocation"
                              placeholder="Enter city, state (e.g., Noida, Uttar Pradesh)"
                              value={customLocation}
                              onChange={(e) => setCustomLocation(e.target.value)}
                            />
                          </div>
                        )}

                        {/* Display selected location */}
                        {((selectedCity && selectedState) || customLocation) && (
                          <div className="bg-emerald-50 p-2 rounded border border-emerald-200">
                            <span className="text-sm text-emerald-700">
                              📍 Location: {isCustomLocation ? customLocation : `${selectedCity}, ${selectedState}`}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Additional Details */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="budget">Budget (₹)</Label>
                        <Input
                          id="budget"
                          type="number"
                          placeholder="e.g., 50000"
                          value={newLead.budget}
                          onChange={(e) => setNewLead({...newLead, budget: e.target.value})}
                        />
                      </div>
                      <div>
                        <Label htmlFor="space_size">Space Size</Label>
                        <Input
                          id="space_size"
                          placeholder="e.g., 2 BHK, 1000 sq ft"
                          value={newLead.space_size}
                          onChange={(e) => setNewLead({...newLead, space_size: e.target.value})}
                        />
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="assigned_to">Assigned To</Label>
                      <Select value={newLead.assigned_to} onValueChange={(value) => setNewLead({...newLead, assigned_to: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select team member" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Sales Team A">Sales Team A</SelectItem>
                          <SelectItem value="Sales Team B">Sales Team B</SelectItem>
                          <SelectItem value="Design Team">Design Team</SelectItem>
                          <SelectItem value="Senior Consultant">Senior Consultant</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="notes">Notes</Label>
                      <Textarea
                        id="notes"
                        placeholder="Additional information about the lead..."
                        value={newLead.notes}
                        onChange={(e) => setNewLead({...newLead, notes: e.target.value})}
                        rows={3}
                      />
                    </div>

                    <div>
                      <Label htmlFor="tags">Tags (comma-separated)</Label>
                      <Input
                        id="tags"
                        placeholder="e.g., urgent, high-value, balcony"
                        value={newLead.tags}
                        onChange={(e) => setNewLead({...newLead, tags: e.target.value})}
                      />
                    </div>

                    <Button type="submit" className="w-full bg-emerald-600 hover:bg-emerald-700">
                      Create Lead
                    </Button>
                  </form>
                </DialogContent>
              </Dialog>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {leads.map((lead) => (
                <Card key={lead.id} className="bg-white shadow-lg border-emerald-100 hover:shadow-xl transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg text-gray-900">{lead.name}</CardTitle>
                        <CardDescription className="flex items-center mt-1">
                          <Phone className="h-3 w-3 mr-1" />
                          {lead.phone}
                        </CardDescription>
                      </div>
                      <Badge className={getStatusColor(lead.status)}>{lead.status}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {lead.email && (
                        <p className="text-sm text-gray-600 flex items-center">
                          <Mail className="h-3 w-3 mr-1" />
                          {lead.email}
                        </p>
                      )}
                      {lead.location && (
                        <p className="text-sm text-gray-600 flex items-center">
                          <MapPin className="h-3 w-3 mr-1" />
                          {lead.location}
                        </p>
                      )}
                      {lead.budget && (
                        <p className="text-sm text-gray-600 flex items-center">
                          <DollarSign className="h-3 w-3 mr-1" />
                          ₹{lead.budget.toLocaleString('en-IN')}
                        </p>
                      )}
                      {lead.notes && (
                        <p className="text-sm text-gray-600 mt-2">{lead.notes}</p>
                      )}
                    </div>
                    <div className="mt-4 flex gap-2">
                      <Select onValueChange={(value) => updateLeadStatus(lead.id, value)}>
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="Update Status" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="New">New</SelectItem>
                          <SelectItem value="Qualified">Qualified</SelectItem>
                          <SelectItem value="Proposal">Proposal</SelectItem>
                          <SelectItem value="Negotiation">Negotiation</SelectItem>
                          <SelectItem value="Won">Won</SelectItem>
                          <SelectItem value="Lost">Lost</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Pipeline Tab */}
          <TabsContent value="pipeline" className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Sales Pipeline</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {["New", "Qualified", "Proposal", "Negotiation", "Won"].map((status) => {
                const statusLeads = leads.filter(lead => lead.status === status);
                return (
                  <Card key={status} className="bg-white shadow-lg border-emerald-100">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg text-gray-900 flex items-center justify-between">
                        {status}
                        <Badge variant="secondary" className="bg-emerald-100 text-emerald-800">
                          {statusLeads.length}
                        </Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="space-y-3 max-h-96 overflow-y-auto">
                        {statusLeads.map((lead) => (
                          <div
                            key={lead.id}
                            className="p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-emerald-50 transition-colors cursor-pointer"
                            onClick={() => setSelectedLead(lead)}
                          >
                            <p className="font-medium text-gray-900 text-sm">{lead.name}</p>
                            <p className="text-xs text-gray-600">{lead.phone}</p>
                            {lead.budget && (
                              <p className="text-xs text-emerald-600 font-medium mt-1">
                                ₹{lead.budget.toLocaleString('en-IN')}
                              </p>
                            )}
                          </div>
                        ))}
                        {statusLeads.length === 0 && (
                          <p className="text-sm text-gray-500 italic text-center py-4">
                            No leads in this stage
                          </p>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>

          {/* Tasks Tab */}
          <TabsContent value="tasks" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Task Management</h2>
              <div className="flex gap-2">
                {/* Voice-to-Task Feature */}
                <div className="flex items-center gap-2 bg-emerald-50 p-2 rounded-lg border border-emerald-200">
                  <Button
                    onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
                    variant={isRecording ? "destructive" : "outline"}
                    size="sm"
                    className={isRecording ? "bg-red-500 hover:bg-red-600" : "border-emerald-300 hover:bg-emerald-100"}
                  >
                    {isRecording ? <MicOff className="h-4 w-4 mr-2" /> : <Mic className="h-4 w-4 mr-2" />}
                    {isRecording ? "Stop" : "Voice Task"}
                  </Button>
                  {voiceInput && (
                    <Button
                      onClick={processVoiceToTask}
                      size="sm"
                      className="bg-emerald-600 hover:bg-emerald-700 text-white"
                    >
                      <Sparkles className="h-4 w-4 mr-2" />
                      Create AI Task
                    </Button>
                  )}
                </div>
                <Dialog>
                  <DialogTrigger asChild>
                    <Button className="bg-emerald-600 hover:bg-emerald-700 text-white">
                      <Plus className="h-4 w-4 mr-2" />
                      Add Task
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-md">
                    <DialogHeader>
                      <DialogTitle>Create New Task</DialogTitle>
                      <DialogDescription>Add a new task to your workflow</DialogDescription>
                    </DialogHeader>
                    <form onSubmit={createTask} className="space-y-4">
                      <div>
                        <Label htmlFor="task-title">Title *</Label>
                        <Input
                          id="task-title"
                          value={newTask.title}
                          onChange={(e) => setNewTask({...newTask, title: e.target.value})}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="task-description">Description</Label>
                        <Textarea
                          id="task-description"
                          value={newTask.description}
                          onChange={(e) => setNewTask({...newTask, description: e.target.value})}
                          rows={3}
                        />
                      </div>
                      <div>
                        <Label htmlFor="task-priority">Priority</Label>
                        <Select value={newTask.priority} onValueChange={(value) => setNewTask({...newTask, priority: value})}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Low">Low</SelectItem>
                            <SelectItem value="Medium">Medium</SelectItem>
                            <SelectItem value="High">High</SelectItem>
                            <SelectItem value="Urgent">Urgent</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label htmlFor="task-due-date">Due Date</Label>
                        <Input
                          id="task-due-date"
                          type="datetime-local"
                          value={newTask.due_date}
                          onChange={(e) => setNewTask({...newTask, due_date: e.target.value})}
                        />
                      </div>
                      <Button type="submit" className="w-full bg-emerald-600 hover:bg-emerald-700">
                        Create Task
                      </Button>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            </div>

            {/* Voice Input Display */}
            {voiceInput && (
              <Card className="bg-emerald-50 border-emerald-200">
                <CardHeader>
                  <CardTitle className="text-emerald-800 flex items-center">
                    <Mic className="h-5 w-5 mr-2" />
                    Voice Input Captured
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-emerald-700 italic">"{voiceInput}"</p>
                  <div className="mt-3 flex gap-2">
                    <Button 
                      onClick={processVoiceToTask}
                      size="sm"
                      className="bg-emerald-600 hover:bg-emerald-700"
                    >
                      <Zap className="h-4 w-4 mr-2" />
                      Convert to Task
                    </Button>
                    <Button 
                      onClick={() => setVoiceInput("")}
                      variant="outline"
                      size="sm"
                    >
                      Clear
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {tasks.map((task) => (
                <Card key={task.id} className="bg-white shadow-lg border-emerald-100 hover:shadow-xl transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-lg text-gray-900">{task.title}</CardTitle>
                      <Badge className={getPriorityColor(task.priority)}>{task.priority}</Badge>
                    </div>
                    {task.description && (
                      <CardDescription>{task.description}</CardDescription>
                    )}
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Status:</span>
                        <Badge variant="outline" className="text-xs">{task.status}</Badge>
                      </div>
                      {task.due_date && (
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">Due:</span>
                          <span className="text-sm text-gray-900">
                            {new Date(task.due_date).toLocaleDateString('en-IN')}
                          </span>
                        </div>
                      )}
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Created:</span>
                        <span className="text-sm text-gray-900">
                          {new Date(task.created_at).toLocaleDateString('en-IN')}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* AI Assistant Tab */}
          <TabsContent value="ai" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                <Brain className="h-8 w-8 mr-3 text-emerald-600" />
                AI Assistant
              </h2>
              <Badge className="bg-emerald-100 text-emerald-800 border-emerald-300">
                Hybrid AI • GPT-5 + Claude + Gemini
              </Badge>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Voice-to-Task Panel */}
              <Card className="bg-gradient-to-br from-emerald-50 to-green-100 border-emerald-200 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-emerald-800 flex items-center">
                    <Mic className="h-5 w-5 mr-2" />
                    Voice-to-Task AI
                  </CardTitle>
                  <CardDescription>
                    Speak naturally and AI will create structured tasks with reminders
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {voiceInput ? (
                    <div className="bg-white p-4 rounded-lg border border-emerald-200">
                      <p className="text-sm text-gray-600 mb-2">Captured Voice Input:</p>
                      <p className="text-emerald-700 font-medium italic">"{voiceInput}"</p>
                      <div className="mt-3 flex gap-2">
                        <Button 
                          onClick={processVoiceToTask}
                          size="sm"
                          className="bg-emerald-600 hover:bg-emerald-700"
                        >
                          <Sparkles className="h-4 w-4 mr-2" />
                          Create AI Task
                        </Button>
                        <Button 
                          onClick={() => setVoiceInput("")}
                          variant="outline"
                          size="sm"
                        >
                          Clear
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Button
                        onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
                        size="lg"
                        variant={isRecording ? "destructive" : "default"}
                        className={isRecording ? 
                          "bg-red-500 hover:bg-red-600 text-white animate-pulse" : 
                          "bg-emerald-600 hover:bg-emerald-700 text-white"
                        }
                      >
                        {isRecording ? (
                          <>
                            <MicOff className="h-6 w-6 mr-2" />
                            Stop Recording
                          </>
                        ) : (
                          <>
                            <Mic className="h-6 w-6 mr-2" />
                            Start Voice Command
                          </>
                        )}
                      </Button>
                      <p className="text-sm text-gray-600 mt-2">
                        {isRecording ? "Listening... Speak your task requirements" : "Click to start voice command"}
                      </p>
                    </div>
                  )}
                  
                  {/* Voice Input Examples */}
                  <div className="bg-white p-3 rounded-lg border border-emerald-200">
                    <p className="text-sm font-medium text-gray-700 mb-2">Example voice commands:</p>
                    <ul className="text-xs text-gray-600 space-y-1">
                      <li>• "Visit Mr. Sharma tomorrow 3 PM for balcony proposal"</li>
                      <li>• "Call Priya regarding garden design by Friday"</li>
                      <li>• "Send catalog to new leads from this week"</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>

              {/* AI Insights Panel */}
              <Card className="bg-white border-emerald-200 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-emerald-800 flex items-center">
                    <Lightbulb className="h-5 w-5 mr-2" />
                    AI Business Insights
                  </CardTitle>
                  <CardDescription>
                    Get intelligent recommendations and performance alerts
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Button 
                      onClick={() => generateAIInsights("leads")}
                      size="sm"
                      variant="outline"
                      className="border-emerald-300 hover:bg-emerald-50"
                    >
                      Lead Insights
                    </Button>
                    <Button 
                      onClick={() => generateAIInsights("performance")}
                      size="sm"
                      variant="outline"
                      className="border-emerald-300 hover:bg-emerald-50"
                    >
                      Performance
                    </Button>
                    <Button 
                      onClick={() => generateAIInsights("opportunities")}
                      size="sm"
                      variant="outline"
                      className="border-emerald-300 hover:bg-emerald-50"
                    >
                      Opportunities
                    </Button>
                  </div>
                  
                  {aiInsights.length > 0 && (
                    <div className="bg-emerald-50 p-4 rounded-lg border border-emerald-200">
                      <h4 className="font-medium text-emerald-800 mb-2">Latest AI Insights:</h4>
                      <ul className="space-y-2">
                        {aiInsights.slice(0, 3).map((insight, index) => (
                          <li key={index} className="text-sm text-emerald-700 flex items-start">
                            <Bot className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                            {insight}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {aiInsights.length === 0 && (
                    <div className="text-center py-6 text-gray-500">
                      <Brain className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                      <p className="text-sm">Click a button above to generate AI insights</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Content Generation Panel */}
              <Card className="bg-white border-emerald-200 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-emerald-800 flex items-center">
                    <Sparkles className="h-5 w-5 mr-2" />
                    AI Content Generator
                  </CardTitle>
                  <CardDescription>
                    Create marketing content, social posts, and advertisements
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2 flex-wrap">
                    <Button 
                      onClick={() => generateContent("social_post")}
                      size="sm"
                      variant="outline"
                      className="border-emerald-300 hover:bg-emerald-50"
                    >
                      Social Post
                    </Button>
                    <Button 
                      onClick={() => generateContent("retail_promotion")}
                      size="sm"
                      variant="outline"
                      className="border-emerald-300 hover:bg-emerald-50"
                    >
                      Store Promotion
                    </Button>
                    <Button 
                      onClick={() => generateContent("google_ads")}
                      size="sm"
                      variant="outline"
                      className="border-emerald-300 hover:bg-emerald-50"
                    >
                      Google Ads
                    </Button>
                    <Button 
                      onClick={() => generateContent("strategic_plan")}
                      size="sm"
                      variant="outline"
                      className="border-emerald-300 hover:bg-emerald-50"
                    >
                      Strategic Plan
                    </Button>
                    <Button 
                      onClick={() => generateContent("online_presence")}
                      size="sm"
                      variant="outline"
                      className="border-emerald-300 hover:bg-emerald-50"
                    >
                      Online Presence
                    </Button>
                    <Button 
                      onClick={() => generateContent("offline_marketing")}
                      size="sm"
                      variant="outline"
                      className="border-emerald-300 hover:bg-emerald-50"
                    >
                      Offline Marketing
                    </Button>
                  </div>
                  
                  {generatedContent && (
                    <div className="bg-emerald-50 p-4 rounded-lg border border-emerald-200 max-h-60 overflow-y-auto">
                      <h4 className="font-medium text-emerald-800 mb-2">Generated Content:</h4>
                      <div className="text-sm text-emerald-700 whitespace-pre-wrap">
                        {generatedContent}
                      </div>
                      <Button 
                        onClick={() => navigator.clipboard.writeText(generatedContent)}
                        size="sm"
                        variant="outline"
                        className="mt-2 border-emerald-300 hover:bg-emerald-100"
                      >
                        Copy to Clipboard
                      </Button>
                    </div>
                  )}
                  
                  {!generatedContent && (
                    <div className="text-center py-6 text-gray-500">
                      <Sparkles className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                      <p className="text-sm">Select a content type to generate AI content</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* AI Model Status Panel */}
              <Card className="bg-white border-emerald-200 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-emerald-800 flex items-center">
                    <Zap className="h-5 w-5 mr-2" />
                    AI System Status
                  </CardTitle>
                  <CardDescription>
                    Hybrid AI orchestration with multiple models
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                      <div>
                        <p className="font-medium text-green-800">GPT-5 (Primary)</p>
                        <p className="text-xs text-green-600">Task automation & workflows</p>
                      </div>
                      <Badge className="bg-green-100 text-green-800">Active</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <div>
                        <p className="font-medium text-blue-800">Claude Sonnet 4</p>
                        <p className="text-xs text-blue-600">Memory & context layer</p>
                      </div>
                      <Badge className="bg-blue-100 text-blue-800">Active</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg border border-purple-200">
                      <div>
                        <p className="font-medium text-purple-800">Gemini 2.0 Flash</p>
                        <p className="text-xs text-purple-600">Multimodal & creative</p>
                      </div>
                      <Badge className="bg-purple-100 text-purple-800">Active</Badge>
                    </div>
                  </div>
                  
                  <div className="pt-2 border-t border-gray-200">
                    <p className="text-xs text-gray-600 text-center">
                      🚀 Automatic task routing for optimal performance
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Admin Panel Tab */}
          <TabsContent value="admin" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                <Settings className="h-8 w-8 mr-3 text-emerald-600" />
                Super Admin Panel
              </h2>
              <Badge className="bg-red-100 text-red-800 border-red-300">
                Full Access Mode
              </Badge>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Category Management */}
              <Card className="bg-white border-emerald-200 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-emerald-800 flex items-center">
                    <Edit className="h-5 w-5 mr-2" />
                    Lead Categories Management
                  </CardTitle>
                  <CardDescription>
                    Add, edit, or delete lead categories for better organization
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Add New Category */}
                  <div className="flex gap-2">
                    <Input
                      placeholder="Enter new category name"
                      value={newCustomCategory}
                      onChange={(e) => setNewCustomCategory(e.target.value)}
                      className="flex-1"
                    />
                    <Button 
                      onClick={addCustomCategory}
                      className="bg-emerald-600 hover:bg-emerald-700"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Add
                    </Button>
                  </div>

                  {/* Default Categories */}
                  <div>
                    <Label className="text-sm font-medium text-gray-700 mb-2 block">Default Categories:</Label>
                    <div className="bg-gray-50 p-3 rounded-lg max-h-40 overflow-y-auto">
                      <div className="grid grid-cols-1 gap-1">
                        {LEAD_CATEGORIES.map((category) => (
                          <div key={category} className="text-sm text-gray-600 px-2 py-1 bg-white rounded border">
                            {category}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Custom Categories */}
                  {customCategories.length > 0 && (
                    <div>
                      <Label className="text-sm font-medium text-emerald-700 mb-2 block">Custom Categories:</Label>
                      <div className="space-y-2">
                        {customCategories.map((category) => (
                          <div key={category} className="flex items-center justify-between p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                            <span className="font-medium text-emerald-800">{category}</span>
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                className="border-emerald-300 hover:bg-emerald-100"
                              >
                                <Edit className="h-3 w-3" />
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => deleteCustomCategory(category)}
                                className="border-red-300 hover:bg-red-100 text-red-600"
                              >
                                <Trash2 className="h-3 w-3" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* System Statistics */}
              <Card className="bg-white border-emerald-200 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-emerald-800 flex items-center">
                    <TrendingUp className="h-5 w-5 mr-2" />
                    System Statistics
                  </CardTitle>
                  <CardDescription>
                    Comprehensive system performance metrics
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {dashboardStats && (
                    <div className="space-y-3">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-blue-50 p-3 rounded-lg">
                          <p className="text-sm text-blue-600">Total Records</p>
                          <p className="text-2xl font-bold text-blue-800">{dashboardStats.total_leads + (dashboardStats.pending_tasks || 0)}</p>
                        </div>
                        <div className="bg-green-50 p-3 rounded-lg">
                          <p className="text-sm text-green-600">Conversion Rate</p>
                          <p className="text-2xl font-bold text-green-800">{dashboardStats.conversion_rate}%</p>
                        </div>
                      </div>

                      <div className="bg-emerald-50 p-4 rounded-lg border border-emerald-200">
                        <h4 className="font-medium text-emerald-800 mb-2">Lead Sources Analysis</h4>
                        <div className="space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-emerald-700">Website Sources</span>
                            <span className="text-sm font-medium text-emerald-800">45%</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-emerald-700">Referrals</span>
                            <span className="text-sm font-medium text-emerald-800">30%</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-emerald-700">Social Media</span>
                            <span className="text-sm font-medium text-emerald-800">25%</span>
                          </div>
                        </div>
                      </div>

                      <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                        <h4 className="font-medium text-purple-800 mb-2">AI System Status</h4>
                        <div className="space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-purple-700">AI Tasks Generated</span>
                            <span className="text-sm font-medium text-purple-800">{dashboardStats.ai_tasks_generated || 0}</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-purple-700">Models Active</span>
                            <Badge className="bg-purple-100 text-purple-800">3 Models</Badge>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* User Management */}
              <Card className="bg-white border-emerald-200 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-emerald-800 flex items-center">
                    <Users className="h-5 w-5 mr-2" />
                    User & Role Management
                  </CardTitle>
                  <CardDescription>
                    Manage user access and permissions
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                      <div>
                        <p className="font-medium text-emerald-800">Super Admin</p>
                        <p className="text-xs text-emerald-600">Full system access</p>
                      </div>
                      <Badge className="bg-emerald-100 text-emerald-800">You</Badge>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <div>
                        <p className="font-medium text-blue-800">Sales Manager</p>
                        <p className="text-xs text-blue-600">Lead & task management</p>
                      </div>
                      <Badge className="bg-blue-100 text-blue-800">Active</Badge>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
                      <div>
                        <p className="font-medium text-gray-800">Sales Executive</p>
                        <p className="text-xs text-gray-600">Lead entry & follow-up</p>
                      </div>
                      <Badge className="bg-gray-100 text-gray-800">Pending</Badge>
                    </div>
                  </div>

                  <Button className="w-full bg-emerald-600 hover:bg-emerald-700 text-white">
                    <Plus className="h-4 w-4 mr-2" />
                    Add New User
                  </Button>
                </CardContent>
              </Card>

              {/* System Configuration */}
              <Card className="bg-white border-emerald-200 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-emerald-800 flex items-center">
                    <Settings className="h-5 w-5 mr-2" />
                    System Configuration
                  </CardTitle>
                  <CardDescription>
                    Configure system settings and integrations
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                      <div>
                        <p className="font-medium text-green-800">Telephony (Twilio)</p>
                        <p className="text-xs text-green-600">8447475761 - Active</p>
                      </div>
                      <Badge className="bg-green-100 text-green-800">Connected</Badge>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                      <div>
                        <p className="font-medium text-green-800">WhatsApp Business</p>
                        <p className="text-xs text-green-600">360 Dialog Integration</p>
                      </div>
                      <Badge className="bg-green-100 text-green-800">Connected</Badge>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                      <div>
                        <p className="font-medium text-green-800">AI Models</p>
                        <p className="text-xs text-green-600">GPT-5 + Claude + Gemini</p>
                      </div>
                      <Badge className="bg-green-100 text-green-800">Active</Badge>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                      <div>
                        <p className="font-medium text-yellow-800">Database Backup</p>
                        <p className="text-xs text-yellow-600">Last backup: 2 hours ago</p>
                      </div>
                      <Badge className="bg-yellow-100 text-yellow-800">Scheduled</Badge>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <Button variant="outline" className="border-emerald-300 hover:bg-emerald-50">
                      <Settings className="h-4 w-4 mr-2" />
                      Configure
                    </Button>
                    <Button variant="outline" className="border-emerald-300 hover:bg-emerald-50">
                      Backup Now
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>
      
      <Toaster />
    </div>
  );
};

export default App;