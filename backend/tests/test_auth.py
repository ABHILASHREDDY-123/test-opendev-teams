from fastapi.testclient import TestClient
from backend.auth import app
from pydantic import BaseModel
import pytest

# OAuth2 schema
class Token(BaseModel):
    access_token: str
    token_type: str

# User schema
class User(BaseModel):
    email: str
    hashed_password: str

client = TestClient(app)

def test_register_new_user):
    response = client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
    assert response.status_code == 200
    assert response.json()['message'] == 'User created successfully'

def test_register_duplicate_user):
    client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
    response = client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
    assert response.status_code == 400
    assert response.json()['detail'] == 'Email already registered'

def test_login_success):
    client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
    response = client.post('/auth/login', data={'username': 'test@example.com', 'password': 'password123'})
    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert 'token_type' in response.json()

def test_login_wrong_password):
    client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
    response = client.post('/auth/login', data={'username': 'test@example.com', 'password': 'wrongpassword'})
    assert response.status_code == 400
    assert response.json()['detail'] == 'Invalid email or password'
