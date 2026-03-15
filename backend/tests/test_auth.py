from fastapi.testclient import TestClient
from main import app
from auth import pwd_context, users
import pytest

client = TestClient(app)

@pytest.fixture
def client():
 return client

def test_register(client):
 response = client.post('/auth/register', json={'email': 'test@example.com', 'hashed_password': pwd_context.hash('password')})
 assert response.status_code == 200
 assert response.json()['message'] == 'User created successfully'

def test_register_duplicate_email(client):
 client.post('/auth/register', json={'email': 'test@example.com', 'hashed_password': pwd_context.hash('password')})
 response = client.post('/auth/register', json={'email': 'test@example.com', 'hashed_password': pwd_context.hash('password')})
 assert response.status_code == 400
 assert response.json()['detail'] == 'Email already registered'

def test_login(client):
 client.post('/auth/register', json={'email': 'test@example.com', 'hashed_password': pwd_context.hash('password')})
 response = client.post('/auth/login', json={'email': 'test@example.com', 'password': 'password'})
 assert response.status_code == 200
 assert 'access_token' in response.json()
 assert 'token_type' in response.json()

def test_login_wrong_password(client):
 client.post('/auth/register', json={'email': 'test@example.com', 'hashed_password': pwd_context.hash('password')})
 response = client.post('/auth/login', json={'email': 'test@example.com', 'password': 'wrong_password'})
 assert response.status_code == 401
 assert response.json()['detail'] == 'Invalid email or password'

def test_login_invalid_email(client):
 response = client.post('/auth/login', json={'email': 'invalid@example.com', 'password': 'password'})
 assert response.status_code == 401
 assert response.json()['detail'] == 'Invalid email or password'
