from fastapi.testclient import TestClient
from backend.main import app
from backend.models import UserRegister, UserLogin, TokenResponse
import pytest

client = TestClient(app)

@pytest.mark.parametrize('mobile, password', [('+1234567890', 'password123')])
def test_register_success(mobile, password):
 response = client.post('/auth/register', json={'mobile': mobile, 'password': password})
 assert response.status_code == 200
 assert response.json()['mobile'] == mobile

@pytest.mark.parametrize('mobile, password', [('+1234567890', 'password123')])
def test_register_duplicate_mobile(mobile, password):
 client.post('/auth/register', json={'mobile': mobile, 'password': password})
 response = client.post('/auth/register', json={'mobile': mobile, 'password': password})
 assert response.status_code == 409

@pytest.mark.parametrize('mobile, password', [('+1234567890', 'password123')])
def test_login_success(mobile, password):
 client.post('/auth/register', json={'mobile': mobile, 'password': password})
 response = client.post('/auth/login', json={'mobile': mobile, 'password': password})
 assert response.status_code == 200
 assert 'access_token' in response.json()

@pytest.mark.parametrize('mobile, password', [('+1234567890', 'wrongpassword')])
def test_login_wrong_password(mobile, password):
 client.post('/auth/register', json={'mobile': '+1234567890', 'password': 'password123'})
 response = client.post('/auth/login', json={'mobile': mobile, 'password': password})
 assert response.status_code == 401

@pytest.mark.parametrize('mobile, password', [('+1234567891', 'password123')])
def test_login_unknown_mobile(mobile, password):
 response = client.post('/auth/login', json={'mobile': mobile, 'password': password})
 assert response.status_code == 401