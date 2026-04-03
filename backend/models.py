from pydantic import BaseModel, validator
from typing import Optional

class UserRegister(BaseModel):
    mobile: str
    password: str

    @validator('mobile')
    def mobile_must_be_10_digits(cls, v):
        if len(v) != 10 or not v.isdigit():
            raise ValueError('Mobile number must be 10 digits')
        return v

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
