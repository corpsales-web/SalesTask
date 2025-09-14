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
  Route,
  Share2,
  Users,
  Zap,
  Settings,
  Plus,
  Edit,
  Trash2,
  ToggleLeft,
  ToggleRight,
  Target,
  Clock,
  MapPin,
  Phone,
  Mail,
  MessageSquare,
  Filter,
  Search,
  Activity,
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  Globe,
  Smartphone,
  Calendar,
  BarChart3
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const LeadRoutingPanel = ({ isVisible }) => {
  const { toast } = useToast();
  const [routingRules, setRoutingRules] = useState([]);
  const [agents, setAgents] = useState([]);
  const [teams, setTeams] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [routingLogs, setRoutingLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newRule, setNewRule] = useState({
    name: '',
    source: '',
    conditions: {
      location: [],
      budget_range: '',
      time_range: { start: 9, end: 18 },
      custom_fields: {}
    },
    target_agent_id: '',
    target_team_id: '',
    workflow_template_id: '',
    priority: 1,
    is_active: true
  });

  const leadSources = [
    { value: 'whatsapp_360dialog', label: 'WhatsApp (360Dialog)' },
    { value: 'facebook', label: 'Facebook' },
    { value: 'instagram', label: 'Instagram' },
    { value: 'google_ads', label: 'Google Ads' },
    { value: 'indiamart', label: 'IndiaMart' },
    { value: 'justdial', label: 'JustDial' },
    { value: 'website_organic', label: 'Website Organic' },
    { value: 'referrals', label: 'Referrals' },
    { value: 'direct_call', label: 'Direct Call' },
    { value: 'walk_in', label: 'Walk-in' }
  ];

  const indianCities = [
    'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 
    'Pune', 'Ahmedabad', 'Surat', 'Jaipur', 'Lucknow', 'Kanpur',
    'Nagpur', 'Indore', 'Thane', 'Bhopal', 'Visakhapatnam', 'Patna'
  ];

  useEffect(() => {
    if (isVisible) {
      loadRoutingData();
    }
  }, [isVisible]);

  const loadRoutingData = async () => {
    setLoading(true);
    try {
      // Load routing rules
      const rulesResponse = await fetch(`${BACKEND_URL}/api/routing/rules`);
      if (rulesResponse.ok) {
        const rulesData = await rulesResponse.json();
        setRoutingRules(rulesData.rules || []);
      }

      // Load agents (mock data for now)
      setAgents([
        { id: '1', name: 'Rajesh Kumar', email: 'rajesh@aavanagreens.com', role: 'Senior Sales Agent', active_leads: 8 },
        { id: '2', name: 'Priya Sharma', email: 'priya@aavanagreens.com', role: 'Lead Agent', active_leads: 12 },
        { id: '3', name: 'Amit Patel', email: 'amit@aavanagreens.com', role: 'Sales Agent', active_leads: 6 },
        { id: '4', name: 'Sneha Reddy', email: 'sneha@aavanagreens.com', role: 'Sales Agent', active_leads: 9 }
      ]);

      // Load teams (mock data)
      setTeams([
        { id: '1', name: 'Mumbai Team', members: 4, lead: 'Rajesh Kumar' },
        { id: '2', name: 'Bangalore Team', members: 3, lead: 'Priya Sharma' },
        { id: '3', name: 'Delhi Team', members: 5, lead: 'Amit Patel' }
      ]);

      // Load workflows (mock data)
      setWorkflows([
        { id: '1', name: 'WhatsApp Welcome Sequence', category: 'lead_nurturing', is_published: true },
        { id: '2', name: 'High-Value Lead Follow-up', category: 'sales', is_published: true },
        { id: '3', name: 'Weekend Inquiry Handler', category: 'support', is_published: false }
      ]);

      // Load routing logs (mock data)
      setRoutingLogs([
        { 
          id: '1', 
          lead_name: 'Suresh Mehta', 
          source: 'whatsapp_360dialog', 
          rule_applied: 'WhatsApp Priority Routing',
          assigned_agent: 'Priya Sharma',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
          status: 'success'
        },
        { 
          id: '2', 
          lead_name: 'Kavitha Nair', 
          source: 'facebook', 
          rule_applied: 'Location-based Routing',
          assigned_agent: 'Rajesh Kumar',
          timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
          status: 'success'
        },
        { 
          id: '3', 
          lead_name: 'Arjun Singh', 
          source: 'google_ads', 
          rule_applied: 'Default Round-Robin',
          assigned_agent: 'Amit Patel',
          timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
          status: 'success'
        }
      ]);

    } catch (error) {
      console.error('Error loading routing data:', error);
      toast({
        title: "Error Loading Data",
        description: "Failed to load routing configuration.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const createRoutingRule = async (e) => {
    e.preventDefault();
    try {
      // Validate rule
      if (!newRule.name || !newRule.source) {
        toast({
          title: "Validation Error",
          description: "Please fill in required fields.",
          variant: "destructive",
        });
        return;
      }

      if (!newRule.target_agent_id && !newRule.target_team_id) {
        toast({
          title: "Validation Error",
          description: "Please assign to either an agent or team.",
          variant: "destructive",
        });
        return;
      }

      const response = await fetch(`${BACKEND_URL}/api/routing/rules`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newRule)
      });

      if (response.ok) {
        const result = await response.json();
        
        // Add to local state
        const createdRule = {
          id: result.rule_id,
          ...newRule,
          created_at: new Date(),
          updated_at: new Date()
        };
        
        setRoutingRules(prev => [...prev, createdRule]);
        
        // Reset form
        setNewRule({
          name: '',
          source: '',
          conditions: {
            location: [],
            budget_range: '',
            time_range: { start: 9, end: 18 },
            custom_fields: {}
          },
          target_agent_id: '',
          target_team_id: '',
          workflow_template_id: '',
          priority: 1,
          is_active: true
        });

        toast({
          title: "Rule Created",
          description: `Routing rule "${createdRule.name}" has been created successfully.`,
        });

      } else {
        throw new Error('Failed to create routing rule');
      }

    } catch (error) {
      console.error('Error creating routing rule:', error);
      toast({
        title: "Error",
        description: "Failed to create routing rule.",
        variant: "destructive",
      });
    }
  };

  const toggleRuleStatus = (ruleId) => {
    setRoutingRules(prev => prev.map(rule => {
      if (rule.id === ruleId) {
        const newStatus = !rule.is_active;
        toast({
          title: "Rule Updated",
          description: `Rule ${newStatus ? 'activated' : 'deactivated'}.`,
        });
        return { ...rule, is_active: newStatus };
      }
      return rule;
    }));
  };

  const getSourceIcon = (source) => {
    switch (source) {
      case 'whatsapp_360dialog': return <MessageSquare className="h-4 w-4" />;
      case 'facebook': case 'instagram': return <Globe className="h-4 w-4" />;
      case 'google_ads': return <Search className="h-4 w-4" />;
      case 'direct_call': return <Phone className="h-4 w-4" />;
      case 'website_organic': return <Globe className="h-4 w-4" />;
      default: return <Route className="h-4 w-4" />;
    }
  };

  const getRuleStatusColor = (isActive) => {
    return isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800';
  };

  const formatTimeRange = (timeRange) => {
    if (!timeRange) return 'Any time';
    return `${timeRange.start}:00 - ${timeRange.end}:00`;
  };

  if (!isVisible) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <Route className="h-8 w-8 mr-3 text-green-600" />
            Lead Source Routing
          </h2>
          <p className="text-gray-600">Automatically route leads to the right agents and workflows</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button onClick={loadRoutingData} variant="outline" size="sm" disabled={loading}>
            <Activity className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          
          <Dialog>
            <DialogTrigger asChild>
              <Button className="bg-green-600 hover:bg-green-700">
                <Plus className="h-4 w-4 mr-2" />
                Create Rule
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Create Routing Rule</DialogTitle>
                <DialogDescription>Set up automatic lead routing based on source and conditions</DialogDescription>
              </DialogHeader>
              <form onSubmit={createRoutingRule} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="rule-name">Rule Name *</Label>
                    <Input
                      id="rule-name"
                      value={newRule.name}
                      onChange={(e) => setNewRule({...newRule, name: e.target.value})}
                      placeholder="e.g., WhatsApp VIP Routing"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="source">Lead Source *</Label>
                    <Select value={newRule.source} onValueChange={(value) => setNewRule({...newRule, source: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select source" />
                      </SelectTrigger>
                      <SelectContent>
                        {leadSources.map((source) => (
                          <SelectItem key={source.value} value={source.value}>
                            {source.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="priority">Priority</Label>
                    <Select 
                      value={newRule.priority.toString()} 
                      onValueChange={(value) => setNewRule({...newRule, priority: parseInt(value)})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">1 (Highest)</SelectItem>
                        <SelectItem value="2">2 (High)</SelectItem>
                        <SelectItem value="3">3 (Medium)</SelectItem>
                        <SelectItem value="4">4 (Low)</SelectItem>
                        <SelectItem value="5">5 (Lowest)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex items-center space-x-2 pt-6">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => setNewRule({...newRule, is_active: !newRule.is_active})}
                    >
                      {newRule.is_active ? <ToggleRight className="h-4 w-4 text-green-600" /> : <ToggleLeft className="h-4 w-4" />}
                      {newRule.is_active ? 'Active' : 'Inactive'}
                    </Button>
                  </div>
                </div>

                {/* Conditions */}
                <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-gray-900">Routing Conditions (Optional)</h4>
                  
                  <div>
                    <Label>Locations</Label>
                    <Select 
                      value="" 
                      onValueChange={(value) => {
                        if (value && !newRule.conditions.location.includes(value)) {
                          setNewRule({
                            ...newRule, 
                            conditions: {
                              ...newRule.conditions,
                              location: [...newRule.conditions.location, value]
                            }
                          });
                        }
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Add location condition" />
                      </SelectTrigger>
                      <SelectContent>
                        {indianCities.map((city) => (
                          <SelectItem key={city} value={city}>{city}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {newRule.conditions.location.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {newRule.conditions.location.map((location, index) => (
                          <Badge key={index} variant="secondary" className="flex items-center">
                            {location}
                            <button
                              type="button"
                              onClick={() => {
                                const newLocations = newRule.conditions.location.filter((_, i) => i !== index);
                                setNewRule({
                                  ...newRule,
                                  conditions: { ...newRule.conditions, location: newLocations }
                                });
                              }}
                              className="ml-1 text-gray-500 hover:text-gray-700"
                            >
                              ×
                            </button>
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="budget-range">Budget Range</Label>
                      <Select 
                        value={newRule.conditions.budget_range}
                        onValueChange={(value) => setNewRule({
                          ...newRule,
                          conditions: { ...newRule.conditions, budget_range: value }
                        })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Any budget" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="under_50k">Under ₹50,000</SelectItem>
                          <SelectItem value="50k_1l">₹50,000 - ₹1,00,000</SelectItem>
                          <SelectItem value="1l_2l">₹1,00,000 - ₹2,00,000</SelectItem>
                          <SelectItem value="2l_5l">₹2,00,000 - ₹5,00,000</SelectItem>
                          <SelectItem value="above_5l">Above ₹5,00,000</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Working Hours</Label>
                      <div className="flex items-center space-x-2">
                        <Input
                          type="number"
                          min="0"
                          max="23"
                          value={newRule.conditions.time_range?.start || 9}
                          onChange={(e) => setNewRule({
                            ...newRule,
                            conditions: {
                              ...newRule.conditions,
                              time_range: {
                                ...newRule.conditions.time_range,
                                start: parseInt(e.target.value)
                              }
                            }
                          })}
                          className="w-20"
                        />
                        <span>to</span>
                        <Input
                          type="number"
                          min="0"
                          max="23"
                          value={newRule.conditions.time_range?.end || 18}
                          onChange={(e) => setNewRule({
                            ...newRule,
                            conditions: {
                              ...newRule.conditions,
                              time_range: {
                                ...newRule.conditions.time_range,
                                end: parseInt(e.target.value)
                              }
                            }
                          })}
                          className="w-20"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Assignment */}
                <div className="space-y-4 p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-gray-900">Assignment Target</h4>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label>Assign to Agent</Label>
                      <Select 
                        value={newRule.target_agent_id}
                        onValueChange={(value) => setNewRule({
                          ...newRule, 
                          target_agent_id: value,
                          target_team_id: '' // Clear team selection
                        })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select agent" />
                        </SelectTrigger>
                        <SelectContent>
                          {agents.map((agent) => (
                            <SelectItem key={agent.id} value={agent.id}>
                              {agent.name} ({agent.active_leads} active leads)
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Or Assign to Team</Label>
                      <Select 
                        value={newRule.target_team_id}
                        onValueChange={(value) => setNewRule({
                          ...newRule, 
                          target_team_id: value,
                          target_agent_id: '' // Clear agent selection
                        })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select team" />
                        </SelectTrigger>
                        <SelectContent>
                          {teams.map((team) => (
                            <SelectItem key={team.id} value={team.id}>
                              {team.name} ({team.members} members)
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label>Trigger Workflow (Optional)</Label>
                    <Select 
                      value={newRule.workflow_template_id}
                      onValueChange={(value) => setNewRule({...newRule, workflow_template_id: value})}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select workflow" />
                      </SelectTrigger>
                      <SelectContent>
                        {workflows.filter(w => w.is_published).map((workflow) => (
                          <SelectItem key={workflow.id} value={workflow.id}>
                            {workflow.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <Button type="submit" className="w-full bg-green-600 hover:bg-green-700">
                  Create Routing Rule
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Tabs defaultValue="rules" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="rules">Routing Rules</TabsTrigger>
          <TabsTrigger value="agents">Agents & Teams</TabsTrigger>
          <TabsTrigger value="logs">Routing Logs</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Rules Tab */}
        <TabsContent value="rules" className="space-y-6">
          <div className="grid gap-6">
            {routingRules.map((rule) => (
              <Card key={rule.id} className="bg-white shadow-lg">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="flex items-center">
                        {getSourceIcon(rule.source)}
                        <span className="ml-2">{rule.name}</span>
                        <Badge className={`ml-2 ${getRuleStatusColor(rule.is_active)}`}>
                          {rule.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                        <Badge variant="outline" className="ml-2">
                          Priority {rule.priority}
                        </Badge>
                      </CardTitle>
                      <CardDescription>
                        {leadSources.find(s => s.value === rule.source)?.label || rule.source}
                      </CardDescription>
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toggleRuleStatus(rule.id)}
                      >
                        {rule.is_active ? <ToggleRight className="h-4 w-4" /> : <ToggleLeft className="h-4 w-4" />}
                      </Button>
                      <Button variant="outline" size="sm">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Conditions */}
                    {(rule.conditions?.location?.length > 0 || rule.conditions?.budget_range || rule.conditions?.time_range) && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Conditions:</h4>
                        <div className="flex flex-wrap gap-2">
                          {rule.conditions.location && rule.conditions.location.length > 0 && (
                            <Badge variant="outline" className="flex items-center">
                              <MapPin className="h-3 w-3 mr-1" />
                              {rule.conditions.location.join(', ')}
                            </Badge>
                          )}
                          {rule.conditions.budget_range && (
                            <Badge variant="outline" className="flex items-center">
                              <Target className="h-3 w-3 mr-1" />
                              {rule.conditions.budget_range}
                            </Badge>
                          )}
                          {rule.conditions.time_range && (
                            <Badge variant="outline" className="flex items-center">
                              <Clock className="h-3 w-3 mr-1" />
                              {formatTimeRange(rule.conditions.time_range)}
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Assignment */}
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900">Assignment:</h4>
                        <div className="flex items-center mt-1">
                          {rule.target_agent_id && (
                            <>
                              <Users className="h-4 w-4 text-blue-600 mr-1" />
                              <span className="text-blue-600">
                                {agents.find(a => a.id === rule.target_agent_id)?.name || 'Unknown Agent'}
                              </span>
                            </>
                          )}
                          {rule.target_team_id && (
                            <>
                              <Users className="h-4 w-4 text-green-600 mr-1" />
                              <span className="text-green-600">
                                {teams.find(t => t.id === rule.target_team_id)?.name || 'Unknown Team'}
                              </span>
                            </>
                          )}
                          {rule.workflow_template_id && (
                            <>
                              <ArrowRight className="h-4 w-4 text-gray-400 mx-2" />
                              <Zap className="h-4 w-4 text-purple-600 mr-1" />
                              <span className="text-purple-600">
                                {workflows.find(w => w.id === rule.workflow_template_id)?.name || 'Unknown Workflow'}
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                      <div className="text-right text-sm text-gray-500">
                        Created: {new Date(rule.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            
            {routingRules.length === 0 && (
              <Card className="p-8 text-center">
                <Route className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Routing Rules</h3>
                <p className="text-gray-600 mb-4">Create your first routing rule to automatically assign leads.</p>
                <Dialog>
                  <DialogTrigger asChild>
                    <Button className="bg-green-600 hover:bg-green-700">
                      <Plus className="h-4 w-4 mr-2" />
                      Create First Rule
                    </Button>
                  </DialogTrigger>
                </Dialog>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Agents & Teams Tab */}
        <TabsContent value="agents" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Agents */}
            <Card>
              <CardHeader>
                <CardTitle>Available Agents</CardTitle>
                <CardDescription>Agents available for lead assignment</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {agents.map((agent) => (
                    <div key={agent.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium">{agent.name}</p>
                        <p className="text-sm text-gray-600">{agent.role}</p>
                        <p className="text-xs text-gray-500">{agent.email}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">{agent.active_leads} active leads</p>
                        <Badge variant="outline" className="text-xs">
                          Available
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Teams */}
            <Card>
              <CardHeader>
                <CardTitle>Teams</CardTitle>
                <CardDescription>Teams available for lead assignment</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {teams.map((team) => (
                    <div key={team.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium">{team.name}</p>
                        <p className="text-sm text-gray-600">Lead: {team.lead}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">{team.members} members</p>
                        <Badge variant="outline" className="text-xs">
                          Active
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Routing Logs Tab */}
        <TabsContent value="logs" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Recent Routing Activity</CardTitle>
              <CardDescription>Latest lead routing decisions and results</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {routingLogs.map((log) => (
                  <div key={log.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center justify-center w-8 h-8 bg-green-100 rounded-full">
                        {log.status === 'success' ? (
                          <CheckCircle2 className="h-4 w-4 text-green-600" />
                        ) : (
                          <AlertCircle className="h-4 w-4 text-red-600" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium">{log.lead_name}</p>
                        <p className="text-sm text-gray-600">
                          {leadSources.find(s => s.value === log.source)?.label || log.source} → {log.assigned_agent}
                        </p>
                        <p className="text-xs text-gray-500">Rule: {log.rule_applied}</p>
                      </div>
                    </div>
                    <div className="text-right text-sm text-gray-500">
                      {log.timestamp.toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Routing Success Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <p className="text-3xl font-bold text-green-600">98.5%</p>
                  <p className="text-sm text-gray-600">Successful routing</p>
                  <p className="text-xs text-gray-500 mt-2">287 of 291 leads routed successfully</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Average Response Time</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <p className="text-3xl font-bold text-blue-600">4.2min</p>
                  <p className="text-sm text-gray-600">First response</p>
                  <p className="text-xs text-gray-500 mt-2">25% faster than manual routing</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Load Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <p className="text-3xl font-bold text-purple-600">92%</p>
                  <p className="text-sm text-gray-600">Balanced load</p>
                  <p className="text-xs text-gray-500 mt-2">Even distribution across agents</p>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Source Performance</CardTitle>
              <CardDescription>Lead routing performance by source</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { source: 'whatsapp_360dialog', label: 'WhatsApp', leads: 89, success_rate: 99.2, avg_response: '2.1min' },
                  { source: 'facebook', label: 'Facebook', leads: 67, success_rate: 97.8, avg_response: '3.5min' },
                  { source: 'google_ads', label: 'Google Ads', leads: 54, success_rate: 98.1, avg_response: '4.8min' },
                  { source: 'indiamart', label: 'IndiaMart', leads: 43, success_rate: 96.5, avg_response: '6.2min' },
                  { source: 'website_organic', label: 'Website', leads: 38, success_rate: 100.0, avg_response: '5.1min' }
                ].map((item) => (
                  <div key={item.source} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      {getSourceIcon(item.source)}
                      <div>
                        <p className="font-medium">{item.label}</p>
                        <p className="text-sm text-gray-600">{item.leads} leads this month</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">{item.success_rate}% success</p>
                      <p className="text-xs text-gray-500">{item.avg_response} avg response</p>
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

export default LeadRoutingPanel;