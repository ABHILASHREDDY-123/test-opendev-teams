from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from python_jose import jwt
import datetime

app = FastAPI()

# In-memory user store for simplicity
users = {}

class User(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Password hashing and verification
pwd_context = CryptContext(schemes=['bcrypt'], default='bcrypt')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# JWT token generation and verification
secret_key = 'secret_key'
algorithm = 'HS256'
access_token_expires_minutes = 30

def create_access_token(data: dict, expires_delta: datetime.timedelta):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')

# Authentication endpoints
@app.post('/auth/register')
async def register(user: User):
    if user.email in users:
        raise HTTPException(status_code=400, detail='Email already registered')
    users[user.email] = get_password_hash(user.password)
    return {'message': 'User created successfully'}

@app.post('/auth/login')
async def login(user: User):
    if user.email not in users:
        raise HTTPException(status_code=401, detail='Invalid email or password')
    if not verify_password(user.password, users[user.email]):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    access_token_expires = datetime.timedelta(minutes=access_token_expires_minutes)
    access_token = create_access_token(data={'sub': user.email}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}
