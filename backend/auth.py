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
    hashed_password: str

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
def register_user(email: str, password: str):
    # Hash the password
    hashed_password = pwd_context.hash(password)
    # Create a new user
    user = User(email=email, hashed_password=hashed_password)
    # Add the user to the in-memory store
    users[email] = user
    # Return a success message
    return {'message': 'User created successfully'}

# Define the login endpoint
@app.post('/auth/login')
def login_user(email: str, password: str):
    # Check if the user exists
    user = users.get(email)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid email or password')
    # Verify the password
    if not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    # Generate a JWT token
    payload = {'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30), 'iat': datetime.datetime.utcnow(), 'sub': email}
    access_token = jwt.encode(payload, 'secret_key', algorithm='HS256')
    # Return the token
    return {'access_token': access_token, 'token_type': 'bearer'}
