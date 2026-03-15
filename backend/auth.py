from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError

app = FastAPI()

# OAuth2 schema
class Token(BaseModel):
    access_token: str
    token_type: str

# User schema
class User(BaseModel):
    email: str
    hashed_password: str

# Password context
pwd_context = CryptContext(schemes=['bcrypt'], default='bcrypt')

# OAuth2 password bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

# In-memory user store (replace with a database in production)
users = {}

# Register a new user
@app.post('/auth/register')
async def register(email: str, password: str):
    if email in users:
        raise HTTPException(status_code=400, detail='Email already registered')
    hashed_password = pwd_context.hash(password)
    users[email] = hashed_password
    return {'message': 'User created successfully'}

# Login and get a JWT token
@app.post('/auth/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username not in users:
        raise HTTPException(status_code=400, detail='Invalid email or password')
    if not pwd_context.verify(form_data.password, users[form_data.username]):
        raise HTTPException(status_code=400, detail='Invalid email or password')
    access_token_expires = timedelta(minutes=30)
    access_token = jwt.encode({'sub': form_data.username, 'exp': datetime.utcnow() + access_token_expires}, 'secret_key', algorithm='HS256')
    return {'access_token': access_token, 'token_type': 'bearer'}
