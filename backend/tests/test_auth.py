from fastapi.testclient import TestClient
from backend.main import app
from backend.auth import User
import pytest

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

# Test the login endpoint with invalid email format
def test_login_invalid_email_format():
 user = User(email='invalid_email', password='password123')
 response = client.post('/auth/login', json=user.dict())
 assert response.status_code == 401
 assert response.json()['detail'] == 'Invalid email or password'

# Test the login endpoint with missing fields
def test_login_missing_fields():
 user = User(email='test@example.com')
 response = client.post('/auth/login', json=user.dict())
 assert response.status_code == 422
 assert 'password' in response.json()['detail']