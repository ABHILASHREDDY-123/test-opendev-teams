from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from backend.models import UserRegister, UserLogin, UserOut, TokenResponse, ContactCreate, ContactUpdate, ContactOut
from backend.auth import hash_password, verify_password, create_access_token, get_current_user
import uuid

app = FastAPI()

# In-memory databases
users_db = {}
contacts_db = {}

@app.post("/auth/register", status_code=201, response_model=UserOut)
async def register(user: UserRegister):
    if user.mobile in users_db:
        raise HTTPException(status_code=409, detail="Mobile number already registered")
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user.password)
    users_db[user.mobile] = {"id": user_id, "mobile": user.mobile, "hashed_password": hashed_password}
    return {"id": user_id, "mobile": user.mobile}

@app.post("/auth/login", response_model=TokenResponse)
async def login(user: UserLogin):
    if user.mobile not in users_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    stored_user = users_db[user.mobile]
    if not verify_password(user.password, stored_user['hashed_password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": stored_user['id']})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/contacts", status_code=201, response_model=ContactOut)
async def create_contact(contact: ContactCreate, current_user: dict = Depends(get_current_user)):
    contact_id = str(uuid.uuid4())
    new_contact = {
        "id": contact_id,
        "name": contact.name,
        "mobile": contact.mobile,
        "owner_id": current_user['id']
    }
    contacts_db[contact_id] = new_contact
    return new_contact

@app.get("/contacts", response_model=list[ContactOut])
async def list_contacts(current_user: dict = Depends(get_current_user)):
    user_contacts = [contact for contact in contacts_db.values() if contact['owner_id'] == current_user['id']]
    return user_contacts

@app.put("/contacts/{contact_id}", response_model=ContactOut)
async def update_contact(contact_id: str, contact: ContactUpdate, current_user: dict = Depends(get_current_user)):
    if contact_id not in contacts_db:
        raise HTTPException(status_code=404, detail="Contact not found")
    stored_contact = contacts_db[contact_id]
    if stored_contact['owner_id'] != current_user['id']:
        raise HTTPException(status_code=404, detail="Contact not found")
    updated_contact = stored_contact.copy()
    if contact.name is not None:
        updated_contact['name'] = contact.name
    if contact.mobile is not None:
        updated_contact['mobile'] = contact.mobile
    contacts_db[contact_id] = updated_contact
    return updated_contact

@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: str, current_user: dict = Depends(get_current_user)):
    if contact_id not in contacts_db:
        raise HTTPException(status_code=404, detail="Contact not found")
    stored_contact = contacts_db[contact_id]
    if stored_contact['owner_id'] != current_user['id']:
        raise HTTPException(status_code=404, detail="Contact not found")
    del contacts_db[contact_id]
    return {"message": "Contact deleted successfully"}