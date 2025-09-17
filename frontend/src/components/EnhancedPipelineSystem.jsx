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
import { 
  TrendingUp, TrendingDown, DollarSign, Users, Target, Calendar,
  Plus, Edit, Trash2, Eye, Filter, Search, MoreHorizontal, Share,
  ArrowRight, ArrowLeft, CheckCircle, XCircle, Clock, AlertCircle,
  BarChart3, PieChart, LineChart, Activity, Brain, Zap, Star,
  Phone, Mail, MessageSquare, FileText, Image, Award, Percent
} from 'lucide-react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const EnhancedPipelineSystem = () => {
  // State Management
  const [activeView, setActiveView] = useState('pipeline');
  const [deals, setDeals] = useState([]);
  const [stages, setStages] = useState([]);
  const [users, setUsers] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [aiPredictions, setAiPredictions] = useState([]);
  const [loading, setLoading] = useState(false);

  // Modal States
  const [showDealModal, setShowDealModal] = useState(false);
  const [showStageModal, setShowStageModal] = useState(false);
  const [showAnalyticsModal, setShowAnalyticsModal] = useState(false);
  const [selectedDeal, setSelectedDeal] = useState(null);

  // Form States
  const [dealForm, setDealForm] = useState({
    title: '',
    company: '',
    contact_name: '',
    contact_email: '',
    contact_phone: '',
    value: '',
    probability: 50,
    stage: '',
    expected_close_date: '',
    description: '',
    source: '',
    assigned_to: '',
    tags: []
  });

  // Filters
  const [filters, setFilters] = useState({
    stage: 'all',
    assigned_to: 'all',
    source: 'all',
    value_range: 'all',
    search: ''
  });

  // Initialize data
  useEffect(() => {
    initializePipelineSystem();
  }, []);

  const initializePipelineSystem = async () => {
    setLoading(true);
    try {
      // Initialize pipeline stages
      setStages([
        { id: '1', name: 'Lead', color: '#64748b', order: 1, conversion_rate: 25 },
        { id: '2', name: 'Qualified', color: '#3b82f6', order: 2, conversion_rate: 40 },
        { id: '3', name: 'Proposal', color: '#f59e0b', order: 3, conversion_rate: 60 },
        { id: '4', name: 'Negotiation', color: '#ef4444', order: 4, conversion_rate: 75 },
        { id: '5', name: 'Closed Won', color: '#10b981', order: 5, conversion_rate: 100 },
        { id: '6', name: 'Closed Lost', color: '#6b7280', order: 6, conversion_rate: 0 }
      ]);

      // Initialize users
      setUsers([
        { id: '1', name: 'Rajesh Kumar', email: 'rajesh@aavanagreens.com', role: 'Sales Executive' },
        { id: '2', name: 'Priya Sharma', email: 'priya@aavanagreens.com', role: 'Sales Manager' },
        { id: '3', name: 'Amit Patel', email: 'amit@aavanagreens.com', role: 'Senior Executive' },
        { id: '4', name: 'Sneha Verma', email: 'sneha@aavanagreens.com', role: 'Sales Associate' }
      ]);

      // Initialize deals with AI scoring
      setDeals([
        {
          id: '1',
          title: 'Corporate Office Landscaping - TechCorp',
          company: 'TechCorp Solutions',
          contact_name: 'Ramesh Gupta',
          contact_email: 'ramesh@techcorp.com',
          contact_phone: '+91 98765 43210',
          value: 250000,
          probability: 75,
          stage: '4',
          expected_close_date: '2024-02-15',
          description: 'Complete rooftop garden and office landscaping project',
          source: 'Website',
          assigned_to: '2',
          tags: ['corporate', 'high-value', 'landscaping'],
          created_date: '2024-01-01',
          last_activity: '2024-01-15',
          ai_score: 92,
          ai_insights: [
            'High engagement with proposals',
            'Budget confirmed and approved',
            'Decision maker identified'
          ],
          activities: [
            { type: 'call', date: '2024-01-15', note: 'Discussed project timeline' },
            { type: 'email', date: '2024-01-12', note: 'Sent detailed proposal' },
            { type: 'meeting', date: '2024-01-10', note: 'Site visit completed' }
          ]
        },
        {
          id: '2',
          title: 'Residential Balcony Garden - Mumbai',
          company: 'Individual',
          contact_name: 'Anjali Sharma',
          contact_email: 'anjali.sharma@email.com',
          contact_phone: '+91 98765 43211',
          value: 45000,
          probability: 60,
          stage: '3',
          expected_close_date: '2024-01-25',
          description: '2 BHK balcony transformation with automated watering',
          source: 'Google Ads',
          assigned_to: '1',
          tags: ['residential', 'balcony', 'automation'],
          created_date: '2024-01-05',
          last_activity: '2024-01-16',
          ai_score: 78,
          ai_insights: [
            'Strong interest shown in automation features',
            'Budget discussions ongoing',
            'Timeline flexibility available'
          ],
          activities: [
            { type: 'call', date: '2024-01-16', note: 'Budget discussion' },
            { type: 'whatsapp', date: '2024-01-14', note: 'Shared design concepts' }
          ]
        },
        {
          id: '3',
          title: 'Green Building Consultation - EcoHomes',
          company: 'EcoHomes Pvt Ltd',
          contact_name: 'Vikram Singh',
          contact_email: 'vikram@ecohomes.com',
          contact_phone: '+91 98765 43212',
          value: 150000,
          probability: 40,
          stage: '2',
          expected_close_date: '2024-02-28',
          description: 'Green building certification and consultancy',
          source: 'Referral',
          assigned_to: '3',
          tags: ['consultation', 'green-building', 'certification'],
          created_date: '2024-01-08',
          last_activity: '2024-01-14',
          ai_score: 65,
          ai_insights: [
            'Multiple stakeholders involved',
            'Longer decision cycle expected',
            'Price sensitivity detected'
          ],
          activities: [
            { type: 'email', date: '2024-01-14', note: 'Initial consultation proposal' },
            { type: 'call', date: '2024-01-10', note: 'Requirements gathering' }
          ]
        },
        {
          id: '4',
          title: 'Urban Farming Setup - FreshMart',
          company: 'FreshMart Chain',
          contact_name: 'Pooja Mehta',
          contact_email: 'pooja@freshmart.com',
          contact_phone: '+91 98765 43213',
          value: 320000,
          probability: 30,
          stage: '1',
          expected_close_date: '2024-03-15',
          description: 'Vertical farming setup for retail chain',
          source: 'Cold Outreach',
          assigned_to: '4',
          tags: ['urban-farming', 'retail', 'vertical'],
          created_date: '2024-01-12',
          last_activity: '2024-01-16',
          ai_score: 58,
          ai_insights: [
            'Early stage opportunity',
            'High potential value',
            'Needs more qualification'
          ],
          activities: [
            { type: 'call', date: '2024-01-16', note: 'Initial interest call' }
          ]
        }
      ]);

      // Initialize analytics
      setAnalytics({
        total_value: 765000,
        weighted_value: 485000,
        win_rate: 35,
        avg_deal_size: 191250,
        sales_cycle: 45,
        deals_this_month: 4,
        closed_won: 2,
        closed_lost: 1,
        pipeline_velocity: 12.5,
        conversion_rates: {
          'lead_to_qualified': 25,
          'qualified_to_proposal': 60,
          'proposal_to_negotiation': 75,
          'negotiation_to_won': 80
        }
      });

      // Initialize AI predictions
      setAiPredictions([
        {
          deal_id: '1',
          close_probability: 92,
          predicted_close_date: '2024-02-12',
          predicted_value: 250000,
          confidence: 'high',
          recommendations: [
            'Schedule final decision meeting',
            'Prepare contract documentation',
            'Confirm project start date'
          ]
        },
        {
          deal_id: '2',
          close_probability: 78,
          predicted_close_date: '2024-01-28',
          predicted_value: 42000,
          confidence: 'medium',
          recommendations: [
            'Address budget concerns',
            'Provide payment plan options',
            'Schedule site measurement'
          ]
        }
      ]);

    } catch (error) {
      console.error('Pipeline system initialization error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Deal Management Functions
  const createDeal = async () => {
    setLoading(true);
    try {
      const newDeal = {
        id: Date.now().toString(),
        ...dealForm,
        value: parseFloat(dealForm.value),
        created_date: new Date().toISOString(),
        last_activity: new Date().toISOString(),
        ai_score: Math.floor(Math.random() * 40) + 60, // Random AI score
        ai_insights: [
          'New opportunity detected',
          'Initial qualification needed',
          'Follow-up recommended'
        ],
        activities: []
      };

      setDeals(prev => [...prev, newDeal]);
      setShowDealModal(false);
      resetDealForm();

      // Generate AI prediction for new deal
      await generateAIPrediction(newDeal);

    } catch (error) {
      console.error('Deal creation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const moveDeal = async (dealId, newStageId) => {
    setDeals(prev => prev.map(deal => 
      deal.id === dealId ? { 
        ...deal, 
        stage: newStageId,
        last_activity: new Date().toISOString()
      } : deal
    ));

    // Update AI prediction when deal moves
    const deal = deals.find(d => d.id === dealId);
    if (deal) {
      await generateAIPrediction({ ...deal, stage: newStageId });
    }
  };

  const generateAIPrediction = async (deal) => {
    try {
      // Mock AI prediction generation
      const stageWeights = { '1': 20, '2': 40, '3': 60, '4': 75, '5': 100, '6': 0 };
      const baseProbability = stageWeights[deal.stage] || 0;
      const aiBoost = Math.floor(Math.random() * 20) - 10; // -10 to +10
      
      const prediction = {
        deal_id: deal.id,
        close_probability: Math.max(0, Math.min(100, baseProbability + aiBoost)),
        predicted_close_date: deal.expected_close_date,
        predicted_value: deal.value,
        confidence: baseProbability > 60 ? 'high' : baseProbability > 30 ? 'medium' : 'low',
        recommendations: generateRecommendations(deal)
      };

      setAiPredictions(prev => {
        const filtered = prev.filter(p => p.deal_id !== deal.id);
        return [...filtered, prediction];
      });

    } catch (error) {
      console.error('AI prediction error:', error);
    }
  };

  const generateRecommendations = (deal) => {
    const recommendations = [];
    const stageRecommendations = {
      '1': ['Qualify budget and timeline', 'Identify decision makers', 'Schedule discovery call'],
      '2': ['Present detailed solution', 'Provide case studies', 'Arrange site visit'],
      '3': ['Address objections', 'Negotiate terms', 'Present ROI analysis'],
      '4': ['Prepare final proposal', 'Schedule decision meeting', 'Confirm budget approval'],
      '5': ['Celebrate success', 'Plan implementation', 'Request testimonial'],
      '6': ['Analyze loss reasons', 'Maintain relationship', 'Future opportunity tracking']
    };

    return stageRecommendations[deal.stage] || ['Continue engagement', 'Monitor progress', 'Update regularly'];
  };

  // Utility Functions
  const resetDealForm = () => {
    setDealForm({
      title: '',
      company: '',
      contact_name: '',
      contact_email: '',
      contact_phone: '',
      value: '',
      probability: 50,
      stage: '',
      expected_close_date: '',
      description: '',
      source: '',
      assigned_to: '',
      tags: []
    });
  };

  const getFilteredDeals = () => {
    return deals.filter(deal => {
      const matchesStage = filters.stage === 'all' || deal.stage === filters.stage;
      const matchesAssignee = filters.assigned_to === 'all' || deal.assigned_to === filters.assigned_to;
      const matchesSource = filters.source === 'all' || deal.source === filters.source;
      const matchesSearch = !filters.search || 
        deal.title.toLowerCase().includes(filters.search.toLowerCase()) ||
        deal.company.toLowerCase().includes(filters.search.toLowerCase()) ||
        deal.contact_name.toLowerCase().includes(filters.search.toLowerCase());

      return matchesStage && matchesAssignee && matchesSource && matchesSearch;
    });
  };

  const getDealsByStage = (stageId) => {
    return getFilteredDeals().filter(deal => deal.stage === stageId);
  };

  const calculateStageValue = (stageId) => {
    return getDealsByStage(stageId).reduce((total, deal) => total + deal.value, 0);
  };

  const getStageConversionRate = (stageId) => {
    const stage = stages.find(s => s.id === stageId);
    return stage ? stage.conversion_rate : 0;
  };

  // Render Functions
  const renderPipelineBoard = () => (
    <div className="grid grid-cols-1 lg:grid-cols-6 gap-4 overflow-x-auto min-h-screen">
      {stages.map((stage) => (
        <div 
          key={stage.id} 
          className="bg-gray-50 rounded-lg p-4 min-w-80"
          style={{ borderTop: `4px solid ${stage.color}` }}
        >
          <div className="flex justify-between items-center mb-4">
            <div>
              <h3 className="font-semibold text-gray-800">{stage.name}</h3>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <span>{getDealsByStage(stage.id).length} deals</span>
                <span>•</span>
                <span className="text-green-600">
                  ₹{(calculateStageValue(stage.id) / 100000).toFixed(1)}L
                </span>
              </div>
            </div>
            <Badge 
              variant="outline" 
              className="text-xs"
              style={{ color: stage.color }}
            >
              {getStageConversionRate(stage.id)}%
            </Badge>
          </div>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {getDealsByStage(stage.id).map((deal) => {
              const assignedUser = users.find(u => u.id === deal.assigned_to);
              const aiPrediction = aiPredictions.find(p => p.deal_id === deal.id);
              
              return (
                <Card 
                  key={deal.id} 
                  className="bg-white shadow-sm hover:shadow-md transition-shadow cursor-pointer border-l-4"
                  style={{ borderLeftColor: stage.color }}
                  onClick={() => setSelectedDeal(deal)}
                >
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-sm line-clamp-2">{deal.title}</h4>
                      <div className="flex items-center space-x-1">
                        {deal.ai_score && (
                          <Badge 
                            variant="outline" 
                            className={`text-xs ${
                              deal.ai_score >= 80 ? 'border-green-500 text-green-700' :
                              deal.ai_score >= 60 ? 'border-yellow-500 text-yellow-700' :
                              'border-red-500 text-red-700'
                            }`}
                          >
                            <Brain className="h-3 w-3 mr-1" />
                            {deal.ai_score}
                          </Badge>
                        )}
                      </div>
                    </div>
                    
                    <div className="space-y-2 mb-3">
                      <div className="flex justify-between items-center">
                        <span className="text-lg font-semibold text-green-600">
                          ₹{(deal.value / 100000).toFixed(1)}L
                        </span>
                        <span className="text-xs text-gray-500">
                          {deal.probability}%
                        </span>
                      </div>
                      
                      <div className="text-xs text-gray-600">
                        <div>{deal.company}</div>
                        <div>{deal.contact_name}</div>
                      </div>
                      
                      <Progress value={deal.probability} className="h-2" />
                    </div>
                    
                    {aiPrediction && (
                      <div className="mb-3 p-2 bg-blue-50 rounded text-xs">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">AI Prediction:</span>
                          <Badge 
                            variant="outline" 
                            className={`text-xs ${
                              aiPrediction.confidence === 'high' ? 'border-green-500 text-green-700' :
                              aiPrediction.confidence === 'medium' ? 'border-yellow-500 text-yellow-700' :
                              'border-red-500 text-red-700'
                            }`}
                          >
                            {aiPrediction.close_probability}%
                          </Badge>
                        </div>
                        <div className="mt-1 text-gray-600">
                          Close: {new Date(aiPrediction.predicted_close_date).toLocaleDateString()}
                        </div>
                      </div>
                    )}
                    
                    <div className="flex justify-between items-center">
                      <div className="flex items-center space-x-2">
                        {assignedUser && (
                          <Avatar className="h-6 w-6">
                            <AvatarFallback className="text-xs">
                              {assignedUser.name.charAt(0)}
                            </AvatarFallback>
                          </Avatar>
                        )}
                        <span className="text-xs text-gray-500">
                          {new Date(deal.expected_close_date).toLocaleDateString()}
                        </span>
                      </div>
                      
                      <div className="flex space-x-1">
                        {deal.activities.length > 0 && (
                          <Activity className="h-4 w-4 text-blue-500" title="Has Activities" />
                        )}
                        {deal.tags.includes('high-value') && (
                          <Star className="h-4 w-4 text-yellow-500" title="High Value" />
                        )}
                      </div>
                    </div>
                    
                    {/* Stage Movement Buttons */}
                    <div className="flex justify-between mt-3 pt-2 border-t">
                      {stage.order > 1 && (
                        <Button 
                          size="sm" 
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation();
                            const prevStage = stages.find(s => s.order === stage.order - 1);
                            if (prevStage) moveDeal(deal.id, prevStage.id);
                          }}
                        >
                          <ArrowLeft className="h-3 w-3" />
                        </Button>
                      )}
                      
                      <Button 
                        size="sm" 
                        variant="ghost"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <MoreHorizontal className="h-3 w-3" />
                      </Button>
                      
                      {stage.order < 5 && (
                        <Button 
                          size="sm" 
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation();
                            const nextStage = stages.find(s => s.order === stage.order + 1);
                            if (nextStage) moveDeal(deal.id, nextStage.id);
                          }}
                        >
                          <ArrowRight className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );

  const renderAnalyticsDashboard = () => (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">Total Pipeline</p>
                <p className="text-3xl font-bold text-blue-700">
                  ₹{(analytics.total_value / 100000).toFixed(1)}L
                </p>
                <p className="text-blue-600 text-xs">
                  Weighted: ₹{(analytics.weighted_value / 100000).toFixed(1)}L
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">Win Rate</p>
                <p className="text-3xl font-bold text-green-700">{analytics.win_rate}%</p>
                <p className="text-green-600 text-xs">This Quarter</p>
              </div>
              <Target className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-yellow-50 border-yellow-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-yellow-600 text-sm font-medium">Avg Deal Size</p>
                <p className="text-3xl font-bold text-yellow-700">
                  ₹{(analytics.avg_deal_size / 100000).toFixed(1)}L
                </p>
                <p className="text-yellow-600 text-xs">Per Deal</p>
              </div>
              <DollarSign className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50 border-purple-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium">Sales Cycle</p>
                <p className="text-3xl font-bold text-purple-700">{analytics.sales_cycle}</p>
                <p className="text-purple-600 text-xs">Days Average</p>
              </div>
              <Clock className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Insights */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Brain className="h-5 w-5 mr-2 text-purple-600" />
            AI Pipeline Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-3 text-gray-800">High Probability Deals</h4>
              <div className="space-y-2">
                {aiPredictions
                  .filter(p => p.close_probability >= 75)
                  .map((prediction) => {
                    const deal = deals.find(d => d.id === prediction.deal_id);
                    return deal ? (
                      <div key={prediction.deal_id} className="flex justify-between items-center p-2 bg-white rounded">
                        <div>
                          <div className="font-medium text-sm">{deal.title}</div>
                          <div className="text-xs text-gray-600">₹{(deal.value / 100000).toFixed(1)}L</div>
                        </div>
                        <Badge className="bg-green-100 text-green-800">
                          {prediction.close_probability}%
                        </Badge>
                      </div>
                    ) : null;
                  })}
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold mb-3 text-gray-800">Needs Attention</h4>
              <div className="space-y-2">
                {deals
                  .filter(deal => {
                    const daysSinceActivity = Math.floor(
                      (new Date() - new Date(deal.last_activity)) / (1000 * 60 * 60 * 24)
                    );
                    return daysSinceActivity > 7;
                  })
                  .slice(0, 3)
                  .map((deal) => (
                    <div key={deal.id} className="flex justify-between items-center p-2 bg-white rounded">
                      <div>
                        <div className="font-medium text-sm">{deal.title}</div>
                        <div className="text-xs text-gray-600">
                          Last activity: {Math.floor((new Date() - new Date(deal.last_activity)) / (1000 * 60 * 60 * 24))} days ago
                        </div>
                      </div>
                      <Badge className="bg-red-100 text-red-800">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        Stale
                      </Badge>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Conversion Funnel */}
      <Card className="bg-white shadow-lg">
        <CardHeader>
          <CardTitle>Conversion Funnel</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {stages.slice(0, 4).map((stage, index) => {
              const stageDeals = getDealsByStage(stage.id);
              const nextStage = stages[index + 1];
              const conversionRate = index < 3 ? getStageConversionRate(nextStage.id) : 100;
              
              return (
                <div key={stage.id} className="flex items-center space-x-4">
                  <div className="w-24 text-sm font-medium">{stage.name}</div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <div 
                        className="h-8 rounded"
                        style={{ 
                          backgroundColor: stage.color,
                          width: `${Math.max(10, (stageDeals.length / deals.length) * 100)}%`
                        }}
                      ></div>
                      <span className="text-sm text-gray-600">
                        {stageDeals.length} deals ({((stageDeals.length / deals.length) * 100).toFixed(0)}%)
                      </span>
                    </div>
                  </div>
                  <div className="w-20 text-sm text-gray-600">
                    ₹{(calculateStageValue(stage.id) / 100000).toFixed(1)}L
                  </div>
                  {index < 3 && (
                    <div className="w-16 text-xs text-green-600">
                      {conversionRate}% →
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Enhanced Sales Pipeline</h2>
          <p className="text-gray-600">AI-powered sales pipeline with deal prediction and analytics</p>
        </div>
        <div className="flex space-x-2">
          <Button 
            variant="outline" 
            onClick={() => {
              setActiveView('analytics');
              console.log('📊 Switching to analytics view');
            }}
          >
            <BarChart3 className="h-4 w-4 mr-2" />
            Analytics
          </Button>
          <Button onClick={() => setShowDealModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Deal
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
                placeholder="Search deals..."
                value={filters.search}
                onChange={(e) => setFilters({...filters, search: e.target.value})}
                className="w-48"
              />
            </div>
            
            <Select value={filters.stage} onValueChange={(value) => setFilters({...filters, stage: value})}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Stages</SelectItem>
                {stages.map((stage) => (
                  <SelectItem key={stage.id} value={stage.id}>{stage.name}</SelectItem>
                ))}
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

            <Select value={filters.source} onValueChange={(value) => setFilters({...filters, source: value})}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sources</SelectItem>
                <SelectItem value="Website">Website</SelectItem>
                <SelectItem value="Google Ads">Google Ads</SelectItem>
                <SelectItem value="Referral">Referral</SelectItem>
                <SelectItem value="Cold Outreach">Cold Outreach</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* View Toggle */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
        <Button
          variant={activeView === 'pipeline' ? 'default' : 'ghost'}
          onClick={() => setActiveView('pipeline')}
          size="sm"
        >
          Pipeline View
        </Button>
        <Button
          variant={activeView === 'analytics' ? 'default' : 'ghost'}
          onClick={() => setActiveView('analytics')}
          size="sm"
        >
          Analytics View
        </Button>
      </div>

      {/* Main Content */}
      {activeView === 'pipeline' && renderPipelineBoard()}
      {activeView === 'analytics' && renderAnalyticsDashboard()}

      {/* Deal Creation Modal */}
      <Dialog open={showDealModal} onOpenChange={setShowDealModal}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New Deal</DialogTitle>
            <DialogDescription>Add a new deal to your sales pipeline</DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Deal Title</Label>
                <Input 
                  value={dealForm.title}
                  onChange={(e) => setDealForm({...dealForm, title: e.target.value})}
                  placeholder="Enter deal title..."
                />
              </div>
              <div>
                <Label>Company</Label>
                <Input 
                  value={dealForm.company}
                  onChange={(e) => setDealForm({...dealForm, company: e.target.value})}
                  placeholder="Company name..."
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Contact Name</Label>
                <Input 
                  value={dealForm.contact_name}
                  onChange={(e) => setDealForm({...dealForm, contact_name: e.target.value})}
                  placeholder="Contact person..."
                />
              </div>
              <div>
                <Label>Contact Email</Label>
                <Input 
                  type="email"
                  value={dealForm.contact_email}
                  onChange={(e) => setDealForm({...dealForm, contact_email: e.target.value})}
                  placeholder="email@example.com"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Deal Value (₹)</Label>
                <Input 
                  type="number"
                  value={dealForm.value}
                  onChange={(e) => setDealForm({...dealForm, value: e.target.value})}
                  placeholder="0"
                />
              </div>
              <div>
                <Label>Probability (%)</Label>
                <Input 
                  type="number"
                  min="0"
                  max="100"
                  value={dealForm.probability}
                  onChange={(e) => setDealForm({...dealForm, probability: parseInt(e.target.value)})}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Stage</Label>
                <Select value={dealForm.stage} onValueChange={(value) => setDealForm({...dealForm, stage: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select stage" />
                  </SelectTrigger>
                  <SelectContent>
                    {stages.slice(0, 4).map((stage) => (
                      <SelectItem key={stage.id} value={stage.id}>{stage.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Assigned To</Label>
                <Select value={dealForm.assigned_to} onValueChange={(value) => setDealForm({...dealForm, assigned_to: value})}>
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
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Expected Close Date</Label>
                <Input 
                  type="date"
                  value={dealForm.expected_close_date}
                  onChange={(e) => setDealForm({...dealForm, expected_close_date: e.target.value})}
                />
              </div>
              <div>
                <Label>Source</Label>
                <Select value={dealForm.source} onValueChange={(value) => setDealForm({...dealForm, source: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select source" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Website">Website</SelectItem>
                    <SelectItem value="Google Ads">Google Ads</SelectItem>
                    <SelectItem value="Referral">Referral</SelectItem>
                    <SelectItem value="Cold Outreach">Cold Outreach</SelectItem>
                    <SelectItem value="Social Media">Social Media</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label>Description</Label>
              <Textarea 
                value={dealForm.description}
                onChange={(e) => setDealForm({...dealForm, description: e.target.value})}
                placeholder="Deal description..."
                rows={3}
              />
            </div>

            <div className="flex space-x-2">
              <Button onClick={createDeal} disabled={loading || !dealForm.title}>
                {loading ? 'Creating...' : 'Create Deal'}
              </Button>
              <Button variant="outline" onClick={() => setShowDealModal(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Deal Details Modal */}
      {selectedDeal && (
        <Dialog open={!!selectedDeal} onOpenChange={() => setSelectedDeal(null)}>
          <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{selectedDeal.title}</DialogTitle>
              <DialogDescription>{selectedDeal.company}</DialogDescription>
            </DialogHeader>
            
            <div className="space-y-6">
              {/* Deal Overview */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-700">
                    ₹{(selectedDeal.value / 100000).toFixed(1)}L
                  </div>
                  <div className="text-sm text-blue-600">Deal Value</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-700">
                    {selectedDeal.probability}%
                  </div>
                  <div className="text-sm text-green-600">Probability</div>
                </div>
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-700">
                    {selectedDeal.ai_score}
                  </div>
                  <div className="text-sm text-yellow-600">AI Score</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-700">
                    {Math.floor((new Date(selectedDeal.expected_close_date) - new Date()) / (1000 * 60 * 60 * 24))}
                  </div>
                  <div className="text-sm text-purple-600">Days to Close</div>
                </div>
              </div>

              {/* AI Insights */}
              {selectedDeal.ai_insights && (
                <Card className="bg-gradient-to-r from-blue-50 to-purple-50">
                  <CardHeader>
                    <CardTitle className="flex items-center text-lg">
                      <Brain className="h-5 w-5 mr-2 text-purple-600" />
                      AI Insights
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {selectedDeal.ai_insights.map((insight, index) => (
                        <li key={index} className="flex items-start">
                          <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5" />
                          <span className="text-sm">{insight}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {/* Recent Activities */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activities</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {selectedDeal.activities.map((activity, index) => (
                      <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                        <div className="p-2 bg-white rounded-full">
                          {activity.type === 'call' && <Phone className="h-4 w-4 text-blue-500" />}
                          {activity.type === 'email' && <Mail className="h-4 w-4 text-green-500" />}
                          {activity.type === 'meeting' && <Users className="h-4 w-4 text-purple-500" />}
                          {activity.type === 'whatsapp' && <MessageSquare className="h-4 w-4 text-green-600" />}
                        </div>
                        <div className="flex-1">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium capitalize">{activity.type}</div>
                              <div className="text-sm text-gray-600">{activity.note}</div>
                            </div>
                            <div className="text-xs text-gray-500">
                              {new Date(activity.date).toLocaleDateString()}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Action Buttons */}
              <div className="flex space-x-2">
                <Button>
                  <Phone className="h-4 w-4 mr-2" />
                  Call
                </Button>
                <Button variant="outline">
                  <Mail className="h-4 w-4 mr-2" />
                  Email
                </Button>
                <Button variant="outline">
                  <Edit className="h-4 w-4 mr-2" />
                  Edit Deal
                </Button>
                <Button variant="outline">
                  <Share className="h-4 w-4 mr-2" />
                  Share
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

export default EnhancedPipelineSystem;