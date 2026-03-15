from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from jose import jwt
from passlib.context import CryptContext
import uvicorn

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
    username: str | None = None

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

class UserOut(BaseModel):
    id: int
    mobile: str

class ContactOut(BaseModel):
    id: int
    name: str
    mobile: str
    owner_id: int

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

token_context = CryptContext(schemes=['bcrypt'], default='bcrypt')
secret_key = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
algorithm = "HS256"
access_token_expire_minutes = 30

dummy_users_db = {}
dummy_contacts_db = {}

def get_password_hash(password):
    return token_context.hash(password)

def verify_password(plain_password, hashed_password):
    return token_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: int | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.JWTError:
        raise credentials_exception
    user = dummy_users_db.get(token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User):
    return current_user

# Define the API endpoints
@app.post("/auth/register")
async def register(user: UserRegister):
    hashed_password = get_password_hash(user.password)
    user_id = len(dummy_users_db) + 1
    dummy_users_db[user_id] = {
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
    user_db = dummy_users_db.get(user.mobile)
    if not user_db:
        raise HTTPException(
            status_code=401,
            detail="Incorrect mobile or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(user.password, user_db['password']):
        raise HTTPException(
            status_code=401,
            detail="Incorrect mobile or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.mobile}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/contacts")
async def create_contact(contact: ContactCreate, token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(token)
    contact_id = len(dummy_contacts_db) + 1
    dummy_contacts_db[contact_id] = {
        "id": contact_id,
        "name": contact.name,
        "mobile": contact.mobile,
        "owner_id": current_user['id']
    }
    return {
        "id": contact_id,
        "name": contact.name,
        "mobile": contact.mobile,
        "owner_id": current_user['id']
    }

@app.get("/contacts")
async def read_contacts(token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(token)
    contacts = [contact for contact in dummy_contacts_db.values() if contact['owner_id'] == current_user['id']]
    return contacts

@app.put("/contacts/{contact_id}")
async def update_contact(contact_id: int, contact: ContactUpdate, token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(token)
    if contact_id not in dummy_contacts_db:
        raise HTTPException(
            status_code=404,
            detail="Contact not found",
        )
    if dummy_contacts_db[contact_id]['owner_id'] != current_user['id']:
        raise HTTPException(
            status_code=403,
            detail="You do not own this contact",
        )
    if contact.name:
        dummy_contacts_db[contact_id]['name'] = contact.name
    if contact.mobile:
        dummy_contacts_db[contact_id]['mobile'] = contact.mobile
    return {
        "id": contact_id,
        "name": dummy_contacts_db[contact_id]['name'],
        "mobile": dummy_contacts_db[contact_id]['mobile'],
        "owner_id": dummy_contacts_db[contact_id]['owner_id']
    }

@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: int, token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(token)
    if contact_id not in dummy_contacts_db:
        raise HTTPException(
            status_code=404,
            detail="Contact not found",
        )
    if dummy_contacts_db[contact_id]['owner_id'] != current_user['id']:
        raise HTTPException(
            status_code=403,
            detail="You do not own this contact",
        )
    del dummy_contacts_db[contact_id]
    return {"message": "Contact deleted"}
