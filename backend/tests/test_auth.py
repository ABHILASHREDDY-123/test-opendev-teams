from fastapi.testclient import TestClient
from backend.auth import app
from backend.auth import User, Token
import pytest

client = TestClient(app)

# Test registration happy path
def test_register_happy_path():
    user = User(email='test@example.com', password='password123')
    response = client.post('/auth/register', json=user.dict())
    assert response.status_code == 200
    assert response.json()['message'] == 'User created successfully'

# Test registration with duplicate email
def test_register_duplicate_email():
    user = User(email='test@example.com', password='password123')
    client.post('/auth/register', json=user.dict())
    response = client.post('/auth/register', json=user.dict())
    assert response.status_code == 400
    assert response.json()['detail'] == 'Email already registered'

# Test login happy path
def test_login_happy_path():
    user = User(email='test@example.com', password='password123')
    client.post('/auth/register', json=user.dict())
    response = client.post('/auth/login', json=user.dict())
    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert 'token_type' in response.json()

# Test login with wrong password
def test_login_wrong_password():
    user = User(email='test@example.com', password='password123')
    client.post('/auth/register', json=user.dict())
    user_wrong_password = User(email='test@example.com', password='wrongpassword')
    response = client.post('/auth/login', json=user_wrong_password.dict())
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid email or password'

# Test login with invalid email format
def test_login_invalid_email_format():
    user = User(email='invalid_email', password='password123')
    response = client.post('/auth/login', json=user.dict())
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid email or password'

# Test login with missing fields
def test_login_missing_fields():
    user = User(email='test@example.com', password='password123')
    client.post('/auth/register', json=user.dict())
    response = client.post('/auth/login', json={})
    assert response.status_code == 422
