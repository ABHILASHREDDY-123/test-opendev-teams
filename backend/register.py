from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bcrypt import hashpw, gensalt
from typing import Optional

app = FastAPI()

class User(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True

# In-memory user store for simplicity
users = {}

@app.post("/auth/register")
async def register(user: User):
    if user.email in users:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hashpw(user.password.encode('utf-8'), gensalt())
    users[user.email] = {
        'username': user.username,
        'email': user.email,
        'hashed_password': hashed_password
    }
    return {'message': 'User created successfully'}