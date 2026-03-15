from fastapi.testclient import TestClient
from backend.main import app
import pytest

client = TestClient(app)

def register_and_login():
 register_response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 assert register_response.status_code == 200
 login_response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 assert login_response.status_code == 200
 return login_response.json()['access_token']

def test_register_success():
 response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 assert response.status_code == 200
 assert 'id' in response.json()
 assert 'mobile' in response.json()

def test_register_duplicate_mobile():
 client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 assert response.status_code == 409

def test_login_success():
 register_and_login()
 response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 assert response.status_code == 200
 assert 'access_token' in response.json()

def test_login_wrong_password():
 register_and_login()
 response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'wrongpassword'})
 assert response.status_code == 401

def test_login_unknown_mobile():
 response = client.post('/auth/login', json={'mobile': 'unknownmobile', 'password': 'password123'})
 assert response.status_code == 401