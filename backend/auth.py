from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

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
secret_key = 'your_secret_key'

# Define the in-memory user store
users = {}

# Register a new user
@app.post('/auth/register')
def register(user: User):
    # Hash the password
    hashed_password = pwd_context.hash(user.password)
    # Check if the user already exists
    if user.email in users:
        raise HTTPException(status_code=400, detail='Email already in use')
    # Create a new user
    users[user.email] = hashed_password
    return {'message': 'User created successfully'}

# Login a user
@app.post('/auth/login')
def login(user: User):
    # Check if the user exists
    if user.email not in users:
        raise HTTPException(status_code=401, detail='Invalid email or password')
    # Verify the password
    if not pwd_context.verify(user.password, users[user.email]):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    # Generate a JWT token
    access_token = jwt.encode({'sub': user.email, 'exp': datetime.utcnow() + timedelta(minutes=30)}, secret_key, algorithm='HS256')
    return {'access_token': access_token, 'token_type': 'bearer'}
