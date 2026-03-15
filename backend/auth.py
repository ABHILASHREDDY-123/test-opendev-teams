from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from python_jose import jwt

app = FastAPI()

class User(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

pwd_context = CryptContext(schemes=['bcrypt'], default='bcrypt')

users = {}

token_secret = 'secret'

token_algorithm = 'HS256'

token_expiration = 3600

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
    token = jwt.encode({'email': user.email}, token_secret, algorithm=token_algorithm, expiration_time=token_expiration)
    return {'access_token': token, 'token_type': 'bearer'}