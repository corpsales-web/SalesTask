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
  Zap
} from "lucide-react";

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
  const mediaRecorder = useRef(null);
  const { toast } = useToast();

  // Form states
  const [newLead, setNewLead] = useState({
    name: "",
    phone: "",
    email: "",
    budget: "",
    space_size: "",
    location: "",
    notes: "",
    tags: "",
    assigned_to: ""
  });

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

  // Create lead function
  const createLead = async (e) => {
    e.preventDefault();
    try {
      const leadData = {
        ...newLead,
        budget: newLead.budget ? parseFloat(newLead.budget) : null,
        tags: Array.isArray(newLead.tags) ? newLead.tags : newLead.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      };
      
      await axios.post(`${API}/leads`, leadData);
      toast({
        title: "Success",
        description: "Lead created successfully"
      });
      
      setNewLead({
        name: "",
        phone: "",
        email: "",
        budget: "",
        space_size: "",
        location: "",
        notes: "",
        tags: "",
        assigned_to: ""
      });
      
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
          <TabsList className="grid w-full grid-cols-4 bg-white shadow-sm border border-emerald-100">
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
                <DialogContent className="max-w-md">
                  <DialogHeader>
                    <DialogTitle>Add New Lead</DialogTitle>
                    <DialogDescription>Create a new lead for potential customers</DialogDescription>
                  </DialogHeader>
                  <form onSubmit={createLead} className="space-y-4">
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
                    <div>
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        value={newLead.email}
                        onChange={(e) => setNewLead({...newLead, email: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="budget">Budget (₹)</Label>
                      <Input
                        id="budget"
                        type="number"
                        value={newLead.budget}
                        onChange={(e) => setNewLead({...newLead, budget: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="location">Location</Label>
                      <Input
                        id="location"
                        value={newLead.location}
                        onChange={(e) => setNewLead({...newLead, location: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="notes">Notes</Label>
                      <Textarea
                        id="notes"
                        value={newLead.notes}
                        onChange={(e) => setNewLead({...newLead, notes: e.target.value})}
                        rows={3}
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
        </Tabs>
      </main>
      
      <Toaster />
    </div>
  );
};

export default App;