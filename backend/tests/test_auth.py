import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.auth import SECRET_KEY, ALGORITHM
from jose import jwt

client = TestClient(app)

def test_register_success():
    response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'securepassword'})
    assert response.status_code == 201
    data = response.json()
    assert 'id' in data
    assert data['mobile'] == '1234567890'

def test_register_duplicate_mobile():
    client.post('/auth/register', json={'mobile': '1234567890', 'password': 'securepassword'})
    response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'differentpassword'})
    assert response.status_code == 409

def test_login_success():
    client.post('/auth/register', json={'mobile': '1234567890', 'password': 'securepassword'})
    response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'securepassword'})
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'

def test_login_wrong_password():
    client.post('/auth/register', json={'mobile': '1234567890', 'password': 'securepassword'})
    response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'wrongpassword'})
    assert response.status_code == 401

def test_login_unknown_mobile():
    response = client.post('/auth/login', json={'mobile': '9999999999', 'password': 'anypassword'})
    assert response.status_code == 401

def test_register_missing_fields():
    response = client.post('/auth/register', json={'mobile': '1234567890'})  # Missing password
    assert response.status_code == 422