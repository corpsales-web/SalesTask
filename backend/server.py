import os
import uuid
import re
import io
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import httpx

# Load environment variables
load_dotenv()

# Configuration
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017/aavana_crm")
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")
UPLOAD_ROOT = "/app/uploads"

# Ensure upload directories exist
os.makedirs(UPLOAD_ROOT, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_ROOT, "visual"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_ROOT, "catalogue"), exist_ok=True)

app = FastAPI(title="CRM Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files via /api/files/*
app.mount("/api/files", StaticFiles(directory=UPLOAD_ROOT), name="files")

mongo_client: Optional[AsyncIOMotorClient] = None

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def build_absolute_url(request: Request, path: str) -> str:
    """Build absolute URL for file access"""
    base_url = str(request.base_url).rstrip('/')
    return f"{base_url}{path}"

# Database connection
async def get_db():
    global mongo_client
    if mongo_client is None:
        mongo_client = AsyncIOMotorClient(MONGO_URL)
    db_name = MONGO_URL.split('/')[-1] if '/' in MONGO_URL else "aavana_crm"
    return mongo_client[db_name]

# Pydantic models
class LeadCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    owner_mobile: Optional[str] = None

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    owner_mobile: Optional[str] = None

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None

class UploadInit(BaseModel):
    filename: str
    file_size: Optional[int] = None
    chunk_size: Optional[int] = 1024 * 1024  # 1MB default
    total_chunks: Optional[int] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    project_id: Optional[str] = None

class UploadComplete(BaseModel):
    upload_id: str
    filename: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    project_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None

class WhatsAppSend(BaseModel):
    to: str
    text: str

# Utility functions
def normalize_phone(phone: str) -> str:
    """Normalize phone number to +91 format"""
    if not phone:
        return phone
    digits = re.sub(r'\D', '', phone)
    if digits.startswith('91') and len(digits) == 12:
        return f"+{digits}"
    elif len(digits) == 10:
        return f"+91{digits}"
    elif digits.startswith('0') and len(digits) == 11:
        return f"+91{digits[1:]}"
    else:
        return f"+91{digits[-10:]}" if len(digits) >= 10 else phone

# -------- Leads Endpoints (abbrev: list/create/get/update/delete) --------
@app.get("/api/leads")
async def list_leads(page: int = 1, limit: int = 50, db=Depends(get_db)):
    cursor = db["leads"].find({}, {"_id": 0}).skip((page-1)*limit).limit(limit)
    items = await cursor.to_list(length=limit)
    total = await db["leads"].count_documents({})
    return {"items": items, "page": page, "limit": limit, "total": total}

@app.post("/api/leads")
async def create_lead(payload: LeadCreate, db=Depends(get_db)):
    lead = payload.dict()
    lead["id"] = str(uuid.uuid4())
    if lead.get("phone"):
        lead["phone"] = normalize_phone(lead["phone"])
    lead["created_at"] = now_iso()
    await db["leads"].insert_one(lead)
    lead.pop("_id", None)
    return {"lead": lead}

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str, db=Depends(get_db)):
    lead = await db["leads"].find_one({"id": lead_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"lead": lead}

@app.put("/api/leads/{lead_id}")
async def update_lead(lead_id: str, payload: LeadUpdate, db=Depends(get_db)):
    updates = {k: v for k, v in payload.dict().items() if v is not None}
    if "phone" in updates and updates["phone"]:
        updates["phone"] = normalize_phone(updates["phone"])
    res = await db["leads"].update_one({"id": lead_id}, {"$set": updates})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead = await db["leads"].find_one({"id": lead_id}, {"_id": 0})
    return {"lead": lead}

@app.delete("/api/leads/{lead_id}")
async def delete_lead(lead_id: str, db=Depends(get_db)):
    res = await db["leads"].delete_one({"id": lead_id})
    return {"deleted": res.deleted_count == 1}

# Leads search for linking/duplicate checks
@app.get("/api/leads/search")
async def search_leads(q: str, page: int = 1, limit: int = 20, db=Depends(get_db)):
    try:
        regex = {"$regex": re.escape(q), "$options": "i"}
        phone_digits = re.sub(r"\D", "", q)
        phone_last10 = phone_digits[-10:] if len(phone_digits) >= 4 else None
        criteria = [{"name": regex}, {"email": regex}]
        if phone_last10:
            criteria.append({"phone": {"$regex": phone_last10 + "$"}})
        cursor = db["leads"].find({"$or": criteria}, {"_id": 0}).skip((page-1)*limit).limit(limit)
        items = await cursor.to_list(length=limit)
        total = await db["leads"].count_documents({"$or": criteria})
        return {"items": items, "page": page, "limit": limit, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------- Tasks Endpoints (list/create) --------
@app.get("/api/tasks")
async def list_tasks(db=Depends(get_db)):
    items = await db["tasks"].find({}, {"_id": 0}).to_list(length=500)
    return {"items": items}

@app.post("/api/tasks")
async def create_task(payload: TaskCreate, db=Depends(get_db)):
    task = payload.dict()
    task["id"] = str(uuid.uuid4())
    task["created_at"] = now_iso()
    if not task.get("status"):
        task["status"] = "open"
    await db["tasks"].insert_one(task)
    task.pop("_id", None)
    return {"task": task}

# -------- Visual Upgrades (simplified; render implementation in visual_upgrades.py originally) --------
@app.post("/api/visual-upgrades/render")
async def visual_upgrades_render(request: Request, image: UploadFile = File(...), prompt: str = Form(...), size: str = Form("1024x1024"), mask: Optional[UploadFile] = File(None), lead_id: Optional[str] = Form(None), response_format: str = Form("url"), db=Depends(get_db)):
    try:
        # Persist base image and optional mask
        base_name = f"{uuid.uuid4()}_base.png"
        base_rel = f"/api/files/visual/{base_name}"
        base_path = os.path.join(UPLOAD_ROOT, "visual", base_name)
        with open(base_path, "wb") as f:
            f.write(await image.read())
        base_url = build_absolute_url(request, base_rel)

        mask_url = None
        if mask is not None:
            mask_name = f"{uuid.uuid4()}_mask.png"
            mask_rel = f"/api/files/visual/{mask_name}"
            mask_path = os.path.join(UPLOAD_ROOT, "visual", mask_name)
            with open(mask_path, "wb") as f:
                f.write(await mask.read())
            mask_url = build_absolute_url(request, mask_rel)

        # Simulate AI result (in real impl, call emergentintegrations/OpenAI)
        result_name = f"{uuid.uuid4()}_result.png"
        result_rel = f"/api/files/visual/{result_name}"
        result_path = os.path.join(UPLOAD_ROOT, "visual", result_name)
        # For MVP, just copy base to result
        import shutil
        shutil.copyfile(base_path, result_path)
        result_url = build_absolute_url(request, result_rel)

        upgrade_record = {
            "id": str(uuid.uuid4()),
            "lead_id": lead_id,
            "prompt": prompt,
            "size": size,
            "base_image": {"url": base_url, "path": base_rel},
            "mask_image": ({"url": mask_url} if mask_url else None),
            "result": {"url": result_url, "path": result_rel},
            "created_at": now_iso(),
        }
        await db["visual_upgrades"].insert_one(upgrade_record)
        upgrade_record.pop("_id", None)
        return {"success": True, "upgrade": upgrade_record}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visual upgrade failed: {str(e)}")

@app.get("/api/visual-upgrades/list")
async def visual_upgrades_list(lead_id: Optional[str] = None, db=Depends(get_db)):
    q: Dict[str, Any] = {}
    if lead_id:
        q["lead_id"] = lead_id
    items = await db["visual_upgrades"].find(q, {"_id": 0}).sort("created_at", -1).to_list(length=200)
    return {"items": items}

# -------- Catalogue Upload endpoints (adapted to frontend contract) --------
upload_sessions: Dict[str, Dict[str, Any]] = {}

@app.post("/api/uploads/catalogue/init")
async def init_catalogue_upload(payload: UploadInit):
    try:
        upload_id = str(uuid.uuid4())
        session = {
            "id": upload_id,
            "filename": payload.filename,
            "file_size": payload.file_size or 0,
            "chunk_size": payload.chunk_size or 1024*1024,
            "total_chunks": payload.total_chunks,
            "uploaded_chunks": set(),
            "status": "initialized",
            "category": payload.category,
            "tags": payload.tags,
            "project_id": payload.project_id,
            "created_at": now_iso(),
        }
        upload_sessions[upload_id] = session
        return {"success": True, "upload_id": upload_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/uploads/catalogue/chunk")
async def upload_catalogue_chunk(request: Request, upload_id: str = Form(...), index: Optional[int] = Form(None), total: Optional[int] = Form(None), chunk_number: Optional[int] = Form(None), chunk: UploadFile = File(...)):
    try:
        if upload_id not in upload_sessions:
            raise HTTPException(status_code=404, detail="Upload session not found")
        session = upload_sessions[upload_id]
        number = index if index is not None else chunk_number
        if number is None:
            raise HTTPException(status_code=400, detail="Missing chunk index")
        if total is not None and session.get("total_chunks") is None:
            session["total_chunks"] = total
        # Save chunk
        chunk_dir = os.path.join(UPLOAD_ROOT, "catalogue", upload_id)
        os.makedirs(chunk_dir, exist_ok=True)
        chunk_path = os.path.join(chunk_dir, f"chunk_{number}")
        contents = await chunk.read()
        with open(chunk_path, "wb") as f:
            f.write(contents)
        session["uploaded_chunks"].add(int(number))
        session["status"] = "uploading"
        return {"success": True, "index": int(number)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/uploads/catalogue/state")
async def get_catalogue_upload_state(upload_id: str):
    try:
        if upload_id not in upload_sessions:
            return {"exists": False, "parts": 0, "status": "missing"}
        session = upload_sessions[upload_id]
        return {
            "exists": True,
            "parts": len(session.get("uploaded_chunks", [])),
            "status": session.get("status", "initialized"),
            "total_chunks": session.get("total_chunks"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/uploads/catalogue/complete")
async def complete_catalogue_upload(request: Request, complete_data: UploadComplete, db=Depends(get_db)):
    try:
        upload_id = complete_data.upload_id
        if upload_id not in upload_sessions:
            raise HTTPException(status_code=404, detail="Upload session not found")
        session = upload_sessions[upload_id]
        # Combine chunks into final file
        chunk_dir = os.path.join(UPLOAD_ROOT, "catalogue", upload_id)
        final_name = complete_data.filename or session["filename"]
        final_file_name = f"{upload_id}_{final_name}"
        final_rel = f"/api/files/catalogue/{final_file_name}"
        final_path = os.path.join(UPLOAD_ROOT, "catalogue", final_file_name)
        with open(final_path, "wb") as final_file:
            for idx in sorted(list(session["uploaded_chunks"])):
                chunk_path = os.path.join(chunk_dir, f"chunk_{idx}")
                if os.path.exists(chunk_path):
                    with open(chunk_path, "rb") as cf:
                        final_file.write(cf.read())
        item = {
            "id": str(uuid.uuid4()),
            "upload_id": upload_id,
            "filename": session["filename"],
            "file_path": final_path,
            "url": build_absolute_url(request, final_rel),
            "status": "completed",
            "created_at": now_iso(),
            "category": complete_data.category or session.get("category"),
            "tags": complete_data.tags or session.get("tags"),
            "project_id": complete_data.project_id or session.get("project_id"),
            "title": complete_data.title,
            "description": complete_data.description,
        }
        await db["catalogue_items"].insert_one(item)
        item.pop("_id", None)
        session["status"] = "completed"
        return {"success": True, "file": item}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/uploads/catalogue/cancel")
async def cancel_catalogue_upload(upload_id: str = Form(...)):
    try:
        if upload_id not in upload_sessions:
            raise HTTPException(status_code=404, detail="Upload session not found")
        # Clean up chunks
        chunk_dir = os.path.join(UPLOAD_ROOT, "catalogue", upload_id)
        if os.path.exists(chunk_dir):
            import shutil
            shutil.rmtree(chunk_dir)
        upload_sessions[upload_id]["status"] = "cancelled"
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/uploads/catalogue/list")
async def list_catalogue_items(request: Request, db=Depends(get_db)):
    try:
        items = await db["catalogue_items"].find({}, {"_id": 0}).sort("created_at", -1).to_list(length=1000)
        # Ensure url is present
        for it in items:
            if not it.get("url") and it.get("file_path"):
                rel = "/api/files/catalogue/" + os.path.basename(it["file_path"]) if it.get("file_path") else None
                if rel:
                    it["url"] = build_absolute_url(request, rel)
        return {"catalogues": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------- WhatsApp stub helpers --------
@app.get("/api/whatsapp/session_status")
async def whatsapp_session_status(contact: str):
    return {"within_24h": True}

@app.get("/api/whatsapp/contact_messages")
async def whatsapp_contact_messages(contact: str):
    now = now_iso()
    return {"items": [
        {"direction": "inbound", "timestamp": now, "text": "Hi"},
        {"direction": "outbound", "timestamp": now, "text": "Hello"},
        {"direction": "inbound", "timestamp": now, "text": "How are you?"}
    ]}

@app.post("/api/whatsapp/conversations/{contact}/read")
async def whatsapp_mark_read(contact: str):
    return {"success": True}

@app.post("/api/whatsapp/conversations/{contact}/link_lead")
async def whatsapp_link_conversation(contact: str, body: Dict[str, Any], db=Depends(get_db)):
    mapping = {"id": str(uuid.uuid4()), "contact": contact, "lead_id": body.get("lead_id"), "linked_at": now_iso()}
    await db["whatsapp_links"].insert_one(mapping)
    mapping.pop("_id", None)
    return {"success": True, "link": mapping}

# -------- Projects (for catalogue grouping) --------
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

@app.get("/api/projects")
async def list_projects(db=Depends(get_db)):
    items = await db["projects"].find({}, {"_id": 0}).sort("created_at", -1).to_list(length=500)
    return {"items": items}

@app.post("/api/projects")
async def create_project(payload: ProjectCreate, db=Depends(get_db)):
    proj = payload.dict()
    proj["id"] = str(uuid.uuid4())
    proj["created_at"] = now_iso()
    await db["projects"].insert_one(proj)
    proj.pop("_id", None)
    return {"project": proj}

# -------- Aavana 2.0 Chat Endpoints (to fix 404 in assistant) --------
try:
    from aavana_2_0_orchestrator import aavana_2_0, ConversationRequest, ChannelType, SupportedLanguage
except Exception:
    aavana_2_0 = None
    ConversationRequest = None
    ChannelType = None
    SupportedLanguage = None

@app.post("/api/ai/specialized-chat")
async def specialized_chat(body: Dict[str, Any]):
    try:
        message = body.get("message", "")
        session_id = body.get("session_id") or str(uuid.uuid4())
        lang = (body.get("language") or "en")
        if aavana_2_0 and ConversationRequest and ChannelType:
            req = ConversationRequest(
                channel=ChannelType.IN_APP_CHAT,
                user_id="web",
                message=message,
                language=SupportedLanguage.ENGLISH if lang == "en" else SupportedLanguage.HINDI,
                session_id=session_id,
                context=body.get("context") or {},
            )
            resp = await aavana_2_0.process_conversation(req)
            return {
                "message_id": str(uuid.uuid4()),
                "message": resp.response_text,
                "timestamp": now_iso(),
                "actions": resp.actions or [],
                "metadata": {"processing_time": resp.processing_time_ms/1000 if hasattr(resp, 'processing_time_ms') else None},
                "agent_used": str(resp.intent) if hasattr(resp, 'intent') else 'specialized',
                "task_type": "specialized"
            }
        # Fallback simple echo
        return {
            "message_id": str(uuid.uuid4()),
            "message": f"[Specialized Fallback] {message}",
            "timestamp": now_iso(),
            "actions": [],
            "metadata": {"processing_time": 0.1},
            "agent_used": "fallback",
            "task_type": "general_chat"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/aavana2/enhanced-chat")
async def enhanced_chat(body: Dict[str, Any]):
    # For now, call the same specialized flow
    return await specialized_chat(body)

@app.post("/api/aavana2/chat")
async def standard_chat(body: Dict[str, Any]):
    message = body.get("message", "")
    return {
        "message_id": str(uuid.uuid4()),
        "message": f"Standard: {message}",
        "timestamp": now_iso(),
        "actions": [],
        "metadata": {"provider": body.get("provider", "openai"), "model": body.get("model", "gpt-4o")},
        "agent_used": "standard",
        "task_type": "general_chat"
    }


# ---- HRMS minimal endpoints ----
_hrms_state: Dict[str, Any] = {"today": {"checked_in": False, "checkin_time": None, "checkout_time": None}}

@app.get("/api/hrms/today")
async def hrms_today():
    return _hrms_state["today"]

@app.post("/api/hrms/checkin")
async def hrms_checkin():
    _hrms_state["today"]["checked_in"] = True
    _hrms_state["today"]["checkin_time"] = now_iso()
    return {"success": True}

@app.post("/api/hrms/checkout")
async def hrms_checkout():
    _hrms_state["today"]["checkout_time"] = now_iso()
    return {"success": True}

@app.get("/api/hrms/summary")
async def hrms_summary(days: int = 7):
    from datetime import date, timedelta
    today = date.today()
    items = []
    for i in range(days):
        d = today - timedelta(days=i)
        items.append({"date": d.isoformat(), "checked_in": True if i % 2 == 0 else False})
    return {"items": items}

# ---- Training modules ----
_training: List[Dict[str, Any]] = []

@app.get("/api/training/modules")
async def training_list(q: Optional[str] = None):
    items = _training
    if q:
        items = [m for m in items if q.lower() in m.get("title", "").lower()]
    return {"items": items}

@app.post("/api/training/modules")
async def training_add(body: Dict[str, Any]):
    item = {
        "id": str(uuid.uuid4()),
        "title": body.get("title"),
        "type": body.get("type"),
        "url": body.get("url"),
        "created_at": now_iso(),
    }
    _training.insert(0, item)
    return {"module": item}

# ---- Admin settings & roles ----
_admin_settings: Dict[str, Any] = {"sla_minutes": 300, "whatsapp_mode": "stub"}
_roles: List[Dict[str, Any]] = [{"id": "admin", "name": "Administrator"}, {"id": "sales", "name": "Sales"}]

@app.get("/api/admin/settings")
async def admin_get_settings():
    return _admin_settings

@app.put("/api/admin/settings")
async def admin_put_settings(body: Dict[str, Any]):
    _admin_settings.update({k: v for k, v in body.items() if v is not None})
    return {"success": True}

@app.get("/api/admin/roles")
async def admin_roles():
    return {"items": _roles}


# Filtered list endpoint (project_id)
@app.get("/api/uploads/catalogue/list")
async def list_catalogue_items_filtered(request: Request, project_id: Optional[str] = None, db=Depends(get_db)):
    try:
        q: Dict[str, Any] = {}
        if project_id:
            q["project_id"] = project_id
        items = await db["catalogue_items"].find(q, {"_id": 0}).sort("created_at", -1).to_list(length=1000)
        for it in items:
            if not it.get("url") and it.get("file_path"):
                rel = "/api/files/catalogue/" + os.path.basename(it["file_path"]) if it.get("file_path") else None
                if rel:
                    it["url"] = build_absolute_url(request, rel)
        return {"catalogues": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Entry point for local run (supervisor will run in platform)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
