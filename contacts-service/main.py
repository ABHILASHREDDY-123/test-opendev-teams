import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from functools import wraps

from fastapi import FastAPI, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.requests import Request
from pydantic import BaseModel, field_validator
import bcrypt
from jose import JWTError, jwt

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "contacts-app-secret-key-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# In-memory data stores
users_db: Dict[str, dict] = {}
contacts_db: Dict[str, dict] = {}

# FastAPI app
app = FastAPI(title="Contacts Service")

# Security
security = HTTPBearer()


# ==================== Pydantic Models ====================

class RegisterRequest(BaseModel):
    mobile: str
    password: str

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if not v or len(v) < 10:
            raise ValueError("Mobile must be at least 10 digits")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    mobile: str
    password: str


class UserResponse(BaseModel):
    id: str
    mobile: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class ContactRequest(BaseModel):
    name: str
    mobile: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name must be non-empty")
        return v

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if not v or len(v) < 10:
            raise ValueError("Mobile must be at least 10 digits")
        return v


class ContactResponse(BaseModel):
    id: str
    name: str
    mobile: str


# ==================== Helper Functions ====================

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_jwt_token(user_id: str, mobile: str) -> str:
    """Create JWT token"""
    now = datetime.utcnow()
    expires = now + timedelta(hours=JWT_EXPIRATION_HOURS)
    expires_timestamp = int(expires.timestamp())
    
    payload = {
        "user_id": user_id,
        "mobile": mobile,
        "exp": expires_timestamp,
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_jwt_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_current_user_from_request(request: Request) -> dict:
    """Extract and verify user from JWT token in Authorization header"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise ValueError()
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )
    
    payload = decode_jwt_token(token)
    user_id = payload.get("user_id")
    
    if not user_id or user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return {"user_id": user_id, "mobile": payload.get("mobile")}


# ==================== Auth Endpoints ====================

@app.post("/api/v1/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest) -> UserResponse:
    """Register a new user"""
    # Check if mobile already exists
    for user in users_db.values():
        if user["mobile"] == request.mobile:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Mobile already registered",
            )
    
    # Create new user
    user_id = str(uuid.uuid4())
    
    user = {
        "user_id": user_id,
        "mobile": request.mobile,
        "password_hash": hash_password(request.password),
    }
    
    users_db[user_id] = user
    
    return UserResponse(
        id=user_id,
        mobile=request.mobile,
    )


@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(request: LoginRequest) -> TokenResponse:
    """Login user and return JWT token"""
    # Find user by mobile
    user = None
    for u in users_db.values():
        if u["mobile"] == request.mobile:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    # Verify password
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    # Create JWT token
    token = create_jwt_token(
        user_id=user["user_id"],
        mobile=user["mobile"],
    )
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )


# ==================== Contacts Endpoints ====================

@app.post("/api/v1/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(request: ContactRequest, req: Request) -> ContactResponse:
    """Add a new contact"""
    # Get current user
    current_user = get_current_user_from_request(req)
    user_id = current_user["user_id"]
    
    # Create contact
    contact_id = str(uuid.uuid4())
    contact = {
        "id": contact_id,
        "user_id": user_id,
        "name": request.name,
        "mobile": request.mobile,
    }
    
    contacts_db[contact_id] = contact
    
    return ContactResponse(
        id=contact_id,
        name=request.name,
        mobile=request.mobile,
    )


@app.get("/api/v1/contacts", response_model=List[ContactResponse])
def list_contacts(req: Request) -> List[ContactResponse]:
    """List all contacts for the current user"""
    # Get current user
    current_user = get_current_user_from_request(req)
    user_id = current_user["user_id"]
    
    # Get user's contacts
    user_contacts = [
        ContactResponse(
            id=contact["id"],
            name=contact["name"],
            mobile=contact["mobile"],
        )
        for contact in contacts_db.values()
        if contact["user_id"] == user_id
    ]
    
    return user_contacts


@app.put("/api/v1/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: str, request: ContactRequest, req: Request) -> ContactResponse:
    """Update a contact"""
    # Get current user
    current_user = get_current_user_from_request(req)
    user_id = current_user["user_id"]
    
    # Check if contact exists
    if contact_id not in contacts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    
    contact = contacts_db[contact_id]
    
    # Check if user owns the contact
    if contact["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this contact",
        )
    
    # Update contact
    contact["name"] = request.name
    contact["mobile"] = request.mobile
    
    return ContactResponse(
        id=contact["id"],
        name=contact["name"],
        mobile=contact["mobile"],
    )


@app.delete("/api/v1/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: str, req: Request):
    """Delete a contact"""
    # Get current user
    current_user = get_current_user_from_request(req)
    user_id = current_user["user_id"]
    
    # Check if contact exists
    if contact_id not in contacts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    
    contact = contacts_db[contact_id]
    
    # Check if user owns the contact
    if contact["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this contact",
        )
    
    # Delete contact
    del contacts_db[contact_id]
    
    return None


# ==================== Health Check ====================

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
