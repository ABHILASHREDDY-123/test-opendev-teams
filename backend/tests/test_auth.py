from fastapi.testclient import TestClient
from main import app
from models import UserRegister, UserLogin
import pytest

client = TestClient(app)

@pytest.mark.asyncio
async def test_register_success():
 response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 assert response.status_code == 200
 assert 'id' in response.json()
 assert 'mobile' in response.json()

@pytest.mark.asyncio
async def test_register_duplicate_mobile():
 client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 assert response.status_code == 409

@pytest.mark.asyncio
async def test_login_success():
 client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 assert response.status_code == 200
 assert 'access_token' in response.json()
 assert 'token_type' in response.json()

@pytest.mark.asyncio
async def test_login_wrong_password():
 client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'wrongpassword'})
 assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_unknown_mobile():
 response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 assert response.status_code == 401