"""
Auth Service for E-Commerce Platform
Handles user registration, login, and profile retrieval with JWT authentication.
Supports both customer and admin roles.
"""

import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from jose import JWTError, jwt

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "ecommerce-platform-secret-key-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "admin-creation-secret-2026")

# Password hashing - use argon2 for better compatibility
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Security
security = HTTPBearer()

# In-memory user store
users_db: dict[str, dict] = {}

# FastAPI app
app = FastAPI(title="Auth Service", version="1.0.0")


# ============================================================================
# Pydantic Models
# ============================================================================

class RegisterRequest(BaseModel):
    """User registration request"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    name: str = Field(..., min_length=1, description="User name")


class AdminRegisterRequest(BaseModel):
    """Admin user registration request"""
    email: str = Field(..., description="Admin email address")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    name: str = Field(..., min_length=1, description="Admin name")
    admin_secret: str = Field(..., description="Admin creation secret")


class LoginRequest(BaseModel):
    """User login request"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserProfile(BaseModel):
    """User profile response"""
    id: str
    email: str
    name: str
    role: str = "customer"


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


# ============================================================================
# Utility Functions
# ============================================================================

def validate_email(email: str) -> bool:
    """
    Validate email format using RFC 5322 simplified pattern.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def hash_password(password: str) -> str:
    """Hash password using argon2"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def generate_jwt_token(user_id: str, email: str, role: str = "customer") -> str:
    """Generate JWT token with 24h expiry and user role"""
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(hours=JWT_EXPIRY_HOURS)
    
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": expiry,
        "iat": now
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_jwt_token(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        ) from e


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency to extract and validate JWT from Authorization header"""
    token = credentials.credentials
    payload = decode_jwt_token(token)
    user_id = payload.get("sub")
    
    if not user_id or user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return users_db[user_id]


def get_admin_user(user: dict = Depends(get_current_user)) -> dict:
    """Dependency to ensure current user is an admin"""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


# ============================================================================
# Endpoints
# ============================================================================

@app.post("/auth/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest) -> UserProfile:
    """
    Register a new customer user.
    
    - email: Valid email address
    - password: At least 8 characters
    - name: Non-empty name
    
    Returns user profile with generated ID and customer role.
    """
    # Validate email format
    if not validate_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Validate password length
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    # Validate name is non-empty
    if not request.name or not request.name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty"
        )
    
    # Check for duplicate email
    for user in users_db.values():
        if user["email"] == request.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
    
    # Create user with customer role
    user_id = str(uuid.uuid4())
    user_data = {
        "id": user_id,
        "email": request.email,
        "name": request.name,
        "password_hash": hash_password(request.password),
        "role": "customer"
    }
    
    users_db[user_id] = user_data
    
    return UserProfile(
        id=user_id,
        email=request.email,
        name=request.name,
        role="customer"
    )


@app.post("/auth/admin/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
def register_admin(request: AdminRegisterRequest) -> UserProfile:
    """
    Register a new admin user.
    
    Requires admin_secret for security. This endpoint is used for platform setup
    and testing admin functionality.
    
    - email: Valid email address
    - password: At least 8 characters
    - name: Non-empty name
    - admin_secret: Secret key for admin creation
    
    Returns user profile with generated ID and admin role.
    """
    # Verify admin secret
    if request.admin_secret != ADMIN_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin secret"
        )
    
    # Validate email format
    if not validate_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Validate password length
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    # Validate name is non-empty
    if not request.name or not request.name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty"
        )
    
    # Check for duplicate email
    for user in users_db.values():
        if user["email"] == request.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
    
    # Create admin user
    user_id = str(uuid.uuid4())
    user_data = {
        "id": user_id,
        "email": request.email,
        "name": request.name,
        "password_hash": hash_password(request.password),
        "role": "admin"
    }
    
    users_db[user_id] = user_data
    
    return UserProfile(
        id=user_id,
        email=request.email,
        name=request.name,
        role="admin"
    )


@app.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest) -> TokenResponse:
    """
    Login with email and password.
    
    Returns JWT access token with 24h expiry. Token includes user role (customer or admin).
    """
    # Find user by email
    user = None
    for u in users_db.values():
        if u["email"] == request.email:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate JWT token with user's actual role
    token = generate_jwt_token(user["id"], user["email"], user["role"])
    
    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )


@app.get("/auth/me", response_model=UserProfile)
def get_current_user_profile(user: dict = Depends(get_current_user)) -> UserProfile:
    """
    Get current user profile from JWT token.
    
    Requires valid JWT in Authorization header (Bearer token).
    Returns user profile including role (customer or admin).
    """
    return UserProfile(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        role=user["role"]
    )


@app.get("/auth/admin/verify", response_model=UserProfile)
def verify_admin(admin: dict = Depends(get_admin_user)) -> UserProfile:
    """
    Verify that current user is an admin.
    
    Requires valid JWT with admin role in Authorization header.
    Returns admin user profile.
    """
    return UserProfile(
        id=admin["id"],
        email=admin["email"],
        name=admin["name"],
        role=admin["role"]
    )


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
