from fastapi.testclient import TestClient
from backend.auth import app
from backend.models import User, Token
import pytest

client = TestClient(app)

def test_register_user():
 response = client.post('/auth/register', json={'email': 'test@example.com', 'hashed_password': 'password123'})
 assert response.status_code == 200
 assert response.json()['message'] == 'User created successfully'

def test_login_user():
 response = client.post('/auth/login', data={'username': 'test@example.com', 'password': 'password123'})
 assert response.status_code == 200
 assert response.json()['token_type'] == 'bearer'

def test_register_duplicate_user():
 client.post('/auth/register', json={'email': 'test@example.com', 'hashed_password': 'password123'})
 response = client.post('/auth/register', json={'email': 'test@example.com', 'hashed_password': 'password123'})
 assert response.status_code == 400
 assert response.json()['detail'] == 'Email already registered'

def test_login_wrong_password():
 response = client.post('/auth/login', data={'username': 'test@example.com', 'password': 'wrongpassword'})
 assert response.status_code == 401
 assert response.json()['detail'] == 'Incorrect username or password'
