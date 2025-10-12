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
from urllib.parse import urljoin

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

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

UPLOAD_ROOT = "/app/data/uploads"
os.makedirs(UPLOAD_ROOT, exist_ok=True)
app.mount("/api/files", StaticFiles(directory=UPLOAD_ROOT), name="uploaded-files")

DEFAULT_COUNTRY_CODE = "+91"
DEFAULT_OWNER_MOBILE = "+919999139938"  # Manager

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# Phone normalization helper (India default)
from typing import Optional as _Opt

def normalize_phone_india(raw: _Opt[str]) -> _Opt[str]:
    if not raw:
        return None
    digits = "".join(ch for ch in str(raw) if ch.isdigit())
    if not digits:
        return None
    # Drop leading 0 in 0XXXXXXXXXX format
    if digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]
    # If starts with 91 and has at least country+10 digits
    if digits.startswith("91") and len(digits) >= 12:
        return "+" + digits[:12]
    # If exactly 10, assume +91
    if len(digits) == 10:
        return "+91" + digits
    # Fallback
    return "+" + digits if not str(raw).startswith("+") else str(raw)

def build_absolute_url(request: Request, path: str) -> str:
    proto = request.headers.get("x-forwarded-proto") or "https"
    host = request.headers.get("x-forwarded-host") or request.client.host
    base = f"{proto}://{host}"
    if not path.startswith("/"):
        path = "/" + path
    return base.rstrip("/") + path

# ... (other sections unchanged above)

# ======== Leads (reordered: search before get by id to avoid route conflicts) ========
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

# Backward compatible search route
@app.get("/api/leads/search")
async def search_leads_alias(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=50), db=Depends(get_db)):
    return await search_leads_new(q=q, limit=limit, db=db)

    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    owner_mobile: Optional[str] = None

@app.get("/api/leads/_search")
async def search_leads_new(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=50), db=Depends(get_db)):
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

@app.get("/api/leads")
async def list_leads(status: Optional[str] = None, source: Optional[str] = None, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), db=Depends(get_db)):
    q: Dict[str, Any] = {}
    if status:
        q["status"] = status
    if source:
        q["source"] = source
    skip = (page - 1) * limit
    cursor = db["leads"].find(q, {"_id": 0}).sort("updated_at", -1).skip(skip).limit(limit)
    items = await cursor.to_list(length=limit)
    total = await db["leads"].count_documents(q)
    return {"items": items, "page": page, "limit": limit, "total": total}

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str, db=Depends(get_db)):
    doc = await db["leads"].find_one({"id": lead_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"success": True, "lead": doc}

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
    return {"success": True, "lead": doc}

@app.delete("/api/leads/{lead_id}")
async def delete_lead(lead_id: str, db=Depends(get_db)):
    res = await db["leads"].delete_one({"id": lead_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"success": True}

# ... (rest of file unchanged)
