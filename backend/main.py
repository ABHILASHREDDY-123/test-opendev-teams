"""
FastAPI REST API for Contacts Website
Includes user authentication and per-user contact management
"""

from fastapi import FastAPI, HTTPException, Header, status
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, timedelta
import bcrypt
import jwt
from uuid import uuid4

# ============================================================================
# Configuration
# ============================================================================
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ============================================================================
# In-Memory Data Stores
# ============================================================================
users_db = {}  # {user_id: {id, mobile, password_hash}}
contacts_db = {}  # {contact_id: {id, name, mobile, user_id}}

# ============================================================================
# Pydantic Models
# ============================================================================
class RegisterRequest(BaseModel):
    mobile: str
    password: str
    
    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        if not v or not v.isdigit() or len(v) < 10:
            raise ValueError('Mobile must be 10+ digits')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError('Password must be 6+ characters')
        return v

class LoginRequest(BaseModel):
    mobile: str
    password: str
    
    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        if not v or not v.isdigit() or len(v) < 10:
            raise ValueError('Mobile must be 10+ digits')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError('Password must be 6+ characters')
        return v

class LoginResponse(BaseModel):
    access_token: str

class ContactCreate(BaseModel):
    name: str
    mobile: str
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        return v
    
    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        if not v or not v.isdigit() or len(v) < 10:
            raise ValueError('Mobile must be 10+ digits')
        return v

class ContactResponse(BaseModel):
    id: str
    name: str
    mobile: str
    user_id: str

class UserResponse(BaseModel):
    id: str
    mobile: str

# ============================================================================
# Utility Functions
# ============================================================================
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode(), password_hash.encode())

def create_access_token(user_id: str) -> str:
    """Create JWT access token"""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> str:
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """Extract and verify user from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = parts[1]
    return verify_token(token)

# ============================================================================
# FastAPI App
# ============================================================================
app = FastAPI(title="Contacts API")

# ============================================================================
# Authentication Endpoints
# ============================================================================
@app.post("/api/auth/register", response_model=UserResponse, status_code=201)
def register(request: RegisterRequest):
    """Register a new user"""
    # Check for duplicate mobile
    for user in users_db.values():
        if user["mobile"] == request.mobile:
            raise HTTPException(status_code=409, detail="Mobile already registered")
    
    # Create new user
    user_id = str(uuid4())
    password_hash = hash_password(request.password)
    
    users_db[user_id] = {
        "id": user_id,
        "mobile": request.mobile,
        "password_hash": password_hash
    }
    
    return UserResponse(id=user_id, mobile=request.mobile)

@app.post("/api/auth/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """Login user and return JWT token"""
    # Find user by mobile
    user = None
    for u in users_db.values():
        if u["mobile"] == request.mobile:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create and return token
    access_token = create_access_token(user["id"])
    return LoginResponse(access_token=access_token)

# ============================================================================
# Contacts Endpoints
# ============================================================================
@app.post("/api/contacts", response_model=ContactResponse, status_code=201)
def create_contact(
    request: ContactCreate,
    authorization: Optional[str] = Header(None)
):
    """Create a new contact for authenticated user"""
    # Authenticate user
    user_id = get_current_user(authorization)
    
    # Create contact
    contact_id = str(uuid4())
    contacts_db[contact_id] = {
        "id": contact_id,
        "name": request.name,
        "mobile": request.mobile,
        "user_id": user_id
    }
    
    return ContactResponse(**contacts_db[contact_id])

@app.get("/api/contacts", response_model=List[ContactResponse])
def list_contacts(authorization: Optional[str] = Header(None)):
    """List all contacts for authenticated user"""
    # Authenticate user
    user_id = get_current_user(authorization)
    
    # Return user's contacts
    user_contacts = [
        ContactResponse(**contact)
        for contact in contacts_db.values()
        if contact["user_id"] == user_id
    ]
    
    return user_contacts

@app.put("/api/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: str,
    request: ContactCreate,
    authorization: Optional[str] = Header(None)
):
    """Update a contact"""
    # Authenticate user
    user_id = get_current_user(authorization)
    
    # Check if contact exists
    if contact_id not in contacts_db:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    contact = contacts_db[contact_id]
    
    # Check ownership
    if contact["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Update contact
    contact["name"] = request.name
    contact["mobile"] = request.mobile
    
    return ContactResponse(**contact)

@app.delete("/api/contacts/{contact_id}", status_code=204)
def delete_contact(
    contact_id: str,
    authorization: Optional[str] = Header(None)
):
    """Delete a contact"""
    # Authenticate user
    user_id = get_current_user(authorization)
    
    # Check if contact exists
    if contact_id not in contacts_db:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    contact = contacts_db[contact_id]
    
    # Check ownership
    if contact["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Delete contact
    del contacts_db[contact_id]
    
    return None
