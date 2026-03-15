from fastapi.testclient import TestClient
from backend.auth import app
from pydantic import BaseModel
import pytest

class User(BaseModel):
    email: str
    password: str

class TestAuth:
    def test_register(self):
        client = TestClient(app)
        user = User(email='test@example.com', password='password123')
        response = client.post('/auth/register', json=user.dict())
        assert response.status_code == 200
        assert response.json()['message'] == 'User created successfully'

    def test_login(self):
        client = TestClient(app)
        user = User(email='test@example.com', password='password123')
        client.post('/auth/register', json=user.dict())
        response = client.post('/auth/login', json=user.dict())
        assert response.status_code == 200
        assert 'access_token' in response.json()
        assert 'token_type' in response.json()

    def test_duplicate_email(self):
        client = TestClient(app)
        user = User(email='test@example.com', password='password123')
        client.post('/auth/register', json=user.dict())
        response = client.post('/auth/register', json=user.dict())
        assert response.status_code == 400
        assert response.json()['detail'] == 'Email already registered'

    def test_wrong_password(self):
        client = TestClient(app)
        user = User(email='test@example.com', password='password123')
        client.post('/auth/register', json=user.dict())
        user_wrong_password = User(email='test@example.com', password='wrongpassword')
        response = client.post('/auth/login', json=user_wrong_password.dict())
        assert response.status_code == 401
        assert response.json()['detail'] == 'Invalid email or password'
