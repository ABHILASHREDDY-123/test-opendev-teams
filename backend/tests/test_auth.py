from fastapi.testclient import TestClient
from backend.auth import app
from pydantic import BaseModel
import pytest

# Define the user model
class User(BaseModel):
    email: str
    password: str

# Create a test client
client = TestClient(app)

# Test the registration endpoint
def test_register():
    user = User(email='test@example.com', password='password123')
    response = client.post('/auth/register', json=user.dict())
    assert response.status_code == 200
    assert response.json()['message'] == 'User created successfully'

# Test the login endpoint
def test_login():
    user = User(email='test@example.com', password='password123')
    response = client.post('/auth/login', json=user.dict())
    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert 'token_type' in response.json()

# Test the registration endpoint with duplicate email
def test_register_duplicate_email():
    user = User(email='test@example.com', password='password123')
    client.post('/auth/register', json=user.dict())
    response = client.post('/auth/register', json=user.dict())
    assert response.status_code == 400
    assert response.json()['detail'] == 'Email already exists'

# Test the login endpoint with wrong password
def test_login_wrong_password():
    user = User(email='test@example.com', password='wrongpassword')
    response = client.post('/auth/login', json=user.dict())
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid email or password'
