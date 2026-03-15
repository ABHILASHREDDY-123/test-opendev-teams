from pydantic import BaseModel, Field
from typing import Optional
import uuid

class UserRegister(BaseModel):
    mobile: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    password: str

class UserLogin(BaseModel):
    mobile: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    password: str

class UserOut(BaseModel):
    id: str
    mobile: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class ContactCreate(BaseModel):
    name: str
    mobile: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')

class ContactOut(BaseModel):
    id: str
    name: str
    mobile: str
    owner_id: str