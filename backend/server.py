import os
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, WebSocket, HTTPException, Depends, Query, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import hmac
import hashlib
import httpx
import re
import shutil

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = FastAPI(title="Aavana CRM API")

# CORS
CORS_ORIGINS = os.environ.get("CRM_CORS_ORIGINS", "*")
CORS_LIST = [o.strip().rstrip('/') for o in CORS_ORIGINS.split(',') if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_LIST if CORS_LIST else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mongo
MONGO_URL = os.environ.get("MONGO_URL")
_mongo_client: Optional[AsyncIOMotorClient] = None

async def get_db() -> AsyncIOMotorDatabase:
    global _mongo_client
    if not MONGO_URL:
        raise HTTPException(status_code=500, detail="MONGO_URL is not configured")
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(MONGO_URL)
    db = _mongo_client.get_default_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Mongo URI must include a database name (e.g., mongodb://host:27017/aavana_crm)")
    return db

# Uploads static root
UPLOAD_ROOT = "/app/data/uploads"
os.makedirs(UPLOAD_ROOT, exist_ok=True)
app.mount("/api/files", StaticFiles(directory=UPLOAD_ROOT), name="uploaded-files")

# Utils
DEFAULT_COUNTRY_CODE = "+91"
DEFAULT_OWNER_MOBILE = "+919999139938"  # Manager

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def normalize_phone_india(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    digits = "".join(ch for ch in str(raw) if ch.isdigit())
    if not digits:
        return None
    if digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]
    if digits.startswith("91"):
        if len(digits) >= 12:
            return "+" + digits[:12]
    if len(digits) == 10:
        return DEFAULT_COUNTRY_CODE + digits
    return "+" + digits if not str(raw).startswith("+") else str(raw)

async def find_lead_by_phone(db: AsyncIOMotorDatabase, phone_norm: str) -> Optional[Dict[str, Any]]:
    cursor = db["leads"].find({}, {"_id": 0})
    leads = await cursor.to_list(length=None)
    for ld in leads:
        p = ld.get("phone")
        if p and normalize_phone_india(p) == phone_norm:
            return ld
    return None

# Build absolute URL behind ingress
from urllib.parse import urljoin

def build_absolute_url(request: Request, path: str) -> str:
    proto = request.headers.get("x-forwarded-proto") or "https"
    host = request.headers.get("x-forwarded-host") or request.client.host
    base = f"{proto}://{host}"
    if not path.startswith("/"):
        path = "/" + path
    return base.rstrip("/") + path

# Health
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "crm-backend", "time": now_iso()}

# ======== Models ========
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
    due_date: Optional[str] = None
    status: Optional[str] = Field(default="Open")
    lead_id: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None
    lead_id: Optional[str] = None

# ======== Leads ========
@app.post("/api/leads")
async def create_lead(body: LeadCreate, db=Depends(get_db)):
    doc = body.dict(exclude_none=True)
    if doc.get("phone"):
        doc["phone"] = normalize_phone_india(doc.get("phone"))
    if doc.get("owner_mobile"):
        doc["owner_mobile"] = normalize_phone_india(doc.get("owner_mobile"))
    else:
        doc["owner_mobile"] = DEFAULT_OWNER_MOBILE
    doc["id"] = str(uuid.uuid4())
    doc.setdefault("status", "New")
    doc["created_at"] = now_iso()
    doc["updated_at"] = now_iso()
    await db["leads"].insert_one(doc)
    doc.pop("_id", None)
    return {"success": True, "lead": doc}

@app.get("/api/leads")
async def list_leads(status: Optional[str] = None, source: Optional[str] = None, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), db=Depends(get_db)):
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

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str, db=Depends(get_db)):
    doc = await db["leads"].find_one({"id": lead_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"success": True, "lead": doc}

@app.get("/api/leads/search")
async def search_leads(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=50), db=Depends(get_db)):
    phone_norm = normalize_phone_india(q)
    regex = {"$regex": re.escape(q), "$options": "i"}
    digits = "".join(ch for ch in q if ch.isdigit())
    phone_regex = {"$regex": digits} if digits and len(digits) >= 4 else None
    ors: List[Dict[str, Any]] = [{"name": regex}, {"email": regex}]
    if phone_norm:
        ors.append({"phone": phone_norm})
    if phone_regex:
        ors.append({"phone": phone_regex})
    cursor = db["leads"].find({"$or": ors}, {"_id": 0}).limit(limit)
    items = await cursor.to_list(length=limit)
    return {"items": items}

@app.put("/api/leads/{lead_id}")
async def update_lead(lead_id: str, body: LeadUpdate, db=Depends(get_db)):
    updates = body.dict(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    if updates.get("phone"):
        updates["phone"] = normalize_phone_india(updates.get("phone"))
    if updates.get("owner_mobile"):
        updates["owner_mobile"] = normalize_phone_india(updates.get("owner_mobile"))
    updates["updated_at"] = now_iso()
    res = await db["leads"].update_one({"id": lead_id}, {"$set": updates})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    doc = await db["leads"].find_one({"id": lead_id}, {"_id": 0})
# ======== Uploads (Chunked) ========
class UploadInit(BaseModel):
    filename: str
    category: Optional[str] = "general"
    tags: Optional[str] = None

@app.post("/api/uploads/catalogue/init")
async def upload_init(body: UploadInit):
    upload_id = str(uuid.uuid4())
    tmp_dir = os.path.join(UPLOAD_ROOT, "tmp", upload_id)
    os.makedirs(tmp_dir, exist_ok=True)
    return {"success": True, "upload_id": upload_id, "filename": body.filename, "category": body.category or "general", "tags": body.tags}

@app.post("/api/uploads/catalogue/chunk")
async def upload_chunk(upload_id: str = Form(...), index: int = Form(...), total: int = Form(...), chunk: UploadFile = File(...)):
    tmp_dir = os.path.join(UPLOAD_ROOT, "tmp", upload_id)
    if not os.path.isdir(tmp_dir):
        raise HTTPException(status_code=400, detail="Invalid upload_id")
    part_path = os.path.join(tmp_dir, f"part_{index:06d}")
    with open(part_path, "wb") as out:
        shutil.copyfileobj(chunk.file, out)
    return {"success": True, "index": index, "received": True}

class UploadComplete(BaseModel):
    upload_id: str
    filename: str
    category: Optional[str] = "general"
    tags: Optional[str] = None

@app.post("/api/uploads/catalogue/complete")
async def upload_complete(request: Request, body: UploadComplete, db=Depends(get_db)):
    tmp_dir = os.path.join(UPLOAD_ROOT, "tmp", body.upload_id)
    if not os.path.isdir(tmp_dir):
        raise HTTPException(status_code=400, detail="Invalid upload_id")
    # Merge
    final_name = f"{uuid.uuid4()}_{re.sub(r'[^a-zA-Z0-9._-]', '_', body.filename or 'file')}"
    final_path = os.path.join(UPLOAD_ROOT, final_name)
    parts = sorted([p for p in os.listdir(tmp_dir) if p.startswith("part_")])
    with open(final_path, "wb") as out:
        for p in parts:
            with open(os.path.join(tmp_dir, p), "rb") as src:
                shutil.copyfileobj(src, out)
    # Cleanup tmp
    shutil.rmtree(tmp_dir, ignore_errors=True)
    rel_path = f"/api/files/{final_name}"
    abs_url = build_absolute_url(request, rel_path)
    doc = {
        "id": str(uuid.uuid4()),
        "original_name": body.filename,
        "stored_as": final_name,
        "url": abs_url,
        "path": rel_path,
        "category": body.category or "general",
        "tags": body.tags,
        "uploaded_at": now_iso(),
    }
    await db["catalogues"].insert_one(doc)
    return {"success": True, "file": doc}

@app.get("/api/uploads/catalogue/list")
async def uploads_list(limit: int = Query(50, ge=1, le=200), category: Optional[str] = None, db=Depends(get_db)):
    q: Dict[str, Any] = {}
    if category:
        q["category"] = category
    cursor = db["catalogues"].find(q, {"_id": 0}).sort("uploaded_at", -1).limit(limit)
    items = await cursor.to_list(length=limit)
    return {"catalogues": items}

@app.get("/api/uploads/catalogue/categories")
async def uploads_categories(db=Depends(get_db)):
    cats = await db["catalogues"].distinct("category")
    return {"categories": cats}

    return {"success": True, "lead": doc}

@app.delete("/api/leads/{lead_id}")
async def delete_lead(lead_id: str, db=Depends(get_db)):
    res = await db["leads"].delete_one({"id": lead_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"success": True}

# ======== Tasks ========
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
async def list_tasks(status: Optional[str] = None, assignee: Optional[str] = None, lead_id: Optional[str] = None, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), db=Depends(get_db)):
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

# ======== Dashboard ========
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

# ======== Uploads ========
@app.post("/api/uploads/catalogue")
async def upload_catalogue(request: Request, file: UploadFile = File(...), category: str = Form("general")):
    try:
        filename = f"{uuid.uuid4()}_{re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename or 'file')}"
        dest_path = os.path.join(UPLOAD_ROOT, filename)
        with open(dest_path, "wb") as out:
            shutil.copyfileobj(file.file, out)
        rel_path = f"/api/files/{filename}"
        abs_url = build_absolute_url(request, rel_path)
        return {"success": True, "file": {"name": file.filename, "stored_as": filename, "url": abs_url, "path": rel_path, "category": category}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# ======== WhatsApp (Meta Cloud API) ========
META_ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN", "")
META_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
META_BUSINESS_ACCOUNT_ID = os.environ.get("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
META_APP_SECRET = os.environ.get("WHATSAPP_APP_SECRET", "")
META_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "")
META_API_VERSION = os.environ.get("WHATSAPP_API_VERSION", "v20.0")
META_BASE_URL = f"https://graph.facebook.com/{META_API_VERSION}"

IS_STUB = not (META_ACCESS_TOKEN and META_PHONE_NUMBER_ID)

def _hmac_valid(body: bytes, signature_header: Optional[str]) -> bool:
    # Meta: X-Hub-Signature-256 = sha256=...
    if not META_APP_SECRET:
        return True
    if not signature_header:
        return False
    try:
        provided = signature_header
        if provided.lower().startswith("sha256="):
            provided = provided.split("=", 1)[1]
        digest = hmac.new(META_APP_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(digest, provided)
    except Exception:
        return False

class WhatsAppMediaRequest(BaseModel):
    to: str
    media_url: str
    media_type: str = Field(..., pattern="^(image|document)$")
    caption: Optional[str] = None

@app.get("/api/whatsapp/webhook")
async def whatsapp_webhook_verify(hub_mode: str = Query(None, alias="hub.mode"), hub_token: str = Query(None, alias="hub.verify_token"), hub_challenge: str = Query(None, alias="hub.challenge")):
    if hub_mode == "subscribe" and hub_token and META_VERIFY_TOKEN and hub_token == META_VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge or "")
    raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/api/whatsapp/webhook")
async def whatsapp_webhook_receive(request: Request, db=Depends(get_db)):
    body = await request.body()
    sig = request.headers.get("X-Hub-Signature-256") or request.headers.get("x-hub-signature-256")
    if not _hmac_valid(body, sig):
        raise HTTPException(status_code=401, detail="Invalid signature")
    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Store raw event
    await db["whatsapp_events"].insert_one({
        "id": str(uuid.uuid4()),
        "received_at": now_iso(),
        "raw": payload,
        "source": "meta",
        "type": payload.get("object", "event")
    })

    # Normalize inbound messages and upsert conversations
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

                    linked_lead = await find_lead_by_phone(db, from_norm) if from_norm else None
                    lead_id = linked_lead.get("id") if linked_lead else None

                    await db["whatsapp_messages"].insert_one({
                        "id": str(uuid.uuid4()),
                        "direction": "inbound",
                        "from": from_norm,
                        "to": meta.get("display_phone_number"),
                        "type": mtype,
                        "text": text,
                        "timestamp": ts_dt.isoformat(),
                        "lead_id": lead_id,
                    })

                    owner_mobile = normalize_phone_india(linked_lead.get("owner_mobile")) if linked_lead and linked_lead.get("owner_mobile") else DEFAULT_OWNER_MOBILE
                    await db["whatsapp_conversations"].update_one(
                        {"contact": from_norm},
                        {"$set": {
                            "contact": from_norm,
                            "lead_id": lead_id,
                            "owner_mobile": owner_mobile,
                            "last_message_at": ts_dt.isoformat(),
                            "last_message_text": text or f"[{mtype}]",
                            "last_message_dir": "in",
                        }, "$inc": {"unread_count": 1}},
                        upsert=True
                    )
    except Exception:
        pass

    return {"success": True}

@app.get("/api/whatsapp/conversations")
async def whatsapp_conversations(limit: int = Query(50, ge=1, le=200), db=Depends(get_db)):
    cursor = db["whatsapp_conversations"].find({}, {"_id": 0}).sort("last_message_at", -1).limit(limit)
    items = await cursor.to_list(length=limit)
    result = []
    for it in items:
        lead_name = None
        if it.get("lead_id"):
            lead = await db["leads"].find_one({"id": it["lead_id"]}, {"_id": 0, "name": 1})
            lead_name = lead.get("name") if lead else None
        try:
            last_dt = datetime.fromisoformat(it.get("last_message_at")).astimezone(timezone.utc)
        except Exception:
            last_dt = datetime.now(timezone.utc)
        it["lead_name"] = lead_name
        it["age_sec"] = int((datetime.now(timezone.utc) - last_dt).total_seconds())
        result.append(it)
    return result

@app.post("/api/whatsapp/conversations/{contact}/read")
async def whatsapp_conversation_read(contact: str, db=Depends(get_db)):
    contact_norm = normalize_phone_india(contact)
    await db["whatsapp_conversations"].update_one({"contact": contact_norm}, {"$set": {"unread_count": 0, "last_read_at": now_iso()}})
    return {"success": True}

@app.post("/api/whatsapp/conversations/{contact}/link_lead")
async def whatsapp_conversation_link_lead(contact: str, body: Dict[str, Any], db=Depends(get_db)):
    contact_norm = normalize_phone_india(contact)
    lead_id = (body or {}).get("lead_id")
    if not lead_id:
        raise HTTPException(status_code=400, detail="lead_id required")
    lead = await db["leads"].find_one({"id": lead_id}, {"_id": 0})
    owner_mobile = normalize_phone_india(lead.get("owner_mobile") if lead else DEFAULT_OWNER_MOBILE)
    await db["whatsapp_conversations"].update_one({"contact": contact_norm}, {"$set": {"lead_id": lead_id, "owner_mobile": owner_mobile}}, upsert=True)
    await db["whatsapp_messages"].update_many({"from": contact_norm}, {"$set": {"lead_id": lead_id}})
    return {"success": True}

@app.get("/api/whatsapp/lead_timeline/{lead_id}")
async def whatsapp_lead_timeline(lead_id: str, limit: int = Query(10, ge=1, le=100), db=Depends(get_db)):
    cursor = db["whatsapp_messages"].find({"lead_id": lead_id}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    msgs = await cursor.to_list(length=limit)
    return {"items": msgs}

@app.get("/api/whatsapp/contact_messages")
async def whatsapp_contact_messages(contact: str, limit: int = Query(3, ge=1, le=50), db=Depends(get_db)):
    contact_norm = normalize_phone_india(contact)
    cursor = db["whatsapp_messages"].find({"from": contact_norm}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    msgs = await cursor.to_list(length=limit)
    return {"items": msgs}

@app.get("/api/whatsapp/session_status")
async def whatsapp_session_status(contact: str, db=Depends(get_db)):
    contact_norm = normalize_phone_india(contact)
    last = await db["whatsapp_messages"].find_one({"from": contact_norm, "direction": "inbound"}, sort=[("timestamp", -1)])
    if not last:
        return {"within_24h": False, "last_inbound": None}
    try:
        last_dt = datetime.fromisoformat(last.get("timestamp")).astimezone(timezone.utc)
    except Exception:
        last_dt = datetime.now(timezone.utc) - timedelta(days=2)
    within = (datetime.now(timezone.utc) - last_dt) < timedelta(hours=24)
    return {"within_24h": within, "last_inbound": last.get("timestamp")}

# Sending helpers (Meta)
async def meta_send_text(to_norm: str, text: str, db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    if IS_STUB:
        rec = {"id": str(uuid.uuid4()), "queued_at": now_iso(), "to": to_norm, "text": text or "", "mode": "stub", "provider": "meta"}
        await db["whatsapp_outbox"].insert_one(rec)
        await db["whatsapp_conversations"].update_one({"contact": to_norm}, {"$set": {"unread_count": 0, "last_message_at": now_iso(), "last_message_text": text or "", "last_message_dir": "out"}}, upsert=True)
        return {"success": True, "mode": "stub", "id": rec["id"]}
    headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_norm,
        "type": "text",
        "text": {"body": text or ""},
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(f"{META_BASE_URL}/{META_PHONE_NUMBER_ID}/messages", headers=headers, json=payload)
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=f"Provider error: {resp.text}")
        data = resp.json()
    await db["whatsapp_sent"].insert_one({"id": str(uuid.uuid4()), "sent_at": now_iso(), "to": to_norm, "payload": payload, "provider_response": data})
    await db["whatsapp_conversations"].update_one({"contact": to_norm}, {"$set": {"unread_count": 0, "last_message_at": now_iso(), "last_message_text": text or "", "last_message_dir": "out"}})
    return {"success": True, "provider": "meta", "data": data}

async def meta_send_media(to_norm: str, media_url: str, media_type: str, caption: Optional[str], db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    if IS_STUB:
        rec = {"id": str(uuid.uuid4()), "queued_at": now_iso(), "to": to_norm, "media_url": media_url, "media_type": media_type, "caption": caption or "", "mode": "stub", "provider": "meta"}
        await db["whatsapp_outbox"].insert_one(rec)
        await db["whatsapp_conversations"].update_one({"contact": to_norm}, {"$set": {"unread_count": 0, "last_message_at": now_iso(), "last_message_text": caption or f"[{media_type}]", "last_message_dir": "out"}}, upsert=True)
        return {"success": True, "mode": "stub"}
    headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload: Dict[str, Any] = {"messaging_product": "whatsapp", "recipient_type": "individual", "to": to_norm, "type": media_type}
    if media_type == "image":
        payload["image"] = {"link": media_url}
        if caption:
            payload["image"]["caption"] = caption
    else:
        payload["document"] = {"link": media_url}
        if caption:
            payload["document"]["caption"] = caption
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(f"{META_BASE_URL}/{META_PHONE_NUMBER_ID}/messages", headers=headers, json=payload)
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=f"Provider error: {resp.text}")
        data = resp.json()
    await db["whatsapp_sent"].insert_one({"id": str(uuid.uuid4()), "sent_at": now_iso(), "to": to_norm, "payload": payload, "provider_response": data})
    await db["whatsapp_conversations"].update_one({"contact": to_norm}, {"$set": {"unread_count": 0, "last_message_at": now_iso(), "last_message_text": caption or f"[{media_type}]", "last_message_dir": "out"}})
    return {"success": True}

class WhatsAppSendRequest(BaseModel):
    to: str
    text: Optional[str] = None

class WhatsAppSendTemplateRequest(BaseModel):
    to: str
    template_name: str
    language_code: Optional[str] = "en"
    components: Optional[List[Dict[str, Any]]] = None

@app.post("/api/whatsapp/send")
async def whatsapp_send(body: WhatsAppSendRequest, db=Depends(get_db)):
    if not body.to:
        raise HTTPException(status_code=400, detail="'to' is required")
    to_norm = normalize_phone_india(body.to)
    return await meta_send_text(to_norm, body.text or "", db)

@app.post("/api/whatsapp/send_media")
async def whatsapp_send_media_endpoint(body: WhatsAppMediaRequest, db=Depends(get_db)):
    to_norm = normalize_phone_india(body.to)
    if not to_norm:
        raise HTTPException(status_code=400, detail="Invalid recipient number")
    return await meta_send_media(to_norm, body.media_url, body.media_type, body.caption, db)

@app.post("/api/whatsapp/send_template")
async def whatsapp_send_template(body: WhatsAppSendTemplateRequest, db=Depends(get_db)):
    to_norm = normalize_phone_india(body.to)
    if IS_STUB:
        rec = {"id": str(uuid.uuid4()), "queued_at": now_iso(), "to": to_norm, "template": body.template_name, "mode": "stub", "provider": "meta"}
        await db["whatsapp_outbox"].insert_one(rec)
        return {"success": True, "mode": "stub", "id": rec["id"], "message": "Template send stored (stub)."}
    headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload: Dict[str, Any] = {
        "messaging_product": "whatsapp",
        "to": to_norm,
        "type": "template",
        "template": {
            "name": body.template_name,
            "language": {"code": body.language_code or "en"}
        }
    }
    if body.components:
        payload["template"]["components"] = body.components
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(f"{META_BASE_URL}/{META_PHONE_NUMBER_ID}/messages", headers=headers, json=payload)
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=f"Provider error: {resp.text}")
        data = resp.json()
    await db["whatsapp_sent"].insert_one({"id": str(uuid.uuid4()), "sent_at": now_iso(), "to": to_norm, "payload": payload, "provider_response": data})
    return {"success": True, "provider": "meta", "data": data}

# ======== Lead Actions ========
class LeadActionRequest(BaseModel):
    action_type: str
    method: Optional[str] = None
    message: Optional[str] = None
    images: Optional[List[str]] = None
    file_url: Optional[str] = None
    catalogue_type: Optional[str] = None

@app.get("/api/leads/{lead_id}/actions")
async def list_lead_actions(lead_id: str, limit: int = Query(20, ge=1, le=100), db=Depends(get_db)):
    cursor = db["lead_actions"].find({"lead_id": lead_id}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    items = await cursor.to_list(length=limit)
    return {"actions": items}

@app.post("/api/leads/{lead_id}/actions")
async def execute_lead_action(lead_id: str, body: LeadActionRequest, request: Request, db=Depends(get_db)):
    action = body.dict(exclude_none=True)
    action_id = str(uuid.uuid4())
    await db["lead_actions"].insert_one({"id": action_id, "lead_id": lead_id, "action_type": body.action_type, "timestamp": now_iso(), "status": "processing", "payload": action})

    lead = await db["leads"].find_one({"id": lead_id}, {"_id": 0})
    if not lead:
        await db["lead_actions"].update_one({"id": action_id}, {"$set": {"status": "failed", "error": "Lead not found"}})
        raise HTTPException(status_code=404, detail="Lead not found")

    try:
        if body.action_type in ("send_catalogue", "send_gallery_images", "capture_and_send_images"):
            to = normalize_phone_india(lead.get("phone"))
            if not to:
                raise HTTPException(status_code=400, detail="Lead has no phone number")
            urls: List[str] = []
            if body.file_url:
                urls.append(body.file_url)
            if body.images:
                for it in body.images:
                    if it.startswith("http"):
                        urls.append(it)
                    else:
                        urls.append(build_absolute_url(request, f"/api/files/{it}"))
            if not urls:
                raise HTTPException(status_code=400, detail="No files to send")
            for u in urls:
                media_type = "document" if u.lower().endswith((".pdf", ".doc", ".docx")) else "image"
                await meta_send_media(to, u, media_type, body.message or "", db)
            await db["lead_actions"].update_one({"id": action_id}, {"$set": {"status": "completed"}})
            return {"success": True, "id": action_id}
        elif body.action_type == "whatsapp":
            to = normalize_phone_india(lead.get("phone"))
            if not to:
                raise HTTPException(status_code=400, detail="Lead has no phone number")
            res = await meta_send_text(to, body.message or "", db)
            await db["lead_actions"].update_one({"id": action_id}, {"$set": {"status": "completed", "provider": res}})
            return {"success": True, "id": action_id}
        else:
            await db["lead_actions"].update_one({"id": action_id}, {"$set": {"status": "completed"}})
            return {"success": True, "id": action_id}
    except HTTPException:
        raise
    except Exception as e:
        await db["lead_actions"].update_one({"id": action_id}, {"$set": {"status": "failed", "error": str(e)}})
        raise HTTPException(status_code=500, detail=f"Action failed: {str(e)}")
