from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json
import uuid
import os
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

# AI Models Configuration
class AIOrchestrator:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        # Initialize different AI models for different purposes
        self.gpt5_chat = LlmChat(
            api_key=self.api_key,
            session_id="aavana-gpt5-main",
            system_message="You are an AI assistant for Aavana Greens CRM. You specialize in task automation, workflow optimization, and business insights. Provide precise, actionable responses."
        ).with_model("openai", "gpt-5")
        
        self.claude_chat = LlmChat(
            api_key=self.api_key,
            session_id="aavana-claude-memory",
            system_message="You are the memory layer for Aavana Greens CRM. Store, recall, and organize information about clients, interactions, proposals, and business context. Provide detailed, contextual responses."
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        self.gemini_chat = LlmChat(
            api_key=self.api_key,
            session_id="aavana-gemini-multimodal",
            system_message="You are the multimodal AI for Aavana Greens. Handle image analysis, content creation, and Google ecosystem integration. Be creative and visual."
        ).with_model("gemini", "gemini-2.0-flash")

    async def route_task(self, task_type: str, content: str, context: Dict = None) -> str:
        """Route tasks to the most appropriate AI model"""
        try:
            if task_type in ["automation", "workflow", "insights", "analytics"]:
                return await self._use_gpt5(content, context)
            elif task_type in ["memory", "recall", "history", "context"]:
                return await self._use_claude(content, context)
            elif task_type in ["image", "creative", "content", "multimodal"]:
                return await self._use_gemini(content, context)
            else:
                # Default to GPT-5 for general tasks
                return await self._use_gpt5(content, context)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

    async def _use_gpt5(self, content: str, context: Dict = None) -> str:
        """Use GPT-5 for task automation and insights"""
        full_message = content
        if context:
            full_message = f"Context: {json.dumps(context)}\n\nTask: {content}"
        
        message = UserMessage(text=full_message)
        response = await self.gpt5_chat.send_message(message)
        return response

    async def _use_claude(self, content: str, context: Dict = None) -> str:
        """Use Claude for memory and contextual responses"""
        full_message = content
        if context:
            full_message = f"Context: {json.dumps(context)}\n\nQuery: {content}"
        
        message = UserMessage(text=full_message)
        response = await self.claude_chat.send_message(message)
        return response

    async def _use_gemini(self, content: str, context: Dict = None) -> str:
        """Use Gemini for multimodal and creative tasks"""
        full_message = content
        if context:
            full_message = f"Context: {json.dumps(context)}\n\nRequest: {content}"
        
        message = UserMessage(text=full_message)
        response = await self.gemini_chat.send_message(message)
        return response

# Voice-to-Task Models
class VoiceTaskRequest(BaseModel):
    voice_input: str
    context: Optional[Dict] = None

class VoiceTaskResponse(BaseModel):
    task_breakdown: Dict[str, Any]
    suggested_actions: List[str]
    calendar_event: Optional[Dict] = None
    follow_up_tasks: List[str] = []

class AIInsightRequest(BaseModel):
    type: str  # "leads", "performance", "opportunities", "alerts"
    data: Optional[Dict] = None
    timeframe: Optional[str] = "current"

class AIInsightResponse(BaseModel):
    insights: List[str]
    recommendations: List[str]
    priority_actions: List[str]
    performance_metrics: Optional[Dict] = None

class ContentGenerationRequest(BaseModel):
    type: str  # "social_post", "ad_copy", "blog", "reel_script"
    topic: str
    brand_context: Optional[str] = None
    target_audience: Optional[str] = None

class ContentGenerationResponse(BaseModel):
    content: str
    variations: List[str] = []
    hashtags: List[str] = []
    call_to_action: Optional[str] = None

# AI Service Class
class AIService:
    def __init__(self):
        self.orchestrator = AIOrchestrator()

    async def process_voice_to_task(self, voice_request: VoiceTaskRequest) -> VoiceTaskResponse:
        """Convert voice input to structured task with AI breakdown"""
        try:
            context_str = f"""
            You are processing a voice command for Aavana Greens CRM. 
            Parse this voice input and create a structured task breakdown.
            
            Voice Input: "{voice_request.voice_input}"
            Context: {json.dumps(voice_request.context) if voice_request.context else "None"}
            
            Please provide:
            1. Task breakdown with title, description, priority, due date
            2. Suggested actions to complete the task
            3. Calendar event details if meeting/appointment mentioned
            4. Follow-up tasks if applicable
            
            Format response as JSON with keys: task_breakdown, suggested_actions, calendar_event, follow_up_tasks
            """
            
            response = await self.orchestrator.route_task("automation", context_str)
            
            # Parse AI response and structure it
            try:
                parsed_response = json.loads(response)
            except:
                # Fallback parsing if AI doesn't return valid JSON
                parsed_response = {
                    "task_breakdown": {
                        "title": self._extract_task_title(voice_request.voice_input),
                        "description": voice_request.voice_input,
                        "priority": "Medium",
                        "due_date": self._extract_due_date(voice_request.voice_input)
                    },
                    "suggested_actions": [
                        "Follow up with client",
                        "Prepare necessary materials",
                        "Schedule reminder"
                    ],
                    "calendar_event": None,
                    "follow_up_tasks": []
                }
            
            return VoiceTaskResponse(**parsed_response)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")

    async def generate_ai_insights(self, insight_request: AIInsightRequest) -> AIInsightResponse:
        """Generate AI insights for business operations"""
        try:
            context_str = f"""
            Generate business insights for Aavana Greens based on:
            Type: {insight_request.type}
            Data: {json.dumps(insight_request.data) if insight_request.data else "No specific data"}
            Timeframe: {insight_request.timeframe}
            
            Provide insights, recommendations, and priority actions for a green building/nursery business.
            Focus on practical, actionable advice for CRM optimization, lead conversion, and business growth.
            """
            
            response = await self.orchestrator.route_task("insights", context_str)
            
            # Structure the response
            insights = self._parse_insights(response)
            
            return AIInsightResponse(
                insights=insights.get("insights", ["AI analysis completed"]),
                recommendations=insights.get("recommendations", ["Continue monitoring"]),
                priority_actions=insights.get("priority_actions", ["Review data"]),
                performance_metrics=insights.get("performance_metrics")
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Insight generation error: {str(e)}")

    async def generate_content(self, content_request: ContentGenerationRequest) -> ContentGenerationResponse:
        """Generate marketing content using AI"""
        try:
            context_str = f"""
            Create {content_request.type} content for Aavana Greens (green building/nursery business).
            Topic: {content_request.topic}
            Brand Context: {content_request.brand_context or "Eco-friendly, sustainable green solutions"}
            Target Audience: {content_request.target_audience or "Homeowners interested in green living"}
            
            Make it engaging, relevant to green/eco-friendly themes, and include appropriate hashtags.
            """
            
            response = await self.orchestrator.route_task("creative", context_str)
            
            # Parse and structure the content response
            content_data = self._parse_content(response, content_request.type)
            
            return ContentGenerationResponse(**content_data)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Content generation error: {str(e)}")

    async def recall_client_context(self, client_id: str, query: str) -> str:
        """Use Claude's memory layer to recall client context"""
        try:
            context_str = f"""
            Recall all available information about client ID: {client_id}
            Query: {query}
            
            Provide comprehensive context including past interactions, preferences, proposals, and relevant history.
            """
            
            response = await self.orchestrator.route_task("memory", context_str, {"client_id": client_id})
            return response
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Context recall error: {str(e)}")

    # Helper methods
    def _extract_task_title(self, voice_input: str) -> str:
        """Extract task title from voice input"""
        words = voice_input.split()[:6]  # First 6 words
        return " ".join(words).capitalize()

    def _extract_due_date(self, voice_input: str) -> Optional[str]:
        """Extract due date from voice input"""
        # Simple date extraction logic
        if "tomorrow" in voice_input.lower():
            return (datetime.now(timezone.utc).replace(hour=10, minute=0)).isoformat()
        elif "today" in voice_input.lower():
            return (datetime.now(timezone.utc).replace(hour=16, minute=0)).isoformat()
        return None

    def _parse_insights(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI insights response"""
        try:
            return json.loads(ai_response)
        except:
            # Fallback parsing
            lines = ai_response.split('\n')
            return {
                "insights": [line.strip() for line in lines[:3] if line.strip()],
                "recommendations": [line.strip() for line in lines[3:6] if line.strip()],
                "priority_actions": [line.strip() for line in lines[6:9] if line.strip()]
            }

    def _parse_content(self, ai_response: str, content_type: str) -> Dict[str, Any]:
        """Parse AI content generation response"""
        try:
            return json.loads(ai_response)
        except:
            # Fallback parsing
            return {
                "content": ai_response,
                "variations": [],
                "hashtags": ["#AavanaGreens", "#GreenLiving", "#Sustainable", "#EcoFriendly"],
                "call_to_action": "Contact us for your green solution needs!"
            }

# Global AI service instance
ai_service = AIService()