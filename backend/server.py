import os
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Tuple

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

DEFAULT_COUNTRY_CODE = "+91"
DEFAULT_OWNER_MOBILE = "+919999139938"  # Manager


def normalize_phone_india(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    digits = "".join(ch for ch in str(raw) if ch.isdigit())
    if not digits:
        return None
    # If starts with country 91 and total 12, keep
    if digits.startswith("91"):
        if len(digits) == 12:
            return "+" + digits
        # Sometimes comes as 91 + 10 digits or just 91 + extra
        if len(digits) > 12:
            digits = digits[:12]
            return "+" + digits
        if len(digits) == 11:  # rare cases missing a digit
            return "+" + digits
    # If exactly 10, assume India
    if len(digits) == 10:
        return DEFAULT_COUNTRY_CODE + digits
    # Fallback: prefix '+' if missing
    return "+" + digits if not raw.startswith("+") else raw

async def find_lead_by_phone(db: AsyncIOMotorDatabase, phone_norm: str) -> Optional[Dict[str, Any]]:
    # Iterate leads and compare normalized phones (MVP)
    cursor = db["leads"].find({}, {"_id": 0})
    leads = await cursor.to_list(length=None)
    for ld in leads:
        p = ld.get("phone")
        if p:
            if normalize_phone_india(p) == phone_norm:
                return ld
    return None

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
    owner_mobile: Optional[str] = None

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    owner_mobile: Optional[str] = None

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

    # Store raw event
    event_doc = {
        "id": str(uuid.uuid4()),
        "received_at": now_iso(),
        "raw": payload,
        "source": "360dialog",
        "type": payload.get("object", "event")
    }
    await db["whatsapp_events"].insert_one(event_doc)

    # Normalize and store messages + upsert conversation
    try:
        entries = payload.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for ch in changes:
                val = ch.get("value", {})
                msgs = val.get("messages", [])
                meta = val.get("metadata", {})
                for m in msgs:
                    from_raw = m.get("from")
                    from_norm = normalize_phone_india(from_raw)
                    ts = m.get("timestamp")
                    ts_dt = datetime.fromtimestamp(int(ts), tz=timezone.utc) if ts else datetime.now(timezone.utc)
                    mtype = m.get("type", "text")
                    text = (m.get("text") or {}).get("body") if mtype == "text" else None

                    # Link to lead if possible
                    linked_lead = await find_lead_by_phone(db, from_norm) if from_norm else None
                    lead_id = linked_lead.get("id") if linked_lead else None

                    # Store normalized message
                    msg_doc = {
                        "id": str(uuid.uuid4()),
                        "direction": "inbound",
                        "from": from_norm,
                        "to": meta.get("display_phone_number"),
                        "type": mtype,
                        "text": text,
                        "timestamp": ts_dt.isoformat(),
                        "lead_id": lead_id,
                    }
                    await db["whatsapp_messages"].insert_one(msg_doc)

                    # Upsert conversation
                    conv_key = {"contact": from_norm}
                    existing = await db["whatsapp_conversations"].find_one(conv_key)
                    owner_mobile = None
                    if linked_lead and linked_lead.get("owner_mobile"):
                        owner_mobile = normalize_phone_india(linked_lead.get("owner_mobile"))
                    if not owner_mobile:
                        owner_mobile = DEFAULT_OWNER_MOBILE

                    conv_update = {
                        "$set": {
                            "contact": from_norm,
                            "lead_id": lead_id,
                            "owner_mobile": owner_mobile,
                            "last_message_at": ts_dt.isoformat(),
                        },
                        "$inc": {"unread_count": 1}
                    }
                    await db["whatsapp_conversations"].update_one(conv_key, conv_update, upsert=True)
    except Exception:
        # Do not fail webhook on normalization issues
        pass

    return {"success": True}


class WhatsAppSendRequest(BaseModel):
    to: str
    text: Optional[str] = None

class WhatsAppSendTemplateRequest(BaseModel):
    to: str
    template_name: str
    language_code: Optional[str] = "en"
    components: Optional[List[Dict[str, Any]]] = None


@app.get("/api/whatsapp/messages")
async def whatsapp_messages(limit: int = Query(20, ge=1, le=100), db=Depends(get_db)):
    cursor = db["whatsapp_events"].find({}, {"_id": 0}).sort("received_at", -1).limit(limit)
    items = await cursor.to_list(length=limit)
    return items


@app.get("/api/whatsapp/conversations")
async def whatsapp_conversations(limit: int = Query(50, ge=1, le=200), db=Depends(get_db)):
    cursor = db["whatsapp_conversations"].find({}, {"_id": 0}).sort("last_message_at", -1).limit(limit)
    items = await cursor.to_list(length=limit)
    # enrich with lead name if available
    result = []
    for it in items:
        lead_name = None
        if it.get("lead_id"):
            lead = await db["leads"].find_one({"id": it["lead_id"]}, {"_id": 0, "name": 1})
            lead_name = lead.get("name") if lead else None
        # SLA age seconds
        try:
            last_dt = datetime.fromisoformat(it.get("last_message_at")).astimezone(timezone.utc)
        except Exception:
            last_dt = datetime.now(timezone.utc)
        age_sec = int((datetime.now(timezone.utc) - last_dt).total_seconds())
        it["lead_name"] = lead_name
        it["age_sec"] = age_sec
        result.append(it)
    return result


@app.post("/api/whatsapp/conversations/{contact}/read")
async def whatsapp_conversation_read(contact: str, db=Depends(get_db)):
    contact_norm = normalize_phone_india(contact)
    await db["whatsapp_conversations"].update_one({"contact": contact_norm}, {"$set": {"unread_count": 0, "last_read_at": now_iso()}})
    return {"success": True}


@app.get("/api/whatsapp/lead_timeline/{lead_id}")
async def whatsapp_lead_timeline(lead_id: str, limit: int = Query(10, ge=1, le=100), db=Depends(get_db)):
    # find messages linked by lead_id
    cursor = db["whatsapp_messages"].find({"lead_id": lead_id}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    msgs = await cursor.to_list(length=limit)
    return {"items": msgs}


@app.get("/api/whatsapp/session_status")
async def whatsapp_session_status(contact: str, db=Depends(get_db)):
    contact_norm = normalize_phone_india(contact)
    # last inbound message from this contact within 24h
    last = await db["whatsapp_messages"].find_one({"from": contact_norm, "direction": "inbound"}, sort=[("timestamp", -1)])
    if not last:
        return {"within_24h": False, "last_inbound": None}
    try:
        last_dt = datetime.fromisoformat(last.get("timestamp")).astimezone(timezone.utc)
    except Exception:
        last_dt = datetime.now(timezone.utc) - timedelta(days=2)
    within = (datetime.now(timezone.utc) - last_dt) < timedelta(hours=24)
    return {"within_24h": within, "last_inbound": last.get("timestamp")}


@app.post("/api/whatsapp/send")
async def whatsapp_send(body: WhatsAppSendRequest, db=Depends(get_db)):
    if not body.to:
        raise HTTPException(status_code=400, detail="'to' is required")
    to_norm = normalize_phone_india(body.to)

    # If API key missing → stub mode: store and return mocked success
    if not D360_API_KEY:
        rec = {
            "id": str(uuid.uuid4()),
            "queued_at": now_iso(),
            "to": to_norm,
            "text": body.text or "",
            "mode": "stub",
            "provider": "360dialog",
        }
        await db["whatsapp_outbox"].insert_one(rec)
        # reduce unread Count of conversation since we responded
        await db["whatsapp_conversations"].update_one({"contact": to_norm}, {"$set": {"unread_count": 0}})
        return {"success": True, "mode": "stub", "message": "No API key configured. Stored locally.", "id": rec["id"]}

    # Real send via 360dialog
    payload: Dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_norm,
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
        "to": to_norm,
        "payload": payload,
        "provider_response": data,
        "provider": "360dialog",
    }
    await db["whatsapp_sent"].insert_one(stored)
    await db["whatsapp_conversations"].update_one({"contact": to_norm}, {"$set": {"unread_count": 0}})

    return {"success": True, "provider": "360dialog", "data": data}


@app.post("/api/whatsapp/send_template")
async def whatsapp_send_template(body: WhatsAppSendTemplateRequest, db=Depends(get_db)):
    to_norm = normalize_phone_india(body.to)
    if not D360_API_KEY:
        rec = {
            "id": str(uuid.uuid4()),
            "queued_at": now_iso(),
            "to": to_norm,
            "template": body.template_name,
            "mode": "stub",
            "provider": "360dialog",
        }
        await db["whatsapp_outbox"].insert_one(rec)
        return {"success": True, "mode": "stub", "id": rec["id"], "message": "Template send stored (stub)."}

    headers = {
        "D360-API-KEY": D360_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_norm,
        "type": "template",
        "template": {
            "name": body.template_name,
            "language": {"code": body.language_code or "en"},
            **({"components": body.components} if body.components else {})
        }
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(f"{D360_BASE_URL}/messages", headers=headers, json=payload)
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=f"Provider error: {resp.text}")
        data = resp.json()
    await db["whatsapp_sent"].insert_one({
        "id": str(uuid.uuid4()),
        "sent_at": now_iso(),
        "to": to_norm,
        "payload": payload,
        "provider_response": data,
    })
    return {"success": True, "provider": "360dialog", "data": data}
