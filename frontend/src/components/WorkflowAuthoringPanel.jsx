import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { useToast } from '../hooks/use-toast';
import {
  Zap,
  Bot,
  Brain,
  MessageSquare,
  Clock,
  GitBranch,
  Users,
  Bell,
  Edit,
  Settings,
  Plus,
  Play,
  Pause,
  RotateCcw,
  Save,
  Upload,
  Download,
  Eye,
  Trash2,
  Copy,
  CheckCircle2,
  AlertCircle,
  Activity,
  BarChart3,
  TestTube,
  Lightbulb,
  Sparkles,
  ArrowRight,
  ArrowDown,
  Filter,
  Search,
  Calendar,
  Target,
  Send,
  Timer,
  Globe
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const WorkflowAuthoringPanel = ({ isVisible }) => {
  const { toast } = useToast();
  const [workflows, setWorkflows] = useState([]);
  const [promptTemplates, setPromptTemplates] = useState([]);
  const [testResults, setTestResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [activeTab, setActiveTab] = useState('workflows');
  const [newWorkflow, setNewWorkflow] = useState({
    name: '',
    description: '',
    category: 'lead_nurturing',
    trigger_conditions: {},
    steps: [],
    global_variables: {},
    settings: {
      auto_assign: false,
      send_notifications: true,
      max_execution_time: 3600,
      retry_on_failure: true
    },
    tags: [],
    is_active: false
  });
  const [newPromptTemplate, setNewPromptTemplate] = useState({
    name: '',
    description: '',
    category: 'general',
    system_prompt: '',
    user_prompt_template: '',
    variables: [],
    ai_model: 'gpt-5',
    temperature: 0.7,
    max_tokens: 1000,
    tags: [],
    is_active: true
  });

  const stepTypes = [
    { value: 'ai_response', label: 'AI Response', icon: <Bot className="h-4 w-4" />, description: 'Generate AI-powered response' },
    { value: 'send_message', label: 'Send Message', icon: <Send className="h-4 w-4" />, description: 'Send automated message' },
    { value: 'wait_for_response', label: 'Wait for Response', icon: <Timer className="h-4 w-4" />, description: 'Wait for user response' },
    { value: 'conditional', label: 'Conditional Logic', icon: <GitBranch className="h-4 w-4" />, description: 'Branch based on conditions' },
    { value: 'assign_agent', label: 'Assign Agent', icon: <Users className="h-4 w-4" />, description: 'Assign to agent or team' },
    { value: 'schedule_followup', label: 'Schedule Follow-up', icon: <Calendar className="h-4 w-4" />, description: 'Schedule future action' },
    { value: 'update_lead', label: 'Update Lead', icon: <Edit className="h-4 w-4" />, description: 'Update lead information' },
    { value: 'trigger_notification', label: 'Send Notification', icon: <Bell className="h-4 w-4" />, description: 'Notify agent or manager' }
  ];

  const aiModels = [
    { value: 'gpt-5', label: 'GPT-5', provider: 'OpenAI' },
    { value: 'claude-sonnet-4', label: 'Claude Sonnet 4', provider: 'Anthropic' },
    { value: 'gemini-2.5-pro', label: 'Gemini 2.5 Pro', provider: 'Google' }
  ];

  const workflowCategories = [
    { value: 'lead_nurturing', label: 'Lead Nurturing' },
    { value: 'sales', label: 'Sales Process' },
    { value: 'support', label: 'Customer Support' },
    { value: 'onboarding', label: 'Onboarding' },
    { value: 'follow_up', label: 'Follow-up' },
    { value: 'qualification', label: 'Lead Qualification' }
  ];

  useEffect(() => {
    if (isVisible) {
      loadWorkflowData();
    }
  }, [isVisible]);

  const loadWorkflowData = async () => {
    setLoading(true);
    try {
      // Load workflows
      const workflowsResponse = await fetch(`${BACKEND_URL}/api/workflows`);
      if (workflowsResponse.ok) {
        const workflowsData = await workflowsResponse.json();
        setWorkflows(workflowsData.workflows || []);
      }

      // Load prompt templates
      const templatesResponse = await fetch(`${BACKEND_URL}/api/workflows/prompt-templates`);
      if (templatesResponse.ok) {
        const templatesData = await templatesResponse.json();
        setPromptTemplates(templatesData.templates || []);
      }

      // Mock test results
      setTestResults([
        {
          id: '1',
          workflow_name: 'WhatsApp Welcome Sequence',
          test_variables: { lead_name: 'Rajesh Kumar', budget: '₹75,000' },
          success: true,
          duration: 4.2,
          ai_calls: 3,
          tokens_used: 1250,
          tested_at: new Date(Date.now() - 2 * 60 * 60 * 1000)
        },
        {
          id: '2',
          workflow_name: 'High-Value Lead Follow-up',
          test_variables: { lead_name: 'Priya Sharma', budget: '₹2,50,000' },
          success: true,
          duration: 6.8,
          ai_calls: 5,
          tokens_used: 2100,
          tested_at: new Date(Date.now() - 4 * 60 * 60 * 1000)
        }
      ]);

    } catch (error) {
      console.error('Error loading workflow data:', error);
      toast({
        title: "Error Loading Data",
        description: "Failed to load workflow data.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const createPromptTemplate = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${BACKEND_URL}/api/workflows/prompt-templates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newPromptTemplate)
      });

      if (response.ok) {
        const result = await response.json();
        
        const createdTemplate = {
          id: result.template_id,
          ...newPromptTemplate,
          created_at: new Date(),
          updated_at: new Date()
        };
        
        setPromptTemplates(prev => [...prev, createdTemplate]);
        
        // Reset form
        setNewPromptTemplate({
          name: '',
          description: '',
          category: 'general',
          system_prompt: '',
          user_prompt_template: '',
          variables: [],
          ai_model: 'gpt-5',
          temperature: 0.7,
          max_tokens: 1000,
          tags: [],
          is_active: true
        });

        toast({
          title: "Template Created",
          description: `Prompt template "${createdTemplate.name}" has been created successfully.`,
        });

      } else {
        throw new Error('Failed to create prompt template');
      }

    } catch (error) {
      console.error('Error creating prompt template:', error);
      toast({
        title: "Error",
        description: "Failed to create prompt template.",
        variant: "destructive",
      });
    }
  };

  const testPromptTemplate = async (templateId, testVariables) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/workflows/prompt-templates/${templateId}/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ variables: testVariables })
      });

      if (response.ok) {
        const result = await response.json();
        
        toast({
          title: "Test Completed",
          description: `AI response generated successfully. Tokens used: ${result.tokens_used?.total_tokens || 0}`,
        });

        return result;
      } else {
        throw new Error('Failed to test prompt template');
      }

    } catch (error) {
      console.error('Error testing prompt template:', error);
      toast({
        title: "Test Failed",
        description: "Failed to test prompt template.",
        variant: "destructive",
      });
    }
  };

  const createWorkflow = async (e) => {
    e.preventDefault();
    try {
      if (!newWorkflow.name || newWorkflow.steps.length === 0) {
        toast({
          title: "Validation Error",
          description: "Please provide a name and at least one step.",
          variant: "destructive",
        });
        return;
      }

      const response = await fetch(`${BACKEND_URL}/api/workflows`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newWorkflow)
      });

      if (response.ok) {
        const result = await response.json();
        
        const createdWorkflow = {
          id: result.workflow_id,
          ...newWorkflow,
          created_at: new Date(),
          updated_at: new Date()
        };
        
        setWorkflows(prev => [...prev, createdWorkflow]);
        setSelectedWorkflow(null);
        
        // Reset form
        setNewWorkflow({
          name: '',
          description: '',
          category: 'lead_nurturing',
          trigger_conditions: {},
          steps: [],
          global_variables: {},
          settings: {
            auto_assign: false,
            send_notifications: true,
            max_execution_time: 3600,
            retry_on_failure: true
          },
          tags: [],
          is_active: false
        });

        toast({
          title: "Workflow Created",
          description: `Workflow "${createdWorkflow.name}" has been created successfully.`,
        });

      } else {
        throw new Error('Failed to create workflow');
      }

    } catch (error) {
      console.error('Error creating workflow:', error);
      toast({
        title: "Error",
        description: "Failed to create workflow.",
        variant: "destructive",
      });
    }
  };

  const testWorkflow = async (workflowId, testVariables) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/workflows/${workflowId}/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ variables: testVariables })
      });

      if (response.ok) {
        const result = await response.json();
        
        toast({
          title: "Workflow Test Completed",
          description: `Test completed in ${result.execution_result?.duration || 0}s. ${result.execution_result?.ai_calls || 0} AI calls made.`,
        });

        return result;
      } else {
        throw new Error('Failed to test workflow');
      }

    } catch (error) {
      console.error('Error testing workflow:', error);
      toast({
        title: "Test Failed",
        description: "Failed to test workflow.",
        variant: "destructive",
      });
    }
  };

  const publishWorkflow = async (workflowId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/workflows/${workflowId}/publish`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const result = await response.json();
        
        setWorkflows(prev => prev.map(w => 
          w.id === workflowId 
            ? { ...w, is_published: true, is_active: true, version: result.version }
            : w
        ));

        toast({
          title: "Workflow Published",
          description: "Workflow is now available for production use.",
        });

      } else {
        throw new Error('Failed to publish workflow');
      }

    } catch (error) {
      console.error('Error publishing workflow:', error);
      toast({
        title: "Publish Failed",
        description: "Failed to publish workflow.",
        variant: "destructive",
      });
    }
  };

  const addWorkflowStep = (stepType) => {
    const newStep = {
      id: Date.now().toString(),
      type: stepType,
      name: `${stepTypes.find(t => t.value === stepType)?.label || stepType} Step`,
      config: {},
      conditions: []
    };

    setNewWorkflow(prev => ({
      ...prev,
      steps: [...prev.steps, newStep]
    }));
  };

  const removeWorkflowStep = (stepId) => {
    setNewWorkflow(prev => ({
      ...prev,
      steps: prev.steps.filter(step => step.id !== stepId)
    }));
  };

  const getWorkflowStatusColor = (workflow) => {
    if (workflow.is_published) return 'bg-green-100 text-green-800';
    if (workflow.is_active) return 'bg-blue-100 text-blue-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getWorkflowStatus = (workflow) => {
    if (workflow.is_published) return 'Published';
    if (workflow.is_active) return 'Active';
    return 'Draft';
  };

  if (!isVisible) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <Zap className="h-8 w-8 mr-3 text-purple-600" />
            Workflow Authoring
          </h2>
          <p className="text-gray-600">Create and manage AI-powered workflows and prompt templates</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button onClick={loadWorkflowData} variant="outline" size="sm" disabled={loading}>
            <Activity className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      <Tabs defaultValue="workflows" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
          <TabsTrigger value="prompts">Prompt Templates</TabsTrigger>
          <TabsTrigger value="builder">Workflow Builder</TabsTrigger>
          <TabsTrigger value="testing">Testing & Analytics</TabsTrigger>
        </TabsList>

        {/* Workflows Tab */}
        <TabsContent value="workflows" className="space-y-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <Input placeholder="Search workflows..." className="w-64" />
              <Select defaultValue="all">
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {workflowCategories.map(cat => (
                    <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button onClick={() => setSelectedWorkflow('new')} className="bg-purple-600 hover:bg-purple-700">
              <Plus className="h-4 w-4 mr-2" />
              New Workflow
            </Button>
          </div>

          <div className="grid gap-6">
            {(workflows || []).map((workflow) => (
              <Card key={workflow.id} className="bg-white shadow-lg">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="flex items-center">
                        <Zap className="h-5 w-5 mr-2 text-purple-600" />
                        {workflow.name}
                        <Badge className={`ml-2 ${getWorkflowStatusColor(workflow)}`}>
                          {getWorkflowStatus(workflow)}
                        </Badge>
                        {workflow.version && (
                          <Badge variant="outline" className="ml-2">
                            v{workflow.version}
                          </Badge>
                        )}
                      </CardTitle>
                      <CardDescription>{workflow.description}</CardDescription>
                      <div className="flex items-center space-x-4 mt-2">
                        <Badge variant="outline">
                          {workflowCategories.find(c => c.value === workflow.category)?.label || workflow.category}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {workflow.steps?.length || 0} steps
                        </span>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => testWorkflow(workflow.id, { lead_name: 'Test User', budget: '₹50,000' })}
                      >
                        <TestTube className="h-4 w-4 mr-1" />
                        Test
                      </Button>
                      {!workflow.is_published && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => publishWorkflow(workflow.id)}
                          className="text-green-700 border-green-200 hover:bg-green-50"
                        >
                          <Upload className="h-4 w-4 mr-1" />
                          Publish
                        </Button>
                      )}
                      <Button variant="outline" size="sm">
                        <Edit className="h-4 w-4 mr-1" />
                        Edit
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Workflow Steps Preview */}
                    {workflow.steps && workflow.steps.length > 0 && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Workflow Steps:</h4>
                        <div className="flex items-center space-x-2 overflow-x-auto pb-2">
                          {(workflow.steps || []).map((step, index) => (
                            <div key={index} className="flex items-center space-x-2 flex-shrink-0">
                              <div className="flex items-center space-x-1 bg-gray-100 px-2 py-1 rounded-full">
                                {stepTypes.find(t => t.value === step.type)?.icon}
                                <span className="text-xs">{step.name || step.type}</span>
                              </div>
                              {index < workflow.steps.length - 1 && (
                                <ArrowRight className="h-3 w-3 text-gray-400" />
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Settings */}
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex space-x-4">
                        {workflow.settings?.auto_assign && (
                          <Badge variant="outline" className="text-xs">Auto-assign</Badge>
                        )}
                        {workflow.settings?.send_notifications && (
                          <Badge variant="outline" className="text-xs">Notifications</Badge>
                        )}
                        {workflow.settings?.retry_on_failure && (
                          <Badge variant="outline" className="text-xs">Auto-retry</Badge>
                        )}
                      </div>
                      <span className="text-gray-500">
                        Created: {new Date(workflow.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            
            {workflows.length === 0 && (
              <Card className="p-8 text-center">
                <Zap className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Workflows</h3>
                <p className="text-gray-600 mb-4">Create your first AI-powered workflow.</p>
                <Button onClick={() => setSelectedWorkflow('new')} className="bg-purple-600 hover:bg-purple-700">
                  <Plus className="h-4 w-4 mr-2" />
                  Create First Workflow
                </Button>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Prompt Templates Tab */}
        <TabsContent value="prompts" className="space-y-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <Input placeholder="Search templates..." className="w-64" />
              <Select defaultValue="all">
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  <SelectItem value="general">General</SelectItem>
                  <SelectItem value="sales">Sales</SelectItem>
                  <SelectItem value="support">Support</SelectItem>
                  <SelectItem value="qualification">Qualification</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Dialog>
              <DialogTrigger asChild>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  <Plus className="h-4 w-4 mr-2" />
                  New Template
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Create Prompt Template</DialogTitle>
                  <DialogDescription>Design reusable AI prompt templates for your workflows</DialogDescription>
                </DialogHeader>
                <form onSubmit={createPromptTemplate} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="template-name">Template Name *</Label>
                      <Input
                        id="template-name"
                        value={newPromptTemplate.name}
                        onChange={(e) => setNewPromptTemplate({...newPromptTemplate, name: e.target.value})}
                        placeholder="e.g., Lead Qualification Prompt"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="category">Category</Label>
                      <Select value={newPromptTemplate.category} onValueChange={(value) => setNewPromptTemplate({...newPromptTemplate, category: value})}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="general">General</SelectItem>
                          <SelectItem value="sales">Sales</SelectItem>
                          <SelectItem value="support">Support</SelectItem>
                          <SelectItem value="qualification">Qualification</SelectItem>
                          <SelectItem value="follow_up">Follow-up</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="description">Description</Label>
                    <Input
                      id="description"
                      value={newPromptTemplate.description}
                      onChange={(e) => setNewPromptTemplate({...newPromptTemplate, description: e.target.value})}
                      placeholder="Brief description of the template purpose"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="ai-model">AI Model</Label>
                      <Select value={newPromptTemplate.ai_model} onValueChange={(value) => setNewPromptTemplate({...newPromptTemplate, ai_model: value})}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {aiModels.map((model) => (
                            <SelectItem key={model.value} value={model.value}>
                              {model.label} ({model.provider})
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="temperature">Temperature ({newPromptTemplate.temperature})</Label>
                      <Input
                        id="temperature"
                        type="range"
                        min="0"
                        max="2"
                        step="0.1"
                        value={newPromptTemplate.temperature}
                        onChange={(e) => setNewPromptTemplate({...newPromptTemplate, temperature: parseFloat(e.target.value)})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="max-tokens">Max Tokens</Label>
                      <Input
                        id="max-tokens"
                        type="number"
                        min="100"
                        max="4000"
                        value={newPromptTemplate.max_tokens}
                        onChange={(e) => setNewPromptTemplate({...newPromptTemplate, max_tokens: parseInt(e.target.value)})}
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="system-prompt">System Prompt</Label>
                    <Textarea
                      id="system-prompt"
                      value={newPromptTemplate.system_prompt}
                      onChange={(e) => setNewPromptTemplate({...newPromptTemplate, system_prompt: e.target.value})}
                      placeholder="System instructions for the AI..."
                      rows={4}
                    />
                  </div>

                  <div>
                    <Label htmlFor="user-prompt">User Prompt Template</Label>
                    <Textarea
                      id="user-prompt"
                      value={newPromptTemplate.user_prompt_template}
                      onChange={(e) => setNewPromptTemplate({...newPromptTemplate, user_prompt_template: e.target.value})}
                      placeholder="Use {variable_name} for dynamic content. Example: Hello {lead_name}, I see you're interested in {project_type}..."
                      rows={6}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Use curly braces for variables: {'{lead_name}'}, {'{budget}'}, {'{location}'}, etc.
                    </p>
                  </div>

                  <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700">
                    Create Prompt Template
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {(promptTemplates || []).map((template) => (
              <Card key={template.id} className="bg-white shadow-lg">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="flex items-center">
                        <Brain className="h-5 w-5 mr-2 text-blue-600" />
                        {template.name}
                      </CardTitle>
                      <CardDescription>{template.description}</CardDescription>
                      <div className="flex items-center space-x-2 mt-2">
                        <Badge variant="outline">{template.category}</Badge>
                        <Badge variant="outline">{aiModels.find(m => m.value === template.ai_model)?.label}</Badge>
                        <span className="text-xs text-gray-500">T: {template.temperature}</span>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => testPromptTemplate(template.id, { lead_name: 'Test User', budget: '₹50,000', location: 'Mumbai' })}
                      >
                        <TestTube className="h-4 w-4 mr-1" />
                        Test
                      </Button>
                      <Button variant="outline" size="sm">
                        <Edit className="h-4 w-4 mr-1" />
                        Edit
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">System Prompt:</h4>
                      <p className="text-sm text-gray-600 bg-gray-50 p-2 rounded mt-1">
                        {template.system_prompt ? template.system_prompt.substring(0, 120) : 'No system prompt'}...
                      </p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">User Prompt Template:</h4>
                      <p className="text-sm text-gray-600 bg-gray-50 p-2 rounded mt-1">
                        {template.user_prompt_template ? template.user_prompt_template.substring(0, 120) : 'No user prompt template'}...
                      </p>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Max tokens: {template.max_tokens}</span>
                      <span>Created: {new Date(template.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Workflow Builder Tab */}
        <TabsContent value="builder" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Workflow Builder</CardTitle>
              <CardDescription>Design your workflow step by step</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Basic Info */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="workflow-name">Workflow Name *</Label>
                    <Input
                      id="workflow-name"
                      value={newWorkflow.name}
                      onChange={(e) => setNewWorkflow({...newWorkflow, name: e.target.value})}
                      placeholder="e.g., WhatsApp Lead Nurturing"
                    />
                  </div>
                  <div>
                    <Label htmlFor="workflow-category">Category</Label>
                    <Select value={newWorkflow.category} onValueChange={(value) => setNewWorkflow({...newWorkflow, category: value})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {workflowCategories.map((cat) => (
                          <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <Label htmlFor="workflow-description">Description</Label>
                  <Textarea
                    id="workflow-description"
                    value={newWorkflow.description}
                    onChange={(e) => setNewWorkflow({...newWorkflow, description: e.target.value})}
                    placeholder="Describe what this workflow does..."
                    rows={3}
                  />
                </div>

                {/* Step Builder */}
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium">Workflow Steps</h3>
                    <div className="flex space-x-2">
                      {stepTypes.map((stepType) => (
                        <Button
                          key={stepType.value}
                          variant="outline"
                          size="sm"
                          onClick={() => addWorkflowStep(stepType.value)}
                          className="flex items-center"
                        >
                          {stepType.icon}
                          <span className="ml-1 hidden md:inline">{stepType.label}</span>
                        </Button>
                      ))}
                    </div>
                  </div>

                  {/* Steps List */}
                  <div className="space-y-4">
                    {(newWorkflow.steps || []).map((step, index) => (
                      <Card key={step.id} className="border-l-4 border-l-purple-500">
                        <CardContent className="pt-4">
                          <div className="flex justify-between items-start">
                            <div className="flex items-center space-x-3 flex-1">
                              <div className="flex items-center justify-center w-8 h-8 bg-purple-100 rounded-full">
                                {stepTypes.find(t => t.value === step.type)?.icon}
                              </div>
                              <div className="flex-1">
                                <Input
                                  value={step.name}
                                  onChange={(e) => {
                                    const updatedSteps = newWorkflow.steps.map(s => 
                                      s.id === step.id ? { ...s, name: e.target.value } : s
                                    );
                                    setNewWorkflow({...newWorkflow, steps: updatedSteps});
                                  }}
                                  placeholder="Step name"
                                  className="font-medium"
                                />
                                <p className="text-sm text-gray-600 mt-1">
                                  {stepTypes.find(t => t.value === step.type)?.description}
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <span className="text-sm text-gray-500">#{index + 1}</span>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => removeWorkflowStep(step.id)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}

                    {newWorkflow.steps.length === 0 && (
                      <div className="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
                        <Zap className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-gray-600">Add steps to build your workflow</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Settings */}
                <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium text-gray-900">Workflow Settings</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={newWorkflow.settings.auto_assign}
                        onChange={(e) => setNewWorkflow({
                          ...newWorkflow,
                          settings: { ...newWorkflow.settings, auto_assign: e.target.checked }
                        })}
                      />
                      <Label>Auto-assign leads</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={newWorkflow.settings.send_notifications}
                        onChange={(e) => setNewWorkflow({
                          ...newWorkflow,
                          settings: { ...newWorkflow.settings, send_notifications: e.target.checked }
                        })}
                      />
                      <Label>Send notifications</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={newWorkflow.settings.retry_on_failure}
                        onChange={(e) => setNewWorkflow({
                          ...newWorkflow,
                          settings: { ...newWorkflow.settings, retry_on_failure: e.target.checked }
                        })}
                      />
                      <Label>Retry on failure</Label>
                    </div>
                    <div>
                      <Label>Max execution time (seconds)</Label>
                      <Input
                        type="number"
                        value={newWorkflow.settings.max_execution_time}
                        onChange={(e) => setNewWorkflow({
                          ...newWorkflow,
                          settings: { ...newWorkflow.settings, max_execution_time: parseInt(e.target.value) }
                        })}
                      />
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex justify-end space-x-3">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setNewWorkflow({
                        name: '',
                        description: '',
                        category: 'lead_nurturing',
                        trigger_conditions: {},
                        steps: [],
                        global_variables: {},
                        settings: {
                          auto_assign: false,
                          send_notifications: true,
                          max_execution_time: 3600,
                          retry_on_failure: true
                        },
                        tags: [],
                        is_active: false
                      });
                    }}
                  >
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Reset
                  </Button>
                  <Button
                    onClick={() => testWorkflow('draft', { lead_name: 'Test User', budget: '₹50,000' })}
                    variant="outline"
                  >
                    <TestTube className="h-4 w-4 mr-2" />
                    Test Workflow
                  </Button>
                  <Button onClick={createWorkflow} className="bg-purple-600 hover:bg-purple-700">
                    <Save className="h-4 w-4 mr-2" />
                    Save Workflow
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Testing & Analytics Tab */}
        <TabsContent value="testing" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Test Success Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <p className="text-3xl font-bold text-green-600">94.2%</p>
                  <p className="text-sm text-gray-600">Tests passed</p>
                  <p className="text-xs text-gray-500 mt-2">67 of 71 test cases successful</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Avg Response Time</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <p className="text-3xl font-bold text-blue-600">3.8s</p>
                  <p className="text-sm text-gray-600">Average execution</p>
                  <p className="text-xs text-gray-500 mt-2">15% faster than last month</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Token Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <p className="text-3xl font-bold text-purple-600">1,247</p>
                  <p className="text-sm text-gray-600">Avg tokens/test</p>
                  <p className="text-xs text-gray-500 mt-2">Within efficiency target</p>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Recent Test Results</CardTitle>
              <CardDescription>Latest workflow and template test executions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {(testResults || []).map((result) => (
                  <div key={result.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center justify-center w-8 h-8 bg-green-100 rounded-full">
                        {result.success ? (
                          <CheckCircle2 className="h-4 w-4 text-green-600" />
                        ) : (
                          <AlertCircle className="h-4 w-4 text-red-600" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium">{result.workflow_name}</p>
                        <p className="text-sm text-gray-600">
                          Variables: {result.test_variables ? JSON.stringify(result.test_variables).substring(0, 50) : 'No variables'}...
                        </p>
                        <div className="flex items-center space-x-4 text-xs text-gray-500 mt-1">
                          <span>Duration: {result.duration}s</span>
                          <span>AI calls: {result.ai_calls}</span>
                          <span>Tokens: {result.tokens_used}</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right text-sm text-gray-500">
                      {result.tested_at ? new Date(result.tested_at).toLocaleString() : 'Unknown time'}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default WorkflowAuthoringPanel;