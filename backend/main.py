"""
Contacts API Backend - FastAPI Application
Implements user registration, login, and per-user contact management with JWT authentication.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime, timedelta
import bcrypt
from jose import JWTError, jwt
import re

# ============================================================================
# CONFIGURATION
# ============================================================================
SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

# ============================================================================
# DATA MODELS
# ============================================================================

class RegisterRequest(BaseModel):
    mobile: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=6)

    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        if not re.match(r'^\d{10,}$', v):
            raise ValueError('Mobile must contain at least 10 digits')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


class LoginRequest(BaseModel):
    mobile: str = Field(..., min_length=10)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=1, max_length=20)


class ContactUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=1, max_length=20)


class Contact(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    created_at: str


class User(BaseModel):
    user_id: str
    mobile: str
    password_hash: str


# ============================================================================
# IN-MEMORY DATA STORES
# ============================================================================

users_db: dict = {}  # {mobile: User}
contacts_db: dict = {}  # {user_id: {contact_id: Contact}}
contact_counter: dict = {}  # {user_id: counter}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user_id: str) -> str:
    """Create JWT access token."""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> str:
    """Verify JWT token and return user_id."""
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
            detail="Invalid or expired token"
        )


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(title="Contacts API", version="1.0.0")
security = HTTPBearer()


def get_current_user(credentials = Depends(security)) -> str:
    """Dependency to extract and verify JWT from Authorization header."""
    token = credentials.credentials
    return verify_token(token)


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.post("/auth/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest):
    """
    Register a new user with mobile and password.
    Mobile must be unique and contain at least 10 digits.
    """
    # Check if mobile already exists
    if request.mobile in users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mobile number already registered"
        )

    # Create new user
    user_id = f"user_{len(users_db) + 1}"
    password_hash = hash_password(request.password)

    user = User(
        user_id=user_id,
        mobile=request.mobile,
        password_hash=password_hash
    )

    users_db[request.mobile] = user
    contacts_db[user_id] = {}
    contact_counter[user_id] = 0

    return {
        "user_id": user_id,
        "mobile": request.mobile,
        "message": "User registered successfully"
    }


@app.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """
    Login with mobile and password.
    Returns JWT access token.
    """
    # Find user by mobile
    if request.mobile not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mobile or password"
        )

    user = users_db[request.mobile]

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mobile or password"
        )

    # Create token
    access_token = create_access_token(user.user_id)

    return TokenResponse(access_token=access_token)


@app.post("/contacts", response_model=Contact, status_code=status.HTTP_201_CREATED)
def create_contact(
    request: ContactCreate,
    current_user: str = Depends(get_current_user)
):
    """
    Create a new contact for the authenticated user.
    """
    contact_counter[current_user] += 1
    contact_id = f"contact_{contact_counter[current_user]}"

    contact = Contact(
        id=contact_id,
        name=request.name,
        email=request.email,
        phone=request.phone,
        created_at=datetime.utcnow().isoformat()
    )

    contacts_db[current_user][contact_id] = contact

    return contact


@app.get("/contacts", response_model=List[Contact])
def list_contacts(current_user: str = Depends(get_current_user)):
    """
    List all contacts for the authenticated user.
    Per-user isolation: only returns contacts belonging to current user.
    """
    user_contacts = contacts_db.get(current_user, {})
    return list(user_contacts.values())


@app.put("/contacts/{contact_id}", response_model=Contact)
def update_contact(
    contact_id: str,
    request: ContactUpdate,
    current_user: str = Depends(get_current_user)
):
    """
    Update a contact by ID.
    Per-user isolation: user can only update their own contacts.
    """
    user_contacts = contacts_db.get(current_user, {})

    if contact_id not in user_contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    contact = user_contacts[contact_id]

    # Update fields if provided
    if request.name is not None:
        contact.name = request.name
    if request.email is not None:
        contact.email = request.email
    if request.phone is not None:
        contact.phone = request.phone

    user_contacts[contact_id] = contact

    return contact


@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Delete a contact by ID.
    Per-user isolation: user can only delete their own contacts.
    """
    user_contacts = contacts_db.get(current_user, {})

    if contact_id not in user_contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    del user_contacts[contact_id]

    return None
