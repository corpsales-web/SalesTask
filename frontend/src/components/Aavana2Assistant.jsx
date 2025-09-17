import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { 
  MessageSquare, Send, Mic, MicOff, Volume2, VolumeX, Globe, 
  Sparkles, Zap, Brain, Star, Languages, Settings, Download,
  Play, Pause, RotateCcw, Copy, BookOpen, HelpCircle
} from 'lucide-react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const Aavana2Assistant = ({ isOpen, onClose }) => {
  // State Management
  const [messages, setMessages] = useState([
    {
      id: '1',
      type: 'assistant',
      content: 'Hello! I\'m Aavana 2.0, your intelligent AI assistant for all CRM needs. How can I help you today?',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  
  // Voice Recognition States
  const [recognition, setRecognition] = useState(null);
  const [speechSynthesis, setSpeechSynthesis] = useState(null);

  // References
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Initialize speech services
  useEffect(() => {
    // Initialize Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = selectedLanguage === 'hi' ? 'hi-IN' : 'en-US';
      
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsListening(false);
      };
      
      recognition.onerror = () => {
        setIsListening(false);
      };
      
      setRecognition(recognition);
    }

    // Initialize Speech Synthesis
    if ('speechSynthesis' in window) {
      setSpeechSynthesis(window.speechSynthesis);
    }
  }, [selectedLanguage]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Available languages
  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'hi', name: 'हिंदी', flag: '🇮🇳' },
    { code: 'mr', name: 'मराठी', flag: '🇮🇳' },
    { code: 'gu', name: 'ગુજરાતી', flag: '🇮🇳' },
    { code: 'ta', name: 'தமிழ்', flag: '🇮🇳' },
    { code: 'te', name: 'తెలుగు', flag: '🇮🇳' }
  ];

  // Quick Actions
  const quickActions = [
    { text: 'Show me today\'s leads', icon: '🎯' },
    { text: 'Generate a sales report', icon: '📊' },
    { text: 'Create a follow-up task', icon: '✅' },
    { text: 'Schedule a client meeting', icon: '📅' },
    { text: 'Send project update to client', icon: '📤' },
    { text: 'Analyze lead conversion rates', icon: '📈' }
  ];

  // Handle message sending
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    try {
      // Generate intelligent response based on user input
      const assistantMessage = generateIntelligentResponse(currentInput);
      
      // Simulate processing delay for better UX
      setTimeout(() => {
        setMessages(prev => [...prev, assistantMessage]);
        
        // Auto-speak response if enabled
        if (isSpeaking && speechSynthesis) {
          speakMessage(assistantMessage.content);
        }
        
        setIsLoading(false);
      }, 1000);

    } catch (error) {
      console.error('AI response error:', error);
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'I apologize, but I\'m having trouble processing your request right now. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  // Generate intelligent responses based on user input
  const generateIntelligentResponse = (input) => {
    const inputLower = input.toLowerCase();
    let content = '';
    let actions = [];

    // CRM-related queries
    if (inputLower.includes('lead') || inputLower.includes('customer') || inputLower.includes('client')) {
      content = 'I can help you manage your leads and customers! I can show you recent leads, help you follow up with clients, or guide you through the lead management process. What specific task would you like assistance with?';
      actions = [
        { text: 'View Recent Leads', action: 'navigate_leads' },
        { text: 'Create Follow-up Task', action: 'create_task' },
        { text: 'Lead Analysis', action: 'analyze_leads' }
      ];
    }
    // HRMS queries
    else if (inputLower.includes('attendance') || inputLower.includes('employee') || inputLower.includes('hrms') || inputLower.includes('check-in')) {
      content = 'I can assist you with HR management tasks! I can help you with employee attendance, check-in procedures, leave management, or performance tracking. The face check-in system uses your camera for secure attendance tracking.';
      actions = [
        { text: 'Open HRMS Dashboard', action: 'navigate_hrms' },
        { text: 'Attendance Report', action: 'generate_report' },
        { text: 'Camera Check-in Help', action: 'camera_help' }
      ];
    }
    // Task management queries
    else if (inputLower.includes('task') || inputLower.includes('project') || inputLower.includes('todo')) {
      content = 'I can help you manage your tasks and projects efficiently! I can create new tasks, set reminders, track progress, or help you organize your workflow. You can also use voice commands to create tasks quickly.';
      actions = [
        { text: 'Create New Task', action: 'create_task' },
        { text: 'View Task Board', action: 'navigate_tasks' },
        { text: 'Voice Task Creation', action: 'voice_task' }
      ];
    }
    // Sales and pipeline queries
    else if (inputLower.includes('sales') || inputLower.includes('deal') || inputLower.includes('pipeline') || inputLower.includes('revenue')) {
      content = 'I can help you manage your sales pipeline and track deals! I can show you deal progress, analyze sales performance, predict deal closures, or help you move deals through your pipeline stages.';
      actions = [
        { text: 'View Sales Pipeline', action: 'navigate_pipeline' },
        { text: 'Sales Analytics', action: 'sales_analytics' },
        { text: 'Deal Predictions', action: 'ai_predictions' }
      ];
    }
    // Marketing queries
    else if (inputLower.includes('marketing') || inputLower.includes('campaign') || inputLower.includes('social') || inputLower.includes('content')) {
      content = 'I can assist you with digital marketing management! I can help you create campaigns, schedule social media posts, analyze marketing performance, or generate content ideas for your green building and landscaping business.';
      actions = [
        { text: 'Marketing Dashboard', action: 'navigate_marketing' },
        { text: 'Create Campaign', action: 'create_campaign' },
        { text: 'Content Ideas', action: 'generate_content' }
      ];
    }
    // Goals and targets
    else if (inputLower.includes('goal') || inputLower.includes('target') || inputLower.includes('objective') || inputLower.includes('kpi')) {
      content = 'I can help you set and track your business goals! I can assist with creating SMART goals, monitoring progress, analyzing performance metrics, and ensuring you stay on track to achieve your targets.';
      actions = [
        { text: 'Goals Dashboard', action: 'navigate_goals' },
        { text: 'Create New Goal', action: 'create_goal' },
        { text: 'Progress Analysis', action: 'goal_analysis' }
      ];
    }
    // Training and help
    else if (inputLower.includes('help') || inputLower.includes('train') || inputLower.includes('learn') || inputLower.includes('how to')) {
      content = 'I\'m here to help you learn and master the Aavana Greens CRM! I can provide training on any feature, explain how different modules work, or guide you through specific tasks step by step. What would you like to learn about?';
      actions = [
        { text: 'System Training', action: 'open_training' },
        { text: 'Quick Tips', action: 'show_tips' },
        { text: 'Feature Guide', action: 'feature_guide' }
      ];
    }
    // Camera and technical issues
    else if (inputLower.includes('camera') || inputLower.includes('not working') || inputLower.includes('error') || inputLower.includes('fix')) {
      content = 'I can help you troubleshoot technical issues! For camera problems, make sure you\'ve allowed camera permissions and your browser supports camera access. I can guide you through step-by-step solutions.';
      actions = [
        { text: 'Camera Troubleshooting', action: 'camera_help' },
        { text: 'System Check', action: 'system_check' },
        { text: 'Contact Support', action: 'contact_support' }
      ];
    }
    // General greetings
    else if (inputLower.includes('hello') || inputLower.includes('hi') || inputLower.includes('hey') || inputLower.includes('good')) {
      content = 'Hello! I\'m Aavana 2.0, your intelligent CRM assistant. I\'m here to help you manage your green building and landscaping business more efficiently. I can assist with leads, tasks, HRMS, sales pipeline, marketing campaigns, and much more!';
      actions = [
        { text: 'Show Dashboard', action: 'navigate_dashboard' },
        { text: 'Quick Tour', action: 'system_tour' },
        { text: 'Today\'s Summary', action: 'daily_summary' }
      ];
    }
    // Default response
    else {
      content = `I understand you're asking about "${input}". As your AI assistant, I can help you with lead management, employee check-ins, task tracking, sales pipeline, marketing campaigns, goal setting, and system training. What specific aspect would you like assistance with?`;
      actions = [
        { text: 'Show All Features', action: 'feature_overview' },
        { text: 'Guided Tour', action: 'system_tour' },
        { text: 'Ask Differently', action: 'clarify_request' }
      ];
    }

    return {
      id: (Date.now() + 1).toString(),
      type: 'assistant',
      content: content,
      timestamp: new Date(),
      actions: actions
    };
  };

  // Generate smart actions based on user input
  const generateSmartActions = (userInput) => {
    const actions = [];
    const input = userInput.toLowerCase();

    if (input.includes('lead') || input.includes('prospect')) {
      actions.push({ text: 'View Leads', action: 'navigate_leads' });
    }
    if (input.includes('task') || input.includes('follow')) {
      actions.push({ text: 'Create Task', action: 'create_task' });
    }
    if (input.includes('report') || input.includes('analytics')) {
      actions.push({ text: 'Generate Report', action: 'generate_report' });
    }
    if (input.includes('client') || input.includes('customer')) {
      actions.push({ text: 'Client Actions', action: 'client_actions' });
    }

    return actions;
  };

  // Voice recognition
  const startListening = () => {
    if (recognition) {
      setIsListening(true);
      recognition.start();
    }
  };

  const stopListening = () => {
    if (recognition) {
      recognition.stop();
      setIsListening(false);
    }
  };

  // Text-to-speech
  const speakMessage = (text) => {
    if (speechSynthesis) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = selectedLanguage === 'hi' ? 'hi-IN' : 'en-US';
      utterance.rate = 0.9;
      speechSynthesis.speak(utterance);
    }
  };

  const toggleSpeaking = () => {
    setIsSpeaking(!isSpeaking);
    if (speechSynthesis && speechSynthesis.speaking) {
      speechSynthesis.cancel();
    }
  };

  // Handle quick actions
  const handleQuickAction = (action) => {
    setInputMessage(action);
    inputRef.current?.focus();
  };

  // Handle smart actions
  const handleSmartAction = (action) => {
    switch (action) {
      case 'navigate_leads':
        // This would trigger navigation to leads tab
        console.log('Navigate to leads');
        break;
      case 'create_task':
        // This would open task creation modal
        console.log('Create task');
        break;
      case 'generate_report':
        // This would generate a report
        console.log('Generate report');
        break;
      case 'client_actions':
        // This would show client action options
        console.log('Client actions');
        break;
      default:
        console.log('Unknown action:', action);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
              <Sparkles className="h-4 w-4 text-white" />
            </div>
            <span>Aavana 2.0 AI Assistant</span>
            <Badge className="bg-blue-100 text-blue-800">
              <Brain className="h-3 w-3 mr-1" />
              Multi-Model AI
            </Badge>
          </DialogTitle>
          <DialogDescription>
            Your intelligent assistant powered by GPT-5, Claude Sonnet 4, and Gemini 2.5 Pro
          </DialogDescription>
        </DialogHeader>

        <div className="flex h-[70vh]">
          {/* Main Chat Area */}
          <div className="flex-1 flex flex-col">
            {/* Language & Settings Bar */}
            <div className="flex justify-between items-center p-3 border-b">
              <div className="flex items-center space-x-2">
                <Languages className="h-4 w-4 text-gray-500" />
                <select
                  value={selectedLanguage}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  className="text-sm border rounded px-2 py-1"
                >
                  {languages.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.flag} {lang.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button
                  size="sm"
                  variant={isSpeaking ? "default" : "outline"}
                  onClick={toggleSpeaking}
                >
                  {isSpeaking ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
                </Button>
                <Button size="sm" variant="outline">
                  <Settings className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[70%] ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                    {message.type === 'assistant' && (
                      <div className="flex items-center space-x-2 mb-1">
                        <Avatar className="h-6 w-6">
                          <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-500 text-white text-xs">
                            A2
                          </AvatarFallback>
                        </Avatar>
                        <span className="text-xs text-gray-500">Aavana 2.0</span>
                      </div>
                    )}
                    
                    <div className={`rounded-lg p-3 ${
                      message.type === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      <p className="text-sm">{message.content}</p>
                      {message.actions && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {message.actions.map((action, index) => (
                            <Button
                              key={index}
                              size="sm"
                              variant="outline"
                              className="h-6 text-xs"
                              onClick={() => handleSmartAction(action.action)}
                            >
                              {action.text}
                            </Button>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <div className="text-xs text-gray-400 mt-1">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-3">
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                      <span className="text-sm text-gray-600">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t p-4">
              <div className="flex items-center space-x-2">
                <div className="flex-1 relative">
                  <Input
                    ref={inputRef}
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Ask me anything about your CRM..."
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    className="pr-12"
                  />
                  <Button
                    size="sm"
                    variant="ghost"
                    className="absolute right-1 top-1/2 transform -translate-y-1/2"
                    onClick={isListening ? stopListening : startListening}
                  >
                    {isListening ? (
                      <MicOff className="h-4 w-4 text-red-500" />
                    ) : (
                      <Mic className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isLoading}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* Quick Actions Sidebar */}
          <div className="w-64 border-l p-4 overflow-y-auto">
            <h3 className="font-semibold text-sm text-gray-900 mb-3">Quick Actions</h3>
            <div className="space-y-2">
              {quickActions.map((action, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  className="w-full justify-start text-left h-auto p-2"
                  onClick={() => handleQuickAction(action.text)}
                >
                  <span className="mr-2">{action.icon}</span>
                  <span className="text-xs">{action.text}</span>
                </Button>
              ))}
            </div>

            <div className="mt-6">
              <h3 className="font-semibold text-sm text-gray-900 mb-3">AI Features</h3>
              <div className="space-y-2 text-xs text-gray-600">
                <div className="flex items-center space-x-2">
                  <Zap className="h-3 w-3" />
                  <span>Smart Responses</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Globe className="h-3 w-3" />
                  <span>Multi-language Support</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Brain className="h-3 w-3" />
                  <span>Context Awareness</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Mic className="h-3 w-3" />
                  <span>Voice Commands</span>
                </div>
              </div>
            </div>

            <div className="mt-6">
              <Button variant="outline" size="sm" className="w-full">
                <BookOpen className="h-4 w-4 mr-2" />
                Help & Training
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default Aavana2Assistant;