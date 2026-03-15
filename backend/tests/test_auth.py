from fastapi.testclient import TestClient
from backend.auth import app
from backend.models import User, Token
import jwt

client = TestClient(app)

def test_register_user():
 response = client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password'})
 assert response.status_code == 200
 assert response.json()['message'] == 'User created successfully'

def test_register_duplicate_user():
 client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password'})
 response = client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password'})
 assert response.status_code == 400
 assert response.json()['detail'] == 'Email already exists'

def test_login_user():
 client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password'})
 response = client.post('/auth/login', json={'email': 'test@example.com', 'password': 'password'})
 assert response.status_code == 200
 assert 'access_token' in response.json()
 assert 'token_type' in response.json()

def test_login_invalid_credentials():
 client.post('/auth/register', json={'email': 'test@example.com', 'password': 'password'})
 response = client.post('/auth/login', json={'email': 'test@example.com', 'password': 'wrong_password'})
 assert response.status_code == 401
 assert response.json()['detail'] == 'Invalid email or password'

def test_login_invalid_email():
 response = client.post('/auth/login', json={'email': 'invalid@example.com', 'password': 'password'})
 assert response.status_code == 401
 assert response.json()['detail'] == 'Invalid email or password'
