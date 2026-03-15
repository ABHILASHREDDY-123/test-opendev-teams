from fastapi.testclient import TestClient
from backend.register import app
from pydantic import BaseModel
from typing import Optional
import pytest

class User(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True

test_client = TestClient(app)

def test_register_happy_path():
    user = User(username='testuser', email='test@example.com', password='testpassword')
    response = test_client.post('/auth/register', json=user.dict())
    assert response.status_code == 200
    assert response.json()['message'] == 'User created successfully'

def test_register_duplicate_email():
    user = User(username='testuser', email='test@example.com', password='testpassword')
    test_client.post('/auth/register', json=user.dict())
    response = test_client.post('/auth/register', json=user.dict())
    assert response.status_code == 400
    assert response.json()['detail'] == 'Email already registered'
