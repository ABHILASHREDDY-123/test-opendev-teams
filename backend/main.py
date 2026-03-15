from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from pydantic import EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional

app = FastAPI()

# Define the Pydantic models
class User(BaseModel):
    id: int
    mobile: str
    password: str
    class Config:
        orm_mode = True

class UserRegister(BaseModel):
    mobile: str
    password: str
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    mobile: str
    password: str
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    class Config:
        orm_mode = True

class TokenData(BaseModel):
    mobile: Optional[str] = None
    class Config:
        orm_mode = True

class Contact(BaseModel):
    id: int
    name: str
    mobile: str
    owner_id: int
    class Config:
        orm_mode = True

class ContactCreate(BaseModel):
    name: str
    mobile: str
    class Config:
        orm_mode = True

class ContactUpdate(BaseModel):
    name: Optional[str]
    mobile: Optional[str]
    class Config:
        orm_mode = True

# In-memory data stores
users_db = {}
contacts_db = {}

# Password hashing
pwd_context = CryptContext(schemes=['bcrypt'], default='bcrypt')

# JWT settings
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Authentication utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        mobile: str = payload.get("sub")
        if mobile is None:
            raise credentials_exception
        token_data = TokenData(mobile=mobile)
    except JWTError:
        raise credentials_exception
    user = users_db.get(token_data.mobile)
    if user is None:
        raise credentials_exception
    return user

# Dependency for protected routes
async def get_current_active_user(token: str = Depends()):
    user = get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Inactive user")
    return user

# Routes
@app.post("/auth/register")
async def register(user: UserRegister):
    if users_db.get(user.mobile):
        raise HTTPException(status_code=400, detail="Mobile number already registered")
    hashed_password = get_password_hash(user.password)
    user_id = len(users_db) + 1
    users_db[user.mobile] = {
        "id": user_id,
        "mobile": user.mobile,
        "password": hashed_password
    }
    return {
        "id": user_id,
        "mobile": user.mobile
    }

@app.post("/auth/login")
async def login(user: UserLogin):
    user_db = users_db.get(user.mobile)
    if not user_db:
        raise HTTPException(status_code=401, detail="Incorrect mobile or password")
    if not verify_password(user.password, user_db['password']):
        raise HTTPException(status_code=401, detail="Incorrect mobile or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.mobile}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/contacts")
async def create_contact(contact: ContactCreate, token: str = Depends(get_current_active_user)):
    contact_id = len(contacts_db) + 1
    contacts_db[contact_id] = {
        "id": contact_id,
        "name": contact.name,
        "mobile": contact.mobile,
        "owner_id": token['id']
    }
    return {
        "id": contact_id,
        "name": contact.name,
        "mobile": contact.mobile
    }

@app.get("/contacts")
async def read_contacts(token: str = Depends(get_current_active_user)):
    contacts = [contact for contact in contacts_db.values() if contact['owner_id'] == token['id']]
    return contacts

@app.put("/contacts/{contact_id}")
async def update_contact(contact_id: int, contact: ContactUpdate, token: str = Depends(get_current_active_user)):
    if contact_id not in contacts_db:
        raise HTTPException(status_code=404, detail="Contact not found")
    if contacts_db[contact_id]['owner_id'] != token['id']:
        raise HTTPException(status_code=401, detail="You do not own this contact")
    if contact.name:
        contacts_db[contact_id]['name'] = contact.name
    if contact.mobile:
        contacts_db[contact_id]['mobile'] = contact.mobile
    return {
        "id": contact_id,
        "name": contacts_db[contact_id]['name'],
        "mobile": contacts_db[contact_id]['mobile']
    }

@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: int, token: str = Depends(get_current_active_user)):
    if contact_id not in contacts_db:
        raise HTTPException(status_code=404, detail="Contact not found")
    if contacts_db[contact_id]['owner_id'] != token['id']:
        raise HTTPException(status_code=401, detail="You do not own this contact")
    del contacts_db[contact_id]
    return {"message": "Contact deleted"}