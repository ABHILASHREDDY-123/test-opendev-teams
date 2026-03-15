from fastapi.testclient import TestClient
from backend.auth import app
import pytest

client = TestClient(app)

@pytest.mark.parametrize("email, password", [("user@example.com", "password123")])
def test_register_success(email, password):
    response = client.post("/auth/register", json={"email": email, "password": password})
    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"

def test_register_duplicate_email):
    response = client.post("/auth/register", json={"email": "user@example.com", "password": "password123"})
    assert response.status_code == 400
    assert response.json()["message"] == "Email already exists"

def test_login_success():
    response = client.post("/auth/login", json={"email": "user@example.com", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["message"] == "User logged in successfully"

def test_login_wrong_password():
    response = client.post("/auth/login", json={"email": "user@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["message"] == "Invalid password"
