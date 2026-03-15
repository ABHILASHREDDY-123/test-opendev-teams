from pydantic import BaseModel
from typing import Optional

class UserRegister(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str
    email: str
    full_name: str
    class Config:
        orm_mode = True

class ContactCreate(BaseModel):
    name: str
    mobile: str

class ContactOut(BaseModel):
    id: int
    name: str
    mobile: str
    owner_id: int
    class Config:
        orm_mode = True
