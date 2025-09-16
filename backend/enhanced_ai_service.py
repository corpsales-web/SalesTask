"""
Enhanced AI Service with Multi-Model Support using Emergent LLM Key
Supports GPT-5, Claude Sonnet 4, and Gemini 2.5 Pro
"""

import os
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
except ImportError:
    print("emergentintegrations not installed. Installing...")
    import subprocess
    subprocess.run([
        "pip", "install", "emergentintegrations", 
        "--extra-index-url", "https://d33sy5i8bnduwe.cloudfront.net/simple/"
    ])
    from emergentintegrations.llm.chat import LlmChat, UserMessage

class AIProvider:
    """Available AI providers and their models"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    
class AIModel:
    """Available AI models"""
    # OpenAI Models
    GPT_5 = "gpt-5"
    GPT_4O = "gpt-4o"
    
    # Anthropic Models
    CLAUDE_4_SONNET = "claude-4-sonnet-20250514"
    CLAUDE_3_7_SONNET = "claude-3-7-sonnet-20250219"
    
    # Gemini Models
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"

class AIRequest(BaseModel):
    """Base AI request model"""
    prompt: str
    provider: str = AIProvider.OPENAI
    model: str = AIModel.GPT_5
    temperature: float = 0.7
    max_tokens: int = 2000
    system_message: Optional[str] = None
    session_id: Optional[str] = None

class AIResponse(BaseModel):
    """AI response model"""
    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    session_id: str
    timestamp: datetime

class EnhancedAIService:
    """Enhanced AI service with multi-model support"""
    
    def __init__(self):
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
        
        # Default configurations for different use cases
        self.model_configs = {
            "creative": {
                "provider": AIProvider.ANTHROPIC,
                "model": AIModel.CLAUDE_4_SONNET,
                "temperature": 0.8
            },
            "analytical": {
                "provider": AIProvider.OPENAI,
                "model": AIModel.GPT_5,
                "temperature": 0.3
            },
            "conversational": {
                "provider": AIProvider.GEMINI,
                "model": AIModel.GEMINI_2_5_PRO,
                "temperature": 0.6
            },
            "business": {
                "provider": AIProvider.OPENAI,
                "model": AIModel.GPT_5,
                "temperature": 0.4
            }
        }
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate AI response using specified provider and model"""
        try:
            session_id = request.session_id or str(uuid.uuid4())
            
            # Initialize chat with the provider and model
            chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=request.system_message or "You are a helpful AI assistant for Aavana Greens CRM."
            ).with_model(request.provider, request.model)
            
            # Create user message
            user_message = UserMessage(text=request.prompt)
            
            # Send message and get response
            response = await chat.send_message(user_message)
            
            return AIResponse(
                content=response,
                provider=request.provider,
                model=request.model,
                session_id=session_id,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            print(f"AI generation error: {str(e)}")
            # Fallback to GPT-4o if the requested model fails
            if request.model != AIModel.GPT_4O:
                fallback_request = AIRequest(
                    prompt=request.prompt,
                    provider=AIProvider.OPENAI,
                    model=AIModel.GPT_4O,
                    system_message=request.system_message,
                    session_id=request.session_id
                )
                return await self.generate_response(fallback_request)
            else:
                raise Exception(f"AI service failed: {str(e)}")
    
    async def smart_model_selection(self, task_type: str, prompt: str) -> AIResponse:
        """Automatically select the best model based on task type"""
        config = self.model_configs.get(task_type, self.model_configs["business"])
        
        request = AIRequest(
            prompt=prompt,
            provider=config["provider"],
            model=config["model"],
            temperature=config["temperature"],
            system_message=self._get_system_message_for_task(task_type)
        )
        
        return await self.generate_response(request)
    
    def _get_system_message_for_task(self, task_type: str) -> str:
        """Get appropriate system message for different task types"""
        system_messages = {
            "creative": "You are a creative AI assistant specializing in content creation, marketing copy, and innovative solutions for Aavana Greens, a green building and landscaping company.",
            "analytical": "You are an analytical AI assistant specializing in data analysis, business intelligence, and strategic insights for Aavana Greens CRM.",
            "conversational": "You are a conversational AI assistant helping with customer interactions, lead qualification, and communication for Aavana Greens.",
            "business": "You are a business AI assistant helping with CRM operations, workflow automation, and business process optimization for Aavana Greens."
        }
        return system_messages.get(task_type, system_messages["business"])
    
    # Specialized AI functions for different CRM features
    
    async def analyze_lead_conversation(self, conversation_data: Dict) -> Dict:
        """Analyze customer conversations for sentiment and insights"""
        prompt = f"""
        Analyze this customer conversation for Aavana Greens (green building & landscaping company):
        
        Conversation: {json.dumps(conversation_data)}
        
        Provide a JSON response with:
        {{
            "sentiment": "positive/neutral/negative",
            "customer_intent": "specific intent detected",
            "pain_points": ["list of pain points"],
            "buying_signals": ["list of buying signals"],
            "next_best_action": "recommended action",
            "urgency_level": "low/medium/high",
            "product_interest": ["interested products/services"],
            "budget_indicators": "budget range if mentioned",
            "timeline_indicators": "timeline if mentioned"
        }}
        """
        
        response = await self.smart_model_selection("analytical", prompt)
        try:
            return json.loads(response.content)
        except:
            return {"error": "Failed to parse AI response", "raw_response": response.content}
    
    async def generate_smart_proposal(self, lead_data: Dict, service_type: str) -> Dict:
        """Generate AI-powered custom proposals"""
        prompt = f"""
        Generate a comprehensive, personalized proposal for Aavana Greens client:
        
        Client Details: {json.dumps(lead_data)}
        Service Type: {service_type}
        
        Create a detailed proposal with these sections:
        1. Executive Summary
        2. Understanding of Client Needs
        3. Proposed Solutions & Services
        4. Timeline & Milestones
        5. Investment Details
        6. Value Proposition
        7. Next Steps
        8. Terms & Conditions
        
        Format as a professional, compelling proposal for green building/landscaping services.
        Include specific benefits for their space: {lead_data.get('space_size', 'N/A')} and budget: ₹{lead_data.get('budget', 'N/A')}
        
        Return as structured JSON with each section.
        """
        
        response = await self.smart_model_selection("creative", prompt)
        try:
            return json.loads(response.content)
        except:
            return {"proposal_text": response.content, "formatted": False}
    
    async def optimize_workflow(self, workflow_data: Dict) -> Dict:
        """AI-powered workflow optimization"""
        prompt = f"""
        Optimize this workflow for Aavana Greens:
        
        Current Workflow: {json.dumps(workflow_data)}
        
        Analyze and provide optimization recommendations:
        {{
            "bottlenecks": ["identified bottlenecks"],
            "automation_opportunities": ["steps that can be automated"],
            "efficiency_improvements": ["specific improvements"],
            "resource_optimization": ["resource allocation suggestions"],
            "estimated_time_savings": "percentage improvement",
            "implementation_priority": ["high/medium/low priority items"],
            "roi_potential": "estimated return on investment"
        }}
        """
        
        response = await self.smart_model_selection("analytical", prompt)
        try:
            return json.loads(response.content)
        except:
            return {"error": "Failed to parse AI response", "raw_response": response.content}
    
    async def generate_marketing_content(self, campaign_data: Dict) -> Dict:
        """Generate marketing content using AI"""
        prompt = f"""
        Create marketing content for Aavana Greens based on:
        
        Campaign Data: {json.dumps(campaign_data)}
        
        Generate:
        {{
            "headline": "compelling headline",
            "description": "engaging description",
            "call_to_action": "strong CTA",
            "social_media_posts": {{
                "facebook": "Facebook post",
                "instagram": "Instagram caption",
                "linkedin": "LinkedIn post"
            }},
            "email_subject": "email subject line",
            "email_content": "email body content",
            "whatsapp_message": "WhatsApp message",
            "ad_variations": ["ad variation 1", "ad variation 2", "ad variation 3"]
        }}
        
        Focus on green building, landscaping, and sustainable living themes.
        """
        
        response = await self.smart_model_selection("creative", prompt)
        try:
            return json.loads(response.content)
        except:
            return {"content": response.content, "formatted": False}
    
    async def predict_deal_closure(self, deals_data: List[Dict]) -> Dict:
        """Predict deal closure probability using AI"""
        prompt = f"""
        Analyze these active deals for Aavana Greens and predict closure probability:
        
        Active Deals: {json.dumps(deals_data)}
        
        For each deal, provide analysis in this format:
        {{
            "deal_predictions": [
                {{
                    "deal_id": "deal_id",
                    "closure_probability": "percentage",
                    "expected_close_date": "estimated date",
                    "revenue_forecast": "amount",
                    "risk_factors": ["factors that could prevent closure"],
                    "acceleration_strategies": ["actions to speed up closure"]
                }}
            ],
            "pipeline_health": {{
                "overall_score": "0-100",
                "total_predicted_revenue": "amount",
                "high_probability_deals": "count",
                "deals_at_risk": "count"
            }},
            "quarterly_forecast": {{
                "q1_revenue": "amount",
                "q2_revenue": "amount",
                "confidence_level": "percentage"
            }}
        }}
        """
        
        response = await self.smart_model_selection("analytical", prompt)
        try:
            return json.loads(response.content)
        except:
            return {"error": "Failed to parse AI response", "raw_response": response.content}
    
    async def generate_task_automation(self, task_data: Dict) -> Dict:
        """Generate AI-powered task automation suggestions"""
        prompt = f"""
        Analyze this task for automation opportunities in Aavana Greens CRM:
        
        Task Data: {json.dumps(task_data)}
        
        Provide automation suggestions:
        {{
            "automation_potential": "high/medium/low",
            "automation_type": "workflow/reminder/assignment/escalation",
            "automation_steps": ["step 1", "step 2", "step 3"],
            "trigger_conditions": ["when to trigger automation"],
            "expected_benefits": ["benefit 1", "benefit 2"],
            "implementation_complexity": "simple/moderate/complex",
            "estimated_time_savings": "hours per week",
            "required_integrations": ["system integrations needed"]
        }}
        """
        
        response = await self.smart_model_selection("analytical", prompt)
        try:
            return json.loads(response.content)
        except:
            return {"error": "Failed to parse AI response", "raw_response": response.content}

# Create global instance
enhanced_ai_service = EnhancedAIService()