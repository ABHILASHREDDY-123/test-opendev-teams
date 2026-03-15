from fastapi.testclient import TestClient
from backend.main import app
import pytest
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

# Define the Pydantic models
class User(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

client = TestClient(app)

# Define the password context
pwd_context = CryptContext(schemes=['bcrypt'], default='bcrypt')

# Define the secret key for JWT
secret_key = 'your_secret_key'

# Test the register endpoint
def test_register_success():
    user = User(email='test@example.com', password='password123')
    response = client.post('/auth/register', json=user.dict())
    assert response.status_code == 200
    assert response.json()['message'] == 'User created successfully'

# Test the register endpoint with duplicate email
def test_register_duplicate_email():
    user = User(email='test@example.com', password='password123')
    client.post('/auth/register', json=user.dict())
    response = client.post('/auth/register', json=user.dict())
    assert response.status_code == 400
    assert response.json()['detail'] == 'Email already in use'

# Test the login endpoint with valid credentials
def test_login_success():
    user = User(email='test@example.com', password='password123')
    client.post('/auth/register', json=user.dict())
    response = client.post('/auth/login', json=user.dict())
    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert 'token_type' in response.json()

# Test the login endpoint with invalid credentials
def test_login_invalid_credentials():
    user = User(email='test@example.com', password='wrongpassword')
    client.post('/auth/register', json=User(email='test@example.com', password='password123').dict())
    response = client.post('/auth/login', json=user.dict())
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid email or password'
