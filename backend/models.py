from pydantic import BaseModel, ConfigDict
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
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class ContactCreate(BaseModel):
    name: str
    mobile: str

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None

class ContactOut(BaseModel):
    id: str
    name: str
    mobile: str
    owner_id: str
    model_config = ConfigDict(from_attributes=True)