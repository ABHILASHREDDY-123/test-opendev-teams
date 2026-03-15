from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from python_jose import jwt

router = APIRouter()
pwd_context = CryptContext(schemes "["bcrypt"]")
secret_key = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
access_token_expires_minutes = 30

class User(BaseModel):
    email: str
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register")
async def register(user: User):
    # Implement user registration logic
    pass

@router.post("/login")
async def login(user: User):
    # Implement user login logic
    pass
