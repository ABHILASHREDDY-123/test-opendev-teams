from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

app = FastAPI()

class User(BaseModel):
    email: str
    hashed_password: str

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
    users[user.email] = user
    return {'message': 'User created successfully'}

@app.post('/auth/login')
def login(email: str, password: str):
    if email not in users:
        raise HTTPException(status_code=401, detail='Invalid email or password')
    user = users[email]
    if not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode({'sub': email, 'exp': datetime.utcnow() + access_token_expires}, SECRET_KEY, algorithm=ALGORITHM)
    return {'access_token': access_token, 'token_type': 'bearer'}
