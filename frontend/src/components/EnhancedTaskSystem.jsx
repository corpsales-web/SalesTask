import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Progress } from './ui/progress';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Separator } from './ui/separator';
import { 
  CheckCircle, Clock, AlertCircle, Users, MessageSquare, Calendar, 
  Plus, Edit, Trash2, Share, Bell, Filter, Search, MoreHorizontal,
  Zap, Brain, Target, TrendingUp, Link, FileText, Image, 
  Play, Pause, RotateCcw, Send, Tag, Flag, ArrowRight, ArrowUp,
  Mic, MicOff, Bot, User, CheckCircle2, XCircle, PlayCircle
} from 'lucide-react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const EnhancedTaskSystem = () => {
  // State Management
  const [activeView, setActiveView] = useState('board');
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(false);

  // Modal States
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [showWorkflowModal, setShowWorkflowModal] = useState(false);
  const [showCollaborationModal, setShowCollaborationModal] = useState(false);
  const [showVoiceModal, setShowVoiceModal] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);

  // Voice Recording State
  const [isRecording, setIsRecording] = useState(false);
  const [recordedAudio, setRecordedAudio] = useState(null);
  const [transcription, setTranscription] = useState('');

  // Form States
  const [taskForm, setTaskForm] = useState({
    title: '',
    description: '',
    priority: 'medium',
    status: 'todo',
    assigned_to: [],
    due_date: '',
    project_id: '',
    tags: [],
    dependencies: [],
    estimated_hours: '',
    ai_automation: false
  });

  const [workflowForm, setWorkflowForm] = useState({
    name: '',
    trigger: 'manual',
    conditions: [],
    actions: [],
    is_active: true
  });

  // Filters
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    assigned_to: 'all',
    project: 'all',
    search: ''
  });

  // Initialize data
  useEffect(() => {
    initializeTaskSystem();
  }, []);

  const initializeTaskSystem = async () => {
    setLoading(true);
    try {
      // Mock data initialization
      setUsers([
        { id: '1', name: 'Rajesh Kumar', email: 'rajesh@aavanagreens.com', avatar: '', role: 'Sales Executive' },
        { id: '2', name: 'Priya Sharma', email: 'priya@aavanagreens.com', avatar: '', role: 'Marketing Manager' },
        { id: '3', name: 'Amit Patel', email: 'amit@aavanagreens.com', avatar: '', role: 'Field Executive' },
        { id: '4', name: 'Sneha Verma', email: 'sneha@aavanagreens.com', avatar: '', role: 'HR Assistant' }
      ]);

      setProjects([
        { id: '1', name: 'Green Building Consultancy', color: '#10b981', status: 'active' },
        { id: '2', name: 'Balcony Garden Solutions', color: '#3b82f6', status: 'active' },
        { id: '3', name: 'Corporate Landscaping', color: '#8b5cf6', status: 'active' },
        { id: '4', name: 'Urban Farming Initiative', color: '#f59e0b', status: 'planning' }
      ]);

      setTasks([
        {
          id: '1',
          title: 'Follow up with Rajesh Kumar lead',
          description: 'Call regarding balcony garden consultation',
          priority: 'high',
          status: 'in_progress',
          assigned_to: ['1'],
          due_date: '2024-01-20',
          project_id: '2',
          tags: ['follow-up', 'consultation'],
          progress: 60,
          estimated_hours: 2,
          actual_hours: 1.2,
          ai_generated: true,
          dependencies: [],
          comments: [
            { id: '1', user_id: '1', user_name: 'Rajesh Kumar', message: 'Initial call completed, scheduling site visit', timestamp: '2024-01-15T10:30:00Z' }
          ],
          attachments: []
        },
        {
          id: '2',
          title: 'Prepare proposal for Mumbai client',
          description: 'Create detailed proposal for 3 BHK balcony transformation',
          priority: 'medium',
          status: 'todo',
          assigned_to: ['2', '3'],
          due_date: '2024-01-25',
          project_id: '2',
          tags: ['proposal', 'mumbai'],
          progress: 0,
          estimated_hours: 4,
          actual_hours: 0,
          ai_generated: false,
          dependencies: ['1'],
          comments: [],
          attachments: []
        },
        {
          id: '3',
          title: 'Site visit for corporate office',
          description: 'Assess rooftop garden potential for IT company',
          priority: 'high',
          status: 'review',
          assigned_to: ['3'],
          due_date: '2024-01-18',
          project_id: '3',
          tags: ['site-visit', 'corporate'],
          progress: 90,
          estimated_hours: 3,
          actual_hours: 2.8,
          ai_generated: false,
          dependencies: [],
          comments: [
            { id: '2', user_id: '3', user_name: 'Amit Patel', message: 'Site assessment completed, preparing report', timestamp: '2024-01-16T14:15:00Z' }
          ],
          attachments: [
            { id: '1', name: 'site_photos.zip', type: 'image', size: '2.4 MB' }
          ]
        }
      ]);

      setWorkflows([
        {
          id: '1',
          name: 'Lead Follow-up Automation',
          trigger: 'new_lead',
          conditions: [{ field: 'lead_source', operator: 'equals', value: 'website' }],
          actions: [
            { type: 'create_task', template: 'initial_call', assignee: 'auto' },
            { type: 'send_email', template: 'welcome_email' },
            { type: 'schedule_reminder', delay: '24_hours' }
          ],
          is_active: true,
          created_by: '2'
        },
        {
          id: '2',
          name: 'Task Escalation',
          trigger: 'task_overdue',
          conditions: [{ field: 'priority', operator: 'equals', value: 'high' }],
          actions: [
            { type: 'notify_manager', message: 'High priority task overdue' },
            { type: 'reassign_task', to: 'manager' }
          ],
          is_active: true,
          created_by: '4'
        }
      ]);

    } catch (error) {
      console.error('Task system initialization error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Task Management Functions
  const createTask = async () => {
    setLoading(true);
    try {
      const newTask = {
        id: Date.now().toString(),
        ...taskForm,
        progress: 0,
        actual_hours: 0,
        ai_generated: taskForm.ai_automation,
        comments: [],
        attachments: [],
        created_at: new Date().toISOString(),
        created_by: '1' // Current user
      };

      setTasks(prev => [...prev, newTask]);
      setShowTaskModal(false);
      resetTaskForm();

      // If AI automation is enabled, create automated workflow
      if (taskForm.ai_automation) {
        await createAIWorkflow(newTask);
      }

    } catch (error) {
      console.error('Task creation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateTaskStatus = async (taskId, newStatus) => {
    setTasks(prev => prev.map(task => 
      task.id === taskId ? { 
        ...task, 
        status: newStatus,
        progress: newStatus === 'completed' ? 100 : task.progress
      } : task
    ));
  };

  const updateTaskProgress = async (taskId, progress) => {
    setTasks(prev => prev.map(task => 
      task.id === taskId ? { ...task, progress } : task
    ));
  };

  const addTaskComment = async (taskId, comment) => {
    const newComment = {
      id: Date.now().toString(),
      user_id: '1', // Current user
      user_name: users.find(u => u.id === '1')?.name || 'Unknown',
      message: comment,
      timestamp: new Date().toISOString()
    };

    setTasks(prev => prev.map(task => 
      task.id === taskId ? { 
        ...task, 
        comments: [...task.comments, newComment]
      } : task
    ));
  };

  const createAIWorkflow = async (task) => {
    try {
      // AI-powered workflow creation
      const aiWorkflow = {
        id: Date.now().toString(),
        name: `AI Workflow for ${task.title}`,
        trigger: 'task_created',
        conditions: [{ field: 'task_id', operator: 'equals', value: task.id }],
        actions: [
          { type: 'analyze_task', ai_model: 'gpt-5' },
          { type: 'suggest_dependencies' },
          { type: 'estimate_completion_time' },
          { type: 'recommend_resources' }
        ],
        is_active: true,
        ai_generated: true,
        created_by: 'ai_system'
      };

      setWorkflows(prev => [...prev, aiWorkflow]);
    } catch (error) {
      console.error('AI workflow creation error:', error);
    }
  };

  // Voice-to-Task Integration
  const startVoiceRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const audioChunks = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        setRecordedAudio(audioBlob);
        
        // Process voice-to-task conversion
        await processVoiceToTask(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
      
      // Auto-stop after 30 seconds
      setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
          mediaRecorder.stop();
          setIsRecording(false);
        }
      }, 30000);

    } catch (error) {
      console.error('Voice recording error:', error);
      alert('Unable to access microphone. Please check permissions.');
    }
  };

  const stopVoiceRecording = () => {
    setIsRecording(false);
  };

  const processVoiceToTask = async (audioBlob) => {
    try {
      setLoading(true);
      
      // Mock AI processing (replace with actual API call)
      const mockTranscription = "Create a follow-up task for the Mumbai client regarding their balcony garden project. High priority, due next week.";
      setTranscription(mockTranscription);

      // AI-powered task extraction
      const extractedTask = {
        title: "Follow-up: Mumbai client balcony garden",
        description: "Follow up regarding balcony garden project requirements and scheduling",
        priority: "high",
        due_date: getNextWeekDate(),
        tags: ["follow-up", "mumbai", "balcony-garden"],
        ai_generated: true
      };

      // Pre-fill task form
      setTaskForm(prev => ({
        ...prev,
        ...extractedTask
      }));

    } catch (error) {
      console.error('Voice processing error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getNextWeekDate = () => {
    const date = new Date();
    date.setDate(date.getDate() + 7);
    return date.toISOString().split('T')[0];
  };

  // Collaboration Features
  const shareTask = async (taskId) => {
    try {
      const task = tasks.find(t => t.id === taskId);
      if (!task) return;

      // Mock sharing functionality
      const shareLink = `${window.location.origin}/tasks/${taskId}`;
      await navigator.clipboard.writeText(shareLink);
      alert('Task link copied to clipboard!');
    } catch (error) {
      console.error('Task sharing error:', error);
    }
  };

  const assignTaskToUsers = async (taskId, userIds) => {
    setTasks(prev => prev.map(task => 
      task.id === taskId ? { ...task, assigned_to: userIds } : task
    ));

    // Send notifications to assigned users
    userIds.forEach(userId => {
      sendNotification(userId, `You have been assigned to task: ${tasks.find(t => t.id === taskId)?.title}`);
    });
  };

  const sendNotification = (userId, message) => {
    // Mock notification system
    console.log(`Notification to user ${userId}: ${message}`);
  };

  // Utility Functions
  const resetTaskForm = () => {
    setTaskForm({
      title: '',
      description: '',
      priority: 'medium',
      status: 'todo',
      assigned_to: [],
      due_date: '',
      project_id: '',
      tags: [],
      dependencies: [],
      estimated_hours: '',
      ai_automation: false
    });
  };

  const getFilteredTasks = () => {
    return tasks.filter(task => {
      const matchesStatus = filters.status === 'all' || task.status === filters.status;
      const matchesPriority = filters.priority === 'all' || task.priority === filters.priority;
      const matchesAssignee = filters.assigned_to === 'all' || task.assigned_to.includes(filters.assigned_to);
      const matchesProject = filters.project === 'all' || task.project_id === filters.project;
      const matchesSearch = !filters.search || 
        task.title.toLowerCase().includes(filters.search.toLowerCase()) ||
        task.description.toLowerCase().includes(filters.search.toLowerCase());

      return matchesStatus && matchesPriority && matchesAssignee && matchesProject && matchesSearch;
    });
  };

  const getTasksByStatus = (status) => {
    return getFilteredTasks().filter(task => task.status === status);
  };

  // Render Functions
  const renderTaskBoard = () => {
    const statuses = [
      { key: 'todo', title: 'To Do', color: 'bg-gray-100' },
      { key: 'in_progress', title: 'In Progress', color: 'bg-blue-100' },
      { key: 'review', title: 'Review', color: 'bg-yellow-100' },
      { key: 'completed', title: 'Completed', color: 'bg-green-100' }
    ];

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statuses.map((status) => (
          <div key={status.key} className={`${status.color} p-4 rounded-lg`}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-semibold text-gray-800">{status.title}</h3>
              <Badge variant="outline">
                {getTasksByStatus(status.key).length}
              </Badge>
            </div>
            
            <div className="space-y-3">
              {getTasksByStatus(status.key).map((task) => (
                <Card key={task.id} className="bg-white shadow-sm hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-sm">{task.title}</h4>
                      <Badge className={
                        task.priority === 'high' ? 'bg-red-100 text-red-800' :
                        task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }>
                        {task.priority}
                      </Badge>
                    </div>
                    
                    <p className="text-xs text-gray-600 mb-3 line-clamp-2">
                      {task.description}
                    </p>
                    
                    {task.progress > 0 && (
                      <div className="mb-3">
                        <Progress value={task.progress} className="h-2" />
                        <p className="text-xs text-gray-500 mt-1">{task.progress}% complete</p>
                      </div>
                    )}
                    
                    <div className="flex justify-between items-center">
                      <div className="flex -space-x-2">
                        {task.assigned_to.slice(0, 3).map((userId) => {
                          const user = users.find(u => u.id === userId);
                          return (
                            <Avatar key={userId} className="h-6 w-6 border-2 border-white">
                              <AvatarFallback className="text-xs">
                                {user?.name.charAt(0) || '?'}
                              </AvatarFallback>
                            </Avatar>
                          );
                        })}
                        {task.assigned_to.length > 3 && (
                          <div className="h-6 w-6 rounded-full bg-gray-200 border-2 border-white flex items-center justify-center">
                            <span className="text-xs">+{task.assigned_to.length - 3}</span>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex space-x-1">
                        {task.ai_generated && (
                          <Bot className="h-4 w-4 text-purple-500" title="AI Generated" />
                        )}
                        {task.comments.length > 0 && (
                          <MessageSquare className="h-4 w-4 text-blue-500" title="Has Comments" />
                        )}
                        {task.attachments.length > 0 && (
                          <FileText className="h-4 w-4 text-green-500" title="Has Attachments" />
                        )}
                      </div>
                    </div>
                    
                    <div className="flex justify-between items-center mt-3 pt-2 border-t">
                      <span className="text-xs text-gray-500">
                        Due: {new Date(task.due_date).toLocaleDateString()}
                      </span>
                      <div className="flex space-x-1">
                        <Button size="sm" variant="ghost" onClick={() => setSelectedTask(task)}>
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="ghost" onClick={() => shareTask(task.id)}>
                          <Share className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderTaskList = () => (
    <Card className="bg-white shadow-lg">
      <CardHeader>
        <CardTitle>All Tasks</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b">
                <th className="text-left p-3">Task</th>
                <th className="text-left p-3">Status</th>
                <th className="text-left p-3">Priority</th>
                <th className="text-left p-3">Assigned To</th>
                <th className="text-left p-3">Due Date</th>
                <th className="text-left p-3">Progress</th>
                <th className="text-left p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {getFilteredTasks().map((task) => (
                <tr key={task.id} className="border-b hover:bg-gray-50">
                  <td className="p-3">
                    <div>
                      <div className="font-medium">{task.title}</div>
                      <div className="text-sm text-gray-600 line-clamp-1">{task.description}</div>
                    </div>
                  </td>
                  <td className="p-3">
                    <Badge className={
                      task.status === 'completed' ? 'bg-green-100 text-green-800' :
                      task.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                      task.status === 'review' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }>
                      {task.status.replace('_', ' ')}
                    </Badge>
                  </td>
                  <td className="p-3">
                    <Badge className={
                      task.priority === 'high' ? 'bg-red-100 text-red-800' :
                      task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }>
                      {task.priority}
                    </Badge>
                  </td>
                  <td className="p-3">
                    <div className="flex -space-x-1">
                      {task.assigned_to.slice(0, 2).map((userId) => {
                        const user = users.find(u => u.id === userId);
                        return (
                          <Avatar key={userId} className="h-6 w-6 border-2 border-white">
                            <AvatarFallback className="text-xs">
                              {user?.name.charAt(0) || '?'}
                            </AvatarFallback>
                          </Avatar>
                        );
                      })}
                      {task.assigned_to.length > 2 && (
                        <span className="text-xs text-gray-500 ml-2">
                          +{task.assigned_to.length - 2}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="p-3 text-sm">
                    {new Date(task.due_date).toLocaleDateString()}
                  </td>
                  <td className="p-3">
                    <div className="flex items-center space-x-2">
                      <Progress value={task.progress} className="w-16 h-2" />
                      <span className="text-xs">{task.progress}%</span>
                    </div>
                  </td>
                  <td className="p-3">
                    <div className="flex space-x-1">
                      <Button size="sm" variant="ghost" onClick={() => setSelectedTask(task)}>
                        <Edit className="h-3 w-3" />
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => shareTask(task.id)}>
                        <Share className="h-3 w-3" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      {/* Header with Actions */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Enhanced Task Management</h2>
          <p className="text-gray-600">Collaborative task management with AI automation</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={() => {
            console.log('🔧 Workflow button clicked');
            setShowWorkflowModal(true);
          }}>
            <Zap className="h-4 w-4 mr-2" />
            Workflow
          </Button>
          <Button onClick={() => setShowTaskModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Create New Task
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="bg-white shadow-sm">
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center space-x-2">
              <Search className="h-4 w-4 text-gray-500" />
              <Input 
                placeholder="Search tasks..."
                value={filters.search}
                onChange={(e) => setFilters({...filters, search: e.target.value})}
                className="w-48"
              />
            </div>
            
            <Select value={filters.status} onValueChange={(value) => setFilters({...filters, status: value})}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="todo">To Do</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="review">Review</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
              </SelectContent>
            </Select>

            <Select value={filters.priority} onValueChange={(value) => setFilters({...filters, priority: value})}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priority</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>

            <Select value={filters.assigned_to} onValueChange={(value) => setFilters({...filters, assigned_to: value})}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Assignees</SelectItem>
                {users.map((user) => (
                  <SelectItem key={user.id} value={user.id}>{user.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* View Toggle */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
        <Button
          variant={activeView === 'board' ? 'default' : 'ghost'}
          onClick={() => setActiveView('board')}
          size="sm"
        >
          Board View
        </Button>
        <Button
          variant={activeView === 'list' ? 'default' : 'ghost'}
          onClick={() => setActiveView('list')}
          size="sm"
        >
          List View
        </Button>
      </div>

      {/* Task Views */}
      {activeView === 'board' && renderTaskBoard()}
      {activeView === 'list' && renderTaskList()}

      {/* Task Creation Modal */}
      <Dialog open={showTaskModal} onOpenChange={setShowTaskModal}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New Task</DialogTitle>
            <DialogDescription>Add a new task with collaboration and AI features</DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label>Task Title</Label>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
                    className={`${isRecording ? 'bg-red-50 text-red-600 border-red-200' : ''}`}
                  >
                    <Mic className={`h-4 w-4 mr-1 ${isRecording ? 'animate-pulse' : ''}`} />
                    {isRecording ? 'Stop' : 'Voice'}
                  </Button>
                </div>
                <Input 
                  value={taskForm.title}
                  onChange={(e) => setTaskForm({...taskForm, title: e.target.value})}
                  placeholder="Enter task title or use voice input"
                />
                {transcription && (
                  <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded text-sm">
                    <div className="font-medium text-blue-800">Voice Input:</div>
                    <div className="text-blue-700">{transcription}</div>
                    <Button
                      type="button"
                      size="sm"
                      className="mt-2"
                      onClick={() => {
                        setTaskForm({...taskForm, title: transcription});
                        setTranscription('');
                      }}
                    >
                      Use This Text
                    </Button>
                  </div>
                )}
              </div>
              <div>
                <Label>Priority</Label>
                <Select value={taskForm.priority} onValueChange={(value) => setTaskForm({...taskForm, priority: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label>Description</Label>
              <Textarea 
                value={taskForm.description}
                onChange={(e) => setTaskForm({...taskForm, description: e.target.value})}
                placeholder="Describe the task..."
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Assign To</Label>
                <Select value={taskForm.assigned_to[0] || ''} onValueChange={(value) => setTaskForm({...taskForm, assigned_to: [value]})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select assignee" />
                  </SelectTrigger>
                  <SelectContent>
                    {users.map((user) => (
                      <SelectItem key={user.id} value={user.id}>{user.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Due Date</Label>
                <Input 
                  type="date"
                  value={taskForm.due_date}
                  onChange={(e) => setTaskForm({...taskForm, due_date: e.target.value})}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Project</Label>
                <Select value={taskForm.project_id} onValueChange={(value) => setTaskForm({...taskForm, project_id: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select project" />
                  </SelectTrigger>
                  <SelectContent>
                    {projects.map((project) => (
                      <SelectItem key={project.id} value={project.id}>{project.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Estimated Hours</Label>
                <Input 
                  type="number"
                  value={taskForm.estimated_hours}
                  onChange={(e) => setTaskForm({...taskForm, estimated_hours: e.target.value})}
                  placeholder="0"
                />
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <input 
                type="checkbox"
                id="ai_automation"
                checked={taskForm.ai_automation}
                onChange={(e) => setTaskForm({...taskForm, ai_automation: e.target.checked})}
              />
              <Label htmlFor="ai_automation" className="flex items-center">
                <Bot className="h-4 w-4 mr-2" />
                Enable AI Automation
              </Label>
            </div>

            <div className="flex space-x-2">
              <Button onClick={createTask} disabled={loading || !taskForm.title}>
                {loading ? 'Creating...' : 'Create Task'}
              </Button>
              <Button variant="outline" onClick={() => setShowTaskModal(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Voice Task Modal */}
      <Dialog open={showVoiceModal} onOpenChange={setShowVoiceModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Voice to Task</DialogTitle>
            <DialogDescription>Create tasks using voice commands</DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 text-center">
            {!isRecording && !transcription && (
              <div>
                <div className="mb-4">
                  <Mic className="h-16 w-16 mx-auto text-blue-500" />
                </div>
                <p className="text-gray-600 mb-4">Tap to start recording your task</p>
                <Button onClick={startVoiceRecording}>
                  <Mic className="h-4 w-4 mr-2" />
                  Start Recording
                </Button>
              </div>
            )}

            {isRecording && (
              <div>
                <div className="mb-4">
                  <div className="animate-pulse">
                    <MicOff className="h-16 w-16 mx-auto text-red-500" />
                  </div>
                </div>
                <p className="text-gray-600 mb-4">Recording... Speak your task details</p>
                <Button onClick={stopVoiceRecording} variant="outline">
                  <MicOff className="h-4 w-4 mr-2" />
                  Stop Recording
                </Button>
              </div>
            )}

            {transcription && (
              <div>
                <div className="mb-4">
                  <CheckCircle2 className="h-16 w-16 mx-auto text-green-500" />
                </div>
                <div className="bg-gray-50 p-4 rounded-lg mb-4">
                  <p className="text-sm text-gray-800">{transcription}</p>
                </div>
                <div className="flex space-x-2">
                  <Button onClick={() => {
                    setShowVoiceModal(false);
                    setShowTaskModal(true);
                  }}>
                    Create Task
                  </Button>
                  <Button variant="outline" onClick={() => {
                    setTranscription('');
                    setRecordedAudio(null);
                  }}>
                    Try Again
                  </Button>
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default EnhancedTaskSystem;