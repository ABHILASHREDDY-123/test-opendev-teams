"""
Contacts API Backend - FastAPI Application
Personal contacts management with user authentication and CRUD operations.
"""

from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import jwt
import bcrypt
import re

# ============================================================================
# Configuration
# ============================================================================

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ============================================================================
# In-Memory Data Store
# ============================================================================

# Users store: {mobile: {password_hash, user_id}}
users_db: Dict[str, dict] = {}

# Contacts store: {user_id: [{id, name, phone, email, created_at}]}
contacts_db: Dict[int, List[dict]] = {}

# Counter for user IDs and contact IDs
user_id_counter = 0
contact_id_counter = 0

# ============================================================================
# Pydantic Models
# ============================================================================


class UserRegisterRequest(BaseModel):
    mobile: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=6)

    @validator("mobile")
    def validate_mobile(cls, v):
        if not re.match(r"^\d{10,}$", v):
            raise ValueError("Mobile must contain 10+ digits only")
        return v

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLoginRequest(BaseModel):
    mobile: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=6)


class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int


class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    email: str = Field(..., min_length=5, max_length=100)

    @validator("phone")
    def validate_phone(cls, v):
        if not re.match(r"^\d{10,}$", v):
            raise ValueError("Phone must contain 10+ digits only")
        return v

    @validator("email")
    def validate_email(cls, v):
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid email format")
        return v


class ContactUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[str] = Field(None, min_length=5, max_length=100)

    @validator("phone")
    def validate_phone(cls, v):
        if v is not None and not re.match(r"^\d{10,}$", v):
            raise ValueError("Phone must contain 10+ digits only")
        return v

    @validator("email")
    def validate_email(cls, v):
        if v is not None and not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid email format")
        return v


class ContactResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    created_at: str


class UserRegisterResponse(BaseModel):
    user_id: int
    mobile: str
    message: str = "User registered successfully"


# ============================================================================
# FastAPI App Setup
# ============================================================================

app = FastAPI(
    title="Contacts API",
    description="Personal contacts management with user authentication",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Utility Functions
# ============================================================================


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def create_access_token(user_id: int) -> str:
    """Create JWT access token."""
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> int:
    """Verify JWT token and return user_id."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def get_current_user(authorization: str = Header(None)) -> int:
    """Dependency to get current user from JWT token."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    token = parts[1]
    return verify_token(token)


# ============================================================================
# Endpoints: User Registration
# ============================================================================


@app.post("/api/v1/register", status_code=201, response_model=UserRegisterResponse)
def register_user(request: UserRegisterRequest):
    """
    Register a new user with mobile number and password.

    - **mobile**: 10+ digits required
    - **password**: 6+ characters required
    - Returns 201 on success
    - Returns 400 on validation error
    - Returns 409 if mobile already registered
    """
    global user_id_counter

    # Check if mobile already exists
    if request.mobile in users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mobile number already registered",
        )

    # Create new user
    user_id_counter += 1
    user_id = user_id_counter
    hashed_password = hash_password(request.password)

    users_db[request.mobile] = {
        "user_id": user_id,
        "password_hash": hashed_password,
    }

    # Initialize contacts list for user
    contacts_db[user_id] = []

    return UserRegisterResponse(
        user_id=user_id,
        mobile=request.mobile,
    )


# ============================================================================
# Endpoints: User Login
# ============================================================================


@app.post("/api/v1/login", response_model=UserLoginResponse)
def login_user(request: UserLoginRequest):
    """
    Login user with mobile number and password.

    - Returns 200 with JWT token on success
    - Returns 401 on invalid credentials
    - Returns 400 on missing/invalid input
    """
    # Check if mobile exists
    if request.mobile not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    user_data = users_db[request.mobile]

    # Verify password
    if not verify_password(request.password, user_data["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Generate JWT token
    user_id = user_data["user_id"]
    token = create_access_token(user_id)

    return UserLoginResponse(
        access_token=token,
        user_id=user_id,
    )


# ============================================================================
# Endpoints: Contacts CRUD
# ============================================================================


@app.post("/api/v1/contacts", status_code=201, response_model=ContactResponse)
def add_contact(
    request: ContactCreate,
    user_id: int = Depends(get_current_user),
):
    """
    Add a new contact for the authenticated user.

    - Requires valid JWT token in Authorization header
    - Returns 201 on success
    - Returns 400 on validation error
    - Returns 401 on missing/invalid token
    """
    global contact_id_counter

    # Create new contact
    contact_id_counter += 1
    contact = {
        "id": contact_id_counter,
        "name": request.name,
        "phone": request.phone,
        "email": request.email,
        "created_at": datetime.utcnow().isoformat(),
    }

    contacts_db[user_id].append(contact)

    return ContactResponse(**contact)


@app.get("/api/v1/contacts", response_model=List[ContactResponse])
def list_contacts(user_id: int = Depends(get_current_user)):
    """
    List all contacts for the authenticated user.

    - Requires valid JWT token in Authorization header
    - Returns 200 with list of contacts
    - Returns 401 on missing/invalid token
    - User-isolated: only returns current user's contacts
    """
    contacts = contacts_db.get(user_id, [])
    return [ContactResponse(**contact) for contact in contacts]


@app.put("/api/v1/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    request: ContactUpdate,
    user_id: int = Depends(get_current_user),
):
    """
    Update an existing contact for the authenticated user.

    - Requires valid JWT token in Authorization header
    - Returns 200 on success
    - Returns 400 on validation error
    - Returns 401 on missing/invalid token
    - Returns 403 if user tries to access another user's contact
    - Returns 404 if contact not found
    """
    # Find contact
    contacts = contacts_db.get(user_id, [])
    contact = None
    for c in contacts:
        if c["id"] == contact_id:
            contact = c
            break

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    # Update contact fields
    if request.name is not None:
        contact["name"] = request.name
    if request.phone is not None:
        contact["phone"] = request.phone
    if request.email is not None:
        contact["email"] = request.email

    return ContactResponse(**contact)


@app.delete("/api/v1/contacts/{contact_id}", status_code=204)
def delete_contact(
    contact_id: int,
    user_id: int = Depends(get_current_user),
):
    """
    Delete a contact for the authenticated user.

    - Requires valid JWT token in Authorization header
    - Returns 204 on success
    - Returns 401 on missing/invalid token
    - Returns 403 if user tries to access another user's contact
    - Returns 404 if contact not found
    """
    # Find and delete contact
    contacts = contacts_db.get(user_id, [])
    for i, c in enumerate(contacts):
        if c["id"] == contact_id:
            contacts.pop(i)
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Contact not found",
    )


# ============================================================================
# Health Check
# ============================================================================


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
