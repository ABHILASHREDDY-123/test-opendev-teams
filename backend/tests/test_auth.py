from fastapi.testclient import TestClient
from backend.auth import app
import pytest

client = TestClient(app)

# Test the register endpoint
def test_register_user):
 response = client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
 assert response.status_code == 200
 assert response.json()['message'] == 'User created successfully'

# Test the login endpoint
def test_login_user):
 response = client.post('/auth/login', json={'email': 'test@example.com', 'password': 'password123'})
 assert response.status_code == 200
 assert 'access_token' in response.json()
 assert 'token_type' in response.json()

# Test the login endpoint with invalid credentials
def test_login_user_invalid_credentials):
 response = client.post('/auth/login', json={'email': 'test@example.com', 'password': 'wrongpassword'})
 assert response.status_code == 401
 assert response.json()['detail'] == 'Invalid email or password'

# Test the register endpoint with duplicate email
def test_register_user_duplicate_email):
 client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
 response = client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
 assert response.status_code == 400
