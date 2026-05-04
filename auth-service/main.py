import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from starlette.requests import Request
from pydantic import BaseModel, EmailStr, field_validator
import bcrypt
from jose import JWTError, jwt

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "ecommerce-platform-secret-key-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# In-memory user store
users_db: Dict[str, dict] = {}

# FastAPI app
app = FastAPI(title="Auth Service")

# Security
security = HTTPBearer()


# Pydantic models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name must be non-empty")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    created_at: str
    role: Optional[str] = "customer"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


# Helper functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_jwt_token(user_id: str, email: str, role: str = "customer") -> tuple[str, int]:
    """Create JWT token with expiration"""
    now = datetime.utcnow()
    expires = now + timedelta(hours=JWT_EXPIRATION_HOURS)
    expires_timestamp = int(expires.timestamp())
    
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": expires_timestamp,
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    expires_in = int((expires - now).total_seconds())
    
    return token, expires_in


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


def get_current_user(request: Request) -> dict:
    """Extract and verify user from JWT token"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing authorization header",
        )
    
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise ValueError()
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authorization header",
        )
    
    payload = decode_jwt_token(token)
    user_id = payload.get("sub")
    
    if not user_id or user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return users_db[user_id]


# Endpoints
@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest) -> UserResponse:
    """Register a new user"""
    # Check if email already exists
    for user in users_db.values():
        if user["email"].lower() == request.email.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
    
    # Create new user
    user_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    
    user = {
        "user_id": user_id,
        "email": request.email,
        "name": request.name,
        "password_hash": hash_password(request.password),
        "created_at": created_at,
        "role": "customer",
    }
    
    users_db[user_id] = user
    
    return UserResponse(
        user_id=user_id,
        email=request.email,
        name=request.name,
        created_at=created_at,
        role="customer",
    )


@app.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest) -> TokenResponse:
    """Login user and return JWT token"""
    # Find user by email
    user = None
    for u in users_db.values():
        if u["email"].lower() == request.email.lower():
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
    token, expires_in = create_jwt_token(
        user_id=user["user_id"],
        email=user["email"],
        role=user["role"],
    )
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
    )


@app.get("/auth/me", response_model=UserResponse)
def get_profile(user: dict = Depends(get_current_user)) -> UserResponse:
    """Get current user profile"""
    return UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        name=user["name"],
        created_at=user["created_at"],
        role=user["role"],
    )


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
