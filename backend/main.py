from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Contact(BaseModel):
    id: int
    name: str
    mobile: str
    owner_id: int

class ContactCreate(BaseModel):
    name: str
    mobile: str

contacts = {}

@app.get('/contacts/')
def get_contacts(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # authenticate token
    # return contacts for authenticated user
    pass

@app.post('/contacts/')
def create_contact(contact: ContactCreate, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # authenticate token
    # create new contact for authenticated user
    pass

@app.get('/contacts/{contact_id}')
def get_contact(contact_id: int, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # authenticate token
    # return contact by ID for authenticated user
    pass

@app.put('/contacts/{contact_id}')
def update_contact(contact_id: int, contact: ContactCreate, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # authenticate token
    # update contact by ID for authenticated user
    pass

@app.delete('/contacts/{contact_id}')
def delete_contact(contact_id: int, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # authenticate token
    # delete contact by ID for authenticated user
    pass
