from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
import pytest
from pytest import fixture
app = FastAPI()

# Define the User model
class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    disabled: bool = False
    # Add password hashing
    password: str
    # Add JWT token
    token: str
    # Add contact list
    contacts: List[str] = []

# Define the Contact model
class Contact(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    owner_id: int
    # Add contact details
    details: str = ""

# In-memory data store for users and contacts (replace with a database in production)
users = {}
contacts = {}

# OAuth2 scheme definition
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get the current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Implement token verification and user retrieval
    for user_id, user in users.items():
        if user.token == token:
            return user
    raise HTTPException(status_code=401, detail="Invalid token")

# User registration endpoint
@app.post("/register")
async def register(user: User):
    # Implement user registration logic
    if user.username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    users[user.username] = user
    return user

# User login endpoint
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Implement user login logic
    for user_id, user in users.items():
        if user.username == form_data.username and user.password == form_data.password:
            # Generate and return a JWT token
            token = "example_token"
            user.token = token
            return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid username or password")

# Contact creation endpoint
@app.post("/contacts")
async def create_contact(contact: Contact, current_user: User = Depends(get_current_user)):
    # Implement contact creation logic
    contact.owner_id = current_user.id
    contacts[contact.id] = contact
    return contact

# Contact retrieval endpoint
@app.get("/contacts")
async def read_contacts(current_user: User = Depends(get_current_user)):
    # Implement contact retrieval logic
    user_contacts = [contact for contact in contacts.values() if contact.owner_id == current_user.id]
    return user_contacts

# Contact update endpoint
@app.put("/contacts/{contact_id}")
async def update_contact(contact_id: int, contact: Contact, current_user: User = Depends(get_current_user)):
    # Implement contact update logic
    if contact_id not in contacts:
        raise HTTPException(status_code=404, detail="Contact not found")
    if contacts[contact_id].owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    contacts[contact_id] = contact
    return contact

# Contact deletion endpoint
@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: int, current_user: User = Depends(get_current_user)):
    # Implement contact deletion logic
    if contact_id not in contacts:
        raise HTTPException(status_code=404, detail="Contact not found")
    if contacts[contact_id].owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    del contacts[contact_id]
    return {"message": "Contact deleted"}
