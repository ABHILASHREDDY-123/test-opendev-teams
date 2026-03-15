from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
from . import models, auth

class Contact(BaseModel):
    name: str
    mobile: str
    owner_id: str
    id: str

class ContactOut(BaseModel):
    name: str
    mobile: str
    owner_id: str
    id: str

class User(BaseModel):
    mobile: str
    password: str
    id: str

class UserOut(BaseModel):
    mobile: str
    id: str

class Token(BaseModel):
    access_token: str
    token_type: str

app = FastAPI()
users_db = {}
contacts_db = {}

@app.post('/auth/register')
async def register(user: models.UserRegister):
    if user.mobile in users_db:
        raise HTTPException(status_code=400, detail='Mobile number already registered')
    hashed_password = auth.hash_password(user.password)
    user_id = str(len(users_db) + 1)
    users_db[user.mobile] = {'id': user_id, 'password': hashed_password}
    return {'id': user_id, 'mobile': user.mobile}

@app.post('/auth/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail='Mobile number not registered')
    if not auth.verify_password(form_data.password, user['password']):
        raise HTTPException(status_code=400, detail='Incorrect password')
    access_token_expires = datetime.timedelta(minutes=auth.access_token_expire_minutes)
    access_token = auth.create_access_token(data={'sub': user['id']}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}

@app.post('/contacts')
async def create_contact(contact: models.ContactCreate, token: str = Depends(auth.oauth2_scheme)):
    user_id = auth.get_current_user(token)
    contact_id = str(len(contacts_db) + 1)
    contacts_db[contact_id] = {'name': contact.name, 'mobile': contact.mobile, 'owner_id': user_id}
    return {'id': contact_id, 'name': contact.name, 'mobile': contact.mobile, 'owner_id': user_id}

@app.get('/contacts')
async def get_contacts(token: str = Depends(auth.oauth2_scheme)):
    user_id = auth.get_current_user(token)
    user_contacts = [contact for contact in contacts_db.values() if contact['owner_id'] == user_id]
    return user_contacts

@app.put('/contacts/{contact_id}')
async def update_contact(contact_id: str, contact: models.ContactUpdate, token: str = Depends(auth.oauth2_scheme)):
    user_id = auth.get_current_user(token)
    if contact_id not in contacts_db:
        raise HTTPException(status_code=404, detail='Contact not found')
    if contacts_db[contact_id]['owner_id'] != user_id:
        raise HTTPException(status_code=403, detail='Forbidden')
    if contact.name:
        contacts_db[contact_id]['name'] = contact.name
    if contact.mobile:
        contacts_db[contact_id]['mobile'] = contact.mobile
    return {'id': contact_id, 'name': contacts_db[contact_id]['name'], 'mobile': contacts_db[contact_id]['mobile'], 'owner_id': user_id}

@app.delete('/contacts/{contact_id}')
async def delete_contact(contact_id: str, token: str = Depends(auth.oauth2_scheme)):
    user_id = auth.get_current_user(token)
    if contact_id not in contacts_db:
        raise HTTPException(status_code=404, detail='Contact not found')
    if contacts_db[contact_id]['owner_id'] != user_id:
        raise HTTPException(status_code=403, detail='Forbidden')
    del contacts_db[contact_id]
    return {'message': 'Contact deleted successfully'}