"""
Contacts Website REST API
FastAPI application with authentication and contacts management.
"""

from fastapi import FastAPI, HTTPException, Depends, status, Header
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
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
# In-Memory Storage
# ============================================================================

users_db: Dict[str, dict] = {}  # {user_id: {mobile, password_hash, created_at}}
contacts_db: Dict[str, dict] = {}  # {contact_id: {user_id, name, mobile, created_at}}
mobile_to_user: Dict[str, str] = {}  # {mobile: user_id} for quick lookup

# ============================================================================
# Pydantic Models
# ============================================================================


class RegisterRequest(BaseModel):
    """User registration request."""
    mobile: str = Field(..., min_length=10)
    password: str = Field(..., min_length=6)

    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        if not v.isdigit():
            raise ValueError('Mobile must contain only digits')
        if len(v) < 10:
            raise ValueError('Mobile must be at least 10 digits')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


class RegisterResponse(BaseModel):
    """User registration response."""
    id: str
    mobile: str


class LoginRequest(BaseModel):
    """User login request."""
    mobile: str = Field(..., min_length=10)
    password: str = Field(..., min_length=6)


class LoginResponse(BaseModel):
    """User login response."""
    token: str


class ContactCreateRequest(BaseModel):
    """Contact creation request."""
    name: str = Field(..., min_length=1)
    mobile: str = Field(..., min_length=10)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        return v

    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        if not v.isdigit():
            raise ValueError('Mobile must contain only digits')
        if len(v) < 10:
            raise ValueError('Mobile must be at least 10 digits')
        return v


class ContactUpdateRequest(BaseModel):
    """Contact update request."""
    name: Optional[str] = None
    mobile: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        return v

    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        if v is not None:
            if not v.isdigit():
                raise ValueError('Mobile must contain only digits')
            if len(v) < 10:
                raise ValueError('Mobile must be at least 10 digits')
        return v


class ContactResponse(BaseModel):
    """Contact response."""
    id: str
    name: str
    mobile: str
    user_id: str


class TokenData(BaseModel):
    """JWT token data."""
    user_id: str
    mobile: str


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(title="Contacts API", version="1.0.0")

# ============================================================================
# Helper Functions
# ============================================================================


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user_id: str, mobile: str) -> str:
    """Create JWT access token."""
    payload = {
        "user_id": user_id,
        "mobile": mobile,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str) -> TokenData:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        mobile: str = payload.get("mobile")
        if user_id is None or mobile is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return TokenData(user_id=user_id, mobile=mobile)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def get_current_user(authorization: Optional[str] = Header(None)) -> TokenData:
    """Dependency to get current authenticated user."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    token = parts[1]
    return verify_token(token)


# ============================================================================
# Endpoints
# ============================================================================


@app.post("/api/auth/register", response_model=RegisterResponse, status_code=201)
def register(request: RegisterRequest):
    """
    Register a new user.
    
    - mobile: 10+ digits, must be unique
    - password: 6+ characters, hashed with bcrypt
    """
    # Check if mobile already exists
    if request.mobile in mobile_to_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered"
        )
    
    # Create new user
    user_id = str(uuid.uuid4())
    password_hash = hash_password(request.password)
    
    users_db[user_id] = {
        "mobile": request.mobile,
        "password_hash": password_hash,
        "created_at": datetime.utcnow().isoformat()
    }
    mobile_to_user[request.mobile] = user_id
    
    return RegisterResponse(id=user_id, mobile=request.mobile)


@app.post("/api/auth/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """
    Login user and return JWT token.
    
    - mobile: registered mobile number
    - password: user password
    - Returns JWT token on success
    """
    # Find user by mobile
    user_id = mobile_to_user.get(request.mobile)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create and return token
    token = create_access_token(user_id, request.mobile)
    return LoginResponse(token=token)


@app.post("/api/contacts", response_model=ContactResponse, status_code=201)
def create_contact(
    request: ContactCreateRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Create a new contact for authenticated user.
    
    - Requires JWT authentication
    - name: contact name (required)
    - mobile: contact mobile (required, 10+ digits)
    """
    # Create contact
    contact_id = str(uuid.uuid4())
    contacts_db[contact_id] = {
        "user_id": current_user.user_id,
        "name": request.name,
        "mobile": request.mobile,
        "created_at": datetime.utcnow().isoformat()
    }
    
    return ContactResponse(
        id=contact_id,
        name=request.name,
        mobile=request.mobile,
        user_id=current_user.user_id
    )


@app.get("/api/contacts", response_model=List[ContactResponse])
def list_contacts(current_user: TokenData = Depends(get_current_user)):
    """
    List all contacts for authenticated user.
    
    - Requires JWT authentication
    - Returns only contacts belonging to the authenticated user
    """
    # Filter contacts by user_id
    user_contacts = [
        ContactResponse(
            id=contact_id,
            name=contact["name"],
            mobile=contact["mobile"],
            user_id=contact["user_id"]
        )
        for contact_id, contact in contacts_db.items()
        if contact["user_id"] == current_user.user_id
    ]
    
    return user_contacts


@app.put("/api/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: str,
    request: ContactUpdateRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Update a contact.
    
    - Requires JWT authentication
    - Contact must belong to authenticated user
    - name and mobile are optional
    """
    # Check if contact exists
    contact = contacts_db.get(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Check if contact belongs to user
    if contact["user_id"] != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Update fields
    if request.name is not None:
        contact["name"] = request.name
    if request.mobile is not None:
        contact["mobile"] = request.mobile
    
    return ContactResponse(
        id=contact_id,
        name=contact["name"],
        mobile=contact["mobile"],
        user_id=contact["user_id"]
    )


@app.delete("/api/contacts/{contact_id}", status_code=204)
def delete_contact(
    contact_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Delete a contact.
    
    - Requires JWT authentication
    - Contact must belong to authenticated user
    - Returns 204 on success
    """
    # Check if contact exists
    contact = contacts_db.get(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Check if contact belongs to user
    if contact["user_id"] != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
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
