from pydantic import BaseModel
from typing import List

class Contact(BaseModel):
    id: int
    name: str
    mobile: str
    owner_id: int

class ContactCreate(BaseModel):
    name: str
    mobile: str

class User(BaseModel):
    id: int
    mobile: str
    password: str

class UserCreate(BaseModel):
    mobile: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
