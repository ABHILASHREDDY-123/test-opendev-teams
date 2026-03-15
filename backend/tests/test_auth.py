from fastapi.testclient import TestClient
from backend.auth import app
import pytest

client = TestClient(app)

def test_register_valid_user():
 response = client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
 assert response.status_code == 200
 assert response.json()['message'] == 'User created successfully'

def test_register_duplicate_email():
 client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
 response = client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
 assert response.status_code == 400
 assert response.json()['detail'] == 'Email already registered'

def test_login_valid_credentials():
 client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
 response = client.post('/auth/login', json={'email': 'test@example.com', 'password': 'password123'})
 assert response.status_code == 200
 assert 'access_token' in response.json()
 assert response.json()['token_type'] == 'bearer'

def test_login_invalid_credentials():
 client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
 response = client.post('/auth/login', json={'email': 'test@example.com', 'password': 'wrongpassword'})
 assert response.status_code == 401
 assert response.json()['detail'] == 'Invalid email or password'
