from fastapi.testclient import TestClient
from main import app
import pytest
from pydantic import BaseModel
from python_jose import jwt

client = TestClient(app)

class User(BaseModel):
    email: str
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def test_register_success():
    # Test successful registration
    response = client.post("/auth/register", json={"email": "user@example.com", "hashed_password": "password"})
    assert response.status_code == 200

def test_register_duplicate_email():
    # Test registration with duplicate email
    response = client.post("/auth/register", json={"email": "user@example.com", "hashed_password": "password"})
    response = client.post("/auth/register", json={"email": "user@example.com", "hashed_password": "password"})
    assert response.status_code == 400

def test_login_success():
    # Test successful login
    response = client.post("/auth/login", data={"grant_type": "password", "username": "user@example.com", "password": "password"})
    assert response.status_code == 200

def test_login_wrong_password():
    # Test login with wrong password
    response = client.post("/auth/login", data={"grant_type": "password", "username": "user@example.com", "password": "wrong_password"})
    assert response.status_code == 401