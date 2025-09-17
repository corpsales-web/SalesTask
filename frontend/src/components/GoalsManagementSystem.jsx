import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { 
  Target, TrendingUp, Calendar, Clock, Users, Star, Award, 
  Plus, Edit, Trash2, Eye, Filter, BarChart3, PieChart,
  CheckCircle, AlertCircle, ArrowUp, ArrowDown, Zap
} from 'lucide-react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const GoalsManagementSystem = ({ isOpen, onClose }) => {
  // State Management
  const [activeView, setActiveView] = useState('overview');
  const [goals, setGoals] = useState([]);
  const [teams, setTeams] = useState([]);
  const [goalTemplates, setGoalTemplates] = useState([]);
  const [loading, setLoading] = useState(false);

  // Modal States
  const [showCreateGoalModal, setShowCreateGoalModal] = useState(false);
  const [showGoalDetailsModal, setShowGoalDetailsModal] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState(null);

  // Form State
  const [goalForm, setGoalForm] = useState({
    title: '',
    description: '',
    type: 'individual',
    category: 'sales',
    target_value: '',
    current_value: 0,
    metric_unit: 'number',
    start_date: '',
    end_date: '',
    assigned_to: [],
    priority: 'medium',
    status: 'active'
  });

  // Initialize data
  useEffect(() => {
    if (isOpen) {
      initializeGoalsData();
    }
  }, [isOpen]);

  const initializeGoalsData = async () => {
    setLoading(true);
    try {
      // Initialize teams
      setTeams([
        { id: '1', name: 'Sales Team', members: ['Rajesh Kumar', 'Priya Sharma'] },
        { id: '2', name: 'Marketing Team', members: ['Amit Patel', 'Sneha Verma'] },
        { id: '3', name: 'Operations Team', members: ['Vikram Singh', 'Pooja Mehta'] }
      ]);

      // Initialize goal templates
      setGoalTemplates([
        { id: '1', title: 'Monthly Sales Target', category: 'sales', target_value: 100000, unit: 'currency' },
        { id: '2', title: 'Lead Generation', category: 'marketing', target_value: 50, unit: 'number' },
        { id: '3', title: 'Customer Satisfaction', category: 'service', target_value: 95, unit: 'percentage' },
        { id: '4', title: 'Project Completion', category: 'operations', target_value: 10, unit: 'number' }
      ]);

      // Initialize goals with comprehensive data
      setGoals([
        {
          id: '1',
          title: 'Q1 Sales Revenue Target',
          description: 'Achieve quarterly sales revenue target for green building projects',
          type: 'team',
          category: 'sales',
          target_value: 5000000,
          current_value: 3250000,
          metric_unit: 'currency',
          start_date: '2024-01-01',
          end_date: '2024-03-31',
          assigned_to: ['1'], // Sales Team
          priority: 'high',
          status: 'active',
          progress: 65,
          created_by: 'Admin',
          created_at: '2024-01-01',
          milestones: [
            { title: 'Month 1 Target', target: 1500000, achieved: 1200000, status: 'completed' },
            { title: 'Month 2 Target', target: 3000000, achieved: 2100000, status: 'completed' },
            { title: 'Month 3 Target', target: 5000000, achieved: 3250000, status: 'in_progress' }
          ],
          kpis: [
            { name: 'Deals Closed', current: 42, target: 60 },
            { name: 'Average Deal Size', current: 77381, target: 83333 },
            { name: 'Conversion Rate', current: 28, target: 35 }
          ]
        },
        {
          id: '2',
          title: 'Lead Generation - New Customers',
          description: 'Generate high-quality leads for balcony garden solutions',
          type: 'team',
          category: 'marketing',
          target_value: 200,
          current_value: 156,
          metric_unit: 'number',
          start_date: '2024-01-01',
          end_date: '2024-03-31',
          assigned_to: ['2'], // Marketing Team
          priority: 'high',
          status: 'active',
          progress: 78,
          created_by: 'Marketing Head',
          created_at: '2024-01-01',
          milestones: [
            { title: 'Digital Campaign Launch', target: 50, achieved: 62, status: 'completed' },
            { title: 'Social Media Outreach', target: 100, achieved: 94, status: 'completed' },
            { title: 'Referral Program', target: 200, achieved: 156, status: 'in_progress' }
          ],
          kpis: [
            { name: 'Website Leads', current: 89, target: 120 },
            { name: 'Social Media Leads', current: 41, target: 50 },
            { name: 'Referral Leads', current: 26, target: 30 }
          ]
        },
        {
          id: '3',
          title: 'Individual Sales Performance - Rajesh',
          description: 'Personal sales target for premium villa projects',
          type: 'individual',
          category: 'sales',
          target_value: 1500000,
          current_value: 1125000,
          metric_unit: 'currency',
          start_date: '2024-01-01',
          end_date: '2024-03-31',
          assigned_to: ['Rajesh Kumar'],
          priority: 'medium',
          status: 'active',
          progress: 75,
          created_by: 'Sales Manager',
          created_at: '2024-01-01',
          milestones: [
            { title: 'First Month', target: 500000, achieved: 425000, status: 'completed' },
            { title: 'Second Month', target: 1000000, achieved: 800000, status: 'completed' },
            { title: 'Third Month', target: 1500000, achieved: 1125000, status: 'in_progress' }
          ],
          kpis: [
            { name: 'Deals Closed', current: 15, target: 20 },
            { name: 'Meetings Scheduled', current: 45, target: 60 },
            { name: 'Follow-ups Completed', current: 89, target: 100 }
          ]
        },
        {
          id: '4',
          title: 'Customer Satisfaction Score',
          description: 'Maintain high customer satisfaction for completed projects',
          type: 'company',
          category: 'service',
          target_value: 95,
          current_value: 92,
          metric_unit: 'percentage',
          start_date: '2024-01-01',
          end_date: '2024-12-31',
          assigned_to: ['1', '3'], // Sales and Operations
          priority: 'high',
          status: 'active',
          progress: 97,
          created_by: 'CEO',
          created_at: '2024-01-01',
          milestones: [
            { title: 'Q1 Survey', target: 90, achieved: 92, status: 'completed' },
            { title: 'Q2 Survey', target: 93, achieved: 0, status: 'pending' },
            { title: 'Q3 Survey', target: 94, achieved: 0, status: 'pending' }
          ],
          kpis: [
            { name: 'Response Rate', current: 78, target: 85 },
            { name: 'Net Promoter Score', current: 67, target: 70 },
            { name: 'Repeat Customers', current: 34, target: 40 }
          ]
        }
      ]);

    } catch (error) {
      console.error('Goals initialization error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Goal Management Functions
  const createGoal = async () => {
    setLoading(true);
    try {
      const newGoal = {
        id: Date.now().toString(),
        ...goalForm,
        current_value: 0,
        progress: 0,
        created_by: 'Current User',
        created_at: new Date().toISOString(),
        milestones: [],
        kpis: []
      };

      setGoals(prev => [...prev, newGoal]);
      setShowCreateGoalModal(false);
      resetGoalForm();

      // In production, make API call
      // await axios.post(`${API}/api/goals`, newGoal);

    } catch (error) {
      console.error('Goal creation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateGoalProgress = async (goalId, newValue) => {
    setGoals(prev => prev.map(goal => {
      if (goal.id === goalId) {
        const progress = Math.min((newValue / goal.target_value) * 100, 100);
        return { ...goal, current_value: newValue, progress };
      }
      return goal;
    }));
  };

  const deleteGoal = async (goalId) => {
    setGoals(prev => prev.filter(goal => goal.id !== goalId));
  };

  const resetGoalForm = () => {
    setGoalForm({
      title: '',
      description: '',
      type: 'individual',
      category: 'sales',
      target_value: '',
      current_value: 0,
      metric_unit: 'number',
      start_date: '',
      end_date: '',
      assigned_to: [],
      priority: 'medium',
      status: 'active'
    });
  };

  // Analytics Functions
  const getGoalsByStatus = (status) => goals.filter(goal => goal.status === status);
  const getAverageProgress = () => {
    const totalProgress = goals.reduce((sum, goal) => sum + goal.progress, 0);
    return goals.length > 0 ? Math.round(totalProgress / goals.length) : 0;
  };

  const getGoalsByCategory = () => {
    const categories = {};
    goals.forEach(goal => {
      if (!categories[goal.category]) {
        categories[goal.category] = [];
      }
      categories[goal.category].push(goal);
    });
    return categories;
  };

  // Render Functions
  const renderOverview = () => (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">Total Goals</p>
                <p className="text-3xl font-bold text-blue-700">{goals.length}</p>
              </div>
              <Target className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">Active Goals</p>
                <p className="text-3xl font-bold text-green-700">
                  {getGoalsByStatus('active').length}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-yellow-50 border-yellow-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-yellow-600 text-sm font-medium">Avg Progress</p>
                <p className="text-3xl font-bold text-yellow-700">{getAverageProgress()}%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50 border-purple-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium">Completed</p>
                <p className="text-3xl font-bold text-purple-700">
                  {goals.filter(g => g.progress >= 100).length}
                </p>
              </div>
              <Award className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Goals by Category */}
      <Card>
        <CardHeader>
          <CardTitle>Goals by Category</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(getGoalsByCategory()).map(([category, categoryGoals]) => (
              <div key={category} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold capitalize">{category}</h3>
                  <Badge variant="outline">{categoryGoals.length}</Badge>
                </div>
                <div className="space-y-2">
                  {categoryGoals.slice(0, 3).map(goal => (
                    <div key={goal.id} className="text-sm">
                      <div className="flex justify-between items-center">
                        <span className="truncate">{goal.title}</span>
                        <span className="text-green-600 font-medium">{goal.progress}%</span>
                      </div>
                      <Progress value={goal.progress} className="h-1 mt-1" />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderGoalsList = () => (
    <div className="space-y-4">
      {goals.map(goal => (
        <Card key={goal.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <h3 className="text-lg font-semibold">{goal.title}</h3>
                  <Badge className={
                    goal.priority === 'high' ? 'bg-red-100 text-red-800' :
                    goal.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }>
                    {goal.priority}
                  </Badge>
                  <Badge variant="outline" className="capitalize">
                    {goal.category}
                  </Badge>
                </div>
                <p className="text-gray-600 text-sm mb-3">{goal.description}</p>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <p className="text-xs text-gray-500">Progress</p>
                    <div className="flex items-center space-x-2">
                      <Progress value={goal.progress} className="flex-1" />
                      <span className="text-sm font-medium">{goal.progress}%</span>
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Current / Target</p>
                    <p className="font-medium">
                      {goal.metric_unit === 'currency' 
                        ? `₹${(goal.current_value / 100000).toFixed(1)}L / ₹${(goal.target_value / 100000).toFixed(1)}L`
                        : `${goal.current_value} / ${goal.target_value} ${goal.metric_unit === 'percentage' ? '%' : ''}`
                      }
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Due Date</p>
                    <p className="font-medium">{new Date(goal.end_date).toLocaleDateString()}</p>
                  </div>
                </div>

                {/* KPIs */}
                {goal.kpis && goal.kpis.length > 0 && (
                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">Key Performance Indicators</p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                      {goal.kpis.map((kpi, index) => (
                        <div key={index} className="bg-gray-50 p-2 rounded text-sm">
                          <p className="font-medium">{kpi.name}</p>
                          <p className="text-gray-600">{kpi.current} / {kpi.target}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex space-x-2 ml-4">
                <Button size="sm" variant="outline" onClick={() => {
                  setSelectedGoal(goal);
                  setShowGoalDetailsModal(true);
                }}>
                  <Eye className="h-4 w-4" />
                </Button>
                <Button size="sm" variant="outline" onClick={() => {
                  setGoalForm({
                    title: goal.title,
                    description: goal.description,
                    type: goal.type,
                    category: goal.category,
                    target_value: goal.target_value.toString(),
                    current_value: goal.current_value,
                    metric_unit: goal.metric_unit,
                    start_date: goal.start_date,
                    end_date: goal.end_date,
                    assigned_to: goal.assigned_to,
                    priority: goal.priority,
                    status: goal.status
                  });
                  setShowCreateGoalModal(true);
                }}>
                  <Edit className="h-4 w-4" />
                </Button>
                <Button size="sm" variant="outline" onClick={() => deleteGoal(goal.id)}>
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Target className="h-5 w-5" />
            <span>Goals & Targets Management</span>
          </DialogTitle>
          <DialogDescription>
            Set, track, and achieve your business goals with comprehensive analytics
          </DialogDescription>
        </DialogHeader>

        <div className="flex h-[75vh]">
          {/* Sidebar Navigation */}
          <div className="w-48 border-r p-4">
            <div className="space-y-1">
              <Button
                variant={activeView === 'overview' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => setActiveView('overview')}
              >
                <BarChart3 className="h-4 w-4 mr-2" />
                Overview
              </Button>
              <Button
                variant={activeView === 'goals' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => setActiveView('goals')}
              >
                <Target className="h-4 w-4 mr-2" />
                All Goals
              </Button>
              <Button
                variant={activeView === 'templates' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => setActiveView('templates')}
              >
                <Star className="h-4 w-4 mr-2" />
                Templates
              </Button>
              <Button
                variant={activeView === 'analytics' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => setActiveView('analytics')}
              >
                <PieChart className="h-4 w-4 mr-2" />
                Analytics
              </Button>
            </div>

            <div className="mt-6">
              <Button
                onClick={() => setShowCreateGoalModal(true)}
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                New Goal
              </Button>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 p-6 overflow-y-auto">
            {loading && (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-2">Loading goals...</span>
              </div>
            )}

            {!loading && activeView === 'overview' && renderOverview()}
            {!loading && activeView === 'goals' && renderGoalsList()}
            {!loading && activeView === 'templates' && (
              <div className="text-center py-12">
                <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Goal Templates</h3>
                <p className="text-gray-600">Pre-built goal templates coming soon</p>
              </div>
            )}
            {!loading && activeView === 'analytics' && (
              <div className="text-center py-12">
                <PieChart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Advanced Analytics</h3>
                <p className="text-gray-600">Detailed goal analytics and insights coming soon</p>
              </div>
            )}
          </div>
        </div>

        {/* Create Goal Modal */}
        <Dialog open={showCreateGoalModal} onOpenChange={setShowCreateGoalModal}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Goal</DialogTitle>
              <DialogDescription>Set up a new goal with targets and tracking</DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4 max-h-96 overflow-y-auto">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Goal Title</Label>
                  <Input 
                    value={goalForm.title}
                    onChange={(e) => setGoalForm({...goalForm, title: e.target.value})}
                    placeholder="Enter goal title..."
                  />
                </div>
                <div>
                  <Label>Category</Label>
                  <Select value={goalForm.category} onValueChange={(value) => setGoalForm({...goalForm, category: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sales">Sales</SelectItem>
                      <SelectItem value="marketing">Marketing</SelectItem>
                      <SelectItem value="operations">Operations</SelectItem>
                      <SelectItem value="service">Service</SelectItem>
                      <SelectItem value="finance">Finance</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label>Description</Label>
                <Textarea 
                  value={goalForm.description}
                  onChange={(e) => setGoalForm({...goalForm, description: e.target.value})}
                  placeholder="Describe the goal..."
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label>Goal Type</Label>
                  <Select value={goalForm.type} onValueChange={(value) => setGoalForm({...goalForm, type: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="individual">Individual</SelectItem>
                      <SelectItem value="team">Team</SelectItem>
                      <SelectItem value="company">Company</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Target Value</Label>
                  <Input 
                    type="number"
                    value={goalForm.target_value}
                    onChange={(e) => setGoalForm({...goalForm, target_value: e.target.value})}
                    placeholder="0"
                  />
                </div>
                <div>
                  <Label>Unit</Label>
                  <Select value={goalForm.metric_unit} onValueChange={(value) => setGoalForm({...goalForm, metric_unit: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="number">Number</SelectItem>
                      <SelectItem value="currency">Currency (₹)</SelectItem>
                      <SelectItem value="percentage">Percentage (%)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Start Date</Label>
                  <Input 
                    type="date"
                    value={goalForm.start_date}
                    onChange={(e) => setGoalForm({...goalForm, start_date: e.target.value})}
                  />
                </div>
                <div>
                  <Label>End Date</Label>
                  <Input 
                    type="date"
                    value={goalForm.end_date}
                    onChange={(e) => setGoalForm({...goalForm, end_date: e.target.value})}
                  />
                </div>
              </div>

              <div>
                <Label>Priority</Label>
                <Select value={goalForm.priority} onValueChange={(value) => setGoalForm({...goalForm, priority: value})}>
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

              <div className="flex space-x-2 pt-4">
                <Button onClick={createGoal} disabled={loading || !goalForm.title}>
                  {loading ? 'Creating...' : 'Create Goal'}
                </Button>
                <Button variant="outline" onClick={() => setShowCreateGoalModal(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {/* Goal Details Modal */}
        {selectedGoal && (
          <Dialog open={showGoalDetailsModal} onOpenChange={setShowGoalDetailsModal}>
            <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>{selectedGoal.title}</DialogTitle>
                <DialogDescription>{selectedGoal.description}</DialogDescription>
              </DialogHeader>
              
              <div className="space-y-6">
                {/* Progress Overview */}
                <div className="grid grid-cols-3 gap-4">
                  <Card>
                    <CardContent className="p-4 text-center">
                      <div className="text-2xl font-bold text-blue-600">{selectedGoal.progress}%</div>
                      <div className="text-sm text-gray-600">Progress</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {selectedGoal.metric_unit === 'currency' 
                          ? `₹${(selectedGoal.current_value / 100000).toFixed(1)}L`
                          : selectedGoal.current_value
                        }
                      </div>
                      <div className="text-sm text-gray-600">Current</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {selectedGoal.metric_unit === 'currency' 
                          ? `₹${(selectedGoal.target_value / 100000).toFixed(1)}L`
                          : selectedGoal.target_value
                        }
                      </div>
                      <div className="text-sm text-gray-600">Target</div>
                    </CardContent>
                  </Card>
                </div>

                {/* Milestones */}
                {selectedGoal.milestones && selectedGoal.milestones.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Milestones</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {selectedGoal.milestones.map((milestone, index) => (
                          <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded">
                            <div className={`w-3 h-3 rounded-full ${
                              milestone.status === 'completed' ? 'bg-green-500' :
                              milestone.status === 'in_progress' ? 'bg-yellow-500' :
                              'bg-gray-300'
                            }`}></div>
                            <div className="flex-1">
                              <div className="font-medium">{milestone.title}</div>
                              <div className="text-sm text-gray-600">
                                {milestone.achieved} / {milestone.target}
                              </div>
                            </div>
                            <Badge className={
                              milestone.status === 'completed' ? 'bg-green-100 text-green-800' :
                              milestone.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-gray-100 text-gray-800'
                            }>
                              {milestone.status.replace('_', ' ')}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* KPIs */}
                {selectedGoal.kpis && selectedGoal.kpis.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Key Performance Indicators</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {selectedGoal.kpis.map((kpi, index) => (
                          <div key={index} className="p-4 border rounded-lg">
                            <div className="font-medium mb-2">{kpi.name}</div>
                            <div className="flex justify-between items-center mb-2">
                              <span>{kpi.current}</span>
                              <span className="text-gray-500">/ {kpi.target}</span>
                            </div>
                            <Progress value={(kpi.current / kpi.target) * 100} className="h-2" />
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </DialogContent>
          </Dialog>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default GoalsManagementSystem;