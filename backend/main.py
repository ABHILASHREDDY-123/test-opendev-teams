from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
from . import models, auth

class Contact(BaseModel):
    id: int
    name: str
    mobile: str
    owner_id: int

app = FastAPI()

# in-memory data stores (replace with a database in production)
users_db = {}
contacts_db = {}

security = HTTPBearer()

@app.post('/auth/register')
def register(user_register: models.UserRegister):
    if user_register.mobile in users_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Mobile number already registered')
    hashed_password = auth.hash_password(user_register.password)
    user_id = len(users_db) + 1
    users_db[user_register.mobile] = {'id': user_id, 'hashed_password': hashed_password}
    return {'id': user_id, 'mobile': user_register.mobile}

@app.post('/auth/login')
def login(user_login: models.UserLogin):
    if user_login.mobile not in users_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid mobile number or password')
    stored_user = users_db[user_login.mobile]
    if not auth.verify_password(user_login.password, stored_user['hashed_password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid mobile number or password')
    access_token = auth.create_access_token(data={'sub': user_login.mobile})
    return {'access_token': access_token, 'token_type': 'bearer'}

@app.post('/contacts/')
def create_contact(contact: models.ContactCreate, token: HTTPAuthorizationCredentials = Depends(security)):
    # authenticate and authorize the request
    payload = auth.get_current_user(token.credentials)
    owner_id = len(contacts_db) + 1
    contact_id = len(contacts_db) + 1
    contacts_db[contact_id] = {'id': contact_id, 'name': contact.name, 'mobile': contact.mobile, 'owner_id': owner_id}
    return {'id': contact_id, 'name': contact.name, 'mobile': contact.mobile, 'owner_id': owner_id}

@app.get('/contacts/')
def read_contacts(token: HTTPAuthorizationCredentials = Depends(security)):
    # authenticate and authorize the request
    payload = auth.get_current_user(token.credentials)
    contacts = [contact for contact in contacts_db.values() if contact['owner_id'] == payload['sub']]
    return contacts

@app.put('/contacts/{contact_id}')
def update_contact(contact_id: int, contact: models.ContactUpdate, token: HTTPAuthorizationCredentials = Depends(security)):
    # authenticate and authorize the request
    payload = auth.get_current_user(token.credentials)
    if contact_id not in contacts_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    stored_contact = contacts_db[contact_id]
    if stored_contact['owner_id'] != payload['sub']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You do not own this contact')
    if contact.name:
        stored_contact['name'] = contact.name
    if contact.mobile:
        stored_contact['mobile'] = contact.mobile
    return stored_contact

@app.delete('/contacts/{contact_id}')
def delete_contact(contact_id: int, token: HTTPAuthorizationCredentials = Depends(security)):
    # authenticate and authorize the request
    payload = auth.get_current_user(token.credentials)
    if contact_id not in contacts_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    stored_contact = contacts_db[contact_id]
    if stored_contact['owner_id'] != payload['sub']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You do not own this contact')
    del contacts_db[contact_id]
    return {'message': 'Contact deleted successfully'}