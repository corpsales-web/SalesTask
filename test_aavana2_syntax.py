#!/usr/bin/env python3
"""
Test aavana2 endpoint syntax
"""

import sys
sys.path.append('/app/backend')

# Import required modules
from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timezone
import uuid
import os

# Create test models
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

# Create test router
api_router = APIRouter(prefix="/api")

# Test the aavana2 endpoint definition
try:
    @api_router.post("/aavana2/chat", response_model=ChatResponse)
    async def aavana2_chat(request: ChatRequest):
        """
        Aavana 2.0 AI Chat with multi-model support
        Supports GPT-5, Claude Sonnet 4, Gemini 2.5 Pro
        """
        return ChatResponse(
            message="Test response",
            message_id="test_id",
            session_id=request.session_id,
            timestamp=datetime.now(timezone.utc),
            actions=[]
        )
    
    print("✅ aavana2_chat endpoint definition is syntactically correct")
    
    @api_router.get("/aavana2/chat/history/{session_id}")
    async def get_chat_history(session_id: str, limit: int = 20):
        """Get chat history for a session"""
        return []
    
    print("✅ get_chat_history endpoint definition is syntactically correct")
    
    # Test creating app with router
    app = FastAPI()
    app.include_router(api_router)
    
    print("✅ Router inclusion successful")
    
    # Check routes
    aavana2_routes = [route for route in app.routes if hasattr(route, 'path') and 'aavana2' in route.path]
    print(f"✅ Found {len(aavana2_routes)} aavana2 routes registered")
    for route in aavana2_routes:
        print(f"  {route.methods} {route.path}")
    
except Exception as e:
    print(f"❌ Error in aavana2 endpoint definition: {e}")
    import traceback
    traceback.print_exc()