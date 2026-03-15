from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    email: str
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
