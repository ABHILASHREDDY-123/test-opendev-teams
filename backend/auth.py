from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from python_jose import jwt
import datetime

app = FastAPI()

# Define the user model
class User(BaseModel):
    email: str
    password: str

# Define the token model
class Token(BaseModel):
    access_token: str
    token_type: str

# Initialize the password context
pwd_context = CryptContext(schemes=['bcrypt'], default='bcrypt')

# Initialize the in-memory user store
users = {}

# Define the authentication router
@app.post('/auth/register')
def register(user: User):
    # Hash the password
    hashed_password = pwd_context.hash(user.password)
    # Check if the user already exists
    if user.email in users:
        raise HTTPException(status_code=400, detail='Email already exists')
    # Create a new user
    users[user.email] = hashed_password
    return {'message': 'User created successfully'}

# Define the login endpoint
@app.post('/auth/login')
def login(user: User):
    # Check if the user exists
    if user.email not in users:
        raise HTTPException(status_code=401, detail='Invalid email or password')
    # Verify the password
    if not pwd_context.verify(user.password, users[user.email]):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    # Generate a JWT token
    payload = {'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}
    token = jwt.encode(payload, 'secret_key', algorithm='HS256')
    return {'access_token': token, 'token_type': 'bearer'}
