from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import jwt
import bcrypt
from datetime import datetime, timedelta
from backend.models import User, Contact, Token, TokenData, UserRegister, UserLogin, ContactCreate, ContactUpdate, ContactOut, UserOut, TokenResponse

security = HTTPBearer()

def hash_password(password: str) -> str:
 return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
 return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict) -> str:
 to_encode = data.copy()
 if '_iat' in to_encode:
 to_encode['_iat'] = int(to_encode['_iat'])
 to_encode.update({'exp': datetime.utcnow() + timedelta(minutes=30)})
 encoded_jwt = jwt.encode(to_encode, 'secret_key', algorithm='HS256')
 return encoded_jwt

def get_current_user(token: str) -> User:
 credentials_exception = HTTPException(
 status_code=401,
 detail="Could not validate credentials",
 headers={"WWW-Authenticate": "Bearer"},
 )
 try:
 payload = jwt.decode(token, 'secret_key', algorithms=['HS256'])
 mobile: str = payload.get('sub')
 if mobile is None:
 raise credentials_exception
 token_data = TokenData(mobile=mobile)
 except jwt.PyJWTError:
 raise credentials_exception
 user = users_db.get(token_data.mobile)
 if user is None:
 raise credentials_exception
 return user