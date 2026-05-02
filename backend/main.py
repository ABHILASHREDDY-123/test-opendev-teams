"""
Contacts Website API - FastAPI Backend
Implements user registration, login, and contacts CRUD with JWT authentication.
"""

from fastapi import FastAPI, HTTPException, Depends, status, Header
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import uuid
import bcrypt
from jose import JWTError, jwt

# ============================================================================
# Configuration
# ============================================================================
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ============================================================================
# Pydantic Models
# ============================================================================

class RegisterRequest(BaseModel):
    mobile: str = Field(..., description="Mobile number (10+ digits)")
    password: str = Field(..., min_length=6, description="Password (6+ characters)")
    
    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        if not v.isdigit() or len(v) < 10:
            raise ValueError("Mobile must be 10+ digits")
        return v


class LoginRequest(BaseModel):
    mobile: str = Field(..., description="Mobile number")
    password: str = Field(..., min_length=6, description="Password")
    
    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        if not v.isdigit() or len(v) < 10:
            raise ValueError("Mobile must be 10+ digits")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    id: str
    mobile: str


class RegisterResponse(BaseModel):
    user: UserProfile
    access_token: str
    token_type: str = "bearer"


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Contact name")
    mobile: str = Field(..., description="Contact mobile (10+ digits)")
    
    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        if not v.isdigit() or len(v) < 10:
            raise ValueError("Mobile must be 10+ digits")
        return v


class Contact(BaseModel):
    id: str
    user_id: str
    name: str
    mobile: str
    created_at: str


# ============================================================================
# In-Memory Data Stores
# ============================================================================

users_db: Dict[str, Dict] = {}  # {user_id: {mobile, password_hash}}
mobile_to_user: Dict[str, str] = {}  # {mobile: user_id} for quick lookup
contacts_db: Dict[str, Dict] = {}  # {contact_id: {user_id, name, mobile, created_at}}


# ============================================================================
# Utility Functions
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against bcrypt hash."""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> str:
    """Verify JWT token and return user_id."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """Extract and verify user from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )
    
    token = parts[1]
    return verify_token(token)


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(title="Contacts API", version="1.0.0")


# ============================================================================
# Auth Endpoints
# ============================================================================

@app.post("/api/auth/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest):
    """
    Register a new user with mobile and password.
    
    - Mobile must be 10+ digits and unique
    - Password must be 6+ characters
    - Returns user profile and JWT token
    """
    # Check if mobile already exists
    if request.mobile in mobile_to_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile already registered",
        )
    
    # Create new user
    user_id = str(uuid.uuid4())
    password_hash = hash_password(request.password)
    
    users_db[user_id] = {
        "mobile": request.mobile,
        "password_hash": password_hash,
    }
    mobile_to_user[request.mobile] = user_id
    
    # Generate token
    access_token = create_access_token(user_id)
    
    return RegisterResponse(
        user=UserProfile(id=user_id, mobile=request.mobile),
        access_token=access_token,
        token_type="bearer",
    )


@app.post("/api/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """
    Login with mobile and password.
    
    - Returns JWT access token on success
    - 401 if credentials invalid
    """
    # Find user by mobile
    user_id = mobile_to_user.get(request.mobile)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    # Verify password
    user = users_db[user_id]
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    # Generate token
    access_token = create_access_token(user_id)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


# ============================================================================
# Contacts Endpoints
# ============================================================================

@app.post("/api/contacts", response_model=Contact, status_code=status.HTTP_201_CREATED)
def create_contact(request: ContactRequest, user_id: str = Depends(get_current_user)):
    """
    Create a new contact for the logged-in user.
    
    - Requires JWT token in Authorization header
    - Mobile must be 10+ digits
    - Returns created contact object
    """
    # Create contact
    contact_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    
    contacts_db[contact_id] = {
        "user_id": user_id,
        "name": request.name,
        "mobile": request.mobile,
        "created_at": created_at,
    }
    
    return Contact(
        id=contact_id,
        user_id=user_id,
        name=request.name,
        mobile=request.mobile,
        created_at=created_at,
    )


@app.get("/api/contacts", response_model=List[Contact])
def list_contacts(user_id: str = Depends(get_current_user)):
    """
    Get all contacts for the logged-in user.
    
    - Requires JWT token in Authorization header
    - Returns only user's own contacts
    """
    user_contacts = [
        Contact(
            id=contact_id,
            user_id=contact["user_id"],
            name=contact["name"],
            mobile=contact["mobile"],
            created_at=contact["created_at"],
        )
        for contact_id, contact in contacts_db.items()
        if contact["user_id"] == user_id
    ]
    
    return user_contacts


@app.put("/api/contacts/{contact_id}", response_model=Contact)
def update_contact(contact_id: str, request: ContactRequest, user_id: str = Depends(get_current_user)):
    """
    Update a contact.
    
    - Requires JWT token in Authorization header
    - User can only update their own contacts
    - Mobile must be 10+ digits
    - Returns updated contact
    """
    # Check if contact exists
    if contact_id not in contacts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    
    contact = contacts_db[contact_id]
    
    # Enforce ownership
    if contact["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own contacts",
        )
    
    # Update contact
    contact["name"] = request.name
    contact["mobile"] = request.mobile
    
    return Contact(
        id=contact_id,
        user_id=contact["user_id"],
        name=contact["name"],
        mobile=contact["mobile"],
        created_at=contact["created_at"],
    )


@app.delete("/api/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: str, user_id: str = Depends(get_current_user)):
    """
    Delete a contact.
    
    - Requires JWT token in Authorization header
    - User can only delete their own contacts
    - Returns 204 No Content on success
    """
    # Check if contact exists
    if contact_id not in contacts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    
    contact = contacts_db[contact_id]
    
    # Enforce ownership
    if contact["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own contacts",
        )
    
    # Delete contact
    del contacts_db[contact_id]
    
    return None


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
