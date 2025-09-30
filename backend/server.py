import os
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, WebSocket, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# ----------------------
# App & CORS
# ----------------------
app = FastAPI(title="Aavana CRM API")

CORS_ORIGINS = os.environ.get("CRM_CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------
# Mongo
# ----------------------
MONGO_URL = os.environ.get("MONGO_URL")
_mongo_client: Optional[AsyncIOMotorClient] = None

async def get_db() -> AsyncIOMotorDatabase:
    global _mongo_client
    if not MONGO_URL:
        raise HTTPException(status_code=500, detail="MONGO_URL is not configured")
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(MONGO_URL)
    # Use database from URI when present; avoid hardcoding DB name
    db = _mongo_client.get_default_database()
    if db is None:
        # No DB present in URI → require user to include a database in MONGO_URL
        raise HTTPException(status_code=500, detail="Mongo URI must include a database name (e.g., mongodb://host:27017/aavana_crm)")
    return db

# ----------------------
# Helpers
# ----------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# ----------------------
# Health (always on)
# ----------------------
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "crm-backend", "time": now_iso()}

# ----------------------
# STT placeholders (Phase 3 wiring later)
# ----------------------
@app.post("/api/stt/chunk")
async def stt_chunk(_: Dict[str, Any] | None = None):
    return {"success": False, "message": "STT not configured. Will enable after Google STT credentials are provided."}

@app.websocket("/api/stt/stream")
async def stt_stream(ws: WebSocket):
    await ws.accept()
    await ws.send_text(json.dumps({
        "type": "error",
        "message": "STT not configured (awaiting Google STT v2 credentials)",
    }))
    await ws.close()

# ----------------------
# Models (Pydantic)
# ----------------------
class LeadCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = Field(default="New")
    source: Optional[str] = None
    notes: Optional[str] = None

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[str] = None  # ISO string
    status: Optional[str] = Field(default="Open")
    lead_id: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None
    lead_id: Optional[str] = None

# ----------------------
# Leads Endpoints
# ----------------------
@app.post("/api/leads")
async def create_lead(body: LeadCreate, db=Depends(get_db)):
    doc = body.dict(exclude_none=True)
    doc["id"] = str(uuid.uuid4())
    doc.setdefault("status", "New")
    doc["created_at"] = now_iso()
    doc["updated_at"] = now_iso()
    await db["leads"].insert_one(doc)
    doc.pop("_id", None)
    return {"success": True, "lead": doc}

@app.get("/api/leads")
async def list_leads(
    status: Optional[str] = None,
    source: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
):
    q: Dict[str, Any] = {}
    if status:
        q["status"] = status
    if source:
        q["source"] = source
    skip = (page - 1) * limit
    cursor = db["leads"].find(q, {"_id": 0}).skip(skip).limit(limit)
    items = await cursor.to_list(length=limit)
    total = await db["leads"].count_documents(q)
    return {"items": items, "page": page, "limit": limit, "total": total}

@app.put("/api/leads/{lead_id}")
async def update_lead(lead_id: str, body: LeadUpdate, db=Depends(get_db)):
    updates = body.dict(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    updates["updated_at"] = now_iso()
    res = await db["leads"].update_one({"id": lead_id}, {"$set": updates})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    doc = await db["leads"].find_one({"id": lead_id}, {"_id": 0})
    return {"success": True, "lead": doc}

@app.delete("/api/leads/{lead_id}")
async def delete_lead(lead_id: str, db=Depends(get_db)):
    res = await db["leads"].delete_one({"id": lead_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"success": True}

# ----------------------
# Tasks Endpoints
# ----------------------
@app.post("/api/tasks")
async def create_task(body: TaskCreate, db=Depends(get_db)):
    doc = body.dict(exclude_none=True)
    doc["id"] = str(uuid.uuid4())
    doc.setdefault("status", "Open")
    doc["created_at"] = now_iso()
    doc["updated_at"] = now_iso()
    await db["tasks"].insert_one(doc)
    doc.pop("_id", None)
    return {"success": True, "task": doc}

@app.get("/api/tasks")
async def list_tasks(
    status: Optional[str] = None,
    assignee: Optional[str] = None,
    lead_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
):
    q: Dict[str, Any] = {}
    if status:
        q["status"] = status
    if assignee:
        q["assignee"] = assignee
    if lead_id:
        q["lead_id"] = lead_id
    skip = (page - 1) * limit
    cursor = db["tasks"].find(q, {"_id": 0}).skip(skip).limit(limit)
    items = await cursor.to_list(length=limit)
    total = await db["tasks"].count_documents(q)
    return {"items": items, "page": page, "limit": limit, "total": total}

@app.put("/api/tasks/{task_id}")
async def update_task(task_id: str, body: TaskUpdate, db=Depends(get_db)):
    updates = body.dict(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    updates["updated_at"] = now_iso()
    res = await db["tasks"].update_one({"id": task_id}, {"$set": updates})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    doc = await db["tasks"].find_one({"id": task_id}, {"_id": 0})
    return {"success": True, "task": doc}

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str, db=Depends(get_db)):
    res = await db["tasks"].delete_one({"id": task_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True}