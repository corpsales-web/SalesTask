import os
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, WebSocket, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import hmac
import hashlib
import httpx

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# ----------------------
# App & CORS
# ----------------------
app = FastAPI(title="Aavana CRM API")

CORS_ORIGINS = os.environ.get("CRM_CORS_ORIGINS", "*")
CORS_LIST = [o.strip().rstrip('/') for o in CORS_ORIGINS.split(',') if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_LIST if CORS_LIST else ["*"],
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

@app.put("/api/tasks/{task_id}/status")
async def update_task_status(task_id: str, body: Dict[str, Any], db=Depends(get_db)):
    status_val = (body or {}).get("status")
    if not status_val:
        raise HTTPException(status_code=400, detail="status is required")
    res = await db["tasks"].update_one({"id": task_id}, {"$set": {"status": status_val, "updated_at": now_iso()}})
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

# ----------------------
# Dashboard Stats
# ----------------------
@app.get("/api/dashboard/stats")
async def dashboard_stats(db=Depends(get_db)):
    total_leads = await db["leads"].count_documents({})
    active_leads = await db["leads"].count_documents({"status": {"$nin": ["Closed", "Lost", "Archived"]}})
    pending_tasks = await db["tasks"].count_documents({"status": {"$in": ["Open", "Pending", "In Progress"]}})

    won_leads = await db["leads"].count_documents({"status": "Won"})
    conversion_rate = int(round((won_leads / total_leads) * 100)) if total_leads else 0

    total_revenue = 0

    return {
        "totalLeads": total_leads,
        "activeLeads": active_leads,
        "conversion_rate": conversion_rate,
        "totalRevenue": total_revenue,
        "pendingTasks": pending_tasks,
    }

# ----------------------
# WhatsApp (360dialog) Integration
# ----------------------
D360_API_KEY = os.environ.get("WHATSAPP_360DIALOG_API_KEY", "")
D360_BASE_URL = os.environ.get("WHATSAPP_BASE_URL", "https://waba-v2.360dialog.io")
WA_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "")
WA_WEBHOOK_SECRET = os.environ.get("WHATSAPP_WEBHOOK_SECRET", "")


def _hmac_valid(body: bytes, signature_header: Optional[str]) -> bool:
    if not WA_WEBHOOK_SECRET:
        # If no secret configured, skip signature verification (staging)
        return True
    if not signature_header:
        return False
    # Accept forms like 'sha256=...' or raw hex
    try:
        provided = signature_header
        if provided.lower().startswith("sha256="):
            provided = provided.split("=", 1)[1]
        digest = hmac.new(WA_WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(digest, provided)
    except Exception:
        return False


@app.get("/api/whatsapp/webhook")
async def whatsapp_webhook_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_token and WA_VERIFY_TOKEN and hub_token == WA_VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge or "")
    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/api/whatsapp/webhook")
async def whatsapp_webhook_receive(request: Request, db=Depends(get_db)):
    body = await request.body()
    sig = request.headers.get("x-signature") or request.headers.get("X-Signature") or request.headers.get("X-Hub-Signature-256")
    if not _hmac_valid(body, sig):
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    doc = {
        "id": str(uuid.uuid4()),
        "received_at": now_iso(),
        "raw": payload,
        "source": "360dialog",
        "type": payload.get("object", "event")
    }
    await db["whatsapp_events"].insert_one(doc)

    return {"success": True}


class WhatsAppSendRequest(BaseModel):
    to: str
    text: Optional[str] = None
    # Optional future additions: template dict, media, etc.


@app.get("/api/whatsapp/messages")
async def whatsapp_messages(limit: int = Query(20, ge=1, le=100), db=Depends(get_db)):
    cursor = db["whatsapp_events"].find({}, {"_id": 0}).sort("received_at", -1).limit(limit)
    items = await cursor.to_list(length=limit)
    return items


@app.post("/api/whatsapp/send")
async def whatsapp_send(body: WhatsAppSendRequest, db=Depends(get_db)):
    if not body.to:
        raise HTTPException(status_code=400, detail="'to' is required")

    # If API key missing → stub mode: store and return mocked success
    if not D360_API_KEY:
        rec = {
            "id": str(uuid.uuid4()),
            "queued_at": now_iso(),
            "to": body.to,
            "text": body.text or "",
            "mode": "stub",
            "provider": "360dialog",
        }
        await db["whatsapp_outbox"].insert_one(rec)
        return {"success": True, "mode": "stub", "message": "No API key configured. Stored locally.", "id": rec["id"]}

    # Real send via 360dialog
    payload: Dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": body.to,
        "type": "text",
        "text": {"body": body.text or ""},
    }

    headers = {
        "D360-API-KEY": D360_API_KEY,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(f"{D360_BASE_URL}/messages", headers=headers, json=payload)
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=f"Provider error: {resp.text}")
        data = resp.json()

    stored = {
        "id": str(uuid.uuid4()),
        "sent_at": now_iso(),
        "to": body.to,
        "payload": payload,
        "provider_response": data,
        "provider": "360dialog",
    }
    await db["whatsapp_sent"].insert_one(stored)

    return {"success": True, "provider": "360dialog", "data": data}
