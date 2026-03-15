from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
import pytest
import uvicorn
import jwt
import bcrypt
from datetime import datetime, timedelta

app = FastAPI()

# Define the Pydantic models
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

class TokenData(BaseModel):
    mobile: str | None = None

class UserRegister(BaseModel):
    mobile: str
    password: str

class UserLogin(BaseModel):
    mobile: str
    password: str

class ContactCreate(BaseModel):
    name: str
    mobile: str

class ContactUpdate(BaseModel):
    name: str | None
    mobile: str | None

class ContactOut(BaseModel):
    id: int
    name: str
    mobile: str
    owner_id: int

class UserOut(BaseModel):
    id: int
    mobile: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# In-memory data stores
users_db = {}
contacts_db = {}

# Authentication utilities
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    if '_iat' in to_encode:
        to_encode['_iat'] = int(to_encode['_iat'])
    to_encode.update({'exp': datetime.utcnow() + timedelta(minutes=30)})
    encoded_jwt = jwt.encode(to_encode, 'secret_key', algorithm='HS256')
    return encoded_jwt

def get_current_user(token: str) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        mobile: str = payload.get('sub')
        if mobile is None:
            raise credentials_exception
        token_data = TokenData(mobile=mobile)
    except jwt.PyJWTError:
        raise credentials_exception
    user = users_db.get(token_data.mobile)
    if user is None:
        raise credentials_exception
    return user

# Define the authentication dependency
security = HTTPBearer()

# Define the routes
@app.post('/auth/register', response_model=UserOut)
async def register(user: UserRegister):
    if user.mobile in users_db:
        raise HTTPException(status_code=409, detail='Mobile number already registered')
    hashed_password = hash_password(user.password)
    user_id = len(users_db) + 1
    users_db[user.mobile] = User(id=user_id, mobile=user.mobile, password=hashed_password)
    return UserOut(id=user_id, mobile=user.mobile)

@app.post('/auth/login', response_model=TokenResponse)
async def login(user: UserLogin):
    if user.mobile not in users_db:
        raise HTTPException(status_code=401, detail='Invalid mobile number or password')
    stored_user = users_db[user.mobile]
    if not verify_password(user.password, stored_user.password):
        raise HTTPException(status_code=401, detail='Invalid mobile number or password')
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={'sub': user.mobile})
    return TokenResponse(access_token=access_token, token_type='bearer')

@app.post('/contacts/', response_model=ContactOut)
async def create_contact(contact: ContactCreate, token: HTTPAuthorizationCredentials = Depends(security)):
    user = get_current_user(token.credentials)
    contact_id = len(contacts_db) + 1
    contacts_db[contact_id] = Contact(id=contact_id, name=contact.name, mobile=contact.mobile, owner_id=user.id)
    return ContactOut(id=contact_id, name=contact.name, mobile=contact.mobile, owner_id=user.id)

@app.get('/contacts/', response_model=List[ContactOut])
async def read_contacts(token: HTTPAuthorizationCredentials = Depends(security)):
    user = get_current_user(token.credentials)
    return [contact for contact in contacts_db.values() if contact.owner_id == user.id]

@app.put('/contacts/{contact_id}', response_model=ContactOut)
async def update_contact(contact_id: int, contact: ContactUpdate, token: HTTPAuthorizationCredentials = Depends(security)):
    user = get_current_user(token.credentials)
    if contact_id not in contacts_db:
        raise HTTPException(status_code=404, detail='Contact not found')
    stored_contact = contacts_db[contact_id]
    if stored_contact.owner_id != user.id:
        raise HTTPException(status_code=401, detail='You do not own this contact')
    if contact.name:
        stored_contact.name = contact.name
    if contact.mobile:
        stored_contact.mobile = contact.mobile
    return ContactOut(id=contact_id, name=stored_contact.name, mobile=stored_contact.mobile, owner_id=stored_contact.owner_id)

@app.delete('/contacts/{contact_id}')
async def delete_contact(contact_id: int, token: HTTPAuthorizationCredentials = Depends(security)):
    user = get_current_user(token.credentials)
    if contact_id not in contacts_db:
        raise HTTPException(status_code=404, detail='Contact not found')
    stored_contact = contacts_db[contact_id]
    if stored_contact.owner_id != user.id:
        raise HTTPException(status_code=401, detail='You do not own this contact')
    del contacts_db[contact_id]
    return {'message': 'Contact deleted successfully'}
