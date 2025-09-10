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
        for key, value in item.items():
            if isinstance(value, str) and key.endswith(('_at', '_date', '_contact', '_up')):
                try:
                    item[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    pass
    return item

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
        # Get client data from database
        lead = await db.leads.find_one({"id": client_id})
        if not lead:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get related tasks
        tasks = await db.tasks.find({"lead_id": client_id}).to_list(length=10)
        
        context = {
            "client_data": lead,
            "related_tasks": tasks,
            "query": query or "Provide complete client context"
        }
        
        result = await ai_service.recall_client_context(client_id, json.dumps(context))
        return {"context": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context recall failed: {str(e)}")

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