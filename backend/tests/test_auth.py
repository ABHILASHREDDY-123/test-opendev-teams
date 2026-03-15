from fastapi.testclient import TestClient
from backend.auth import app
from pydantic import BaseModel
import pytest

client = TestClient(app)

# Test register user
def test_register_user():
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "test_password"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"

# Test login user
def test_login_user():
    # Register user
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "test_password"},
    )
    # Login user
    response = client.post(
        "/auth/login",
        data={"grant_type": "password", "username": "test@example.com", "password": "test_password"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

# Test duplicate email
def test_duplicate_email():
    # Register user
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "test_password"},
    )
    # Try to register again with same email
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "test_password"},
    )
    assert response.status_code == 400

# Test wrong password
def test_wrong_password():
    # Register user
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "test_password"},
    )
    # Try to login with wrong password
    response = client.post(
        "/auth/login",
        data={"grant_type": "password", "username": "test@example.com", "password": "wrong_password"},
    )
    assert response.status_code == 400
