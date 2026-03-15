from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from jwt import encode, decode
from datetime import datetime, timedelta
import bcrypt

app = FastAPI()

class User(BaseModel):
    username: str
    password: str

class Contact(BaseModel):
    name: str
    phone: str

# In-memory storage for users and contacts
users = {}
contacts = {}

# Register a new user
@app.post("/register")
def register(user: User):
    if user.username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    users[user.username] = {
        "password": bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    }
    return {"message": "User created successfully"}

# Login a user
@app.post("/login")
def login(user: User):
    if user.username not in users:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not bcrypt.checkpw(user.password.encode(), users[user.username]["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    payload = {
        "username": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = encode(payload, "secret_key", algorithm="HS256")
    return {"token": token}

# Create a new contact
@app.post("/contacts")
def create_contact(contact: Contact, token: str):
    try:
        payload = decode(token, "secret_key", algorithms=["HS256"])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    contacts[payload["username"]] = contacts.get(payload["username"], []) + [contact]
    return {"message": "Contact created successfully"}

# Get all contacts for a user
@app.get("/contacts")
def get_contacts(token: str):
    try:
        payload = decode(token, "secret_key", algorithms=["HS256"])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    return contacts.get(payload["username"], [])
