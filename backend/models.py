from pydantic import BaseModel
from typing import Optional

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str
    class Config:
        orm_mode = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class ContactCreate(BaseModel):
    name: str
    phone: str

class ContactUpdate(BaseModel):
    name: Optional[str]
    phone: Optional[str]

class ContactOut(BaseModel):
    id: int
    name: str
    phone: str
    class Config:
        orm_mode = True
