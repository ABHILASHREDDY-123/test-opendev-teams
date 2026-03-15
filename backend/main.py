from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from jwt import encode, decode
from passlib.context import CryptContext

app = FastAPI()
pwd_context = CryptContext(schemes=['bcrypt'], default='bcrypt')

class User(BaseModel):
    username: str
    password: str

class Contact(BaseModel):
    name: str
    phone: str

@app.post('/register')
def register(user: User):
    hashed_password = pwd_context.hash(user.password)
    # store user in database
    return {'message': 'User registered successfully'}

@app.post('/login')
def login(user: User):
    # retrieve user from database
    # compare hashed password
    token = encode({'username': user.username}, 'secret_key', algorithm='HS256')
    return {'token': token}

@app.post('/contacts')
def create_contact(contact: Contact, token: str):
    try:
        payload = decode(token, 'secret_key', algorithms=['HS256'])
        # store contact in database
        return {'message': 'Contact created successfully'}
    except Exception as e:
        raise HTTPException(status_code=401, detail='Invalid token')

@app.get('/contacts')
def get_contacts(token: str):
    try:
        payload = decode(token, 'secret_key', algorithms=['HS256'])
        # retrieve contacts from database
        return [{'name': 'John Doe', 'phone': '1234567890'}]
    except Exception as e:
        raise HTTPException(status_code=401, detail='Invalid token')
