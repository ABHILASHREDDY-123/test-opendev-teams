from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import ValidationError
from backend.models import UserRegister, UserLogin, UserOut, TokenResponse, ContactCreate, ContactUpdate, ContactOut
from backend.auth import hash_password, verify_password, create_access_token, get_current_user, oauth2_scheme
import uuid
from typing import List

app = FastAPI()

# In-memory data stores
users_db = {}
contacts_db = {}

@app.post('/auth/register', status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def register(user: UserRegister):
    if user.mobile in users_db:
        raise HTTPException(status_code=409, detail='Mobile number already registered')
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user.password)
    users_db[user.mobile] = {'id': user_id, 'mobile': user.mobile, 'hashed_password': hashed_password}
    return UserOut(id=user_id, mobile=user.mobile)

@app.post('/auth/login', response_model=TokenResponse)
async def login(user: UserLogin):
    stored_user = users_db.get(user.mobile)
    if not stored_user or not verify_password(user.password, stored_user['hashed_password']):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    access_token = create_access_token({'sub': stored_user['id']})
    return TokenResponse(access_token=access_token, token_type='bearer')

@app.post('/contacts', status_code=201, response_model=ContactOut)
async def create_contact(contact: ContactCreate, current_user: dict = Depends(get_current_user)):
    contact_id = str(uuid.uuid4())
    new_contact = ContactOut(id=contact_id, owner_id=current_user['id'], **contact.dict())
    if current_user['id'] not in contacts_db:
        contacts_db[current_user['id']] = []
    contacts_db[current_user['id']].append(new_contact.dict())
    return new_contact

@app.get('/contacts', response_model=List[ContactOut])
async def list_contacts(current_user: dict = Depends(get_current_user)):
    return contacts_db.get(current_user['id'], [])

@app.put('/contacts/{contact_id}', response_model=ContactOut)
async def update_contact(contact_id: str, contact: ContactUpdate, current_user: dict = Depends(get_current_user)):
    user_contacts = contacts_db.get(current_user['id'], [])
    for stored_contact in user_contacts:
        if stored_contact['id'] == contact_id:
            updated_contact = stored_contact.copy()
            if contact.name is not None:
                updated_contact['name'] = contact.name
            if contact.mobile is not None:
                updated_contact['mobile'] = contact.mobile
            user_contacts.remove(stored_contact)
            user_contacts.append(updated_contact)
            return ContactOut(**updated_contact)
    raise HTTPException(status_code=404, detail='Contact not found')

@app.delete('/contacts/{contact_id}')
async def delete_contact(contact_id: str, current_user: dict = Depends(get_current_user)):
    user_contacts = contacts_db.get(current_user['id'], [])
    for contact in user_contacts:
        if contact['id'] == contact_id:
            user_contacts.remove(contact)
            return {'message': 'Contact deleted successfully'}
    raise HTTPException(status_code=404, detail='Contact not found')