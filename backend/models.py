from pydantic import BaseModel
from typing import List

class UserRegister(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class ContactCreate(BaseModel):
    name: str
    email: str
    phone: str

class ContactUpdate(BaseModel):
    name: str | None
    email: str | None
    phone: str | None

class ContactOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    owner_id: int
