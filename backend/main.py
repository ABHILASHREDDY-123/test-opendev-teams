from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List
from uuid import uuid4
from backend.models import UserRegister, UserLogin, UserOut, TokenResponse, ContactCreate, ContactUpdate, ContactOut
from backend.auth import hash_password, verify_password, create_access_token, get_current_user

app = FastAPI()

users_db = {}
contacts_db = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

@app.post('/auth/register', response_model=UserOut, status_code=201)
async def register(user: UserRegister):
    if user.mobile in users_db:
        raise HTTPException(status_code=409, detail='Mobile number already registered')
    user_id = str(uuid4())
    hashed_password = hash_password(user.password)
    users_db[user.mobile] = {'id': user_id, 'mobile': user.mobile, 'hashed_password': hashed_password}
    return {'id': user_id, 'mobile': user.mobile}

@app.post('/auth/login', response_model=TokenResponse)
async def login(user: UserLogin):
    stored_user = users_db.get(user.mobile)
    if not stored_user or not verify_password(user.password, stored_user['hashed_password']):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    access_token = create_access_token({'sub': stored_user['id']})
    return {'access_token': access_token, 'token_type': 'bearer'}

async def get_current_active_user(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid token')
    stored_user = next((u for u in users_db.values() if u['id'] == user['sub']), None)
    if not stored_user:
        raise HTTPException(status_code=401, detail='User not found')
    return stored_user

@app.post('/contacts', response_model=ContactOut, status_code=201)
async def create_contact(contact: ContactCreate, current_user = Depends(get_current_active_user)):
    contact_id = str(uuid4())
    new_contact = {'id': contact_id, 'name': contact.name, 'mobile': contact.mobile, 'owner_id': current_user['id']}
    contacts_db[contact_id] = new_contact
    return new_contact

@app.get('/contacts', response_model=List[ContactOut])
async def list_contacts(current_user = Depends(get_current_active_user)):
    return [c for c in contacts_db.values() if c['owner_id'] == current_user['id']]

@app.put('/contacts/{contact_id}', response_model=ContactOut)
async def update_contact(contact_id: str, contact: ContactUpdate, current_user = Depends(get_current_active_user)):
    stored_contact = contacts_db.get(contact_id)
    if not stored_contact or stored_contact['owner_id'] != current_user['id']:
        raise HTTPException(status_code=404, detail='Contact not found')
    if contact.name is not None:
        stored_contact['name'] = contact.name
    if contact.mobile is not None:
        stored_contact['mobile'] = contact.mobile
    return stored_contact

@app.delete('/contacts/{contact_id}')
async def delete_contact(contact_id: str, current_user = Depends(get_current_active_user)):
    stored_contact = contacts_db.get(contact_id)
    if not stored_contact or stored_contact['owner_id'] != current_user['id']:
        raise HTTPException(status_code=404, detail='Contact not found')
    del contacts_db[contact_id]
    return {'message': 'Contact deleted successfully'}
