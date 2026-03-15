from pydantic import BaseModel
from datetime import datetime

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class ContactCreate(BaseModel):
    name: str
    email: str

class ContactUpdate(BaseModel):
    name: str | None
    email: str | None

class ContactOut(BaseModel):
    id: int
    name: str
    email: str
    owner: str