from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    id: int
    mobile: str
    password: str

class Contact(BaseModel):
    id: int
    name: str
    mobile: str
    owner_id: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    mobile: Optional[str] = None

class UserRegister(BaseModel):
    mobile: str
    password: str

class UserLogin(BaseModel):
    mobile: str
    password: str

class ContactCreate(BaseModel):
    name: str
    mobile: str

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None

class ContactOut(BaseModel):
    id: int
    name: str
    mobile: str
    owner_id: int

class UserOut(BaseModel):
    id: int
    mobile: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str