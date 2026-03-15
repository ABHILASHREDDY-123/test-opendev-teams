from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError

app = FastAPI()

# OAuth2 schema
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

# JWT secret key
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# User model
class User(BaseModel):
    email: str
    hashed_password: str

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

# In-memory user store
users = {}

# Register user
@app.post("/auth/register")
def register(email: str, password: str):
    # Hash password
    hashed_password = pwd_context.hash(password)
    # Create user
    user = User(email=email, hashed_password=hashed_password)
    # Add user to in-memory store
    users[email] = user
    return {
        "message": "User created successfully"
    }

# Login user
@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Find user
    user = users.get(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    # Verify password
    if not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    # Generate JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {
            "sub": user.email,
            "exp": datetime.utcnow() + access_token_expires
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
