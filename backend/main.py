from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from jwt import encode, decode
from passlib.context import CryptContext
import pytest

app = FastAPI()
pwd_context = CryptContext(schemes=['bcrypt'], default='bcrypt')

class User(BaseModel):
    username: str
    password: str

class Contact(BaseModel):
    name: str
    phone: str

# in-memory data store for demonstration purposes
users = {}
contacts = {}

@app.post('/register')
def register(user: User):
    if user.username in users:
        raise HTTPException(status_code=400, detail='Username already exists')
    users[user.username] = pwd_context.hash(user.password)
    return {'message': 'User created successfully'}

@app.post('/login')
def login(user: User):
    if user.username not in users:
        raise HTTPException(status_code=401, detail='Invalid username or password')
    if not pwd_context.verify(user.password, users[user.username]):
        raise HTTPException(status_code=401, detail='Invalid username or password')
    token = encode({'username': user.username}, 'secret_key', algorithm='HS256')
    return {'token': token}

@app.post('/contacts')
def create_contact(contact: Contact, token: str):
    try:
        payload = decode(token, 'secret_key', algorithms=['HS256'])
    except:
        raise HTTPException(status_code=401, detail='Invalid token')
    contacts[contact.name] = contact.phone
    return {'message': 'Contact created successfully'}

@app.get('/contacts')
def get_contacts(token: str):
    try:
        payload = decode(token, 'secret_key', algorithms=['HS256'])
    except:
        raise HTTPException(status_code=401, detail='Invalid token')
    return {'contacts': contacts}

@app.put('/contacts/{name}')
def update_contact(name: str, contact: Contact, token: str):
    try:
        payload = decode(token, 'secret_key', algorithms=['HS256'])
    except:
        raise HTTPException(status_code=401, detail='Invalid token')
    if name not in contacts:
        raise HTTPException(status_code=404, detail='Contact not found')
    contacts[name] = contact.phone
    return {'message': 'Contact updated successfully'}

@app.delete('/contacts/{name}')
def delete_contact(name: str, token: str):
    try:
        payload = decode(token, 'secret_key', algorithms=['HS256'])
    except:
        raise HTTPException(status_code=401, detail='Invalid token')
    if name not in contacts:
        raise HTTPException(status_code=404, detail='Contact not found')
    del contacts[name]
    return {'message': 'Contact deleted successfully'}
