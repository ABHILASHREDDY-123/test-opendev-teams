from fastapi.testclient import TestClient
from backend.auth import app
from pydantic import BaseModel
import pytest

# Define the user model
class User(BaseModel):
    email: str
    password: str

class TestAuth:
    def test_register(self):
        # Create a test client
        client = TestClient(app)
        # Define a test user
        user = {'email': 'test@example.com', 'password': 'password123'}
        # Send a registration request
        response = client.post('/auth/register', json=user)
        # Assert that the response is successful
        assert response.status_code == 200
        # Assert that the response contains the expected message
        assert response.json()['message'] == 'User created successfully'

    def test_login(self):
        # Create a test client
        client = TestClient(app)
        # Define a test user
        user = {'email': 'test@example.com', 'password': 'password123'}
        # Send a registration request
        client.post('/auth/register', json=user)
        # Send a login request
        response = client.post('/auth/login', json=user)
        # Assert that the response is successful
        assert response.status_code == 200
        # Assert that the response contains the expected token
        assert 'access_token' in response.json()
        assert 'token_type' in response.json()
