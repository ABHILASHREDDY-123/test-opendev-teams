from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from backend.models import UserRegister, UserLogin, UserOut, TokenResponse, ContactCreate, ContactUpdate, ContactOut
from backend.auth import hash_password, verify_password, create_access_token, get_current_user
from typing import List

class Contact(BaseModel):
    name: str
    mobile: str
    owner_id: str

app = FastAPI()

# In-memory data stores (replace with a database in production)
users_db = {}
contacts_db = {}

# Authentication scheme
security = HTTPBearer()

@app.post('/auth/register', response_model=UserOut)
def register(user: UserRegister):
    if user.mobile in users_db:
        raise HTTPException(status_code=409, detail='Mobile number already registered')
    hashed_password = hash_password(user.password)
    user_id = len(users_db) + 1
    users_db[user.mobile] = {'id': user_id, 'password': hashed_password}
    return UserOut(id=user_id, mobile=user.mobile)

@app.post('/auth/login', response_model=TokenResponse)
def login(user: UserLogin):
    if user.mobile not in users_db:
        raise HTTPException(status_code=401, detail='Invalid mobile number or password')
    stored_user = users_db[user.mobile]
    if not verify_password(user.password, stored_user['password']):
        raise HTTPException(status_code=401, detail='Invalid mobile number or password')
    access_token = create_access_token(data={'sub': user.mobile})
    return TokenResponse(access_token=access_token, token_type='bearer')

@app.post('/contacts/', response_model=ContactOut)
def create_contact(contact: ContactCreate, token: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(token.credentials)
    contact_id = len(contacts_db) + 1
    contacts_db[contact_id] = Contact(name=contact.name, mobile=contact.mobile, owner_id=current_user['sub'])
    return ContactOut(id=contact_id, name=contact.name, mobile=contact.mobile, owner_id=current_user['sub'])

@app.get('/contacts/', response_model=List[ContactOut])
def read_contacts(token: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(token.credentials)
    contacts = [ContactOut(id=k, name=v.name, mobile=v.mobile, owner_id=v.owner_id) for k, v in contacts_db.items() if v.owner_id == current_user['sub']]
    return contacts

@app.put('/contacts/{contact_id}', response_model=ContactOut)
def update_contact(contact_id: int, contact: ContactUpdate, token: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(token.credentials)
    if contact_id not in contacts_db:
        raise HTTPException(status_code=404, detail='Contact not found')
    if contacts_db[contact_id].owner_id != current_user['sub']:
        raise HTTPException(status_code=401, detail='You do not own this contact')
    if contact.name:
        contacts_db[contact_id].name = contact.name
    if contact.mobile:
        contacts_db[contact_id].mobile = contact.mobile
    return ContactOut(id=contact_id, name=contacts_db[contact_id].name, mobile=contacts_db[contact_id].mobile, owner_id=contacts_db[contact_id].owner_id)

@app.delete('/contacts/{contact_id}')
def delete_contact(contact_id: int, token: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(token.credentials)
    if contact_id not in contacts_db:
        raise HTTPException(status_code=404, detail='Contact not found')
    if contacts_db[contact_id].owner_id != current_user['sub']:
        raise HTTPException(status_code=401, detail='You do not own this contact')
    del contacts_db[contact_id]
    return {'message': 'Contact deleted successfully'}