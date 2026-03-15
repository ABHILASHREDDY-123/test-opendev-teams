from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI()

# OAuth2 scheme definition
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

# JWT secret key
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In-memory user storage
users_db = {}

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False

class UserInDB(User):
    password: str

class Contact(BaseModel):
    name: str
    phone: str

# User registration endpoint
@app.post("/register")
async def register(username: str, password: str):
    if username in users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = pwd_context.hash(password)
    users_db[username] = UserInDB(username=username, password=hashed_password)
    return {"message": "User created successfully"}

# User login endpoint
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode({
        "sub": user.username,
        "exp": datetime.utcnow() + access_token_expires
    }, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}

# Contact creation endpoint
@app.post("/contacts")
async def create_contact(contact: Contact, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        # Add contact to user's contacts
        if username not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        users_db[username].contacts.append(contact)
        return {"message": "Contact created successfully"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# Contact retrieval endpoint
@app.get("/contacts")
async def read_contacts(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        # Return user's contacts
        if username not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        return users_db[username].contacts

    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
