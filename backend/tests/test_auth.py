from fastapi.testclient import TestClient
from backend.auth import app
from backend.models import User, Token
import pytest

client = TestClient(app)

def test_register_user():
 user = {'email': 'test@example.com', 'password': 'password123'}
 response = client.post('/auth/register', json=user)
 assert response.status_code == 200
 assert response.json()['message'] == 'User created successfully'

def test_login_user():
 user = {'email': 'test@example.com', 'password': 'password123'}
 response = client.post('/auth/login', json=user)
 assert response.status_code == 200
 assert 'access_token' in response.json()
 assert 'token_type' in response.json()

def test_register_duplicate_user():
 user = {'email': 'test@example.com', 'password': 'password123'}
 client.post('/auth/register', json=user)
 response = client.post('/auth/register', json=user)
 assert response.status_code == 400
 assert response.json()['detail'] == 'Email already exists'

def test_login_invalid_password():
 user = {'email': 'test@example.com', 'password': 'wrongpassword'}
 response = client.post('/auth/login', json=user)
 assert response.status_code == 401
 assert response.json()['detail'] == 'Invalid email or password'

def test_login_invalid_email():
 user = {'email': 'wrongemail@example.com', 'password': 'password123'}
 response = client.post('/auth/login', json=user)
 assert response.status_code == 401
 assert response.json()['detail'] == 'Invalid email or password'

def test_login_missing_fields():
 user = {'email': 'test@example.com'}
 response = client.post('/auth/login', json=user)
 assert response.status_code == 422
