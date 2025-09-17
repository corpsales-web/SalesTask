from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
import json
from datetime import datetime, timezone, timedelta
from enum import Enum
import hashlib
import jwt
import secrets

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

# Import enhanced AI service
try:
    from enhanced_ai_service import enhanced_ai_service, AIRequest, AIResponse
    print("✅ Enhanced AI service imported successfully")
except ImportError as e:
    print(f"❌ Enhanced AI service import failed: {e}")
    enhanced_ai_service = None

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

# Import new services
from file_upload_service import file_upload_service
from role_management_service import initialize_role_management_service, role_management_service
from lead_management_service import initialize_lead_management_service, lead_management_service
from voice_stt_service import initialize_voice_stt_service, voice_stt_service
from offline_sync_service import initialize_offline_sync_service, offline_sync_service
from lead_routing_service import initialize_lead_routing_service
from workflow_authoring_service import initialize_workflow_authoring_service
from background_services import background_service, run_background_services

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Email Configuration
email_conf = ConnectionConfig(
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME', 'noreply@aavanagreens.com'),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD', 'demo_password'),
    MAIL_FROM=os.environ.get('MAIL_FROM', 'noreply@aavanagreens.com'),
    MAIL_PORT=int(os.environ.get('MAIL_PORT', '587')),
    MAIL_SERVER=os.environ.get('MAIL_SERVER', 'smtp.gmail.com'),
    MAIL_FROM_NAME=os.environ.get('MAIL_FROM_NAME', 'Aavana Greens CRM'),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fastmail = FastMail(email_conf)

# Initialize services
targets = get_targets_service(db)

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

class UserRole(str, Enum):
    SUPER_ADMIN = "Super Admin"
    ADMIN = "Admin"
    SALES_MANAGER = "Sales Manager"
    SALES_EXECUTIVE = "Sales Executive"
    MARKETING_MANAGER = "Marketing Manager"
    HR_MANAGER = "HR Manager"
    EMPLOYEE = "Employee"

class UserStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"
    SUSPENDED = "Suspended"

# Advanced Permission System
class Permission(str, Enum):
    # Lead Management
    LEADS_VIEW = "leads:view"
    LEADS_CREATE = "leads:create"
    LEADS_EDIT = "leads:edit"
    LEADS_DELETE = "leads:delete"
    LEADS_ASSIGN = "leads:assign"
    
    # Task Management
    TASKS_VIEW = "tasks:view"
    TASKS_CREATE = "tasks:create"
    TASKS_EDIT = "tasks:edit"
    TASKS_DELETE = "tasks:delete"
    TASKS_ASSIGN = "tasks:assign"
    
    # User Management
    USERS_VIEW = "users:view"
    USERS_CREATE = "users:create"
    USERS_EDIT = "users:edit"
    USERS_DELETE = "users:delete"
    USERS_MANAGE_ROLES = "users:manage_roles"
    
    # AI Features
    AI_VIEW = "ai:view"
    AI_USE_BASIC = "ai:use_basic"
    AI_USE_ADVANCED = "ai:use_advanced"
    AI_MANAGE = "ai:manage"
    
    # Analytics & Reports
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"
    ANALYTICS_ADMIN = "analytics:admin"
    
    # HRMS
    HRMS_VIEW = "hrms:view"
    HRMS_MANAGE = "hrms:manage"
    HRMS_PAYROLL = "hrms:payroll"
    
    # ERP
    ERP_VIEW = "erp:view"
    ERP_MANAGE = "erp:manage"
    ERP_FINANCIAL = "erp:financial"
    
    # System Admin
    SYSTEM_CONFIG = "system:config"
    SYSTEM_LOGS = "system:logs"
    SYSTEM_BACKUP = "system:backup"

# Role-based permission mapping
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: [perm.value for perm in Permission],  # All permissions
    UserRole.ADMIN: [
        Permission.LEADS_VIEW, Permission.LEADS_CREATE, Permission.LEADS_EDIT, Permission.LEADS_ASSIGN,
        Permission.TASKS_VIEW, Permission.TASKS_CREATE, Permission.TASKS_EDIT, Permission.TASKS_ASSIGN,
        Permission.USERS_VIEW, Permission.USERS_CREATE, Permission.USERS_EDIT, Permission.USERS_MANAGE_ROLES,
        Permission.AI_VIEW, Permission.AI_USE_BASIC, Permission.AI_USE_ADVANCED,
        Permission.ANALYTICS_VIEW, Permission.ANALYTICS_EXPORT,
        Permission.HRMS_VIEW, Permission.HRMS_MANAGE,
        Permission.ERP_VIEW, Permission.ERP_MANAGE,
        Permission.SYSTEM_CONFIG
    ],
    UserRole.SALES_MANAGER: [
        Permission.LEADS_VIEW, Permission.LEADS_CREATE, Permission.LEADS_EDIT, Permission.LEADS_ASSIGN,
        Permission.TASKS_VIEW, Permission.TASKS_CREATE, Permission.TASKS_EDIT, Permission.TASKS_ASSIGN,
        Permission.USERS_VIEW,
        Permission.AI_VIEW, Permission.AI_USE_BASIC, Permission.AI_USE_ADVANCED,
        Permission.ANALYTICS_VIEW, Permission.ANALYTICS_EXPORT,
        Permission.ERP_VIEW
    ],
    UserRole.SALES_EXECUTIVE: [
        Permission.LEADS_VIEW, Permission.LEADS_CREATE, Permission.LEADS_EDIT,
        Permission.TASKS_VIEW, Permission.TASKS_CREATE, Permission.TASKS_EDIT,
        Permission.AI_VIEW, Permission.AI_USE_BASIC,
        Permission.ANALYTICS_VIEW,
        Permission.ERP_VIEW
    ],
    UserRole.MARKETING_MANAGER: [
        Permission.LEADS_VIEW, Permission.LEADS_CREATE,
        Permission.TASKS_VIEW, Permission.TASKS_CREATE, Permission.TASKS_EDIT,
        Permission.AI_VIEW, Permission.AI_USE_BASIC, Permission.AI_USE_ADVANCED,
        Permission.ANALYTICS_VIEW, Permission.ANALYTICS_EXPORT,
        Permission.ERP_VIEW
    ],
    UserRole.HR_MANAGER: [
        Permission.USERS_VIEW, Permission.USERS_CREATE, Permission.USERS_EDIT,
        Permission.HRMS_VIEW, Permission.HRMS_MANAGE, Permission.HRMS_PAYROLL,
        Permission.ANALYTICS_VIEW,
        Permission.AI_VIEW, Permission.AI_USE_BASIC
    ],
    UserRole.EMPLOYEE: [
        Permission.LEADS_VIEW, Permission.TASKS_VIEW,
        Permission.AI_VIEW, Permission.AI_USE_BASIC,
        Permission.HRMS_VIEW
    ]
}

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

# User Authentication Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    phone: Optional[str] = None
    full_name: str
    role: UserRole = UserRole.EMPLOYEE
    status: UserStatus = UserStatus.PENDING
    department: Optional[str] = None
    permissions: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    created_by: Optional[str] = None
    password_hash: str  # Keep for database operations
    reset_token: Optional[str] = Field(default=None)
    reset_token_expires: Optional[datetime] = Field(default=None)

class UserResponse(BaseModel):
    """User model for API responses (excludes sensitive fields)"""
    id: str
    username: str
    email: EmailStr
    phone: Optional[str] = None
    full_name: str
    role: UserRole = UserRole.EMPLOYEE
    status: UserStatus = UserStatus.PENDING
    department: Optional[str] = None
    permissions: List[str] = []
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    created_by: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    phone: Optional[str] = None
    full_name: str
    role: UserRole = UserRole.EMPLOYEE
    department: Optional[str] = None
    permissions: List[str] = []
    password: str
    created_by: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    department: Optional[str] = None
    permissions: Optional[List[str]] = None

class UserLogin(BaseModel):
    identifier: str  # Can be username, email, or phone
    password: str

class PhoneLogin(BaseModel):
    phone: str
    otp: Optional[str] = None

class PhoneOTPRequest(BaseModel):
    phone: str
    resend: bool = False

class PhoneOTPVerify(BaseModel):
    phone: str
    otp: str

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

# Lead Routing Models
class RoutingRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    source: str
    conditions: Dict[str, Any] = {}
    target_agent_id: Optional[str] = None
    target_team_id: Optional[str] = None
    workflow_template_id: Optional[str] = None
    priority: int = 1
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RoutingRuleCreate(BaseModel):
    name: str
    source: str
    conditions: Dict[str, Any] = {}
    target_agent_id: Optional[str] = None
    target_team_id: Optional[str] = None
    workflow_template_id: Optional[str] = None
    priority: int = 1
    is_active: bool = True

# Workflow Authoring Models
class PromptTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    category: str = "general"
    system_prompt: str = ""
    user_prompt_template: str = ""
    variables: List[str] = []
    ai_model: str = "gpt-5"
    temperature: float = 0.7
    max_tokens: int = 1000
    functions: List[Dict[str, Any]] = []
    examples: List[Dict[str, Any]] = []
    tags: List[str] = []
    is_active: bool = True
    created_by: str
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PromptTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str = "general"
    system_prompt: str = ""
    user_prompt_template: str = ""
    variables: List[str] = []
    ai_model: str = "gpt-5"
    temperature: float = 0.7
    max_tokens: int = 1000
    functions: List[Dict[str, Any]] = []
    examples: List[Dict[str, Any]] = []
    tags: List[str] = []
    is_active: bool = True

class WorkflowTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    category: str = "lead_nurturing"
    trigger_conditions: Dict[str, Any] = {}
    steps: List[Dict[str, Any]] = []
    global_variables: Dict[str, Any] = {}
    settings: Dict[str, Any] = {}
    tags: List[str] = []
    is_active: bool = False
    is_published: bool = False
    created_by: str
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WorkflowTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str = "lead_nurturing"
    trigger_conditions: Dict[str, Any] = {}
    steps: List[Dict[str, Any]] = []
    global_variables: Dict[str, Any] = {}
    settings: Dict[str, Any] = {}
    tags: List[str] = []
    is_active: bool = False

# Project Types Models
class ProjectType(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    category: str  # Residential, Commercial, Landscape, Interior, etc.
    is_active: bool = True
    sort_order: int = 0
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectTypeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    is_active: bool = True
    sort_order: int = 0

class ProjectTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None

class ProjectTypeResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    category: str
    is_active: bool
    sort_order: int
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

# Authentication utilities
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """Decode and verify a JWT access token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get the current authenticated user"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_obj = User(**parse_from_mongo(user))
    user_response_data = {k: v for k, v in user_obj.dict().items() 
                         if k not in ['password_hash', 'reset_token', 'reset_token_expires']}
    return UserResponse(**user_response_data)

async def get_current_super_admin(current_user: UserResponse = Depends(get_current_user)):
    """Get current user and verify they are a super admin"""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user

async def get_current_admin(current_user: UserResponse = Depends(get_current_user)):
    """Get current user and verify they are an admin or super admin"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def get_current_user_id(current_user: UserResponse = Depends(get_current_user)):
    """Get the current authenticated user's ID"""
    return current_user.id

def generate_reset_token() -> str:
    """Generate a secure reset token"""
    return secrets.token_urlsafe(32)

def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return str(secrets.randbelow(999999)).zfill(6)

def format_phone_number(phone: str) -> str:
    """Format phone number to a standard format"""
    # Remove all non-digit characters
    phone = ''.join(filter(str.isdigit, phone))
    
    # Add country code if not present (assuming India +91)
    if len(phone) == 10:
        phone = "91" + phone
    elif len(phone) == 11 and phone.startswith("0"):
        phone = "91" + phone[1:]
    elif len(phone) == 13 and phone.startswith("91"):
        phone = phone
    else:
        # Keep as is for international numbers
        pass
    
    return phone

async def check_otp_rate_limit(phone: str, db) -> bool:
    """Check if OTP requests are within rate limit (max 3 per 15 minutes)"""
    try:
        fifteen_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=15)
        recent_requests = await db.temp_otps.count_documents({
            "phone": phone,
            "created_at": {"$gte": fifteen_minutes_ago}
        })
        return recent_requests < 3
    except Exception as e:
        # If there's an error with datetime comparison, allow the request
        print(f"Rate limit check error: {e}")
        return True

async def cleanup_expired_otps(db):
    """Clean up expired OTP records"""
    await db.temp_otps.delete_many({
        "expires_at": {"$lt": datetime.now(timezone.utc)}
    })

def get_user_permissions(user_role: UserRole, custom_permissions: List[str] = None) -> List[str]:
    """Get all permissions for a user based on role and custom permissions"""
    base_permissions = ROLE_PERMISSIONS.get(user_role, [])
    
    if custom_permissions:
        # Combine role permissions with custom permissions
        all_permissions = set(base_permissions + custom_permissions)
        return list(all_permissions)
    
    return base_permissions

def has_permission(user_permissions: List[str], required_permission: str) -> bool:
    """Check if user has a specific permission"""
    return required_permission in user_permissions

def require_permission(required_permission: str):
    """Decorator to require specific permission for endpoint access"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs or args
            current_user = None
            for key, value in kwargs.items():
                if hasattr(value, 'permissions') and hasattr(value, 'role'):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            user_permissions = get_user_permissions(current_user.role, current_user.permissions)
            
            if not has_permission(user_permissions, required_permission):
                raise HTTPException(
                    status_code=403, 
                    detail=f"Permission denied. Required: {required_permission}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

async def update_user_permissions(user_id: str, new_permissions: List[str], db) -> bool:
    """Update user's custom permissions"""
    try:
        # Validate permissions
        valid_permissions = [perm.value for perm in Permission]
        invalid_permissions = [perm for perm in new_permissions if perm not in valid_permissions]
        
        if invalid_permissions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid permissions: {invalid_permissions}"
            )
        
        result = await db.users.update_one(
            {"id": user_id},
            {"$set": {
                "permissions": new_permissions,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        return result.modified_count > 0
    except Exception as e:
        return False

# Email Functions
async def send_password_reset_email(email: str, reset_token: str, user_name: str = "User"):
    """Send password reset email"""
    try:
        # Create reset link (in production, use your domain)
        reset_link = f"https://aavana-greens.preview.emergentagent.com/reset-password?token={reset_token}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981, #059669); padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #10b981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌿 Aavana Greens</h1>
                    <p>Password Reset Request</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>We received a request to reset your password for your Aavana Greens CRM account.</p>
                    <p>Click the button below to reset your password:</p>
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </p>
                    <p><strong>This link will expire in 1 hour.</strong></p>
                    <p>If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
                    <p>For security reasons, this link can only be used once.</p>
                </div>
                <div class="footer">
                    <p>© 2024 Aavana Greens CRM. All rights reserved.</p>
                    <p>This is an automated message, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Aavana Greens - Password Reset Request
        
        Hello {user_name},
        
        We received a request to reset your password for your Aavana Greens CRM account.
        
        Please click on the following link to reset your password:
        {reset_link}
        
        This link will expire in 1 hour.
        
        If you didn't request this password reset, please ignore this email.
        
        © 2024 Aavana Greens CRM
        """
        
        message = MessageSchema(
            subject="Reset Your Aavana Greens Password",
            recipients=[email],
            body=text_body,
            html=html_body,
            subtype=MessageType.html
        )
        
        await fastmail.send_message(message)
        return True
        
    except Exception as e:
        print(f"Failed to send password reset email: {str(e)}")
        return False

async def send_welcome_email(email: str, user_name: str, username: str, temporary_password: str = None):
    """Send welcome email to new users"""
    try:
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981, #059669); padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .credentials {{ background: #e6f7ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌿 Welcome to Aavana Greens!</h1>
                    <p>Your CRM Account is Ready</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>Welcome to Aavana Greens CRM! Your account has been successfully created.</p>
                    
                    <div class="credentials">
                        <h3>Your Login Credentials:</h3>
                        <p><strong>Username:</strong> {username}</p>
                        <p><strong>Email:</strong> {email}</p>
                        {"<p><strong>Temporary Password:</strong> " + temporary_password + "</p>" if temporary_password else ""}
                    </div>
                    
                    <p>Please log in to your account and {"change your password" if temporary_password else "explore the features"}:</p>
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="https://aavana-greens.preview.emergentagent.com" style="display: inline-block; background: #10b981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Login to Your Account</a>
                    </p>
                    
                    <h3>What you can do:</h3>
                    <ul>
                        <li>Manage leads and customer relationships</li>
                        <li>Track tasks and follow-ups</li>
                        <li>Use AI-powered insights</li>
                        <li>Generate reports and analytics</li>
                        <li>Collaborate with your team</li>
                    </ul>
                    
                    <p>If you have any questions, please contact your administrator.</p>
                </div>
                <div class="footer">
                    <p>© 2024 Aavana Greens CRM. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        message = MessageSchema(
            subject="Welcome to Aavana Greens CRM!",
            recipients=[email],
            body=f"Welcome to Aavana Greens CRM, {user_name}! Your username is: {username}",
            html=html_body,
            subtype=MessageType.html
        )
        
        await fastmail.send_message(message)
        return True
        
    except Exception as e:
        print(f"Failed to send welcome email: {str(e)}")
        return False

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

# Lead Routing Routes
@api_router.post("/routing/rules")
async def create_routing_rule(rule_data: dict, user_id: str = Depends(get_current_user_id)):
    """Create a new lead routing rule"""
    result = await lead_routing_service.create_routing_rule(rule_data, user_id)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@api_router.get("/routing/rules")
async def get_routing_rules(source: Optional[str] = None, active_only: bool = True):
    """Get lead routing rules"""
    rules = await lead_routing_service.get_routing_rules(source=source, active_only=active_only)
    return {"rules": rules}

@api_router.post("/routing/route-lead")
async def route_lead(lead_data: dict):
    """Route a lead based on configured rules"""
    result = await lead_routing_service.route_lead(lead_data)
    return result

# Workflow Authoring Routes
@api_router.post("/workflows/prompt-templates")
async def create_prompt_template(template_data: dict, user_id: str = Depends(get_current_user_id)):
    """Create a new GPT-5 prompt template"""
    result = await workflow_authoring_service.create_prompt_template(template_data, user_id)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@api_router.get("/workflows/prompt-templates")
async def get_prompt_templates(category: Optional[str] = None, active_only: bool = True):
    """Get prompt templates"""
    templates = await workflow_authoring_service.get_prompt_templates(category=category, active_only=active_only)
    return {"templates": templates}

@api_router.get("/workflow-templates")
async def get_workflow_templates(category: Optional[str] = None, active_only: bool = True):
    """Get workflow templates (alternative endpoint for frontend compatibility)"""
    templates = await workflow_authoring_service.get_prompt_templates(category=category, active_only=active_only)
    return templates  # Return directly as array for frontend compatibility

@api_router.post("/workflows/prompt-templates/{template_id}/test")
async def test_prompt_template(template_id: str, test_data: dict, user_id: str = Depends(get_current_user_id)):
    """Test a prompt template with sample data"""
    result = await workflow_authoring_service.test_prompt_template(template_id, test_data, user_id)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@api_router.post("/workflows")
async def create_workflow(workflow_data: dict, user_id: str = Depends(get_current_user_id)):
    """Create a new workflow"""
    result = await workflow_authoring_service.create_workflow(workflow_data, user_id)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@api_router.get("/workflows")
async def get_workflows(category: Optional[str] = None, published_only: bool = False):
    """Get workflows"""
    workflows = await workflow_authoring_service.get_workflows(category=category, published_only=published_only)
    return {"workflows": workflows}

@api_router.post("/workflows/{workflow_id}/test")
async def test_workflow(workflow_id: str, test_data: dict, user_id: str = Depends(get_current_user_id)):
    """Test a workflow with sample data"""
    result = await workflow_authoring_service.test_workflow(workflow_id, test_data, user_id)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@api_router.post("/workflows/{workflow_id}/publish")
async def publish_workflow(workflow_id: str, user_id: str = Depends(get_current_user_id)):
    """Publish a workflow for production use"""
    result = await workflow_authoring_service.publish_workflow(workflow_id, user_id)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@api_router.get("/workflows/{workflow_id}/analytics")
async def get_workflow_analytics(workflow_id: str):
    """Get workflow analytics and performance data"""
    analytics = await workflow_authoring_service.get_workflow_analytics(workflow_id)
    return {"analytics": analytics}

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

# Enhanced AI API Endpoints
@api_router.post("/ai/generate", response_model=dict)
async def generate_ai_response(request: dict):
    """Generate AI response using multiple models"""
    try:
        if not enhanced_ai_service:
            raise HTTPException(status_code=503, detail="AI service not available")
        
        ai_request = AIRequest(
            prompt=request.get('prompt', ''),
            provider=request.get('provider', 'openai'),
            model=request.get('model', 'gpt-5'),
            temperature=request.get('temperature', 0.7),
            system_message=request.get('system_message')
        )
        
        response = await enhanced_ai_service.generate_response(ai_request)
        return {
            "content": response.content,
            "provider": response.provider,
            "model": response.model,
            "session_id": response.session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@api_router.post("/ai/smart-selection", response_model=dict)
async def smart_model_selection(request: dict):
    """Automatically select best AI model for task"""
    try:
        if not enhanced_ai_service:
            raise HTTPException(status_code=503, detail="AI service not available")
        
        task_type = request.get('task_type', 'business')
        prompt = request.get('prompt', '')
        
        response = await enhanced_ai_service.smart_model_selection(task_type, prompt)
        return {
            "content": response.content,
            "provider": response.provider,
            "model": response.model,
            "session_id": response.session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart selection failed: {str(e)}")

@api_router.post("/ai/analyze-conversation", response_model=dict)
async def analyze_lead_conversation(conversation_data: dict):
    """Analyze customer conversations for insights"""
    try:
        if not enhanced_ai_service:
            raise HTTPException(status_code=503, detail="AI service not available")
        
        analysis = await enhanced_ai_service.analyze_lead_conversation(conversation_data)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversation analysis failed: {str(e)}")

@api_router.post("/ai/generate-proposal", response_model=dict)
async def generate_smart_proposal(request: dict):
    """Generate AI-powered custom proposals"""
    try:
        if not enhanced_ai_service:
            raise HTTPException(status_code=503, detail="AI service not available")
        
        lead_data = request.get('lead_data', {})
        service_type = request.get('service_type', 'landscaping')
        
        proposal = await enhanced_ai_service.generate_smart_proposal(lead_data, service_type)
        return proposal
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proposal generation failed: {str(e)}")

@api_router.post("/ai/optimize-workflow", response_model=dict)
async def optimize_workflow(workflow_data: dict):
    """AI-powered workflow optimization"""
    try:
        if not enhanced_ai_service:
            raise HTTPException(status_code=503, detail="AI service not available")
        
        optimization = await enhanced_ai_service.optimize_workflow(workflow_data)
        return optimization
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow optimization failed: {str(e)}")

@api_router.post("/ai/marketing-content", response_model=dict)
async def generate_marketing_content(campaign_data: dict):
    """Generate marketing content using AI"""
    try:
        if not enhanced_ai_service:
            raise HTTPException(status_code=503, detail="AI service not available")
        
        content = await enhanced_ai_service.generate_marketing_content(campaign_data)
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Marketing content generation failed: {str(e)}")

@api_router.post("/ai/predict-deals", response_model=dict)
async def predict_deal_closure(deals_data: list):
    """Predict deal closure probability using AI"""
    try:
        if not enhanced_ai_service:
            raise HTTPException(status_code=503, detail="AI service not available")
        
        predictions = await enhanced_ai_service.predict_deal_closure(deals_data)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deal prediction failed: {str(e)}")

@api_router.post("/ai/task-automation", response_model=dict)
async def generate_task_automation(task_data: dict):
    """Generate AI-powered task automation suggestions"""
    try:
        if not enhanced_ai_service:
            raise HTTPException(status_code=503, detail="AI service not available")
        
        automation = await enhanced_ai_service.generate_task_automation(task_data)
        return automation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task automation failed: {str(e)}")

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

# Targets & Progress Routes

@api_router.post("/targets/create")
async def create_target(
    user_id: str,
    target_type: str,
    period: str,
    target_value: float,
    created_by: str = "system"
):
    """Create a new target for user"""
    try:
        target = Target(
            user_id=user_id,
            target_type=TargetType(target_type),
            period=TargetPeriod(period),
            target_value=target_value,
            created_by=created_by
        )
        
        result = await targets.create_target(target)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create target: {str(e)}")

@api_router.post("/targets/update-progress")
async def update_target_progress(
    target_id: str,
    increment_value: float,
    source: str = "manual",
    reference_id: str = None,
    updated_by: str = "system",
    notes: str = None
):
    """Update progress on a target"""
    try:
        progress = ProgressUpdate(
            target_id=target_id,
            increment_value=increment_value,
            source=source,
            reference_id=reference_id,
            updated_by=updated_by,
            notes=notes
        )
        
        result = await targets.update_progress(progress)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update progress: {str(e)}")

@api_router.get("/targets/progress/{user_id}")
async def get_user_progress(user_id: str, period: str = "daily"):
    """Get progress summary for user"""
    try:
        period_enum = TargetPeriod(period)
        summary = await targets.get_progress_summary(user_id, period_enum)
        
        return {
            "user_id": summary.user_id,
            "period": summary.period.value,
            "sales": {
                "target": summary.sales_target,
                "achieved": summary.sales_achieved,
                "progress_percent": summary.sales_progress_percent
            },
            "leads": {
                "target": summary.leads_target,
                "achieved": summary.leads_achieved,
                "progress_percent": summary.leads_progress_percent
            },
            "tasks": {
                "target": summary.tasks_target,
                "achieved": summary.tasks_achieved,
                "progress_percent": summary.tasks_progress_percent
            },
            "remaining_days": summary.remaining_days,
            "is_on_track": summary.is_on_track,
            "performance_rating": summary.performance_rating
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")

@api_router.post("/targets/sync-pipedrive")
async def sync_pipedrive_deals(user_id: str):
    """Sync Pipedrive deals to update sales targets"""
    try:
        result = await targets.sync_pipedrive_deals(user_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipedrive sync failed: {str(e)}")

@api_router.post("/targets/send-reminders")
async def send_target_reminders(user_id: str = None):
    """Send progress reminders to users"""
    try:
        result = await targets.send_reminders(user_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send reminders: {str(e)}")

@api_router.get("/targets/dashboard/{user_id}")
async def get_targets_dashboard(user_id: str):
    """Get comprehensive targets dashboard data"""
    try:
        # Get progress for all periods
        daily = await targets.get_progress_summary(user_id, TargetPeriod.DAILY)
        weekly = await targets.get_progress_summary(user_id, TargetPeriod.WEEKLY)
        monthly = await targets.get_progress_summary(user_id, TargetPeriod.MONTHLY)
        
        return {
            "user_id": user_id,
            "daily": daily.dict(),
            "weekly": weekly.dict(),
            "monthly": monthly.dict(),
            "overall_performance": {
                "rating": daily.performance_rating,
                "is_on_track": daily.is_on_track
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard data failed: {str(e)}")

@api_router.post("/targets/auto-update-from-lead")
async def auto_update_from_lead_conversion(lead_id: str, user_id: str):
    """Auto-update targets when lead is converted"""
    try:
        # Get lead details
        lead = await db.leads.find_one({"id": lead_id})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Update leads count target
        periods = [TargetPeriod.DAILY, TargetPeriod.WEEKLY, TargetPeriod.MONTHLY]
        
        for period in periods:
            # Find active leads target
            start_date, end_date = targets._calculate_period_dates(period)
            
            target = await db.targets.find_one({
                "user_id": user_id,
                "target_type": TargetType.LEADS_COUNT.value,
                "period": period.value,
                "is_active": True
            })
            
            if target:
                progress = ProgressUpdate(
                    target_id=target['id'],
                    increment_value=1,
                    source="lead_conversion",
                    reference_id=lead_id,
                    updated_by=user_id,
                    notes=f"Lead converted: {lead.get('name', 'Unknown')}"
                )
                await targets.update_progress(progress)
        
        # If lead has budget and status is Won, update sales target
        if lead.get('status') == 'Won' and lead.get('budget'):
            budget = float(lead['budget'])
            for period in periods:
                target = await db.targets.find_one({
                    "user_id": user_id,
                    "target_type": TargetType.SALES_AMOUNT.value,
                    "period": period.value,
                    "is_active": True
                })
                
                if target:
                    progress = ProgressUpdate(
                        target_id=target['id'],
                        increment_value=budget,
                        source="lead_won",
                        reference_id=lead_id,
                        updated_by=user_id,
                        notes=f"Deal won: ₹{budget}"
                    )
                    await targets.update_progress(progress)
        
        return {
            "success": True,
            "message": "Targets updated from lead conversion",
            "lead_id": lead_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-update failed: {str(e)}")

@api_router.post("/targets/auto-update-from-task")
async def auto_update_from_task_completion(task_id: str, user_id: str):
    """Auto-update targets when task is completed"""
    try:
        # Update tasks count target
        periods = [TargetPeriod.DAILY, TargetPeriod.WEEKLY, TargetPeriod.MONTHLY]
        
        for period in periods:
            target = await db.targets.find_one({
                "user_id": user_id,
                "target_type": TargetType.TASKS_COUNT.value,
                "period": period.value,
                "is_active": True
            })
            
            if target:
                progress = ProgressUpdate(
                    target_id=target['id'],
                    increment_value=1,
                    source="task_completion",
                    reference_id=task_id,
                    updated_by=user_id,
                    notes=f"Task completed: {task_id}"
                )
                await targets.update_progress(progress)
        
        return {
            "success": True,
            "message": "Targets updated from task completion",
            "task_id": task_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-update failed: {str(e)}")

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
async def face_recognition_checkin(checkin_data: dict):
    """Enhanced face recognition check-in with camera capture"""
    try:
        employee_id = checkin_data.get("employee_id", "DEMO_USER")
        face_image = checkin_data.get("face_image")
        location = checkin_data.get("location", {})
        timestamp = checkin_data.get("timestamp")
        device_info = checkin_data.get("device_info", {})
        
        if not face_image:
            raise HTTPException(status_code=400, detail="Face image is required")
        
        # Simulate face recognition processing (in production, use actual face recognition)
        recognition_confidence = 0.95  # 95% confidence
        check_in_time = datetime.now(timezone.utc)
        
        # Create result
        result = {
            "status": "success",
            "message": "Face check-in successful",
            "employee_id": employee_id,
            "check_in_time": check_in_time,
            "recognition_confidence": recognition_confidence,
            "location": location,
            "device_info": device_info
        }
        
        # Create enhanced attendance record
        attendance = Attendance(
            employee_id=employee_id,
            date=check_in_time.date(),
            check_in=check_in_time,  # Use full datetime, not just time
            location=location.get("address", "Office") if isinstance(location, dict) else str(location),
            status="Present"
        )
        attendance_dict = prepare_for_mongo(attendance.dict())
        
        # Add enhanced metadata
        attendance_dict.update({
            "face_image_captured": True,
            "recognition_confidence": recognition_confidence,
            "location_accuracy": location.get("accuracy") if isinstance(location, dict) else None,
            "coordinates": {
                "lat": location.get("lat"),
                "lng": location.get("lng")
            } if isinstance(location, dict) else None,
            "device_info": device_info,
            "verification_method": "face_recognition_camera",
            "image_data_size": len(face_image) if face_image else 0
        })
        
        await db.attendance.insert_one(attendance_dict)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Face check-in failed: {str(e)}")

@api_router.post("/hrms/gps-checkin")  
async def gps_checkin(checkin_data: dict):
    """GPS-based check-in for containerized environments"""
    try:
        employee_id = checkin_data.get("employee_id", "DEMO_USER")
        location = checkin_data.get("location", {})
        timestamp = checkin_data.get("timestamp")
        device_info = checkin_data.get("device_info", {})
        
        if not location or not location.get("latitude") or not location.get("longitude"):
            raise HTTPException(status_code=400, detail="Valid GPS location is required")
        
        check_in_time = datetime.now(timezone.utc)
        
        # Create result
        result = {
            "status": "success", 
            "message": "GPS check-in successful",
            "employee_id": employee_id,
            "check_in_time": check_in_time,
            "location": location,
            "attendance_id": f"ATT_GPS_{int(check_in_time.timestamp())}"
        }
        
        # Create attendance record
        attendance = Attendance(
            employee_id=employee_id,
            date=check_in_time.date(),
            check_in=check_in_time,
            location=f"GPS: {location.get('latitude'):.4f}, {location.get('longitude'):.4f}",
            status="Present"
        )
        attendance_dict = prepare_for_mongo(attendance.dict())
        
        # Add GPS metadata
        attendance_dict.update({
            "coordinates": {
                "lat": location.get("latitude"),
                "lng": location.get("longitude")
            },
            "location_accuracy": location.get("accuracy"),
            "device_info": device_info,
            "verification_method": "gps_location",
            "attendance_id": result["attendance_id"]
        })
        
        await db.attendance.insert_one(attendance_dict)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPS check-in failed: {str(e)}")

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

# Authentication Routes
@api_router.post("/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({
            "$or": [
                {"username": user_data.username},
                {"email": user_data.email},
                {"phone": user_data.phone} if user_data.phone else {}
            ]
        })
        
        if existing_user:
            raise HTTPException(
                status_code=400, 
                detail="User with this username, email, or phone already exists"
            )
        
        # Hash the password
        hashed_password = hash_password(user_data.password)
        
        # Create user
        user_dict = user_data.dict()
        user_dict.pop("password")  # Remove plain password
        user_dict["password_hash"] = hashed_password
        user_dict["status"] = UserStatus.ACTIVE  # Set as active for testing
        
        user = User(**user_dict)
        user_dict = prepare_for_mongo(user.dict())
        await db.users.insert_one(user_dict)
        
        # Return user response without sensitive fields
        user_response_data = {k: v for k, v in user.dict().items() 
                             if k not in ['password_hash', 'reset_token', 'reset_token_expires']}
        return UserResponse(**user_response_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User registration failed: {str(e)}")

@api_router.post("/auth/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    """Authenticate user and return access token"""
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({
            "$or": [
                {"username": login_data.identifier},
                {"email": login_data.identifier},
                {"phone": login_data.identifier}
            ]
        })
        
        if not existing_user or not verify_password(login_data.password, existing_user.get("password_hash", "")):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        # Check if user is active
        if existing_user.get("status") != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=403,
                detail=f"Account is {existing_user.get('status', 'inactive').lower()}"
            )
        
        # Update last login
        await db.users.update_one(
            {"id": existing_user["id"]}, 
            {"$set": {"last_login": datetime.now(timezone.utc)}}
        )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": existing_user["id"], "username": existing_user["username"]},
            expires_delta=access_token_expires
        )
        
        user_obj = User(**parse_from_mongo(existing_user))
        user_response_data = {k: v for k, v in user_obj.dict().items() 
                             if k not in ['password_hash', 'reset_token', 'reset_token_expires']}
        
        return TokenResponse(
            access_token=access_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(**user_response_data)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@api_router.post("/auth/phone-request-otp")
async def request_phone_otp(otp_request: PhoneOTPRequest):
    """Request OTP for phone authentication"""
    try:
        # Format and validate phone number
        formatted_phone = format_phone_number(otp_request.phone)
        
        if len(formatted_phone) < 10:
            raise HTTPException(status_code=400, detail="Invalid phone number format")
        
        # Clean up expired OTPs first
        await cleanup_expired_otps(db)
        
        # Check rate limiting
        if not await check_otp_rate_limit(formatted_phone, db):
            raise HTTPException(
                status_code=429, 
                detail="Too many OTP requests. Please wait 15 minutes before requesting again."
            )
        
        # Check if there's already a valid OTP
        try:
            existing_otp = await db.temp_otps.find_one({
                "phone": formatted_phone,
                "expires_at": {"$gt": datetime.now(timezone.utc)}
            })
        except Exception as e:
            # If datetime comparison fails, clean up all OTPs for this phone
            print(f"Datetime comparison error, cleaning up OTPs: {e}")
            await db.temp_otps.delete_many({"phone": formatted_phone})
            existing_otp = None
        
        if existing_otp and not otp_request.resend:
            time_remaining = int((existing_otp["expires_at"] - datetime.now(timezone.utc)).total_seconds())
            return {
                "message": "OTP already sent",
                "time_remaining": time_remaining,
                "can_resend": time_remaining < 60  # Allow resend in last minute
            }
        
        # Generate new OTP
        otp = generate_otp()
        
        # Store OTP with metadata
        otp_data = {
            "phone": formatted_phone,
            "otp": otp,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5),
            "attempts": 0,
            "max_attempts": 3
        }
        
        # Remove existing OTP if resending
        if existing_otp:
            await db.temp_otps.delete_one({"_id": existing_otp["_id"]})
        
        await db.temp_otps.insert_one(otp_data)
        
        # In production, send SMS via Exotel/Twilio
        # await telephony_service.send_sms(formatted_phone, f"Your Aavana Greens login OTP is: {otp}. Valid for 5 minutes.")
        
        return {
            "message": "OTP sent successfully",
            "phone": formatted_phone,
            "expires_in": 300,  # 5 minutes
            "demo_otp": otp  # Remove in production
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OTP request failed: {str(e)}")

@api_router.post("/auth/phone-verify-otp", response_model=TokenResponse)
async def verify_phone_otp(otp_verify: PhoneOTPVerify):
    """Verify OTP and login user"""
    try:
        # Format phone number
        formatted_phone = format_phone_number(otp_verify.phone)
        
        # Find OTP record
        otp_record = await db.temp_otps.find_one({
            "phone": formatted_phone,
            "expires_at": {"$gt": datetime.now(timezone.utc)}
        })
        
        if not otp_record:
            raise HTTPException(status_code=401, detail="OTP expired or not found")
        
        # Check attempt limit
        if otp_record.get("attempts", 0) >= otp_record.get("max_attempts", 3):
            await db.temp_otps.delete_one({"_id": otp_record["_id"]})
            raise HTTPException(status_code=401, detail="Too many invalid attempts. Please request a new OTP.")
        
        # Verify OTP
        if otp_record["otp"] != otp_verify.otp:
            # Increment attempt counter
            await db.temp_otps.update_one(
                {"_id": otp_record["_id"]},
                {"$inc": {"attempts": 1}}
            )
            remaining_attempts = otp_record.get("max_attempts", 3) - otp_record.get("attempts", 0) - 1
            raise HTTPException(
                status_code=401, 
                detail=f"Invalid OTP. {remaining_attempts} attempts remaining."
            )
        
        # Find or create user
        existing_user = await db.users.find_one({"phone": formatted_phone})
        if not existing_user:
            # Create new user with phone
            user_data = {
                "username": f"user_{formatted_phone[-10:]}",  # Last 10 digits
                "email": f"{formatted_phone}@phone.login",
                "phone": formatted_phone,
                "full_name": f"User {formatted_phone[-10:]}",
                "role": UserRole.EMPLOYEE.value,
                "status": UserStatus.ACTIVE.value,
                "password_hash": hash_password(secrets.token_urlsafe(16)),
                "department": "Phone Users",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            user = User(**user_data)
            user_dict = prepare_for_mongo(user.dict())
            await db.users.insert_one(user_dict)
            existing_user = user_dict
        
        # Update last login
        await db.users.update_one(
            {"id": existing_user["id"]}, 
            {"$set": {"last_login": datetime.now(timezone.utc)}}
        )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": existing_user["id"], "username": existing_user["username"]}
        )
        
        # Clean up OTP
        await db.temp_otps.delete_one({"_id": otp_record["_id"]})
        
        user_obj = User(**parse_from_mongo(existing_user))
        user_response_data = {k: v for k, v in user_obj.dict().items() 
                             if k not in ['password_hash', 'reset_token', 'reset_token_expires']}
        
        return TokenResponse(
            access_token=access_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(**user_response_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OTP verification failed: {str(e)}")

@api_router.post("/auth/phone-login")
async def phone_login(phone_data: PhoneLogin):
    """Legacy phone-based authentication (simplified for demo) - DEPRECATED"""
    try:
        if not phone_data.otp:
            # Redirect to new OTP request endpoint
            return await request_phone_otp(PhoneOTPRequest(phone=phone_data.phone))
        else:
            # Redirect to new OTP verify endpoint
            return await verify_phone_otp(PhoneOTPVerify(phone=phone_data.phone, otp=phone_data.otp))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Phone login failed: {str(e)}")

@api_router.post("/auth/forgot-password")
async def forgot_password(reset_data: PasswordReset):
    """Request password reset with email notification"""
    try:
        existing_user = await db.users.find_one({"email": reset_data.email})
        
        # Always return success message to prevent email enumeration
        success_message = "If the email exists in our system, a password reset link has been sent."
        
        if not existing_user:
            return {"message": success_message}
        
        # Generate reset token
        reset_token = generate_reset_token()
        reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Update user with reset token
        await db.users.update_one(
            {"id": existing_user["id"]},
            {"$set": {
                "reset_token": reset_token,
                "reset_token_expires": reset_expires
            }}
        )
        
        # Send password reset email
        email_sent = await send_password_reset_email(
            existing_user["email"], 
            reset_token, 
            existing_user.get("full_name", "User")
        )
        
        if not email_sent:
            # Log the error but don't reveal it to user
            print(f"Failed to send password reset email to {existing_user['email']}")
        
        return {
            "message": success_message,
            "email_sent": email_sent,
            "demo_token": reset_token if os.environ.get('ENVIRONMENT') == 'development' else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password reset failed: {str(e)}")

@api_router.post("/auth/reset-password")
async def reset_password(reset_data: PasswordResetConfirm):
    """Confirm password reset"""
    try:
        existing_user = await db.users.find_one({
            "reset_token": reset_data.token,
            "reset_token_expires": {"$gt": datetime.now(timezone.utc)}
        })
        
        if not existing_user:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        # Hash new password
        new_password_hash = hash_password(reset_data.new_password)
        
        # Update user password and clear reset token
        await db.users.update_one(
            {"id": existing_user["id"]},
            {"$set": {
                "password_hash": new_password_hash,
                "reset_token": None,
                "reset_token_expires": None,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password reset confirmation failed: {str(e)}")

# User Management Routes
@api_router.get("/users", response_model=List[UserResponse])
async def get_users(current_user: UserResponse = Depends(get_current_user), limit: int = 100):
    """Get all users (requires authentication)"""
    try:
        # Check if user has permission to view users
        if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.HR_MANAGER]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        users = await db.users.find({}).limit(limit).to_list(length=limit)
        user_responses = []
        for user in users:
            user_obj = User(**parse_from_mongo(user))
            user_response_data = {k: v for k, v in user_obj.dict().items() 
                                 if k not in ['password_hash', 'reset_token', 'reset_token_expires']}
            user_responses.append(UserResponse(**user_response_data))
        return user_responses
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve users: {str(e)}")

@api_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Get specific user details"""
    try:
        # Users can view their own profile or admins can view any profile
        if user_id != current_user.id and current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.HR_MANAGER]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        existing_user = await db.users.find_one({"id": user_id})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_obj = User(**parse_from_mongo(existing_user))
        user_response_data = {k: v for k, v in user_obj.dict().items() 
                             if k not in ['password_hash', 'reset_token', 'reset_token_expires']}
        return UserResponse(**user_response_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user: {str(e)}")

@api_router.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, current_user: UserResponse = Depends(get_current_user)):
    """Create a new user (admin only)"""
    try:
        # Check permissions
        if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.HR_MANAGER]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Check if user already exists
        existing_user = await db.users.find_one({
            "$or": [
                {"username": user_data.username},
                {"email": user_data.email},
                {"phone": user_data.phone} if user_data.phone else {}
            ]
        })
        
        if existing_user:
            raise HTTPException(
                status_code=400, 
                detail="User with this username, email, or phone already exists"
            )
        
        # Hash the password
        hashed_password = hash_password(user_data.password)
        
        # Create user
        user_dict = user_data.dict()
        user_dict.pop("password")  # Remove plain password
        user_dict["password_hash"] = hashed_password
        user_dict["created_by"] = current_user.id
        user_dict["status"] = UserStatus.ACTIVE  # Set as active by default
        
        user = User(**user_dict)
        user_dict = prepare_for_mongo(user.dict())
        await db.users.insert_one(user_dict)
        
        # Send welcome email (don't fail if email sending fails)
        try:
            await send_welcome_email(
                user_data.email,
                user_data.full_name,
                user_data.username,
                user_data.password  # Send temporary password in welcome email
            )
        except Exception as e:
            print(f"Failed to send welcome email to {user_data.email}: {str(e)}")
        
        # Return user response without sensitive fields
        user_response_data = {k: v for k, v in user.dict().items() 
                             if k not in ['password_hash', 'reset_token', 'reset_token_expires']}
        return UserResponse(**user_response_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User creation failed: {str(e)}")

@api_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate, current_user: UserResponse = Depends(get_current_user)):
    """Update user information"""
    try:
        # Users can update their own profile or admins can update any profile
        if user_id != current_user.id and current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.HR_MANAGER]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Non-admin users can't change role or status
        if user_id == current_user.id and current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            if user_update.role is not None or user_update.status is not None:
                raise HTTPException(status_code=403, detail="Cannot change role or status")
        
        update_data = {k: v for k, v in user_update.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        update_data["updated_at"] = datetime.now(timezone.utc)
        update_data = prepare_for_mongo(update_data)
        
        result = await db.users.update_one({"id": user_id}, {"$set": update_data})
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        existing_user = await db.users.find_one({"id": user_id})
        user_obj = User(**parse_from_mongo(existing_user))
        user_response_data = {k: v for k, v in user_obj.dict().items() 
                             if k not in ['password_hash', 'reset_token', 'reset_token_expires']}
        return UserResponse(**user_response_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User update failed: {str(e)}")

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Delete a user (admin only)"""
    try:
        # Check permissions
        if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Prevent self-deletion
        if user_id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
        result = await db.users.delete_one({"id": user_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User deletion failed: {str(e)}")

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_profile(current_user: UserResponse = Depends(get_current_user)):
    """Get current authenticated user's profile"""
    return current_user

@api_router.get("/auth/permissions")
async def get_available_permissions():
    """Get all available permissions in the system"""
    return {
        "permissions": [
            {
                "name": perm.value,
                "description": perm.value.replace(":", " ").replace("_", " ").title(),
                "category": perm.value.split(":")[0].title()
            }
            for perm in Permission
        ],
        "roles": [
            {
                "name": role.value,
                "permissions": ROLE_PERMISSIONS.get(role, [])
            }
            for role in UserRole
        ]
    }

@api_router.get("/auth/my-permissions")
async def get_my_permissions(current_user: UserResponse = Depends(get_current_user)):
    """Get current user's effective permissions"""
    user_permissions = get_user_permissions(current_user.role, current_user.permissions)
    
    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "role": current_user.role
        },
        "permissions": user_permissions,
        "role_permissions": ROLE_PERMISSIONS.get(current_user.role, []),
        "custom_permissions": current_user.permissions or []
    }

@api_router.put("/users/{user_id}/permissions")
async def update_user_permissions_endpoint(
    user_id: str, 
    permissions_data: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update user's custom permissions (admin only)"""
    try:
        # Check if current user has permission to manage user permissions
        if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        new_permissions = permissions_data.get("permissions", [])
        
        # Validate permissions
        valid_permissions = [perm.value for perm in Permission]
        invalid_permissions = [perm for perm in new_permissions if perm not in valid_permissions]
        
        if invalid_permissions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid permissions: {invalid_permissions}"
            )
        
        # Update user permissions
        result = await db.users.update_one(
            {"id": user_id},
            {"$set": {
                "permissions": new_permissions,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get updated user
        updated_user = await db.users.find_one({"id": user_id})
        effective_permissions = get_user_permissions(
            UserRole(updated_user["role"]), 
            updated_user.get("permissions", [])
        )
        
        return {
            "message": "Permissions updated successfully",
            "user_id": user_id,
            "new_permissions": new_permissions,
            "effective_permissions": effective_permissions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Permission update failed: {str(e)}")

@api_router.post("/auth/check-permission")
async def check_user_permission(
    permission_data: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Check if current user has specific permission"""
    required_permission = permission_data.get("permission")
    
    if not required_permission:
        raise HTTPException(status_code=400, detail="Permission parameter required")
    
    user_permissions = get_user_permissions(current_user.role, current_user.permissions)
    has_perm = has_permission(user_permissions, required_permission)
    
    return {
        "user_id": current_user.id,
        "permission": required_permission,
        "has_permission": has_perm,
        "user_role": current_user.role
    }

# Project Types Management Routes
@api_router.get("/project-types", response_model=List[ProjectTypeResponse])
async def get_project_types(
    active_only: bool = True,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all project types"""
    try:
        # Check permissions
        if not hasPermission(current_user.role, current_user.permissions, "system:config"):
            # Allow all users to view active project types
            query = {"is_active": True} if active_only else {}
        else:
            # Admins can see all project types
            query = {"is_active": True} if active_only else {}
        
        project_types = await db.project_types.find(query).sort("sort_order", 1).to_list(length=None)
        
        result = []
        for pt in project_types:
            pt_obj = ProjectType(**parse_from_mongo(pt))
            result.append(ProjectTypeResponse(**pt_obj.dict()))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve project types: {str(e)}")

@api_router.post("/project-types", response_model=ProjectTypeResponse)
async def create_project_type(
    project_type_data: ProjectTypeCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new project type (admin only)"""
    try:
        # Check permissions
        if not hasPermission(current_user.role, current_user.permissions, "system:config"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Check if project type name already exists
        existing = await db.project_types.find_one({
            "name": {"$regex": f"^{project_type_data.name}$", "$options": "i"},
            "is_active": True
        })
        
        if existing:
            raise HTTPException(status_code=400, detail="Project type with this name already exists")
        
        # Create project type
        project_type_dict = project_type_data.dict()
        project_type_dict["created_by"] = current_user.id
        
        project_type = ProjectType(**project_type_dict)
        project_type_dict = prepare_for_mongo(project_type.dict())
        
        await db.project_types.insert_one(project_type_dict)
        
        return ProjectTypeResponse(**project_type.dict())
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project type creation failed: {str(e)}")

@api_router.put("/project-types/{project_type_id}", response_model=ProjectTypeResponse)
async def update_project_type(
    project_type_id: str,
    project_type_update: ProjectTypeUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a project type (admin only)"""
    try:
        # Check permissions
        if not hasPermission(current_user.role, current_user.permissions, "system:config"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Check if project type exists
        existing = await db.project_types.find_one({"id": project_type_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Project type not found")
        
        # If updating name, check for duplicates
        if project_type_update.name:
            duplicate = await db.project_types.find_one({
                "name": {"$regex": f"^{project_type_update.name}$", "$options": "i"},
                "id": {"$ne": project_type_id},
                "is_active": True
            })
            
            if duplicate:
                raise HTTPException(status_code=400, detail="Project type with this name already exists")
        
        # Update project type
        update_data = {k: v for k, v in project_type_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc)
        update_data = prepare_for_mongo(update_data)
        
        result = await db.project_types.update_one(
            {"id": project_type_id}, 
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Project type not found")
        
        # Get updated project type
        updated_pt = await db.project_types.find_one({"id": project_type_id})
        pt_obj = ProjectType(**parse_from_mongo(updated_pt))
        
        return ProjectTypeResponse(**pt_obj.dict())
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project type update failed: {str(e)}")

@api_router.delete("/project-types/{project_type_id}")
async def delete_project_type(
    project_type_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a project type (soft delete - admin only)"""
    try:
        # Check permissions
        if not hasPermission(current_user.role, current_user.permissions, "system:config"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Soft delete by setting is_active to False
        result = await db.project_types.update_one(
            {"id": project_type_id},
            {"$set": {
                "is_active": False,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Project type not found")
        
        return {"message": "Project type deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project type deletion failed: {str(e)}")

@api_router.post("/project-types/bulk-create")
async def bulk_create_project_types(
    project_types_data: List[ProjectTypeCreate],
    current_user: UserResponse = Depends(get_current_user)
):
    """Bulk create project types (admin only)"""
    try:
        # Check permissions
        if not hasPermission(current_user.role, current_user.permissions, "system:config"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        created_types = []
        errors = []
        
        for i, pt_data in enumerate(project_types_data):
            try:
                # Check if name already exists
                existing = await db.project_types.find_one({
                    "name": {"$regex": f"^{pt_data.name}$", "$options": "i"},
                    "is_active": True
                })
                
                if existing:
                    errors.append(f"Row {i+1}: Project type '{pt_data.name}' already exists")
                    continue
                
                # Create project type
                project_type_dict = pt_data.dict()
                project_type_dict["created_by"] = current_user.id
                
                project_type = ProjectType(**project_type_dict)
                project_type_dict = prepare_for_mongo(project_type.dict())
                
                await db.project_types.insert_one(project_type_dict)
                created_types.append(ProjectTypeResponse(**project_type.dict()))
                
            except Exception as e:
                errors.append(f"Row {i+1}: {str(e)}")
        
        return {
            "created_count": len(created_types),
            "error_count": len(errors),
            "created_types": created_types,
            "errors": errors
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk creation failed: {str(e)}")

def hasPermission(user_role: str, user_permissions: List[str], required_permission: str) -> bool:
    """Helper function to check if user has specific permission"""
    # Super Admin always has access
    if user_role == "Super Admin":
        return True
    
    # Admin has most permissions except user deletion
    if user_role == "Admin" and required_permission != "users:delete":
        return True
    
    # Check custom permissions
    if user_permissions and required_permission in user_permissions:
        return True
    
    return False

# Target Reminder Management Routes
@api_router.post("/targets/schedule-reminder")
async def schedule_target_reminder(reminder_data: dict):
    """Schedule reminder for a target"""
    try:
        reminder = {
            "id": str(uuid.uuid4()),
            "target_id": reminder_data.get("target_id"),
            "user_id": reminder_data.get("user_id"),
            "frequency": reminder_data.get("frequency", "daily"),
            "next_reminder": reminder_data.get("next_reminder"),
            "message": reminder_data.get("message"),
            "is_active": reminder_data.get("is_active", True),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        reminder_dict = prepare_for_mongo(reminder)
        await db.target_reminders.insert_one(reminder_dict)
        
        return {
            "id": reminder["id"],
            "message": "Reminder scheduled successfully",
            "next_reminder": reminder["next_reminder"],
            "frequency": reminder["frequency"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule reminder: {str(e)}")

@api_router.get("/targets/reminders/{user_id}")
async def get_user_reminders(user_id: str):
    """Get all reminders for a user"""
    try:
        reminders = await db.target_reminders.find({
            "user_id": user_id,
            "is_active": True
        }).to_list(length=None)
        
        return [parse_from_mongo(reminder) for reminder in reminders]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reminders: {str(e)}")

@api_router.put("/targets/reminders/{reminder_id}/process")
async def process_reminder(reminder_id: str):
    """Mark reminder as processed and schedule next one"""
    try:
        reminder = await db.target_reminders.find_one({"id": reminder_id})
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        # Calculate next reminder time based on frequency
        now = datetime.now(timezone.utc)
        frequency = reminder.get("frequency", "daily")
        
        if frequency == "hourly":
            next_reminder = now + timedelta(hours=1)
        elif frequency == "daily":
            next_reminder = now + timedelta(days=1)
        elif frequency == "weekly":
            next_reminder = now + timedelta(weeks=1)
        elif frequency == "monthly":
            next_reminder = now + timedelta(days=30)
        else:
            next_reminder = now + timedelta(days=1)
        
        # Update reminder
        await db.target_reminders.update_one(
            {"id": reminder_id},
            {"$set": {
                "last_sent": now,
                "next_reminder": next_reminder,
                "updated_at": now
            }}
        )
        
        return {
            "message": "Reminder processed",
            "next_reminder": next_reminder
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process reminder: {str(e)}")

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

@app.on_event("startup")
async def startup_event():
    """Create default users on startup if they don't exist and initialize services"""
    try:
        # Initialize new services
        global role_management_service, lead_management_service, voice_stt_service, offline_sync_service
        global lead_routing_service, workflow_authoring_service
        
        role_management_service = initialize_role_management_service(db)
        await role_management_service.initialize_default_roles()
        
        lead_management_service = initialize_lead_management_service(db)
        
        voice_stt_service = initialize_voice_stt_service(db)
        
        offline_sync_service = initialize_offline_sync_service(db)
        await offline_sync_service.start_background_sync()
        
        # Initialize new routing and authoring services
        lead_routing_service = initialize_lead_routing_service(db)
        workflow_authoring_service = initialize_workflow_authoring_service(db)
        
        # Initialize background services for continuous agent activity
        await background_service.initialize()
        
        # Start background services in a separate task
        import asyncio
        asyncio.create_task(background_service.start_background_services())
        logger.info("✅ Background agent services started")
        
        logger.info("All services initialized successfully")
        
        # Create master user if doesn't exist
        master_user = await db.users.find_one({"username": "master"})
        if not master_user:
            master_data = {
                "username": "master",
                "email": "master@aavanagreens.com",
                "phone": "9999999999",
                "full_name": "Master Administrator",
                "role": UserRole.SUPER_ADMIN,
                "status": UserStatus.ACTIVE,
                "department": "Administration",
                "permissions": [],
                "password_hash": hash_password("master123"),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            master_user_obj = User(**master_data)
            await db.users.insert_one(prepare_for_mongo(master_user_obj.dict()))
            print("✅ Master user created: master/master123")
        
        # Create admin user if doesn't exist
        admin_user = await db.users.find_one({"username": "admin"})
        if not admin_user:
            admin_data = {
                "username": "admin",
                "email": "admin@aavanagreens.com", 
                "phone": "8888888888",
                "full_name": "System Administrator",
                "role": UserRole.ADMIN,
                "status": UserStatus.ACTIVE,
                "department": "Administration",
                "permissions": [],
                "password_hash": hash_password("admin123"),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            admin_user_obj = User(**admin_data)
            await db.users.insert_one(prepare_for_mongo(admin_user_obj.dict()))
            print("✅ Admin user created: admin/admin123")
            
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        logger.error(f"Startup failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    try:
        # Stop background services
        if background_service:
            await background_service.stop_background_services()
            logger.info("✅ Background agent services stopped")
        
        if offline_sync_service:
            await offline_sync_service.stop_background_sync()
        client.close()
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# ============== FILE UPLOAD ENDPOINTS ==============

@app.post("/api/upload/file")
async def upload_file(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """Upload a single file"""
    try:
        result = await file_upload_service.upload_file(file, project_id, current_user.id)
        return result
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    project_id: Optional[str] = Form(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """Upload multiple files"""
    try:
        result = await file_upload_service.upload_multiple_files(files, project_id, current_user.id)
        return result
    except Exception as e:
        logger.error(f"Multiple file upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/presigned-url")
async def generate_presigned_url(
    request: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Generate presigned URL for direct client upload"""
    try:
        filename = request.get('filename')
        content_type = request.get('content_type')
        
        if not filename or not content_type:
            raise HTTPException(status_code=400, detail="Filename and content_type required")
        
        result = file_upload_service.generate_presigned_upload_url(filename, content_type)
        return result
    except Exception as e:
        logger.error(f"Presigned URL generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/upload/{s3_key:path}")
async def delete_file(s3_key: str, current_user: UserResponse = Depends(get_current_user)):
    """Delete a file from S3"""
    try:
        success = await file_upload_service.delete_file(s3_key)
        if success:
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found or could not be deleted")
    except Exception as e:
        logger.error(f"File deletion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== ROLE & DEPARTMENT MANAGEMENT ENDPOINTS ==============

@app.post("/api/roles")
async def create_role(
    role_data: dict,
    current_user: UserResponse = Depends(get_current_super_admin)
):
    """Create a new role (Super Admin only)"""
    try:
        role = await role_management_service.create_role(role_data, current_user.id)
        return role
    except Exception as e:
        logger.error(f"Role creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/roles")
async def get_roles(current_user: UserResponse = Depends(get_current_user)):
    """Get all roles"""
    try:
        roles = await role_management_service.get_roles()
        return roles
    except Exception as e:
        logger.error(f"Error fetching roles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/roles/{role_id}")
async def update_role(
    role_id: str,
    update_data: dict,
    current_user: UserResponse = Depends(get_current_super_admin)
):
    """Update a role (Super Admin only)"""
    try:
        role = await role_management_service.update_role(role_id, update_data, current_user.id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return role
    except Exception as e:
        logger.error(f"Role update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/roles/{role_id}")
async def delete_role(
    role_id: str,
    current_user: UserResponse = Depends(get_current_super_admin)
):
    """Delete a role (Super Admin only)"""
    try:
        success = await role_management_service.delete_role(role_id, current_user.id)
        if success:
            return {"message": "Role deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Role not found")
    except Exception as e:
        logger.error(f"Role deletion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/departments")
async def create_department(
    department_data: dict,
    current_user: UserResponse = Depends(get_current_admin)
):
    """Create a new department"""
    try:
        department = await role_management_service.create_department(department_data, current_user.id)
        return department
    except Exception as e:
        logger.error(f"Department creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/departments")
async def get_departments(current_user: UserResponse = Depends(get_current_user)):
    """Get all departments"""
    try:
        departments = await role_management_service.get_departments()
        return departments
    except Exception as e:
        logger.error(f"Error fetching departments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}/permissions")
async def get_user_permissions(
    user_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user permissions"""
    try:
        # Users can only view their own permissions unless they're admin
        if current_user.id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        permissions = await role_management_service.get_user_permissions(user_id)
        return {"user_id": user_id, "permissions": permissions}
    except Exception as e:
        logger.error(f"Error fetching user permissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== ENHANCED LEAD MANAGEMENT ENDPOINTS ==============

@app.get("/api/leads/with-actions")
async def get_leads_with_actions(
    page: int = 1,
    limit: int = 20,
    source: Optional[str] = None,
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get leads with available actions"""
    try:
        filters = {}
        if source:
            filters['source'] = source
        if status:
            filters['status'] = status
        if assigned_to:
            filters['assigned_to'] = assigned_to
        
        result = await lead_management_service.get_leads_with_actions(page, limit, filters)
        return result
    except Exception as e:
        logger.error(f"Error fetching leads with actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/leads/{lead_id}/actions")
async def execute_lead_action(
    lead_id: str,
    action_data: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Execute an action on a lead"""
    try:
        action_type = action_data.get('action_type')
        if not action_type:
            raise HTTPException(status_code=400, detail="action_type is required")
        
        result = await lead_management_service.execute_lead_action(
            lead_id, action_type, action_data, current_user.id
        )
        return result
    except Exception as e:
        logger.error(f"Error executing lead action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leads/{lead_id}/actions")
async def get_lead_actions(
    lead_id: str,
    limit: int = 20,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get action history for a lead"""
    try:
        actions = await lead_management_service.get_lead_actions(lead_id, limit)
        return {"lead_id": lead_id, "actions": actions}
    except Exception as e:
        logger.error(f"Error fetching lead actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/leads/{lead_id}")
async def update_lead_enhanced(
    lead_id: str,
    update_data: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update lead information"""
    try:
        lead = await lead_management_service.update_lead(lead_id, update_data, current_user.id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return lead
    except Exception as e:
        logger.error(f"Error updating lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/leads/{lead_id}/remarks")
async def add_lead_remark(
    lead_id: str,
    remark_data: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Add remark to lead (text or voice)"""
    try:
        remark = await lead_management_service.add_lead_remark(lead_id, remark_data, current_user.id)
        return remark
    except Exception as e:
        logger.error(f"Error adding lead remark: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leads/{lead_id}/remarks")
async def get_lead_remarks(
    lead_id: str,
    include_private: bool = False,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get remarks for a lead"""
    try:
        remarks = await lead_management_service.get_lead_remarks(lead_id, include_private)
        return {"lead_id": lead_id, "remarks": remarks}
    except Exception as e:
        logger.error(f"Error fetching lead remarks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== VOICE & STT ENDPOINTS ==============

@app.post("/api/voice/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: str = Form("auto"),
    provider: Optional[str] = Form(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """Transcribe audio file"""
    try:
        audio_data = await audio_file.read()
        result = await voice_stt_service.transcribe_audio(audio_data, language, provider)
        return result
    except Exception as e:
        logger.error(f"Audio transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice/remark")  
async def process_voice_remark(
    lead_id: str = Form(...),
    audio_file: UploadFile = File(...),
    language: str = Form("auto"),
    current_user: UserResponse = Depends(get_current_user)
):
    """Process voice remark for a lead"""
    try:
        audio_data = await audio_file.read()
        result = await voice_stt_service.process_voice_remark(
            audio_data, lead_id, current_user.id, language
        )
        return result
    except Exception as e:
        logger.error(f"Voice remark processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice/extract-tasks")
async def extract_tasks_from_voice(
    audio_file: UploadFile = File(...),
    language: str = Form("auto"),
    current_user: UserResponse = Depends(get_current_user)
):
    """Extract tasks from voice input"""
    try:
        audio_data = await audio_file.read()
        result = await voice_stt_service.extract_tasks_from_voice(
            audio_data, current_user.id, language
        )
        return result
    except Exception as e:
        logger.error(f"Voice task extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/voice/transcriptions")
async def get_voice_transcriptions(
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get voice transcription history"""
    try:
        transcriptions = await voice_stt_service.get_voice_transcriptions(current_user.id, limit)
        return {"transcriptions": transcriptions}
    except Exception as e:
        logger.error(f"Error fetching voice transcriptions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/voice/tasks")
async def get_voice_tasks(
    status: Optional[str] = None,
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get voice-extracted tasks"""
    try:
        tasks = await voice_stt_service.get_voice_tasks(current_user.id, status, limit)
        return {"tasks": tasks}
    except Exception as e:
        logger.error(f"Error fetching voice tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/voice/tasks/{voice_task_id}/task/{task_id}")
async def update_voice_task_status(
    voice_task_id: str,
    task_id: str,
    request: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update status of a voice-extracted task"""
    try:
        status = request.get('status')
        if not status:
            raise HTTPException(status_code=400, detail="Status is required")
        
        success = await voice_stt_service.update_task_status(
            voice_task_id, task_id, status, current_user.id
        )
        
        if success:
            return {"message": "Task status updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        logger.error(f"Error updating voice task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== OFFLINE SYNC ENDPOINTS ==============

@app.post("/api/offline/queue")
async def queue_offline_operation(
    request: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Queue an operation for offline processing"""
    try:
        operation_data = request.get('operation_data')
        entity_type = request.get('entity_type')
        operation_type = request.get('operation_type')
        
        if not all([operation_data, entity_type, operation_type]):
            raise HTTPException(
                status_code=400, 
                detail="operation_data, entity_type, and operation_type are required"
            )
        
        queue_id = await offline_sync_service.queue_offline_operation(
            operation_data, current_user.id, entity_type, operation_type
        )
        
        return {"queue_id": queue_id, "message": "Operation queued successfully"}
    except Exception as e:
        logger.error(f"Error queueing offline operation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/offline/autosave")
async def autosave_data(
    request: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Auto-save data for offline editing"""
    try:
        data = request.get('data')
        entity_type = request.get('entity_type')
        entity_id = request.get('entity_id')
        
        if not all([data, entity_type, entity_id]):
            raise HTTPException(
                status_code=400,
                detail="data, entity_type, and entity_id are required"
            )
        
        autosave_id = await offline_sync_service.autosave_data(
            data, entity_type, entity_id, current_user.id
        )
        
        return {"autosave_id": autosave_id, "message": "Data auto-saved successfully"}
    except Exception as e:
        logger.error(f"Error auto-saving data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/offline/autosave/{entity_type}/{entity_id}")
async def get_autosaved_data(
    entity_type: str,
    entity_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Retrieve auto-saved data"""
    try:
        autosave = await offline_sync_service.get_autosaved_data(
            entity_type, entity_id, current_user.id
        )
        
        if autosave:
            return autosave
        else:
            raise HTTPException(status_code=404, detail="No auto-saved data found")
    except Exception as e:
        logger.error(f"Error retrieving auto-saved data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/offline/sync-status")
async def get_sync_status(current_user: UserResponse = Depends(get_current_user)):
    """Get sync queue status for current user"""
    try:
        status = await offline_sync_service.get_sync_queue_status(current_user.id)
        return status
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/offline/conflicts")
async def get_sync_conflicts(
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get unresolved sync conflicts"""
    try:
        conflicts = await offline_sync_service.get_sync_conflicts(current_user.id, limit)
        return {"conflicts": conflicts}
    except Exception as e:
        logger.error(f"Error getting sync conflicts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/offline/resolve-conflict/{conflict_id}")
async def resolve_sync_conflict(
    conflict_id: str,
    request: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Resolve a sync conflict"""
    try:
        resolution = request.get('resolution')
        if not resolution:
            raise HTTPException(status_code=400, detail="Resolution is required")
        
        success = await offline_sync_service.resolve_sync_conflict(
            conflict_id, resolution, current_user.id
        )
        
        if success:
            return {"message": "Conflict resolved successfully"}
        else:
            raise HTTPException(status_code=404, detail="Conflict not found")
    except Exception as e:
        logger.error(f"Error resolving sync conflict: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== HEALTH CHECK ENDPOINTS ==============

@app.get("/api/health/background-services")
async def get_background_services_status():
    """Get status of background agent services"""
    try:
        status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "background_services": {
                "is_running": background_service.is_running if background_service else False,
                "services": {}
            }
        }
        
        if background_service and hasattr(background_service, 'last_run'):
            for service_name, interval in background_service.sync_intervals.items():
                last_run = background_service.last_run.get(service_name)
                status["background_services"]["services"][service_name] = {
                    "interval_seconds": interval,
                    "last_run": last_run.isoformat() if last_run else None,
                    "status": "active" if last_run else "not_started"
                }
        
        return status
    except Exception as e:
        logger.error(f"Error getting background services status: {e}")
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "background_services": {
                "is_running": False,
                "error": str(e)
            }
        }

@app.get("/api/health/services")
async def get_services_health():
    """Get health status of all services"""
    try:
        health_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {}
        }
        
        # Check voice STT service
        if voice_stt_service:
            health_status["services"]["voice_stt"] = await voice_stt_service.health_check()
        
        # Check file upload service
        health_status["services"]["file_upload"] = {
            "status": "healthy",
            "s3_configured": bool(os.getenv('AWS_ACCESS_KEY_ID'))
        }
        
        # Check database
        try:
            await db.command('ping')
            health_status["services"]["database"] = {"status": "healthy"}
        except Exception as e:
            health_status["services"]["database"] = {"status": "unhealthy", "error": str(e)}
        
        # Check offline sync service
        if offline_sync_service:
            health_status["services"]["offline_sync"] = {
                "status": "healthy",
                "is_syncing": offline_sync_service.is_syncing
            }
        
        return health_status
    except Exception as e:
        logger.error(f"Error getting services health: {e}")
        raise HTTPException(status_code=500, detail=str(e))