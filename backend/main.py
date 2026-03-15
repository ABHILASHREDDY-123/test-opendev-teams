from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from backend.models import UserRegister, UserLogin, UserOut, TokenResponse, ContactCreate, ContactUpdate, ContactOut
from backend.auth import hash_password, verify_password, create_access_token, get_current_user
from typing import List

class Contact:
 def __init__(self, id: str, name: str, mobile: str, owner_id: str):
 self.id = id
 self.name = name
 self.mobile = mobile
 self.owner_id = owner_id

def get_contact(contact_id: str, contacts: List[Contact]) -> Contact:
 for contact in contacts:
 if contact.id == contact_id:
 return contact
 raise HTTPException(status_code=404, detail="Contact not found")

app = FastAPI()
users_db = {}
contacts_db = {}

@app.post("/auth/register")
async def register(user: UserRegister):
 if user.mobile in users_db:
 raise HTTPException(status_code=409, detail="Mobile number already registered")
 hashed_password = hash_password(user.password)
 user_id = str(len(users_db))
 users_db[user.mobile] = {
 "id": user_id,
 "hashed_password": hashed_password
 }
 return UserOut(id=user_id, mobile=user.mobile)

@app.post("/auth/login")
async def login(user: UserLogin):
 if user.mobile not in users_db:
 raise HTTPException(status_code=401, detail="Mobile number not registered")
 stored_user = users_db[user.mobile]
 if not verify_password(user.password, stored_user["hashed_password"]):
 raise HTTPException(status_code=401, detail="Incorrect password")
 access_token = create_access_token({"user_id": stored_user["id"]})
 return TokenResponse(access_token=access_token, token_type="bearer")

@app.post("/contacts")
async def create_contact(contact: ContactCreate, token: str = Depends(get_current_user)):
 contact_id = str(len(contacts_db))
 contacts_db[contact_id] = Contact(contact_id, contact.name, contact.mobile, token)
 return ContactOut(id=contact_id, name=contact.name, mobile=contact.mobile, owner_id=token)

@app.get("/contacts")
async def read_contacts(token: str = Depends(get_current_user)):
 contacts = [contact for contact in contacts_db.values() if contact.owner_id == token]
 return contacts

@app.put("/contacts/{contact_id}")
async def update_contact(contact_id: str, contact: ContactUpdate, token: str = Depends(get_current_user)):
 contact_obj = get_contact(contact_id, list(contacts_db.values()))
 if contact_obj.owner_id != token:
 raise HTTPException(status_code=404, detail="Contact not found")
 if contact.name:
 contact_obj.name = contact.name
 if contact.mobile:
 contact_obj.mobile = contact.mobile
 return ContactOut(id=contact_id, name=contact_obj.name, mobile=contact_obj.mobile, owner_id=token)

@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: str, token: str = Depends(get_current_user)):
 contact_obj = get_contact(contact_id, list(contacts_db.values()))
 if contact_obj.owner_id != token:
 raise HTTPException(status_code=404, detail="Contact not found")
 del contacts_db[contact_id]
 return {"message": "Contact deleted"}