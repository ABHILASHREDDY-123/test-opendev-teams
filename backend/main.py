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

users = {}
contacts = {}

@app.post("/register")
def register(user: User):
    if user.username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    users[user.username] = {
        "password": bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    }
    return {"message": "User created successfully"}

@app.post("/login")
def login(user: User):
    if user.username not in users:
        raise HTTPException(status_code=400, detail="Username does not exist")
    if not bcrypt.checkpw(user.password.encode(), users[user.username]["password"]):
        raise HTTPException(status_code=400, detail="Incorrect password")
    payload = {
        "username": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = encode(payload, "secretkey", algorithm="HS256")
    return {"token": token}

@app.post("/contacts")
def create_contact(contact: Contact, token: str):
    try:
        payload = decode(token, "secretkey", algorithms=["HS256"])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload["username"] not in users:
        raise HTTPException(status_code=401, detail="User does not exist")
    contacts[contact.name] = contact
    return {"message": "Contact created successfully"}

@app.get("/contacts")
def get_contacts(token: str):
    try:
        payload = decode(token, "secretkey", algorithms=["HS256"])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload["username"] not in users:
        raise HTTPException(status_code=401, detail="User does not exist")
    return list(contacts.values())

@app.put("/contacts/{name}")
def update_contact(name: str, contact: Contact, token: str):
    try:
        payload = decode(token, "secretkey", algorithms=["HS256"])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload["username"] not in users:
        raise HTTPException(status_code=401, detail="User does not exist")
    if name not in contacts:
        raise HTTPException(status_code=404, detail="Contact does not exist")
    contacts[name] = contact
    return {"message": "Contact updated successfully"}

@app.delete("/contacts/{name}")
def delete_contact(name: str, token: str):
    try:
        payload = decode(token, "secretkey", algorithms=["HS256"])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload["username"] not in users:
        raise HTTPException(status_code=401, detail="User does not exist")
    if name not in contacts:
        raise HTTPException(status_code=404, detail="Contact does not exist")
    del contacts[name]
    return {"message": "Contact deleted successfully"}