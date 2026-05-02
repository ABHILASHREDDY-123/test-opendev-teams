"""
Contacts API Backend - FastAPI Implementation
Implements user authentication (JWT) and contacts CRUD with per-user isolation.
"""

from fastapi import FastAPI, HTTPException, status, Header
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
import hashlib

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Password hashing - use SHA256 instead of bcrypt to avoid 72-byte limit
def hash_password(password: str) -> str:
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


# In-memory stores
users_db: Dict[str, dict] = {}  # mobile -> {id, mobile, hashed_password}
contacts_db: Dict[str, dict] = {}  # contact_id -> {id, name, mobile, user_id}
user_id_to_mobile: Dict[str, str] = {}  # user_id -> mobile (for reverse lookup)

# Pydantic models
class RegisterRequest(BaseModel):
    mobile: str = Field(..., min_length=10)
    password: str = Field(..., min_length=6)

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v):
        if not v.isdigit():
            raise ValueError("Mobile must contain only digits")
        if len(v) < 10:
            raise ValueError("Mobile must be at least 10 digits")
        return v


class RegisterResponse(BaseModel):
    id: str
    mobile: str


class LoginRequest(BaseModel):
    mobile: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1)
    mobile: str = Field(..., min_length=10)

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v):
        if not v.isdigit():
            raise ValueError("Mobile must contain only digits")
        if len(v) < 10:
            raise ValueError("Mobile must be at least 10 digits")
        return v


class ContactResponse(BaseModel):
    id: str
    name: str
    mobile: str
    user_id: str


class TokenData(BaseModel):
    user_id: str


# FastAPI app
app = FastAPI(title="Contacts API", version="1.0.0")


# Utility functions
def create_access_token(user_id: str) -> str:
    """Create a JWT access token."""
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode = {"user_id": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> str:
    """Verify a JWT token and return the user_id."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """Extract and verify the current user from the Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = parts[1]
    return verify_token(token)


# Authentication endpoints
@app.post("/api/auth/register", response_model=RegisterResponse, status_code=201)
def register(request: RegisterRequest):
    """Register a new user."""
    # Check if mobile already exists
    if request.mobile in users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mobile number already registered",
        )
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(request.password)
    
    users_db[request.mobile] = {
        "id": user_id,
        "mobile": request.mobile,
        "hashed_password": hashed_password,
    }
    user_id_to_mobile[user_id] = request.mobile
    
    return RegisterResponse(id=user_id, mobile=request.mobile)


@app.post("/api/auth/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """Login and get JWT token."""
    # Find user by mobile
    user = users_db.get(request.mobile)
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    # Create token
    access_token = create_access_token(user["id"])
    return LoginResponse(access_token=access_token)


# Contacts endpoints
@app.post("/api/contacts", response_model=ContactResponse, status_code=201)
def create_contact(
    request: ContactRequest,
    authorization: Optional[str] = Header(None),
):
    """Create a new contact for the authenticated user."""
    user_id = get_current_user(authorization)
    
    # Create contact
    contact_id = str(uuid.uuid4())
    contacts_db[contact_id] = {
        "id": contact_id,
        "name": request.name,
        "mobile": request.mobile,
        "user_id": user_id,
    }
    
    return ContactResponse(**contacts_db[contact_id])


@app.get("/api/contacts", response_model=List[ContactResponse])
def list_contacts(authorization: Optional[str] = Header(None)):
    """Get all contacts for the authenticated user."""
    user_id = get_current_user(authorization)
    
    # Filter contacts by user_id
    user_contacts = [
        ContactResponse(**contact)
        for contact in contacts_db.values()
        if contact["user_id"] == user_id
    ]
    
    return user_contacts


@app.put("/api/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: str,
    request: ContactRequest,
    authorization: Optional[str] = Header(None),
):
    """Update a contact (only owner can update)."""
    user_id = get_current_user(authorization)
    
    # Check if contact exists
    if contact_id not in contacts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    
    contact = contacts_db[contact_id]
    
    # Check ownership
    if contact["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this contact",
        )
    
    # Update contact
    contact["name"] = request.name
    contact["mobile"] = request.mobile
    
    return ContactResponse(**contact)


@app.delete("/api/contacts/{contact_id}", status_code=204)
def delete_contact(
    contact_id: str,
    authorization: Optional[str] = Header(None),
):
    """Delete a contact (only owner can delete)."""
    user_id = get_current_user(authorization)
    
    # Check if contact exists
    if contact_id not in contacts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    
    contact = contacts_db[contact_id]
    
    # Check ownership
    if contact["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this contact",
        )
    
    # Delete contact
    del contacts_db[contact_id]
    
    return None


# Health check
@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}
