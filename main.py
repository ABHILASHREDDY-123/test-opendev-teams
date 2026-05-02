"""
FastAPI REST API for Contacts Website
Includes user registration, login with JWT, and contacts CRUD with per-user isolation.
"""

from fastapi import FastAPI, HTTPException, Header, status
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime, timedelta
import bcrypt
from jose import JWTError, jwt
import uuid

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
    mobile: str = Field(..., min_length=10, max_length=15)
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


class LoginRequest(BaseModel):
    mobile: str
    password: str


class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    mobile: str = Field(..., min_length=10, max_length=15)

    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        if not v.isdigit():
            raise ValueError('Mobile must contain only digits')
        if len(v) < 10:
            raise ValueError('Mobile must be at least 10 digits')
        return v


class ContactUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    mobile: Optional[str] = Field(None, min_length=10, max_length=15)

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
    id: str
    name: str
    mobile: str
    user_id: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class MessageResponse(BaseModel):
    message: str


# ============================================================================
# In-Memory Data Store
# ============================================================================
users_db = {}  # {mobile: {password_hash, user_id}}
contacts_db = {}  # {user_id: [{id, name, mobile, user_id}]}


# ============================================================================
# Utility Functions
# ============================================================================
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against bcrypt hash"""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
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


def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """Extract and verify user from Authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    token = parts[1]
    return verify_token(token)


# ============================================================================
# FastAPI App
# ============================================================================
app = FastAPI(title="Contacts API")


# ============================================================================
# Endpoints
# ============================================================================

@app.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest):
    """
    Register a new user
    - mobile: 10+ digits, must be unique
    - password: 6+ characters, will be bcrypt hashed
    """
    # Check if mobile already exists
    if request.mobile in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile already registered"
        )
    
    # Create user
    user_id = str(uuid.uuid4())
    password_hash = hash_password(request.password)
    users_db[request.mobile] = {
        "password_hash": password_hash,
        "user_id": user_id
    }
    contacts_db[user_id] = []
    
    return {"message": "User registered successfully"}


@app.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """
    Login user and return JWT token
    - mobile: registered mobile number
    - password: user password
    """
    # Check if user exists
    if request.mobile not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user_data = users_db[request.mobile]
    
    # Verify password
    if not verify_password(request.password, user_data["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create and return token
    access_token = create_access_token(user_data["user_id"])
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/contacts", response_model=List[ContactResponse])
def get_contacts(authorization: Optional[str] = Header(None)):
    """
    Get all contacts for the logged-in user
    - Requires: Bearer token in Authorization header
    - Returns: List of contacts for this user only
    """
    user_id = get_current_user(authorization)
    
    if user_id not in contacts_db:
        return []
    
    return contacts_db[user_id]


@app.post("/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact: ContactCreate, authorization: Optional[str] = Header(None)):
    """
    Create a new contact for the logged-in user
    - Requires: Bearer token in Authorization header
    - Input: name, mobile
    """
    user_id = get_current_user(authorization)
    
    # Create contact
    contact_id = str(uuid.uuid4())
    new_contact = {
        "id": contact_id,
        "name": contact.name,
        "mobile": contact.mobile,
        "user_id": user_id
    }
    
    if user_id not in contacts_db:
        contacts_db[user_id] = []
    
    contacts_db[user_id].append(new_contact)
    
    return new_contact


@app.put("/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: str, contact: ContactUpdate, authorization: Optional[str] = Header(None)):
    """
    Update a contact for the logged-in user
    - Requires: Bearer token in Authorization header
    - Validation: Contact must belong to logged-in user
    """
    user_id = get_current_user(authorization)
    
    if user_id not in contacts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Find contact
    contact_obj = None
    for c in contacts_db[user_id]:
        if c["id"] == contact_id:
            contact_obj = c
            break
    
    if not contact_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Update fields
    if contact.name is not None:
        contact_obj["name"] = contact.name
    if contact.mobile is not None:
        contact_obj["mobile"] = contact.mobile
    
    return contact_obj


@app.delete("/contacts/{contact_id}", response_model=MessageResponse)
def delete_contact(contact_id: str, authorization: Optional[str] = Header(None)):
    """
    Delete a contact for the logged-in user
    - Requires: Bearer token in Authorization header
    - Validation: Contact must belong to logged-in user
    """
    user_id = get_current_user(authorization)
    
    if user_id not in contacts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Find and delete contact
    for i, c in enumerate(contacts_db[user_id]):
        if c["id"] == contact_id:
            contacts_db[user_id].pop(i)
            return {"message": "Contact deleted successfully"}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Contact not found"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
