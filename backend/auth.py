from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import jwt
import bcrypt
import os

class Token(BaseModel):
 access_token: str
 token_type: str

token_auth = HTTPBearer()

def hash_password(password: str) -> str:
 return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
 return bcrypt.checkpw(plain.encode(), hashed.encode())

def create_access_token(data: dict) -> str:
 return jwt.encode(data, os.environ['SECRET_KEY'], algorithm='HS256').decode()

def get_current_user(token: str) -> dict:
 try:
 payload = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=['HS256'])
 return payload
 except jwt.ExpiredSignatureError:
 raise HTTPException(status_code=401, detail='Access token expired')
 except jwt.InvalidTokenError:
 raise HTTPException(status_code=401, detail='Invalid access token')
