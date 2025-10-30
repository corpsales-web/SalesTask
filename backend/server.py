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
    file_size: int
    chunk_size: Optional[int] = 1024 * 1024  # 1MB default
    total_chunks: Optional[int] = None

class UploadComplete(BaseModel):
    upload_id: str

class WhatsAppSend(BaseModel):
    to: str
    text: str

# Utility functions
def normalize_phone(phone: str) -> str:
    """Normalize phone number to +91 format"""
    if not phone:
        return phone
    
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    
    # Handle different formats
    if digits.startswith('91') and len(digits) == 12:
        return f"+{digits}"
    elif len(digits) == 10:
        return f"+91{digits}"
    elif digits.startswith('0') and len(digits) == 11:
        return f"+91{digits[1:]}"
    else:
        return f"+91{digits[-10:]}" if len(digits) >= 10 else phone

# Health endpoint
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "crm-backend",
        "time": now_iso()
    }

# Leads CRUD endpoints
@app.post("/api/leads")
async def create_lead(lead: LeadCreate, db=Depends(get_db)):
    try:
        lead_data = lead.dict()
        lead_data["id"] = str(uuid.uuid4())
        lead_data["status"] = lead_data.get("status") or "New"
        lead_data["created_at"] = now_iso()
        lead_data["updated_at"] = now_iso()
        
        # Normalize phone numbers
        if lead_data.get("phone"):
            lead_data["phone"] = normalize_phone(lead_data["phone"])
        
        # Default owner_mobile
        if not lead_data.get("owner_mobile"):
            lead_data["owner_mobile"] = "+919999139938"
        else:
            lead_data["owner_mobile"] = normalize_phone(lead_data["owner_mobile"])
        
        await db["leads"].insert_one(lead_data)
        lead_data.pop("_id", None)
        
        return {"success": True, "lead": lead_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leads")
async def list_leads(page: int = 1, limit: int = 50, db=Depends(get_db)):
    try:
        skip = (page - 1) * limit
        cursor = db["leads"].find({}, {"_id": 0}).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        total = await db["leads"].count_documents({})
        
        return {
            "items": items,
            "page": page,
            "limit": limit,
            "total": total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str, db=Depends(get_db)):
    try:
        lead = await db["leads"].find_one({"id": lead_id}, {"_id": 0})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return {"success": True, "lead": lead}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/leads/{lead_id}")
async def update_lead(lead_id: str, lead_update: LeadUpdate, db=Depends(get_db)):
    try:
        update_data = {k: v for k, v in lead_update.dict().items() if v is not None}
        update_data["updated_at"] = now_iso()
        
        # Normalize phone numbers
        if update_data.get("phone"):
            update_data["phone"] = normalize_phone(update_data["phone"])
        if update_data.get("owner_mobile"):
            update_data["owner_mobile"] = normalize_phone(update_data["owner_mobile"])
        
        result = await db["leads"].update_one(
            {"id": lead_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        updated_lead = await db["leads"].find_one({"id": lead_id}, {"_id": 0})
        return {"success": True, "lead": updated_lead}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/leads/{lead_id}")
async def delete_lead(lead_id: str, db=Depends(get_db)):
    try:
        result = await db["leads"].delete_one({"id": lead_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Lead not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Tasks CRUD endpoints
@app.post("/api/tasks")
async def create_task(task: TaskCreate, db=Depends(get_db)):
    try:
        task_data = task.dict()
        task_data["id"] = str(uuid.uuid4())
        task_data["status"] = task_data.get("status") or "Open"
        task_data["created_at"] = now_iso()
        task_data["updated_at"] = now_iso()
        
        await db["tasks"].insert_one(task_data)
        task_data.pop("_id", None)
        
        return {"success": True, "task": task_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks")
async def list_tasks(page: int = 1, limit: int = 50, db=Depends(get_db)):
    try:
        skip = (page - 1) * limit
        cursor = db["tasks"].find({}, {"_id": 0}).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        total = await db["tasks"].count_documents({})
        
        return {
            "items": items,
            "page": page,
            "limit": limit,
            "total": total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/tasks/{task_id}")
async def update_task(task_id: str, task_update: TaskUpdate, db=Depends(get_db)):
    try:
        update_data = {k: v for k, v in task_update.dict().items() if v is not None}
        update_data["updated_at"] = now_iso()
        
        result = await db["tasks"].update_one(
            {"id": task_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        
        updated_task = await db["tasks"].find_one({"id": task_id}, {"_id": 0})
        return {"success": True, "task": updated_task}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/tasks/{task_id}/status")
async def update_task_status(task_id: str, status_update: Dict[str, str], db=Depends(get_db)):
    try:
        update_data = {
            "status": status_update.get("status"),
            "updated_at": now_iso()
        }
        
        result = await db["tasks"].update_one(
            {"id": task_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        
        updated_task = await db["tasks"].find_one({"id": task_id}, {"_id": 0})
        return {"success": True, "task": updated_task}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str, db=Depends(get_db)):
    try:
        result = await db["tasks"].delete_one({"id": task_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Visual Upgrades endpoints
@app.post("/api/visual-upgrades/render")
async def visual_render(
    request: Request,
    prompt: str = Form(...),
    lead_id: Optional[str] = Form(None),
    size: str = Form("1024x1024"),
    response_format: str = Form("url"),
    image: UploadFile = File(...),
    mask: Optional[UploadFile] = File(None),
    db=Depends(get_db)
):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY is not configured on the server")
    
    # For testing purposes, simulate the visual upgrade process
    try:
        # Save uploaded files
        base_name = f"{uuid.uuid4()}_{image.filename or 'image.png'}"
        base_path = os.path.join(UPLOAD_ROOT, "visual", base_name)
        
        contents = await image.read()
        with open(base_path, "wb") as f:
            f.write(contents)
        
        base_rel = f"/api/files/visual/{base_name}"
        base_url = build_absolute_url(request, base_rel)
        
        mask_url = None
        if mask:
            mask_name = f"{uuid.uuid4()}_{mask.filename or 'mask.png'}"
            mask_path = os.path.join(UPLOAD_ROOT, "visual", mask_name)
            mask_contents = await mask.read()
            with open(mask_path, "wb") as f:
                f.write(mask_contents)
            mask_rel = f"/api/files/visual/{mask_name}"
            mask_url = build_absolute_url(request, mask_rel)
        
        # Simulate result (in real implementation, this would call OpenAI)
        result_name = f"{uuid.uuid4()}_result.png"
        result_path = os.path.join(UPLOAD_ROOT, "visual", result_name)
        # Copy original as result for testing
        with open(result_path, "wb") as f:
            f.write(contents)
        
        result_rel = f"/api/files/visual/{result_name}"
        result_url = build_absolute_url(request, result_rel)
        
        # Record in database
        upgrade_record = {
            "id": str(uuid.uuid4()),
            "lead_id": lead_id,
            "prompt": prompt,
            "size": size,
            "base_image": {"url": base_url, "path": base_rel},
            "mask_image": ({"url": mask_url, "path": f"/api/files/visual/{mask_name}"} if mask else None),
            "result": {"url": result_url, "path": result_rel},
            "created_at": now_iso(),
        }
        
        await db["visual_upgrades"].insert_one(upgrade_record)
        upgrade_record.pop("_id", None)
        
        return {"success": True, "upgrade": upgrade_record}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visual upgrade failed: {str(e)}")

# Catalogue Upload endpoints
upload_sessions = {}  # In-memory storage for upload sessions

@app.post("/api/uploads/catalogue/init")
async def init_catalogue_upload(upload_init: UploadInit):
    try:
        upload_id = str(uuid.uuid4())
        upload_sessions[upload_id] = {
            "id": upload_id,
            "filename": upload_init.filename,
            "file_size": upload_init.file_size,
            "chunk_size": upload_init.chunk_size,
            "total_chunks": upload_init.total_chunks or (upload_init.file_size // upload_init.chunk_size + 1),
            "uploaded_chunks": [],
            "status": "initialized",
            "created_at": now_iso()
        }
        
        return {"success": True, "upload_id": upload_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/uploads/catalogue/chunk")
async def upload_catalogue_chunk(
    upload_id: str = Form(...),
    chunk_number: int = Form(...),
    chunk: UploadFile = File(...)
):
    try:
        if upload_id not in upload_sessions:
            raise HTTPException(status_code=404, detail="Upload session not found")
        
        session = upload_sessions[upload_id]
        
        # Save chunk
        chunk_dir = os.path.join(UPLOAD_ROOT, "catalogue", upload_id)
        os.makedirs(chunk_dir, exist_ok=True)
        
        chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_number}")
        contents = await chunk.read()
        with open(chunk_path, "wb") as f:
            f.write(contents)
        
        session["uploaded_chunks"].append(chunk_number)
        session["status"] = "uploading"
        
        return {"success": True, "chunk_number": chunk_number}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/uploads/catalogue/state")
async def get_catalogue_upload_state(upload_id: str):
    try:
        if upload_id not in upload_sessions:
            raise HTTPException(status_code=404, detail="Upload session not found")
        
        session = upload_sessions[upload_id]
        return {
            "upload_id": upload_id,
            "status": session["status"],
            "uploaded_chunks": len(session["uploaded_chunks"]),
            "total_chunks": session["total_chunks"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/uploads/catalogue/complete")
async def complete_catalogue_upload(complete_data: UploadComplete, db=Depends(get_db)):
    try:
        upload_id = complete_data.upload_id
        
        if upload_id not in upload_sessions:
            raise HTTPException(status_code=404, detail="Upload session not found")
        
        session = upload_sessions[upload_id]
        
        # Combine chunks into final file
        chunk_dir = os.path.join(UPLOAD_ROOT, "catalogue", upload_id)
        final_path = os.path.join(UPLOAD_ROOT, "catalogue", f"{upload_id}_{session['filename']}")
        
        with open(final_path, "wb") as final_file:
            for chunk_num in sorted(session["uploaded_chunks"]):
                chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_num}")
                if os.path.exists(chunk_path):
                    with open(chunk_path, "rb") as chunk_file:
                        final_file.write(chunk_file.read())
        
        # Save to database
        catalogue_item = {
            "id": str(uuid.uuid4()),
            "upload_id": upload_id,
            "filename": session["filename"],
            "file_size": session["file_size"],
            "file_path": final_path,
            "status": "completed",
            "created_at": now_iso()
        }
        
        await db["catalogue_items"].insert_one(catalogue_item)
        catalogue_item.pop("_id", None)
        
        # Update session
        session["status"] = "completed"
        
        return {"success": True, "catalogue_item": catalogue_item}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/uploads/catalogue/cancel")
async def cancel_catalogue_upload(cancel_data: Dict[str, str]):
    try:
        upload_id = cancel_data.get("upload_id")
        
        if upload_id not in upload_sessions:
            raise HTTPException(status_code=404, detail="Upload session not found")
        
        # Clean up chunks
        chunk_dir = os.path.join(UPLOAD_ROOT, "catalogue", upload_id)
        if os.path.exists(chunk_dir):
            import shutil
            shutil.rmtree(chunk_dir)
        
        # Update session
        upload_sessions[upload_id]["status"] = "cancelled"
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/uploads/catalogue/list")
async def list_catalogue_items(db=Depends(get_db)):
    try:
        cursor = db["catalogue_items"].find({}, {"_id": 0})
        catalogues = await cursor.to_list(length=1000)
        return {"catalogues": catalogues}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WhatsApp endpoints (stub mode)
@app.get("/api/whatsapp/webhook")
async def whatsapp_webhook_verify(
    hub_mode: Optional[str] = None,
    hub_challenge: Optional[str] = None,
    hub_verify_token: Optional[str] = None
):
    # In stub mode, return 403 if no verify token configured
    verify_token = os.environ.get("WHATSAPP_VERIFY_TOKEN")
    if not verify_token:
        raise HTTPException(status_code=403, detail="Webhook verification not configured")
    
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        return int(hub_challenge)
    else:
        raise HTTPException(status_code=403, detail="Invalid verification")

@app.post("/api/whatsapp/webhook")
async def whatsapp_webhook_receive(webhook_data: Dict[str, Any], db=Depends(get_db)):
    try:
        # Store webhook event
        event_record = {
            "id": str(uuid.uuid4()),
            "webhook_data": webhook_data,
            "received_at": now_iso()
        }
        
        await db["whatsapp_events"].insert_one(event_record)
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/whatsapp/messages")
async def list_whatsapp_messages(limit: int = 50, db=Depends(get_db)):
    try:
        cursor = db["whatsapp_events"].find({}, {"_id": 0}).limit(limit)
        messages = await cursor.to_list(length=limit)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/whatsapp/send")
async def send_whatsapp_message(message: WhatsAppSend, db=Depends(get_db)):
    try:
        # In stub mode (no D360_API_KEY)
        api_key = os.environ.get("D360_API_KEY")
        
        message_record = {
            "id": str(uuid.uuid4()),
            "to": message.to,
            "text": message.text,
            "mode": "stub" if not api_key else "live",
            "sent_at": now_iso()
        }
        
        await db["whatsapp_sent"].insert_one(message_record)
        message_record.pop("_id", None)
        
        return {"success": True, "mode": "stub", "id": message_record["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Additional WhatsApp helpers used by Inbox flows (stubbed)
@app.get("/api/whatsapp/session_status")
async def whatsapp_session_status(contact: str):
    # Stub: always within 24h
    return {"within_24h": True}

@app.get("/api/whatsapp/contact_messages")
async def whatsapp_contact_messages(contact: str):
    # Stub: return last 3 messages synthetic
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
    # In stub: no-op, but could store mapping
    mapping = {"id": str(uuid.uuid4()), "contact": contact, "lead_id": body.get("lead_id"), "linked_at": now_iso()}
    await db["whatsapp_links"].insert_one(mapping)
    mapping.pop("_id", None)
    return {"success": True, "link": mapping}

@app.get("/api/whatsapp/conversations")
async def list_whatsapp_conversations(db=Depends(get_db)):
    try:
        # Return mock conversations for testing
        conversations = [
            {
                "id": str(uuid.uuid4()),
                "contact": "+919876543210",
                "last_message_text": "Hello from demo inbound 👋",
                "last_message_dir": "in",
                "owner_mobile": "+919999139938",
                "created_at": now_iso()
            }
        ]
        return conversations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)