from fastapi.testclient import TestClient
from main import app
from auth import hash_password, verify_password, create_access_token
from models import UserRegister, UserLogin, TokenResponse
import pytest

client = TestClient(app)

def test_register_success):
 user_data = {'username': 'test_user', 'email': 'test@example.com', 'full_name': 'Test User', 'password': 'test_password'}
 response = client.post('/register', json=user_data)
 assert response.status_code == 200
 assert response.json()['username'] == user_data['username']

def test_register_duplicate_username):
 user_data = {'username': 'test_user', 'email': 'test@example.com', 'full_name': 'Test User', 'password': 'test_password'}
 client.post('/register', json=user_data)
 response = client.post('/register', json=user_data)
 assert response.status_code == 400
 assert response.json()['detail'] == 'Username already exists'

def test_login_success):
 user_data = {'username': 'test_user', 'email': 'test@example.com', 'full_name': 'Test User', 'password': 'test_password'}
 client.post('/register', json=user_data)
 login_data = {'username': user_data['username'], 'password': user_data['password']}
 response = client.post('/login', data=login_data)
 assert response.status_code == 200
 assert 'access_token' in response.json()

def test_login_wrong_password):
 user_data = {'username': 'test_user', 'email': 'test@example.com', 'full_name': 'Test User', 'password': 'test_password'}
 client.post('/register', json=user_data)
 login_data = {'username': user_data['username'], 'password': 'wrong_password'}
 response = client.post('/login', data=login_data)
 assert response.status_code == 401
 assert response.json()['detail'] == 'Invalid username or password'
