from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

app = FastAPI()

# OAuth2 schema
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

# JWT secret key
SECRET_KEY = "secretkey"
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
def register(user: User):
    if user.email in users:
        raise HTTPException(status_code=400, detail="Email already registered")
    users[user.email] = pwd_context.hash(user.hashed_password)
    return {"message": "User created successfully"}

# Login user
@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username not in users:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not pwd_context.verify(form_data.password, users[form_data.username]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode({
        "sub": form_data.username,
        "exp": datetime.utcnow() + access_token_expires
    }, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}