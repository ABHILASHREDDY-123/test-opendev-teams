from fastapi.testclient import TestClient
from backend.auth import app
import pytest

client = TestClient(app)

@pytest.mark.parametrize('email, password, expected_status', [
 ('test@example.com', 'password', 200),
 ('test@example.com', 'wrongpassword', 401),
 ('invalidemail', 'password', 401),
])
def test_login(email, password, expected_status):
 response = client.post('/auth/login', json={'email': email, 'password': password})
 assert response.status_code == expected_status

@pytest.mark.parametrize('email, password, expected_status', [
 ('test@example.com', 'password', 201),
 ('test@example.com', 'password', 400),
])
def test_register(email, password, expected_status):
 response = client.post('/auth/register', json={'email': email, 'password': password})
 assert response.status_code == expected_status