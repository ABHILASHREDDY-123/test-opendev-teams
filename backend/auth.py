from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from python_jose import jwt

app = FastAPI()

class User(BaseModel):
    email: str
    password: str

pwd_context = CryptContext(schemes=['bcrypt'], default='bcrypt')

@app.post('/auth/register')
def register(user: User):
    hashed_password = pwd_context.hash(user.password)
    # store user in in-memory store
    return {'message': 'User created successfully'}

@app.post('/auth/login')
def login(user: User):
    # retrieve user from in-memory store
    # verify password
    access_token = jwt.encode({'sub': user.email}, 'secret_key', algorithm='HS256')
    return {'access_token': access_token, 'token_type': 'bearer'}