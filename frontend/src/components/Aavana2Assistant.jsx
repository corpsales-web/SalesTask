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

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

const Aavana2Assistant = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([
    {
      id: '1',
      type: 'assistant',
      content: `Hello! I'm Aavana 2.0 with Specialized AI Agents. Ask me anything about CRM, HRMS, Tasks, or Pipeline.`,
      timestamp: new Date(),
      enhanced: true,
      agent_used: 'specialized_coordinator',
      task_type: 'welcome'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;
    const currentInput = inputMessage;
    setMessages(prev => [...prev, { id: Date.now().toString(), type: 'user', content: currentInput, timestamp: new Date() }]);
    setInputMessage(''); setIsLoading(true);
    try {
      let response;
      try {
        response = await axios.post(`${API}/api/ai/specialized-chat`, { message: currentInput, session_id: localStorage.getItem('aavana2_session_id') || 'web', language: selectedLanguage, context: { component: 'aavana2_chat' } });
      } catch (e1) {
        try {
          response = await axios.post(`${API}/api/aavana2/enhanced-chat`, { message: currentInput, session_id: 'web', language: selectedLanguage });
        } catch (e2) {
          response = await axios.post(`${API}/api/aavana2/chat`, { message: currentInput, session_id: 'web', language: selectedLanguage, model: 'gpt-4o', provider: 'openai' });
        }
      }
      const data = response.data || {};
      setMessages(prev => [...prev, { id: data.message_id || (Date.now()+1).toString(), type: 'assistant', content: data.message || 'Okay', timestamp: new Date() }]);
    } catch (error) {
      const status = error.response?.status;
      const detail = error.response?.data?.detail || error.message;
      setMessages(prev => [...prev, { id: (Date.now()+2).toString(), type: 'assistant', content: `❌ API Error (${status || 'ERR'}): ${detail}`, timestamp: new Date() }]);
    } finally { setIsLoading(false); }
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
            <Badge className="bg-blue-100 text-blue-800">Multi-Model AI</Badge>
          </DialogTitle>
          <DialogDescription>Your intelligent assistant</DialogDescription>
        </DialogHeader>
        <div className="flex h-[70vh]">
          <div className="flex-1 flex flex-col">
            <div className="flex justify-between items-center p-3 border-b">
              <div className="flex items-center gap-2">
                <Languages className="h-4 w-4 text-gray-500" />
                <select value={selectedLanguage} onChange={(e)=>setSelectedLanguage(e.target.value)} className="text-sm border rounded px-2 py-1">
                  <option value="en">English</option>
                  <option value="hi">Hindi</option>
                </select>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map(m => (
                <div key={m.id} className={`flex ${m.type==='user'? 'justify-end':'justify-start'}`}>
                  <div className={`max-w-[70%] ${m.type==='user'? 'order-2':'order-1'}`}>
                    <div className={`rounded-lg p-3 ${m.type==='user'? 'bg-blue-600 text-white':'bg-gray-100 text-gray-900'}`}>
                      <p className="text-sm whitespace-pre-wrap">{m.content}</p>
                    </div>
                    <div className="text-xs text-gray-400 mt-1">{new Date(m.timestamp).toLocaleTimeString()}</div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            <div className="border-t p-4">
              <div className="flex items-center gap-2">
                <Input ref={inputRef} value={inputMessage} onChange={(e)=>setInputMessage(e.target.value)} placeholder="Ask me anything..." onKeyDown={(e)=>{ if (e.key==='Enter') handleSendMessage() }} className="flex-1" />
                <Button onClick={handleSendMessage} disabled={!inputMessage.trim() || isLoading} className="bg-blue-600 hover:bg-blue-700">
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default Aavana2Assistant;
