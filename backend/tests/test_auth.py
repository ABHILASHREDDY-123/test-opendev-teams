from fastapi.testclient import TestClient
from backend.auth import app
from backend.models import User
import pytest

client = TestClient(app)

@pytest.mark.asyncio
async def test_register_user():
    user = User(email='test@example.com', password='password123')
    response = client.post('/auth/register', json=user.dict())
    assert response.status_code == 200
    assert response.json()['message'] == 'User created successfully'

@pytest.mark.asyncio
async def test_register_duplicate_user():
    user = User(email='test@example.com', password='password123')
    client.post('/auth/register', json=user.dict())
    response = client.post('/auth/register', json=user.dict())
    assert response.status_code == 400
    assert response.json()['detail'] == 'Email already registered'

@pytest.mark.asyncio
async def test_login_user():
    user = User(email='test@example.com', password='password123')
    client.post('/auth/register', json=user.dict())
    response = client.post('/auth/login', json=user.dict())
    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert 'token_type' in response.json()

@pytest.mark.asyncio
async def test_login_invalid_credentials():
    user = User(email='test@example.com', password='wrongpassword')
    client.post('/auth/register', json=User(email='test@example.com', password='password123').dict())
    response = client.post('/auth/login', json=user.dict())
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid email or password'

@pytest.mark.asyncio
async def test_login_invalid_email():
    user = User(email='invalid@example.com', password='password123')
    response = client.post('/auth/login', json=user.dict())
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid email or password'
