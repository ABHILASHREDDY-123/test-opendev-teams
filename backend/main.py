from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import ValidationError
from backend.models import UserRegister, UserLogin, UserOut, TokenResponse, ContactCreate, ContactUpdate, ContactOut
from backend.auth import hash_password, verify_password, create_access_token, get_current_user
from uuid import uuid4
from typing import List

app = FastAPI()

# In-memory data stores
users_db = {}
contacts_db = {}

@app.post("/auth/register", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def register_user(user: UserRegister):
    if user.mobile in users_db:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Mobile number already registered")
    user_id = str(uuid4())
    hashed_password = hash_password(user.password)
    new_user = {"id": user_id, "mobile": user.mobile, "hashed_password": hashed_password}
    users_db[user.mobile] = new_user
    return {"id": user_id, "mobile": user.mobile}

@app.post("/auth/login", response_model=TokenResponse)
async def login_user(user: UserLogin):
    stored_user = users_db.get(user.mobile)
    if not stored_user or not verify_password(user.password, stored_user['hashed_password']):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token({"sub": stored_user['id']})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/contacts", status_code=status.HTTP_201_CREATED, response_model=ContactOut)
async def create_contact(contact: ContactCreate, current_user: dict = Depends(get_current_user)):
    contact_id = str(uuid4())
    new_contact = {"id": contact_id, "name": contact.name, "mobile": contact.mobile, "owner_id": current_user['id']}
    contacts_db[contact_id] = new_contact
    return new_contact

@app.get("/contacts", response_model=List[ContactOut])
async def list_contacts(current_user: dict = Depends(get_current_user)):
    user_contacts = [contact for contact in contacts_db.values() if contact['owner_id'] == current_user['id']]
    return user_contacts

@app.put("/contacts/{contact_id}", response_model=ContactOut)
async def update_contact(contact_id: str, contact: ContactUpdate, current_user: dict = Depends(get_current_user)):
    stored_contact = contacts_db.get(contact_id)
    if not stored_contact or stored_contact['owner_id'] != current_user['id']:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Contact not found")
    update_data = contact.dict(exclude_unset=True)
    stored_contact.update(update_data)
    return stored_contact

@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: str, current_user: dict = Depends(get_current_user)):
    stored_contact = contacts_db.get(contact_id)
    if not stored_contact or stored_contact['owner_id'] != current_user['id']:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Contact not found")
    contacts_db.pop(contact_id, None)
    return {"message": "Contact deleted successfully"}