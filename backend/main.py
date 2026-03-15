from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from backend.models import UserRegister, UserLogin, UserOut, TokenResponse, ContactCreate, ContactUpdate, ContactOut
from backend.auth import hash_password, verify_password, create_access_token
from typing import List

class Contact(BaseModel):
 id: str
 name: str
 mobile: str
 owner_id: str

class User(BaseModel):
 id: str
 mobile: str
 hashed_password: str

app = FastAPI()
auth_scheme = HTTPBearer()
users_db = {}
contacts_db = {}

@app.post('/auth/register')
async def register(user: UserRegister):
 if user.mobile in users_db:
 raise HTTPException(status_code=409, detail='Mobile already registered')
 hashed_password = hash_password(user.password)
 user_id = str(len(users_db))
 users_db[user.mobile] = {'id': user_id, 'hashed_password': hashed_password}
 return UserOut(id=user_id, mobile=user.mobile)

@app.post('/auth/login')
async def login(user: UserLogin):
 if user.mobile not in users_db:
 raise HTTPException(status_code=401, detail='Invalid mobile or password')
 stored_hashed_password = users_db[user.mobile]['hashed_password']
 if not verify_password(user.password, stored_hashed_password):
 raise HTTPException(status_code=401, detail='Invalid mobile or password')
 access_token = create_access_token(data={'sub': user.mobile})
 return TokenResponse(access_token=access_token, token_type='bearer')

async def get_current_user(token: str = Depends(auth_scheme)):
 credentials = HTTPAuthorizationCredentials(scheme='Bearer', credentials=token)
 user_mobile = credentials.credentials
 if user_mobile not in users_db:
 raise HTTPException(status_code=401, detail='Invalid token')
 return users_db[user_mobile]

@app.post('/contacts')
async def create_contact(contact: ContactCreate, current_user: dict = Depends(get_current_user)):
 contact_id = str(len(contacts_db))
 contacts_db[contact_id] = {'name': contact.name, 'mobile': contact.mobile, 'owner_id': current_user['id']}
 return ContactOut(id=contact_id, name=contact.name, mobile=contact.mobile, owner_id=current_user['id'])

@app.get('/contacts')
async def read_contacts(current_user: dict = Depends(get_current_user)):
 user_contacts = [contact for contact in contacts_db.values() if contact['owner_id'] == current_user['id']]
 return user_contacts

@app.put('/contacts/{contact_id}')
async def update_contact(contact_id: str, contact: ContactUpdate, current_user: dict = Depends(get_current_user)):
 if contact_id not in contacts_db:
 raise HTTPException(status_code=404, detail='Contact not found')
 if contacts_db[contact_id]['owner_id'] != current_user['id']:
 raise HTTPException(status_code=403, detail='Not authorized to update this contact')
 contacts_db[contact_id]['name'] = contact.name or contacts_db[contact_id]['name']
 contacts_db[contact_id]['mobile'] = contact.mobile or contacts_db[contact_id]['mobile']
 return ContactOut(id=contact_id, name=contacts_db[contact_id]['name'], mobile=contacts_db[contact_id]['mobile'], owner_id=current_user['id'])

@app.delete('/contacts/{contact_id}')
async def delete_contact(contact_id: str, current_user: dict = Depends(get_current_user)):
 if contact_id not in contacts_db:
 raise HTTPException(status_code=404, detail='Contact not found')
 if contacts_db[contact_id]['owner_id'] != current_user['id']:
 raise HTTPException(status_code=403, detail='Not authorized to delete this contact')
 del contacts_db[contact_id]
 return {'message': 'Contact deleted successfully'}