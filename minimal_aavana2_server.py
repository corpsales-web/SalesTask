#!/usr/bin/env python3
"""
Minimal server to test aavana2 endpoints
"""

import sys
sys.path.append('/app/backend')

from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timezone
import uuid
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

# Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: str

class ChatRequest(BaseModel):
    message: str
    session_id: str
    language: str = "en"
    model: str = "gpt-4o"  # Default model
    provider: str = "openai"  # Default provider

class ChatResponse(BaseModel):
    message: str
    message_id: str
    session_id: str
    timestamp: datetime
    actions: List[dict] = []

# Create app and router
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Test aavana2 endpoints
@api_router.post("/aavana2/chat", response_model=ChatResponse)
async def aavana2_chat(request: ChatRequest):
    """
    Aavana 2.0 AI Chat with multi-model support
    Supports GPT-5, Claude Sonnet 4, Gemini 2.5 Pro
    """
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.getenv('EMERGENT_LLM_KEY')
        
        if not api_key:
            raise HTTPException(status_code=500, detail="LLM API key not configured")
        
        # System message for Aavana 2.0
        system_message = f"""You are Aavana 2.0, an intelligent AI assistant for Aavana Greens CRM.
        
        Instructions:
        1. Always be helpful, professional, and focused on CRM/business needs
        2. Use the language preference: {request.language}
        
        Context: This is session {request.session_id}."""

        # Initialize chat with selected model
        chat = LlmChat(
            api_key=api_key,
            session_id=request.session_id,
            system_message=system_message
        )
        
        # Set model based on request
        if request.provider == "anthropic":
            chat.with_model("anthropic", "claude-3-7-sonnet-20250219")
        elif request.provider == "gemini":
            chat.with_model("gemini", "gemini-2.0-flash")
        else:  # Default to OpenAI
            chat.with_model("openai", request.model)
        
        # Create user message
        user_message = UserMessage(text=request.message)
        
        # Get AI response
        ai_response = await chat.send_message(user_message)
        
        # Create response
        response_msg = ChatMessage(
            role="assistant",
            content=ai_response,
            session_id=request.session_id
        )
        
        return ChatResponse(
            message=ai_response,
            message_id=response_msg.id,
            session_id=request.session_id,
            timestamp=response_msg.timestamp,
            actions=[]
        )
        
    except Exception as e:
        print(f"Aavana 2.0 chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")

@api_router.get("/aavana2/chat/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 20):
    """Get chat history for a session"""
    try:
        # Return empty list for now
        return []
        
    except Exception as e:
        print(f"Chat history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include router
app.include_router(api_router)

if __name__ == "__main__":
    print("Testing minimal aavana2 server...")
    
    # Check routes
    aavana2_routes = [route for route in app.routes if hasattr(route, 'path') and 'aavana2' in route.path]
    print(f"Found {len(aavana2_routes)} aavana2 routes:")
    for route in aavana2_routes:
        print(f"  {route.methods} {route.path}")
    
    if len(aavana2_routes) > 0:
        print("✅ Minimal aavana2 server routes registered successfully")
    else:
        print("❌ No aavana2 routes found in minimal server")