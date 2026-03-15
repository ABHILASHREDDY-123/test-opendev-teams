from fastapi import FastAPI
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

app = FastAPI()

class User(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

pwd_context = CryptContext(schemes=['bcrypt'], default='bcrypt')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(fake_db, email: str, password: str):
    user = fake_db.get(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
    	return False
    return True

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, 'secretkey', algorithm='HS256')
    return encoded_jwt

fake_db = {}

@app.post('/auth/register')
def register(user: User):
    hashed_password = get_password_hash(user.password)
    fake_db[user.email] = {'hashed_password': hashed_password}
    return {'message': 'User created successfully'}

@app.post('/auth/login')
def login(user: User):
    user_data = authenticate_user(fake_db, user.email, user.password)
    if not user_data:
        return {'message': 'Invalid email or password'}
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={'sub': user.email}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}
