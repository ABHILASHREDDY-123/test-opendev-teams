from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
import jwt
import bcrypt
import os
import pytest

app = FastAPI()

# In-memory stores for demonstration purposes only
users_db = {}
contacts_db = {}

class User(BaseModel):
    id: int
    mobile: str
    password: str

class Contact(BaseModel):
    id: int
    name: str
    mobile: str
    owner_id: int

class Token(BaseModel):
    access_token: str
    token_type: str

token_auth = HTTPBearer()

# Authentication utilities
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def create_access_token(data: dict) -> str:
    return jwt.encode(data, os.environ['SECRET_KEY'], algorithm='HS256').decode()

def get_current_user(token: str) -> dict:
    try:
        payload = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Access token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid access token')

# Routes
@app.post('/auth/register', response_model=User)
async def register(user: User):
    if user.mobile in [u['mobile'] for u in users_db.values()]:
        raise HTTPException(status_code=409, detail='Mobile number already registered')
    hashed_password = hash_password(user.password)
    user_id = len(users_db) + 1
    users_db[user_id] = {'id': user_id, 'mobile': user.mobile, 'password': hashed_password}
    return users_db[user_id]

@app.post('/auth/login', response_model=Token)
async def login(mobile: str, password: str):
    for user in users_db.values():
        if user['mobile'] == mobile and verify_password(password, user['password']):
            access_token = create_access_token({'sub': user['id']})
            return {'access_token': access_token, 'token_type': 'bearer'}
    raise HTTPException(status_code=401, detail='Invalid mobile or password')

@app.post('/contacts/', response_model=Contact)
async def create_contact(contact: Contact, token: HTTPAuthorizationCredentials = Depends(token_auth)):
    current_user = get_current_user(token.credentials)
    contact_id = len(contacts_db) + 1
    contacts_db[contact_id] = {'id': contact_id, 'name': contact.name, 'mobile': contact.mobile, 'owner_id': current_user['sub']}
    return contacts_db[contact_id]

@app.get('/contacts/', response_model=List[Contact])
async def read_contacts(token: HTTPAuthorizationCredentials = Depends(token_auth)):
    current_user = get_current_user(token.credentials)
    return [contact for contact in contacts_db.values() if contact['owner_id'] == current_user['sub']]

@app.put('/contacts/{contact_id}', response_model=Contact)
async def update_contact(contact_id: int, contact: Contact, token: HTTPAuthorizationCredentials = Depends(token_auth)):
    current_user = get_current_user(token.credentials)
    if contact_id not in contacts_db:
        raise HTTPException(status_code=404, detail='Contact not found')
    if contacts_db[contact_id]['owner_id'] != current_user['sub']:
        raise HTTPException(status_code=403, detail='You do not own this contact')
    contacts_db[contact_id]['name'] = contact.name
    contacts_db[contact_id]['mobile'] = contact.mobile
    return contacts_db[contact_id]

@app.delete('/contacts/{contact_id}')
async def delete_contact(contact_id: int, token: HTTPAuthorizationCredentials = Depends(token_auth)):
    current_user = get_current_user(token.credentials)
    if contact_id not in contacts_db:
        raise HTTPException(status_code=404, detail='Contact not found')
    if contacts_db[contact_id]['owner_id'] != current_user['sub']:
        raise HTTPException(status_code=403, detail='You do not own this contact')
    del contacts_db[contact_id]
    return {'message': 'Contact deleted'}
