from pydantic import BaseModel, constr
from typing import Optional

class UserRegister(BaseModel):
    mobile: constr(min_length=10, max_length=15)
    password: constr(min_length=6)

class UserLogin(BaseModel):
    mobile: constr(min_length=10, max_length=15)
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