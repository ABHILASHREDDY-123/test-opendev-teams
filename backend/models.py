from pydantic import BaseModel
from typing import Optional

class UserRegister(BaseModel):
    mobile: str
    password: str

class UserLogin(BaseModel):
    mobile: str
    password: str

class UserOut(BaseModel):
    id: str
    mobile: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class ContactCreate(BaseModel):
    name: str
    mobile: str

class ContactUpdate(BaseModel):
    name: Optional[str]
    mobile: Optional[str]

class ContactOut(BaseModel):
    id: str
    name: str
    mobile: str
    owner_id: str