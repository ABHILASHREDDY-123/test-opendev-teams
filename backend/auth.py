from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

app = FastAPI()

class User(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

pwd_context = CryptContext(schemes=['bcrypt'], default='bcrypt')

SECRET_KEY = 'secret_key'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

users = {}

@app.post('/auth/register')
def register(user: User):
    if user.email in users:
        raise HTTPException(status_code=400, detail='Email already registered')
    hashed_password = pwd_context.hash(user.password)
    users[user.email] = hashed_password
    return {'message': 'User created successfully'}

@app.post('/auth/login')
def login(user: User):
    if user.email not in users:
        raise HTTPException(status_code=401, detail='Invalid email or password')
    if not pwd_context.verify(user.password, users[user.email]):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode({'sub': user.email, 'exp': datetime.utcnow() + access_token_expires}, SECRET_KEY, algorithm=ALGORITHM)
    return {'access_token': access_token, 'token_type': 'bearer'}
