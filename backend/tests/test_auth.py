from fastapi.testclient import TestClient
from backend.auth import app
from pydantic import BaseModel
import pytest

class User(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

client = TestClient(app)

def test_register():
    user = User(email='test@example.com', password='password123')
    response = client.post('/auth/register', json=user.dict())
    assert response.status_code == 200
    assert response.json()['message'] == 'User created successfully'

def test_login():
    user = User(email='test@example.com', password='password123')
    response = client.post('/auth/login', json=user.dict())
    assert response.status_code == 200
    assert response.json()['token_type'] == 'bearer'
