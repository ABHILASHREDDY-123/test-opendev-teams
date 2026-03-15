from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

app = FastAPI()

# Define the Pydantic models
class User(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Define the password context
pwd_context = CryptContext(schemes=['bcrypt'], default='bcrypt')

# Define the secret key for JWT
SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In-memory user store (replace with a database in production)
users = {}

# Register a new user
@app.post('/auth/register')
def register(user: User):
    # Check if the user already exists
    if user.email in users:
        raise HTTPException(status_code=400, detail='Email already registered')
    # Hash the password
    hashed_password = pwd_context.hash(user.password)
    # Store the user in the in-memory store
    users[user.email] = hashed_password
    return {'message': 'User created successfully'}

# Login and get a JWT token
@app.post('/auth/login')
def login(user: User):
    # Check if the user exists
    if user.email not in users:
        raise HTTPException(status_code=401, detail='Invalid email or password')
    # Verify the password
    if not pwd_context.verify(user.password, users[user.email]):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    # Generate a JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode({'sub': user.email, 'exp': datetime.utcnow() + access_token_expires}, SECRET_KEY, algorithm=ALGORITHM)
    return {'access_token': access_token, 'token_type': 'bearer'}
