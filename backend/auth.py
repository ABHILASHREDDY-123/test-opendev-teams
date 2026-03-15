from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from pydantic import BaseModel

# Secret key for JWT
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

class TokenData(BaseModel):
 username: str | None = None

class Token(BaseModel):
 access_token: str
 token_type: str

def create_access_token(data: dict, expires_delta: timedelta | None = None):
 to_encode = data.copy()
 if expires_delta:
 expire = datetime.utcnow() + expires_delta
 else:
 expire = datetime.utcnow() + timedelta(minutes=15)
 to_encode.update({"exp": expire})
 encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
 return encoded_jwt

def verify_password(plain_password: str, hashed_password: str):
 return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
 return pwd_context.hash(password)
