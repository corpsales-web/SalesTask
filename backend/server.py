from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from enum import Enum


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

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    assigned_to: Optional[str] = None
    lead_id: Optional[str] = None
    due_date: Optional[datetime] = None

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
    return {"message": "Aavana Greens CRM API"}

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
        conversion_rate=round(conversion_rate, 2)
    )

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