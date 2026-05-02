"""
Contacts API Backend - FastAPI application with auth and CRUD endpoints.
Features:
- User registration with bcrypt password hashing
- JWT-based authentication
- Per-user contact management with isolation
- In-memory data store
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import uuid
import bcrypt
from jose import JWTError, jwt
import re

# ============================================================================
# Configuration
# ============================================================================
SECRET_KEY = "test-secret-key-do-not-use-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ============================================================================
# In-Memory Data Stores
# ============================================================================
users_db: Dict[str, dict] = {}  # {user_id: {mobile, password_hash}}
contacts_db: Dict[str, List[dict]] = {}  # {user_id: [{id, name, mobile, created_at}]}

# ============================================================================
# Pydantic Models
# ============================================================================
class RegisterRequest(BaseModel):
    mobile: str = Field(..., min_length=10)
    password: str = Field(..., min_length=6)

    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        """Validate mobile: 10+ digits only"""
        if not re.match(r'^\d{10,}$', v):
            raise ValueError('Mobile must be 10+ digits')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password: 6+ characters"""
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


class RegisterResponse(BaseModel):
    id: str
    mobile: str


class LoginRequest(BaseModel):
    mobile: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1)
    mobile: str = Field(..., min_length=10)

    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        """Validate mobile: 10+ digits only"""
        if not re.match(r'^\d{10,}$', v):
            raise ValueError('Mobile must be 10+ digits')
        return v


class ContactResponse(BaseModel):
    id: str
    name: str
    mobile: str
    created_at: str


class ContactUpdateRequest(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None

    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        """Validate mobile: 10+ digits only"""
        if v is not None and not re.match(r'^\d{10,}$', v):
            raise ValueError('Mobile must be 10+ digits')
        return v


# ============================================================================
# Utility Functions
# ============================================================================
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    payload = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> str:
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# ============================================================================
# FastAPI App
# ============================================================================
app = FastAPI(title="Contacts API")
security = HTTPBearer()


# ============================================================================
# Authentication Endpoints
# ============================================================================
@app.post("/register", response_model=RegisterResponse, status_code=201)
def register(req: RegisterRequest):
    """
    Register a new user.
    
    - mobile: 10+ digits
    - password: 6+ characters
    - Returns: user_id and mobile
    - Error 400: validation failed
    - Error 409: mobile already registered
    """
    # Check if mobile already exists
    for user in users_db.values():
        if user["mobile"] == req.mobile:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Mobile already registered"
            )
    
    # Create new user
    user_id = str(uuid.uuid4())
    users_db[user_id] = {
        "mobile": req.mobile,
        "password_hash": hash_password(req.password)
    }
    contacts_db[user_id] = []
    
    return RegisterResponse(id=user_id, mobile=req.mobile)


@app.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    """
    Login user and return JWT token.
    
    - mobile: registered mobile
    - password: correct password
    - Returns: JWT access token
    - Error 401: invalid credentials
    """
    # Find user by mobile
    user_id = None
    for uid, user in users_db.items():
        if user["mobile"] == req.mobile:
            user_id = uid
            break
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(req.password, users_db[user_id]["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate token
    token = create_access_token(user_id)
    return LoginResponse(access_token=token, token_type="bearer")


# ============================================================================
# Dependency: Get current user from token
# ============================================================================
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract and verify user_id from Bearer token"""
    token = credentials.credentials
    return verify_token(token)


# ============================================================================
# Contacts CRUD Endpoints
# ============================================================================
@app.post("/contacts", response_model=ContactResponse, status_code=201)
def create_contact(
    req: ContactRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Create a new contact for the logged-in user.
    
    - name: contact name
    - mobile: contact mobile (10+ digits)
    - Returns: contact with id and created_at
    - Error 400: validation failed
    - Error 401: no token or invalid token
    """
    contact_id = str(uuid.uuid4())
    contact = {
        "id": contact_id,
        "name": req.name,
        "mobile": req.mobile,
        "created_at": datetime.utcnow().isoformat()
    }
    contacts_db[user_id].append(contact)
    
    return ContactResponse(**contact)


@app.get("/contacts", response_model=List[ContactResponse])
def list_contacts(user_id: str = Depends(get_current_user)):
    """
    List all contacts for the logged-in user.
    
    - Returns: list of contacts (empty if none)
    - Error 401: no token or invalid token
    """
    return [ContactResponse(**c) for c in contacts_db[user_id]]


@app.put("/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: str,
    req: ContactUpdateRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Update a contact for the logged-in user.
    
    - contact_id: contact to update
    - name: new name (optional)
    - mobile: new mobile (optional)
    - Returns: updated contact
    - Error 401: no token or invalid token
    - Error 403: contact does not belong to user
    - Error 404: contact not found
    """
    # Find contact
    contact = None
    for c in contacts_db[user_id]:
        if c["id"] == contact_id:
            contact = c
            break
    
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Update fields
    if req.name is not None:
        contact["name"] = req.name
    if req.mobile is not None:
        contact["mobile"] = req.mobile
    
    return ContactResponse(**contact)


@app.delete("/contacts/{contact_id}", status_code=204)
def delete_contact(
    contact_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Delete a contact for the logged-in user.
    
    - contact_id: contact to delete
    - Returns: 204 No Content
    - Error 401: no token or invalid token
    - Error 403: contact does not belong to user
    - Error 404: contact not found
    """
    # Find and delete contact
    for i, c in enumerate(contacts_db[user_id]):
        if c["id"] == contact_id:
            contacts_db[user_id].pop(i)
            return
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Contact not found"
    )


# ============================================================================
# Health Check
# ============================================================================
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
