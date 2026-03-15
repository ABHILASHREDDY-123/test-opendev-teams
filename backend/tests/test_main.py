from fastapi.testclient import TestClient
from main import app
import pytest
from pydantic import BaseModel

class User(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

client = TestClient(app)

def test_register_user():
    user = {'email': 'test@example.com', 'password': 'testpassword'}
    response = client.post('/auth/register', json=user)
    assert response.status_code == 200
    assert response.json()['message'] == 'User created successfully'

def test_login_user():
    user = {'email': 'test@example.com', 'password': 'testpassword'}
    response = client.post('/auth/login', json=user)
    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'bearer'

def test_invalid_login():
    user = {'email': 'test@example.com', 'password': 'wrongpassword'}
    response = client.post('/auth/login', json=user)
    assert response.status_code == 200
    assert response.json()['message'] == 'Invalid email or password'

def test_register_duplicate_user():
    user = {'email': 'test@example.com', 'password': 'testpassword'}
    client.post('/auth/register', json=user)
    response = client.post('/auth/register', json=user)
    assert response.status_code == 200
    assert response.json()['message'] == 'User created successfully'
