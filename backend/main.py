from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class User(BaseModel):
    id: int
    username: str
    email: str

class Contact(BaseModel):
    id: int
    name: str
    phone: str
    owner_id: int

# In-memory data store for demonstration purposes
users = {}
contacts = {}

@app.post("/users/", response_model=User)
async def create_user(user: User):
    if user.id in users:
        raise HTTPException(status_code=400, detail="User already exists")
    users[user.id] = user
    return user

@app.post("/contacts/", response_model=Contact)
async def create_contact(contact: Contact):
    if contact.id in contacts:
        raise HTTPException(status_code=400, detail="Contact already exists")
    contacts[contact.id] = contact
    return contact

@app.get("/contacts/")
async def read_contacts():
    return list(contacts.values())

@app.get("/contacts/{contact_id}")
async def read_contact(contact_id: int):
    if contact_id not in contacts:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contacts[contact_id]

@app.put("/contacts/{contact_id}")
async def update_contact(contact_id: int, contact: Contact):
    if contact_id not in contacts:
        raise HTTPException(status_code=404, detail="Contact not found")
    contacts[contact_id] = contact
    return contact

@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: int):
    if contact_id not in contacts:
        raise HTTPException(status_code=404, detail="Contact not found")
    del contacts[contact_id]
    return {"message": "Contact deleted"}