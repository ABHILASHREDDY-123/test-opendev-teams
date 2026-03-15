from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_register_success):
 response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 assert response.status_code == 200
 assert 'id' in response.json()
 assert 'mobile' in response.json()

def test_register_duplicate_mobile():
 client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 assert response.status_code == 400
 assert response.json()['detail'] == 'Mobile number already registered'

def test_login_success():
 client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 response = client.post('/auth/login', data={'grant_type': 'password', 'username': '1234567890', 'password': 'password'})
 assert response.status_code == 200
 assert 'access_token' in response.json()

def test_login_wrong_password():
 client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 response = client.post('/auth/login', data={'grant_type': 'password', 'username': '1234567890', 'password': 'wrong_password'})
 assert response.status_code == 400
 assert response.json()['detail'] == 'Incorrect password'

def test_login_unknown_mobile():
 response = client.post('/auth/login', data={'grant_type': 'password', 'username': '1234567890', 'password': 'password'})
 assert response.status_code == 400
 assert response.json()['detail'] == 'Mobile number not registered'

def test_register_missing_fields():
 response = client.post('/auth/register', json={'mobile': '1234567890'})
 assert response.status_code == 422
