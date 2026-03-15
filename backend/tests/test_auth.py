from fastapi.testclient import TestClient
from backend.auth import app
import pytest
from pydantic import BaseModel
from python_jose import jwt

class User(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

token_key = 'secret'

client = TestClient(app)

def test_register_happy_path():
    response = client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
    assert response.status_code == 200
    assert response.json()['message'] == 'User created successfully'

def test_register_duplicate_email():
    client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
    response = client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
    assert response.status_code == 400
    assert response.json()['detail'] == 'Email already registered'

def test_login_happy_path():
    client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
    response = client.post('/auth/login', json={'email': 'test@example.com', 'password': 'password123'})
    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert 'token_type' in response.json()

def test_login_wrong_password():
    client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
    response = client.post('/auth/login', json={'email': 'test@example.com', 'password': 'wrongpassword'})
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid email or password'

def test_login_invalid_email():
    response = client.post('/auth/login', json={'email': 'invalid@example.com', 'password': 'password123'})
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid email or password'
