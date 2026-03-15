from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from python_jose import jwt

app = FastAPI()

class User(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

pwd_context = CryptContext(schemes "bcrypt", default="bcrypt")

# In-memory user store for simplicity (replace with a database in production)
users = {}

@app.post("/auth/register")
async def register(user: User):
    if user.email in users:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    users[user.email] = hashed_password
    return {"message": "User created successfully"}

@app.post("/auth/login")
async def login(user: User):
    if user.email not in users:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not pwd_context.verify(user.password, users[user.email]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = jwt.encode({"sub": user.email}, "secret_key", algorithm="HS256")
    return {"access_token": access_token, "token_type": "bearer"}