from fastapi.testclient import TestClient
from backend.auth import app
import pytest

client = TestClient(app)

@pytest.mark.parametrize('email, password, expected_status', [
 ('user@example.com', 'password123', 200),
 ('user@example.com', 'wrongpassword', 401),
 ('invalidemail', 'password123', 400),
])
def test_login(email, password, expected_status):
 response = client.post('/auth/login', json={'email': email, 'password': password})
 assert response.status_code == expected_status

def test_register):
 response = client.post('/auth/register', json={'email': 'user@example.com', 'password': 'password123'})
 assert response.status_code == 200