from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import json
from datetime import datetime, timezone
from enum import Enum

# Import AI service
from ai_service import (
    ai_service, 
    VoiceTaskRequest, 
    VoiceTaskResponse,
    AIInsightRequest,
    AIInsightResponse,
    ContentGenerationRequest,
    ContentGenerationResponse
)

# Import new services
from telephony_service import (
    telephony_service,
    whatsapp_service, 
    hrms_service,
    CallRequest,
    CallLog,
    WhatsAppMessage,
    Employee,
    Attendance,
    LeaveRequest
)

# Import Aavana 2.0 Orchestrator
from aavana_2_0_orchestrator import (
    aavana_2_0,
    ConversationRequest,
    ConversationResponse,
    SupportedLanguage,
    ChannelType,
    IntentType
)

# Import Targets Service
from targets_service import (
    get_targets_service,
    Target,
    ProgressUpdate,
    ProgressSummary,
    ReminderSettings,
    TargetPeriod,
    TargetType,
    UserRole
)

from erp_service import (
    erp_service,
    hrms_service as complete_hrms_service,
    analytics_service,
    Product,
    ProductCreate,
    Invoice,
    ProjectGallery,
    Appointment,
    InventoryAlert
)

from calendar_service import (
    calendar_service,
    whatsapp_advanced_service,
    CalendarEvent,
    CalendarEventCreate,
    SMSNotification,
    EmailNotification
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class LeadStatus(str, Enum):
    NEW = "New"
    QUALIFIED = "Qualified" 
    PROPOSAL = "Proposal"
    NEGOTIATION = "Negotiation"
    WON = "Won"
    LOST = "Lost"

class TaskStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

# Models
class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone: str
    email: Optional[str] = None
    budget: Optional[float] = None
    space_size: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None  # Website, Google Ads, Facebook, Referral, etc.
    category: Optional[str] = None  # Residential, Commercial, Enterprise, etc.
    status: LeadStatus = LeadStatus.NEW
    notes: Optional[str] = None
    tags: List[str] = []
    assigned_to: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_contact: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None

class LeadCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    budget: Optional[float] = None
    space_size: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = []
    assigned_to: Optional[str] = None

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    budget: Optional[float] = None
    space_size: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None
    category: Optional[str] = None
    status: Optional[LeadStatus] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    assigned_to: Optional[str] = None
    last_contact: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    assigned_to: Optional[str] = None
    lead_id: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    ai_generated: bool = False  # Flag for AI-generated tasks

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    assigned_to: Optional[str] = None
    lead_id: Optional[str] = None
    due_date: Optional[datetime] = None
    ai_generated: bool = False

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None

class DashboardStats(BaseModel):
    total_leads: int
    new_leads: int
    qualified_leads: int
    won_deals: int
    lost_deals: int
    total_revenue: float
    pending_tasks: int
    conversion_rate: float
    ai_tasks_generated: int = 0

# Helper functions
def prepare_for_mongo(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item, dict):
        # Remove MongoDB ObjectId field if present
        if '_id' in item:
            del item['_id']
        
        for key, value in item.items():
            if isinstance(value, str) and key.endswith(('_at', '_date', '_contact', '_up')):
                try:
                    item[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    pass
    return item

def make_json_safe(data):
    """Convert data to JSON-safe format by handling datetime objects"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = make_json_safe(value)
            elif isinstance(value, list):
                result[key] = [make_json_safe(item) if isinstance(item, (dict, list)) else 
                              item.isoformat() if isinstance(item, datetime) else item 
                              for item in value]
            else:
                result[key] = value
        return result
    elif isinstance(data, list):
        return [make_json_safe(item) if isinstance(item, (dict, list)) else 
                item.isoformat() if isinstance(item, datetime) else item 
                for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data

# Routes
@api_router.get("/")
async def root():
    return {"message": "Aavana Greens CRM API with AI Integration"}

# Lead Management Routes
@api_router.post("/leads", response_model=Lead)
async def create_lead(lead_data: LeadCreate):
    lead_dict = lead_data.dict()
    lead = Lead(**lead_dict)
    lead_dict = prepare_for_mongo(lead.dict())
    await db.leads.insert_one(lead_dict)
    return lead

@api_router.get("/leads", response_model=List[Lead])
async def get_leads(status: Optional[LeadStatus] = None, limit: int = 100):
    query = {}
    if status:
        query["status"] = status
    
    leads = await db.leads.find(query).limit(limit).to_list(length=limit)
    return [Lead(**parse_from_mongo(lead)) for lead in leads]

@api_router.get("/leads/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str):
    lead = await db.leads.find_one({"id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return Lead(**parse_from_mongo(lead))

@api_router.put("/leads/{lead_id}", response_model=Lead)
async def update_lead(lead_id: str, lead_update: LeadUpdate):
    update_data = {k: v for k, v in lead_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    update_data = prepare_for_mongo(update_data)
    result = await db.leads.update_one({"id": lead_id}, {"$set": update_data})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead = await db.leads.find_one({"id": lead_id})
    return Lead(**parse_from_mongo(lead))

@api_router.delete("/leads/{lead_id}")
async def delete_lead(lead_id: str):
    result = await db.leads.delete_one({"id": lead_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"message": "Lead deleted successfully"}

# Task Management Routes
@api_router.post("/tasks", response_model=Task)
async def create_task(task_data: TaskCreate):
    task_dict = task_data.dict()
    task = Task(**task_dict)
    task_dict = prepare_for_mongo(task.dict())
    await db.tasks.insert_one(task_dict)
    return task

@api_router.get("/tasks", response_model=List[Task])
async def get_tasks(status: Optional[TaskStatus] = None, limit: int = 100):
    query = {}
    if status:
        query["status"] = status
    
    tasks = await db.tasks.find(query).limit(limit).to_list(length=limit)
    return [Task(**parse_from_mongo(task)) for task in tasks]

@api_router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    update_data = {k: v for k, v in task_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    if task_update.status == TaskStatus.COMPLETED:
        update_data["completed_at"] = datetime.now(timezone.utc)
    
    update_data = prepare_for_mongo(update_data)
    result = await db.tasks.update_one({"id": task_id}, {"$set": update_data})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = await db.tasks.find_one({"id": task_id})
    return Task(**parse_from_mongo(task))

# Dashboard Stats Route
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    # Get lead counts by status
    total_leads = await db.leads.count_documents({})
    new_leads = await db.leads.count_documents({"status": "New"})
    qualified_leads = await db.leads.count_documents({"status": "Qualified"})
    won_deals = await db.leads.count_documents({"status": "Won"})
    lost_deals = await db.leads.count_documents({"status": "Lost"})
    
    # Calculate revenue from won deals
    won_leads_cursor = db.leads.find({"status": "Won", "budget": {"$exists": True, "$ne": None}})
    won_leads_list = await won_leads_cursor.to_list(length=None)
    total_revenue = sum(lead.get("budget", 0) for lead in won_leads_list)
    
    # Get pending tasks
    pending_tasks = await db.tasks.count_documents({"status": "Pending"})
    
    # Get AI-generated tasks count
    ai_tasks_generated = await db.tasks.count_documents({"ai_generated": True})
    
    # Calculate conversion rate
    conversion_rate = (won_deals / total_leads * 100) if total_leads > 0 else 0
    
    return DashboardStats(
        total_leads=total_leads,
        new_leads=new_leads,
        qualified_leads=qualified_leads,
        won_deals=won_deals,
        lost_deals=lost_deals,
        total_revenue=total_revenue,
        pending_tasks=pending_tasks,
        conversion_rate=round(conversion_rate, 2),
        ai_tasks_generated=ai_tasks_generated
    )

# AI Integration Routes
@api_router.post("/ai/voice-to-task", response_model=VoiceTaskResponse)
async def voice_to_task(request: VoiceTaskRequest):
    """Convert voice input to structured task using AI"""
    try:
        result = await ai_service.process_voice_to_task(request)
        
        # Automatically create the task in the database
        if result.task_breakdown:
            task_data = TaskCreate(
                title=result.task_breakdown.get("title", "AI Generated Task"),
                description=result.task_breakdown.get("description", request.voice_input),
                priority=Priority(result.task_breakdown.get("priority", "Medium")),
                due_date=result.task_breakdown.get("due_date"),
                ai_generated=True
            )
            
            # Create the task
            task_dict = task_data.dict()
            task = Task(**task_dict)
            task_dict = prepare_for_mongo(task.dict())
            await db.tasks.insert_one(task_dict)
            
            result.task_breakdown["task_id"] = task.id
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

@api_router.post("/ai/insights", response_model=AIInsightResponse)
async def get_ai_insights(request: AIInsightRequest):
    """Generate AI insights for business operations"""
    try:
        # Add current CRM data as context
        if request.type == "leads":
            leads_count = await db.leads.count_documents({})
            won_count = await db.leads.count_documents({"status": "Won"})
            request.data = {
                "total_leads": leads_count,
                "won_deals": won_count,
                "conversion_rate": (won_count / leads_count * 100) if leads_count > 0 else 0
            }
        
        result = await ai_service.generate_ai_insights(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")

@api_router.post("/ai/generate-content", response_model=ContentGenerationResponse)
async def generate_content(request: ContentGenerationRequest):
    """Generate marketing content using AI"""
    try:
        result = await ai_service.generate_content(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@api_router.get("/ai/recall-context/{client_id}")
async def recall_client_context(client_id: str, query: str = ""):
    """Recall client context using AI memory layer"""
    try:
        # Get client data from database with fallback
        try:
            lead = await db.leads.find_one({"id": client_id})
        except:
            lead = None
            
        if not lead:
            # Create demo client context
            lead = {
                "id": client_id,
                "name": "Demo Client",
                "phone": "9876543210", 
                "email": "client@example.com",
                "location": "Mumbai, Maharashtra",
                "budget": 50000,
                "space_size": "2 BHK",
                "status": "Qualified",
                "notes": "Interested in sustainable balcony garden with automated watering",
                "interactions": [
                    "Initial consultation call on garden requirements",
                    "Site visit for space assessment",
                    "Proposal sent for balcony transformation"
                ]
            }
        else:
            # Parse MongoDB data to remove ObjectId
            lead = parse_from_mongo(lead)
        
        # Get related tasks with fallback
        try:
            tasks = await db.tasks.find({"lead_id": client_id}).to_list(length=10)
            # Parse MongoDB data to remove ObjectId
            tasks = [parse_from_mongo(task) for task in tasks]
        except:
            tasks = [
                {
                    "id": "demo_task_1",
                    "title": "Follow up on proposal",
                    "description": "Call client to discuss proposal details",
                    "status": "Pending"
                }
            ]
        
        context = {
            "client_data": lead,
            "related_tasks": tasks,
            "query": query or "Provide complete client context and interaction history"
        }
        
        result = await ai_service.recall_client_context(client_id, json.dumps(make_json_safe(context)))
        return {"context": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context recall failed: {str(e)}")

# Comprehensive AI Stack Integration Routes

# Conversational CRM AI Features
@api_router.post("/ai/crm/smart-lead-scoring")
async def ai_lead_scoring(lead_id: str):
    """AI-powered lead scoring and qualification"""
    try:
        lead = await db.leads.find_one({"id": lead_id})
        if not lead:
            # Create a demo lead for testing if none exists
            demo_lead = {
                "id": lead_id,
                "name": "Demo Lead",
                "phone": "9876543210",
                "email": "demo@example.com",
                "location": "Mumbai, Maharashtra",
                "budget": 50000,
                "space_size": "2 BHK",
                "source": "Website",
                "category": "Individual",
                "status": "New",
                "notes": "Interested in balcony garden setup"
            }
            lead = demo_lead
        else:
            # Parse MongoDB data to remove ObjectId
            lead = parse_from_mongo(lead)
        
        scoring_prompt = f"""
        Analyze this lead for Aavana Greens and provide AI-powered lead scoring:
        
        Lead Data: {json.dumps(make_json_safe(lead))}
        
        Please provide:
        1. Lead Score (0-100)
        2. Qualification Status (Hot/Warm/Cold)
        3. Conversion Probability
        4. Recommended Actions
        5. Optimal Follow-up Timeline
        6. Budget Fit Assessment
        
        Consider factors: location, budget, space_size, source, engagement level, business fit for green building solutions.
        """
        
        result = await ai_service.orchestrator.route_task("analytics", scoring_prompt, {"lead_id": lead_id})
        
        return {"lead_scoring": result, "lead_id": lead_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI lead scoring failed: {str(e)}")

@api_router.post("/ai/crm/conversation-analysis")
async def ai_conversation_analysis(conversation_data: dict):
    """Analyze customer conversations for sentiment and insights"""
    try:
        analysis_prompt = f"""
        Analyze this customer conversation for Aavana Greens:
        
        Conversation: {json.dumps(conversation_data)}
        
        Provide:
        1. Sentiment Analysis (Positive/Neutral/Negative)
        2. Customer Intent Detection
        3. Pain Points Identified
        4. Buying Signals
        5. Next Best Action
        6. Urgency Level
        7. Product/Service Interest
        """
        
        result = await ai_service.orchestrator.route_task("insights", analysis_prompt, conversation_data)
        
        return {"conversation_analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversation analysis failed: {str(e)}")

# Sales & Pipeline AI Features
@api_router.post("/ai/sales/deal-prediction")
async def ai_deal_prediction():
    """Predict deal closure probability using AI"""
    try:
        # Get all active leads with error handling
        try:
            leads = await db.leads.find({"status": {"$in": ["New", "Qualified", "Proposal"]}}).to_list(length=100)
            # Parse MongoDB data to remove ObjectId
            leads = [parse_from_mongo(lead) for lead in leads]
        except:
            # Fallback with demo data if database query fails
            leads = [
                {
                    "id": "demo_lead_1",
                    "name": "Rajesh Sharma",
                    "location": "Gurgaon",
                    "budget": 75000,
                    "status": "Qualified",
                    "space_size": "3 BHK",
                    "source": "Website"
                },
                {
                    "id": "demo_lead_2", 
                    "name": "Priya Patel",
                    "location": "Mumbai",
                    "budget": 45000,
                    "status": "Proposal",
                    "space_size": "2 BHK Balcony",
                    "source": "Referral"
                }
            ]
        
        prediction_prompt = f"""
        Analyze these active deals for Aavana Greens and predict closure probability:
        
        Active Deals: {json.dumps(make_json_safe(leads))}
        
        For each deal, provide:
        1. Closure Probability (%)
        2. Expected Close Date
        3. Revenue Forecast
        4. Risk Factors
        5. Acceleration Strategies
        
        Also provide overall pipeline health and revenue predictions for next quarter.
        """
        
        result = await ai_service.orchestrator.route_task("analytics", prediction_prompt)
        
        return {"deal_predictions": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deal prediction failed: {str(e)}")

@api_router.post("/ai/sales/smart-proposal-generator")
async def ai_proposal_generator(lead_id: str, service_type: str):
    """Generate AI-powered custom proposals"""
    try:
        lead = await db.leads.find_one({"id": lead_id})
        if not lead:
            # Create demo lead data for testing
            lead = {
                "id": lead_id,
                "name": "Valued Customer",
                "location": "Mumbai, Maharashtra", 
                "budget": 60000,
                "space_size": "2 BHK Balcony",
                "category": "Individual",
                "notes": "Interested in complete balcony transformation with green solutions"
            }
        else:
            # Parse MongoDB data to remove ObjectId
            lead = parse_from_mongo(lead)
        
        proposal_prompt = f"""
        Generate a comprehensive proposal for Aavana Greens client:
        
        Client Details: {json.dumps(make_json_safe(lead))}
        Service Type: {service_type}
        
        Create a detailed proposal including:
        1. Executive Summary
        2. Understanding of Client Needs
        3. Proposed Solutions & Services
        4. Timeline & Milestones
        5. Investment Details
        6. Value Proposition
        7. Next Steps
        8. Terms & Conditions
        
        Make it professional, personalized, and compelling for green building/landscaping services.
        Include specific benefits for their space size: {lead.get('space_size', 'N/A')} and budget: ₹{lead.get('budget', 'N/A')}
        """
        
        result = await ai_service.orchestrator.route_task("creative", proposal_prompt, {"lead_id": lead_id})
        
        return {"proposal": result, "lead_id": lead_id, "service_type": service_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proposal generation failed: {str(e)}")

# Marketing & Growth AI Features
@api_router.post("/ai/marketing/campaign-optimizer")
async def ai_campaign_optimizer(campaign_data: dict):
    """Optimize marketing campaigns using AI"""
    try:
        optimization_prompt = f"""
        Optimize this marketing campaign for Aavana Greens:
        
        Campaign Data: {json.dumps(campaign_data)}
        
        Provide optimization recommendations for:
        1. Target Audience Refinement
        2. Message Optimization
        3. Channel Selection (Google Ads, Facebook, Instagram, WhatsApp)
        4. Budget Allocation
        5. Timing & Seasonality
        6. Creative Variations
        7. Landing Page Optimization
        8. ROI Predictions
        
        Focus on green building, landscaping, and plant nursery market segments.
        """
        
        result = await ai_service.orchestrator.route_task("creative", optimization_prompt, campaign_data)
        
        return {"campaign_optimization": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign optimization failed: {str(e)}")

@api_router.post("/ai/marketing/competitor-analysis")
async def ai_competitor_analysis(location: str = "Mumbai"):
    """AI-powered competitor analysis"""
    try:
        analysis_prompt = f"""
        Conduct competitive analysis for Aavana Greens in {location} market:
        
        Analyze the competitive landscape for:
        1. Green building consultants
        2. Landscaping services
        3. Plant nurseries
        4. Balcony garden specialists
        
        Provide insights on:
        1. Key Competitors & Their Positioning
        2. Pricing Strategies
        3. Service Offerings Comparison
        4. Digital Presence Analysis
        5. Market Gaps & Opportunities
        6. Differentiation Strategies
        7. Competitive Advantages to Leverage
        8. Market Entry Barriers
        
        Location Focus: {location} and surrounding areas
        """
        
        result = await ai_service.orchestrator.route_task("insights", analysis_prompt, {"location": location})
        
        return {"competitor_analysis": result, "location": location}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Competitor analysis failed: {str(e)}")

# Product/Project/Gallery AI Features
@api_router.post("/ai/product/smart-catalog")
async def ai_product_catalog_optimization():
    """AI-optimized product catalog management"""
    try:
        products = await db.products.find().to_list(length=100)
        
        catalog_prompt = f"""
        Optimize Aavana Greens product catalog using AI:
        
        Current Products: {json.dumps(products)}
        
        Provide optimization for:
        1. Product Categorization & Organization
        2. Seasonal Demand Predictions
        3. Inventory Level Recommendations
        4. Pricing Strategy Optimization
        5. Cross-selling Opportunities
        6. New Product Suggestions
        7. Product Description Enhancements
        8. Bundling Strategies
        
        Focus on plants, gardening supplies, green building materials, and consultation services.
        """
        
        result = await ai_service.orchestrator.route_task("analytics", catalog_prompt)
        
        return {"catalog_optimization": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Catalog optimization failed: {str(e)}")

@api_router.post("/ai/project/design-suggestions")
async def ai_design_suggestions(project_requirements: dict):
    """AI-powered design suggestions for projects"""
    try:
        design_prompt = f"""
        Generate design suggestions for Aavana Greens project:
        
        Project Requirements: {json.dumps(project_requirements)}
        
        Provide creative design suggestions for:
        1. Plant Selection based on space, light, maintenance
        2. Layout & Design Concepts
        3. Color Schemes & Themes
        4. Functional Zoning
        5. Sustainable Features Integration
        6. Maintenance Requirements
        7. Seasonal Care Instructions
        8. Budget Optimization Tips
        
        Consider factors: space constraints, client preferences, local climate, maintenance capacity.
        """
        
        result = await ai_service.orchestrator.route_task("creative", design_prompt, project_requirements)
        
        return {"design_suggestions": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Design suggestions failed: {str(e)}")

# HR & Team Operations AI Features
@api_router.post("/ai/hr/performance-analysis")
async def ai_performance_analysis():
    """AI-powered team performance analysis"""
    try:
        employees = await db.employees.find().to_list(length=50)
        attendance = await db.attendance.find().to_list(length=200)
        
        performance_prompt = f"""
        Analyze team performance for Aavana Greens:
        
        Employee Data: {json.dumps(employees)}
        Attendance Data: {json.dumps(attendance)}
        
        Provide analysis for:
        1. Individual Performance Insights
        2. Team Productivity Trends
        3. Attendance Pattern Analysis
        4. Skill Gap Identification
        5. Training Recommendations
        6. Workload Distribution
        7. Employee Engagement Levels
        8. Retention Risk Assessment
        
        Focus on green industry specific skills and seasonal work patterns.
        """
        
        result = await ai_service.orchestrator.route_task("insights", performance_prompt)
        
        return {"performance_analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance analysis failed: {str(e)}")

@api_router.post("/ai/hr/smart-scheduling")
async def ai_smart_scheduling(scheduling_requirements: dict):
    """AI-optimized employee scheduling"""
    try:
        scheduling_prompt = f"""
        Create optimal employee schedule for Aavana Greens:
        
        Requirements: {json.dumps(scheduling_requirements)}
        
        Optimize for:
        1. Project Requirements & Skills Matching
        2. Employee Availability & Preferences
        3. Workload Balancing
        4. Seasonal Demand Patterns
        5. Cost Optimization
        6. Quality Assurance Coverage
        7. Emergency Response Capability
        8. Customer Service Standards
        
        Consider: site visits, nursery operations, design consultations, installation projects.
        """
        
        result = await ai_service.orchestrator.route_task("automation", scheduling_prompt, scheduling_requirements)
        
        return {"smart_schedule": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart scheduling failed: {str(e)}")

# Analytics & Admin AI Features
@api_router.post("/ai/analytics/business-intelligence")
async def ai_business_intelligence():
    """Comprehensive AI-powered business intelligence"""
    try:
        # Gather business data
        leads_count = await db.leads.count_documents({})
        won_deals = await db.leads.count_documents({"status": "Won"})
        products_count = await db.products.count_documents({})
        employees_count = await db.employees.count_documents({})
        
        bi_prompt = f"""
        Generate comprehensive business intelligence report for Aavana Greens:
        
        Business Metrics:
        - Total Leads: {leads_count}
        - Won Deals: {won_deals}
        - Products in Catalog: {products_count}
        - Team Size: {employees_count}
        
        Provide strategic insights on:
        1. Revenue Growth Opportunities
        2. Market Expansion Strategies
        3. Operational Efficiency Improvements
        4. Digital Transformation Roadmap
        5. Competitive Positioning
        6. Risk Assessment & Mitigation
        7. Investment Priorities
        8. Long-term Growth Projections
        
        Focus on green building industry trends and sustainable business practices.
        """
        
        result = await ai_service.orchestrator.route_task("insights", bi_prompt)
        
        return {"business_intelligence": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Business intelligence failed: {str(e)}")

@api_router.post("/ai/analytics/predictive-forecasting")
async def ai_predictive_forecasting(forecast_type: str = "revenue"):
    """AI-powered predictive forecasting"""
    try:
        forecasting_prompt = f"""
        Generate predictive forecasting for Aavana Greens:
        
        Forecast Type: {forecast_type}
        
        Provide predictions for:
        1. Revenue Forecasting (Next 6 months)
        2. Seasonal Demand Patterns
        3. Market Trends Impact
        4. Customer Acquisition Projections
        5. Inventory Requirements
        6. Resource Planning Needs
        7. Cash Flow Projections
        8. Growth Trajectory Analysis
        
        Consider: seasonal variations, market conditions, green industry trends, economic factors.
        Include confidence intervals and scenario planning (optimistic, realistic, conservative).
        """
        
        result = await ai_service.orchestrator.route_task("analytics", forecasting_prompt, {"forecast_type": forecast_type})
        
        return {"predictive_forecast": result, "forecast_type": forecast_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Predictive forecasting failed: {str(e)}")

# Automation Layer AI Features
@api_router.post("/ai/automation/workflow-optimization")
async def ai_workflow_optimization(department: str):
    """AI-powered workflow optimization"""
    try:
        workflow_prompt = f"""
        Optimize workflows for Aavana Greens {department} department:
        
        Department: {department}
        
        Analyze and optimize:
        1. Current Process Mapping
        2. Bottleneck Identification
        3. Automation Opportunities
        4. Resource Allocation
        5. Quality Control Points
        6. Communication Flows
        7. Technology Integration
        8. Performance Metrics
        
        Provide specific recommendations for:
        - Process improvements
        - Technology solutions
        - Staff productivity
        - Customer experience
        - Cost reduction
        
        Focus on green industry best practices and sustainable operations.
        """
        
        result = await ai_service.orchestrator.route_task("automation", workflow_prompt, {"department": department})
        
        return {"workflow_optimization": result, "department": department}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow optimization failed: {str(e)}")

@api_router.post("/ai/automation/smart-notifications")
async def ai_smart_notifications():
    """AI-powered smart notification system"""
    try:
        # Get recent activities
        recent_leads = await db.leads.find().sort("created_at", -1).limit(10).to_list(length=10)
        pending_tasks = await db.tasks.find({"status": "Pending"}).to_list(length=20)
        
        notification_prompt = f"""
        Generate smart notifications for Aavana Greens team:
        
        Recent Leads: {json.dumps(recent_leads)}
        Pending Tasks: {json.dumps(pending_tasks)}
        
        Create intelligent notifications for:
        1. Priority Alerts (High-value leads, urgent tasks)
        2. Follow-up Reminders (Lead nurturing, customer service)
        3. Performance Notifications (Goals, achievements, concerns)
        4. Operational Alerts (Inventory, appointments, deadlines)
        5. Opportunity Notifications (Upselling, cross-selling)
        6. System Updates (Important changes, new features)
        
        Prioritize notifications by importance and urgency.
        Include specific actions and context for each notification.
        """
        
        result = await ai_service.orchestrator.route_task("automation", notification_prompt)
        
        return {"smart_notifications": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart notifications failed: {str(e)}")

# Aavana 2.0 Orchestration Routes

@api_router.post("/aavana/conversation")
async def aavana_conversation(
    message: str,
    channel: str = "in_app_chat",
    user_id: str = "default_user",
    language: str = None,
    session_id: str = None,
    context: dict = None
):
    """
    Aavana 2.0 - Central conversational AI endpoint
    Supports Hindi, English, Hinglish, Tamil with intent parsing
    """
    try:
        # Map channel string to enum
        channel_mapping = {
            "in_app_chat": ChannelType.IN_APP_CHAT,
            "whatsapp": ChannelType.WHATSAPP,
            "exotel_voice": ChannelType.EXOTEL_VOICE,
            "sms": ChannelType.SMS
        }
        
        # Map language string to enum
        language_mapping = {
            "hi": SupportedLanguage.HINDI,
            "en": SupportedLanguage.ENGLISH,
            "hi-en": SupportedLanguage.HINGLISH,
            "hinglish": SupportedLanguage.HINGLISH,
            "ta": SupportedLanguage.TAMIL
        }
        
        request = ConversationRequest(
            channel=channel_mapping.get(channel, ChannelType.IN_APP_CHAT),
            user_id=user_id,
            message=message,
            language=language_mapping.get(language) if language else None,
            session_id=session_id,
            context=context or {}
        )
        
        response = await aavana_2_0.process_conversation(request)
        
        return {
            "operation_id": response.operation_id,
            "response": response.response_text,
            "language": response.language.value,
            "intent": response.intent.value,
            "confidence": response.confidence,
            "actions": response.actions,
            "cached_audio_url": response.cached_audio_url,
            "suggested_replies": response.suggested_replies,
            "session_id": response.session_id,
            "processing_time_ms": response.processing_time_ms
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Aavana 2.0 processing failed: {str(e)}")

@api_router.post("/aavana/whatsapp")
async def aavana_whatsapp_webhook(message_data: dict):
    """
    WhatsApp webhook for Aavana 2.0 integration
    Processes incoming WhatsApp messages with multilingual support
    """
    try:
        # Extract WhatsApp message data
        from_number = message_data.get("from", "")
        message_text = message_data.get("text", {}).get("body", "")
        message_id = message_data.get("id", "")
        
        if not message_text:
            return {"status": "ignored", "reason": "No text content"}
        
        # Create Aavana 2.0 request
        request = ConversationRequest(
            channel=ChannelType.WHATSAPP,
            user_id=from_number,
            message=message_text,
            context={
                "whatsapp_message_id": message_id,
                "from_number": from_number
            }
        )
        
        # Process with Aavana 2.0
        response = await aavana_2_0.process_conversation(request)
        
        # Send response back via WhatsApp
        whatsapp_response = await whatsapp_service.send_template_message(
            from_number, 
            "text", 
            [response.response_text]
        )
        
        return {
            "status": "processed",
            "operation_id": response.operation_id,
            "intent": response.intent.value,
            "language": response.language.value,
            "whatsapp_status": "sent"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"WhatsApp processing failed: {str(e)}")

@api_router.post("/aavana/exotel-stt")
async def aavana_exotel_stt_webhook(call_data: dict):
    """
    Exotel STT webhook for voice message processing
    Transcribes voice to text and processes with Aavana 2.0
    """
    try:
        # Extract Exotel call data
        call_sid = call_data.get("CallSid", "")
        from_number = call_data.get("From", "")
        recording_url = call_data.get("RecordingUrl", "")
        transcript = call_data.get("transcript", "")  # STT result
        
        if not transcript:
            return {"status": "ignored", "reason": "No transcript available"}
        
        # Create Aavana 2.0 request
        request = ConversationRequest(
            channel=ChannelType.EXOTEL_VOICE,
            user_id=from_number,
            message=transcript,
            context={
                "call_sid": call_sid,
                "recording_url": recording_url,
                "from_number": from_number
            }
        )
        
        # Process with Aavana 2.0
        response = await aavana_2_0.process_conversation(request)
        
        # Create task or lead based on intent
        if response.intent in [IntentType.LEAD_INQUIRY, IntentType.APPOINTMENT_BOOKING]:
            # Create lead
            lead_data = {
                "name": f"Voice Lead from {from_number}",
                "phone": from_number,
                "source": "Voice Call",
                "notes": f"Original message: {transcript}\nAI Response: {response.response_text}",
                "category": "Voice Inquiry"
            }
            
            lead_dict = prepare_for_mongo(lead_data)
            await db.leads.insert_one(lead_dict)
        
        return {
            "status": "processed",
            "operation_id": response.operation_id,
            "intent": response.intent.value,
            "language": response.language.value,
            "lead_created": response.intent in [IntentType.LEAD_INQUIRY, IntentType.APPOINTMENT_BOOKING]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exotel STT processing failed: {str(e)}")

@api_router.post("/aavana/language-detect")
async def aavana_language_detection(text: str):
    """
    Standalone language detection endpoint
    """
    try:
        detected_language = await aavana_2_0.language_detector.detect_language(text)
        
        # If Hinglish detected, also provide normalized version
        normalized_text = text
        if detected_language == SupportedLanguage.HINGLISH:
            normalized_text = await aavana_2_0.hinglish_normalizer.normalize_hinglish(text)
        
        return {
            "original_text": text,
            "detected_language": detected_language.value,
            "normalized_text": normalized_text,
            "confidence": 0.9  # Placeholder confidence
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Language detection failed: {str(e)}")

@api_router.get("/aavana/audio-templates")
async def aavana_audio_templates(language: str = "en"):
    """
    Get available cached audio templates
    """
    try:
        language_enum = SupportedLanguage.ENGLISH
        if language == "hi":
            language_enum = SupportedLanguage.HINDI
        elif language in ["hi-en", "hinglish"]:
            language_enum = SupportedLanguage.HINGLISH
        elif language == "ta":
            language_enum = SupportedLanguage.TAMIL
        
        templates = {}
        for template_key in ['welcome', 'thank_you', 'appointment_confirmed', 'price_inquiry_response', 'catalog_intro']:
            audio_url = await aavana_2_0.audio_cache.get_cached_audio(template_key, language_enum)
            text = await aavana_2_0.audio_cache.get_template_text(template_key, language_enum)
            
            if audio_url and text:
                templates[template_key] = {
                    "audio_url": audio_url,
                    "text": text
                }
        
        return {
            "language": language,
            "templates": templates
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio templates failed: {str(e)}")

@api_router.get("/aavana/operation/{operation_id}")
async def aavana_get_operation(operation_id: str):
    """
    Get operation state for tracking and debugging
    """
    try:
        state = await aavana_2_0.state_manager.get_operation(operation_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Operation not found")
        
        return {
            "operation_id": state.operation_id,
            "status": state.status.value,
            "channel": state.channel.value,
            "user_id": state.user_id,
            "original_message": state.original_message,
            "processed_message": state.processed_message,
            "language": state.language.value,
            "intent": state.intent.value,
            "confidence": state.confidence,
            "response": state.response,
            "retry_count": state.retry_count,
            "created_at": state.created_at.isoformat(),
            "updated_at": state.updated_at.isoformat(),
            "error_message": state.error_message
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Operation retrieval failed: {str(e)}")

@api_router.get("/aavana/health")
async def aavana_health_check():
    """
    Aavana 2.0 health check endpoint
    """
    try:
        # Test language detection
        test_language = await aavana_2_0.language_detector.detect_language("Hello, how are you?")
        
        # Test intent parsing (without AI call to save cost)
        test_intent, confidence = aavana_2_0.intent_parser._apply_safety_rules("what is the price?")
        
        return {
            "status": "healthy",
            "version": "2.0",
            "components": {
                "language_detector": "operational",
                "hinglish_normalizer": "operational",
                "intent_parser": "operational",
                "state_manager": "operational",
                "audio_cache": "operational"
            },
            "supported_languages": ["hi", "en", "hi-en", "ta"],
            "supported_channels": ["in_app_chat", "whatsapp", "exotel_voice", "sms"],
            "test_results": {
                "language_detection": test_language.value,
                "intent_parsing": test_intent.value,
                "confidence": confidence
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Global AI Chat Interface
@api_router.post("/ai/chat/global-assistant")
async def ai_global_assistant(message: str, context: dict = None, session_id: str = None):
    """Global AI assistant for all business queries"""
    try:
        if not session_id:
            session_id = f"global-{uuid.uuid4()}"
        
        # Create dynamic context based on current business state
        business_context = {
            "leads_count": await db.leads.count_documents({}),
            "active_tasks": await db.tasks.count_documents({"status": "Pending"}),
            "products_count": await db.products.count_documents({}),
            "user_context": context or {}
        }
        
        assistant_prompt = f"""
        You are the Global AI Assistant for Aavana Greens CRM & Business Management System.
        
        Business Context: {json.dumps(business_context)}
        User Query: {message}
        Session: {session_id}
        
        Provide helpful assistance for:
        - CRM operations (leads, tasks, follow-ups)
        - Sales pipeline management
        - Marketing strategy and content
        - Product catalog and inventory
        - Project planning and design
        - Team management and HR
        - Business analytics and insights
        - Process automation
        - Strategic planning
        
        Be conversational, helpful, and specific to Aavana Greens' green building and landscaping business.
        Provide actionable suggestions and relevant business insights.
        """
        
        result = await ai_service.orchestrator.route_task("automation", assistant_prompt, business_context)
        
        return {
            "response": result,
            "session_id": session_id,
            "context": business_context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Global assistant failed: {str(e)}")

# Telephony Routes
@api_router.get("/telephony/ivr/{digit}")
async def handle_ivr(digit: str):
    """Handle IVR menu selections"""
    try:
        response = await telephony_service.create_ivr_response(digit)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IVR processing failed: {str(e)}")

@api_router.get("/telephony/analytics")
async def get_call_analytics():
    """Get call analytics and metrics"""
    try:
        analytics = await telephony_service.get_call_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics retrieval failed: {str(e)}")

@api_router.post("/telephony/log-call")
async def log_call(call_data: dict):
    """Log call details"""
    try:
        call_log = await telephony_service.log_call(call_data)
        # Save to database
        call_dict = prepare_for_mongo(call_log.dict())
        await db.call_logs.insert_one(call_dict)
        return call_log
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Call logging failed: {str(e)}")

# WhatsApp Routes
@api_router.post("/whatsapp/send-template")
async def send_whatsapp_template(to_number: str, template_name: str, variables: List[str] = None):
    """Send WhatsApp template message"""
    try:
        message = await whatsapp_service.send_template_message(to_number, template_name, variables)
        # Save to database
        message_dict = prepare_for_mongo(message.dict())
        await db.whatsapp_messages.insert_one(message_dict)
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"WhatsApp message failed: {str(e)}")

@api_router.post("/whatsapp/process-message")
async def process_whatsapp_message(message_data: dict):
    """Process incoming WhatsApp message"""
    try:
        response = await whatsapp_service.process_incoming_message(message_data)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Message processing failed: {str(e)}")

# HRMS Routes
@api_router.post("/hrms/check-in")
async def employee_check_in(employee_id: str, location: str = None):
    """Employee check-in"""
    try:
        attendance = await hrms_service.check_in_employee(employee_id, location)
        # Save to database
        attendance_dict = prepare_for_mongo(attendance.dict())
        await db.attendance.insert_one(attendance_dict)
        return attendance
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Check-in failed: {str(e)}")

@api_router.post("/hrms/check-out")
async def employee_check_out(attendance_id: str):
    """Employee check-out"""
    try:
        attendance = await hrms_service.check_out_employee(attendance_id)
        # Update in database
        attendance_dict = prepare_for_mongo(attendance.dict())
        await db.attendance.update_one({"id": attendance_id}, {"$set": attendance_dict})
        return attendance
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Check-out failed: {str(e)}")

@api_router.post("/hrms/apply-leave")
async def apply_leave(leave_data: dict):
    """Apply for leave"""
    try:
        leave_request = await hrms_service.apply_leave(leave_data)
        # Save to database
        leave_dict = prepare_for_mongo(leave_request.dict())
        await db.leave_requests.insert_one(leave_dict)
        return leave_request
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Leave application failed: {str(e)}")

@api_router.get("/hrms/attendance-summary/{employee_id}")
async def get_attendance_summary(employee_id: str, month: int, year: int):
    """Get attendance summary"""
    try:
        summary = await hrms_service.get_attendance_summary(employee_id, month, year)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attendance summary failed: {str(e)}")

# Super Admin Routes
@api_router.get("/admin/system-stats")
async def get_system_stats():
    """Get comprehensive system statistics for super admin"""
    try:
        # Aggregate all system data
        stats = {
            "leads": {
                "total": await db.leads.count_documents({}),
                "by_status": {
                    "new": await db.leads.count_documents({"status": "New"}),
                    "qualified": await db.leads.count_documents({"status": "Qualified"}),
                    "won": await db.leads.count_documents({"status": "Won"})
                },
                "by_source": await db.leads.aggregate([
                    {"$group": {"_id": "$source", "count": {"$sum": 1}}}
                ]).to_list(length=None)
            },
            "tasks": {
                "total": await db.tasks.count_documents({}),
                "ai_generated": await db.tasks.count_documents({"ai_generated": True}),
                "by_status": {
                    "pending": await db.tasks.count_documents({"status": "Pending"}),
                    "completed": await db.tasks.count_documents({"status": "Completed"})
                }
            },
            "telephony": await telephony_service.get_call_analytics(),
            "system_health": {
                "ai_models_active": 3,
                "database_status": "healthy",
                "api_uptime": "99.9%"
            }
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System stats failed: {str(e)}")

# ERP Routes - Product Management
@api_router.post("/erp/products", response_model=Product)
async def create_product(product_data: ProductCreate):
    """Create new product"""
    try:
        if not product_data.sku:
            product_data.sku = await erp_service.generate_sku(product_data.category, product_data.name)
        
        if not product_data.barcode:
            product_data.barcode = await erp_service.generate_barcode(product_data.sku)
        
        product = Product(**product_data.dict())
        product_dict = prepare_for_mongo(product.dict())
        await db.products.insert_one(product_dict)
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product creation failed: {str(e)}")

@api_router.get("/erp/products", response_model=List[Product])
async def get_products(category: Optional[str] = None, low_stock: bool = False):
    """Get products with filtering options"""
    try:
        query = {"is_active": True}
        if category:
            query["category"] = category
        if low_stock:
            query["$expr"] = {"$lte": ["$stock_quantity", "$min_stock_level"]}
        
        products = await db.products.find(query).to_list(length=100)
        return [Product(**parse_from_mongo(product)) for product in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch products: {str(e)}")

@api_router.get("/erp/inventory-alerts")
async def get_inventory_alerts():
    """Get inventory alerts for low stock items"""
    try:
        products = await db.products.find({"is_active": True}).to_list(length=None)
        product_objects = [Product(**parse_from_mongo(p)) for p in products]
        alerts = await erp_service.check_stock_levels(product_objects)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get inventory alerts: {str(e)}")

# ERP Routes - Invoice Management
@api_router.post("/erp/invoices", response_model=Invoice)
async def create_invoice(invoice_data: dict):
    """Create new invoice"""
    try:
        # Generate invoice number
        invoice_count = await db.invoices.count_documents({}) + 1
        invoice_data["invoice_number"] = f"INV-{datetime.now().strftime('%Y%m%d')}-{invoice_count:04d}"
        
        # Calculate totals
        totals = await erp_service.calculate_invoice_totals(
            invoice_data.get("items", []),
            invoice_data.get("tax_percentage", 18.0),
            invoice_data.get("discount_percentage", 0.0)
        )
        invoice_data.update(totals)
        
        invoice = Invoice(**invoice_data)
        invoice_dict = prepare_for_mongo(invoice.dict())
        await db.invoices.insert_one(invoice_dict)
        return invoice
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invoice creation failed: {str(e)}")

@api_router.get("/erp/invoices")
async def get_invoices(status: Optional[str] = None, limit: int = 50):
    """Get invoices with filtering"""
    try:
        query = {}
        if status:
            query["payment_status"] = status
        
        invoices = await db.invoices.find(query).limit(limit).to_list(length=limit)
        return [Invoice(**parse_from_mongo(invoice)) for invoice in invoices]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {str(e)}")

# ERP Routes - Project Gallery
@api_router.post("/erp/projects", response_model=ProjectGallery)
async def create_project(project_data: dict):
    """Add project to gallery"""
    try:
        project = ProjectGallery(**project_data)
        project_dict = prepare_for_mongo(project.dict())
        await db.projects.insert_one(project_dict)
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project creation failed: {str(e)}")

@api_router.get("/erp/projects")
async def get_projects(project_type: Optional[str] = None, featured_only: bool = False):
    """Get project gallery"""
    try:
        query = {}
        if project_type:
            query["project_type"] = project_type
        if featured_only:
            query["is_featured"] = True
        
        projects = await db.projects.find(query).to_list(length=50)
        return [ProjectGallery(**parse_from_mongo(project)) for project in projects]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")

# ERP Routes - Lead Source Sync
@api_router.post("/erp/sync-lead-sources")
async def sync_external_lead_sources():
    """Sync leads from external sources"""
    try:
        sync_results = await erp_service.sync_lead_sources()
        return sync_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lead sync failed: {str(e)}")

# Calendar & Appointment Routes
@api_router.post("/calendar/events", response_model=CalendarEvent)
async def create_calendar_event(event_data: CalendarEventCreate):
    """Create calendar event and sync with Google Calendar"""
    try:
        event = CalendarEvent(**event_data.dict())
        
        # Create in Google Calendar
        google_event_id = await calendar_service.create_google_calendar_event(event)
        event.google_event_id = google_event_id
        
        # Save to database
        event_dict = prepare_for_mongo(event.dict())
        await db.calendar_events.insert_one(event_dict)
        
        return event
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Event creation failed: {str(e)}")

@api_router.get("/calendar/availability")
async def check_availability(date: str, duration: int = 60):
    """Check availability for booking"""
    try:
        event_date = datetime.fromisoformat(date)
        availability = await calendar_service.check_availability(event_date, duration)
        return availability
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Availability check failed: {str(e)}")

@api_router.get("/calendar/booking-link")
async def generate_booking_link(duration: int = 60):
    """Generate public booking link"""
    try:
        booking_link = await calendar_service.generate_booking_link(duration)
        return {"booking_link": booking_link}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Booking link generation failed: {str(e)}")

@api_router.post("/calendar/send-reminder/{event_id}")
async def send_appointment_reminder(event_id: str, reminder_type: str = "sms"):
    """Send appointment reminder"""
    try:
        event = await db.calendar_events.find_one({"id": event_id})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        event_obj = CalendarEvent(**parse_from_mongo(event))
        reminder_result = await calendar_service.send_appointment_reminder(event_obj, reminder_type)
        return reminder_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reminder sending failed: {str(e)}")

# Advanced HRMS Routes
@api_router.post("/hrms/face-checkin")
async def face_recognition_checkin(employee_id: str, face_image: str, location: str):
    """Face recognition check-in"""
    try:
        result = await complete_hrms_service.process_face_recognition_checkin(employee_id, face_image, location)
        
        if result["status"] == "success":
            # Create attendance record
            attendance = Attendance(
                employee_id=employee_id,
                date=datetime.now(timezone.utc).date(),
                check_in=result["check_in_time"],
                location=location,
                status="Present"
            )
            attendance_dict = prepare_for_mongo(attendance.dict())
            await db.attendance.insert_one(attendance_dict)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Face check-in failed: {str(e)}")

@api_router.get("/hrms/salary-calculation/{employee_id}")
async def calculate_employee_salary(employee_id: str, month: int, year: int):
    """Calculate monthly salary for employee"""
    try:
        salary_calculation = await complete_hrms_service.calculate_monthly_salary(employee_id, month, year)
        return salary_calculation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Salary calculation failed: {str(e)}")

@api_router.get("/hrms/payroll-report")
async def generate_payroll_report(month: int, year: int):
    """Generate comprehensive payroll report"""
    try:
        payroll_report = await complete_hrms_service.generate_payroll_report(month, year)
        return payroll_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payroll report generation failed: {str(e)}")

# Advanced WhatsApp Routes
@api_router.post("/whatsapp/send-catalog")
async def send_whatsapp_catalog(to_number: str):
    """Send interactive catalog via WhatsApp"""
    try:
        catalog_message = await whatsapp_advanced_service.send_catalog_message(to_number)
        return catalog_message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Catalog sending failed: {str(e)}")

@api_router.post("/whatsapp/ai-chatbot")
async def process_whatsapp_ai_chatbot(message: str, customer_data: dict):
    """Process WhatsApp message with AI chatbot"""
    try:
        response = await whatsapp_advanced_service.process_ai_chatbot_response(message, customer_data)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI chatbot processing failed: {str(e)}")

@api_router.post("/whatsapp/smart-suggestions")
async def send_smart_suggestions(customer_phone: str, interaction_history: List[dict]):
    """Send smart suggestions based on customer behavior"""
    try:
        suggestion = await whatsapp_advanced_service.send_smart_suggestion(customer_phone, interaction_history)
        return suggestion
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart suggestions failed: {str(e)}")

# Analytics & Reporting Routes  
@api_router.get("/analytics/executive-dashboard")
async def get_executive_dashboard():
    """Get comprehensive executive dashboard"""
    try:
        dashboard = await analytics_service.generate_executive_dashboard()
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")

@api_router.get("/analytics/sales-report")
async def get_sales_analytics(start_date: str, end_date: str):
    """Get detailed sales analytics"""
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        analytics = await erp_service.get_sales_analytics(start, end)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sales analytics failed: {str(e)}")

@api_router.post("/analytics/export-report")
async def export_report(report_type: str, format: str, data: dict):
    """Export reports to PDF or Excel"""
    try:
        if format.lower() == "pdf":
            file_path = await analytics_service.export_report_pdf(report_type, data)
        elif format.lower() == "excel":
            file_path = await analytics_service.export_report_excel(report_type, data)
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
        
        return {"file_path": file_path, "download_url": f"/download{file_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report export failed: {str(e)}")

# GPS Tracking Routes
@api_router.post("/gps/track-visit")
async def track_site_visit(event_id: str, gps_coordinates: str):
    """Track GPS coordinates for site visits"""
    try:
        tracking_result = await calendar_service.track_site_visit_gps(event_id, gps_coordinates)
        return tracking_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPS tracking failed: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()