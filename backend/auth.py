from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

app = FastAPI()

class User(BaseModel):
    email: str
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

pwd_context = CryptContext(schemes=['bcrypt'], default='bcrypt')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(email: str, password: str):
    # In-memory user store for simplicity
    users = {
        'user@example.com': get_password_hash('password123')
    }
    if email in users:
        if verify_password(password, users[email]):
            return True
    return False

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, 'secret_key', algorithm='HS256')
    return encoded_jwt

@app.post('/auth/register')
async def register(user: User):
    # In-memory user store for simplicity
    users = {
        'user@example.com': get_password_hash('password123')
    }
    if user.email in users:
        raise HTTPException(status_code=400, detail='Email already registered')
    # Add user to in-memory store
    users[user.email] = get_password_hash(user.hashed_password)
    return {'message': 'User created successfully'}

@app.post('/auth/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail='Incorrect username or password')
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={'sub': form_data.username}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}
