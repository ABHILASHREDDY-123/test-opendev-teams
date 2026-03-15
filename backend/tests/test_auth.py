from fastapi.testclient import TestClient
from backend.main import app
from backend.models import UserRegister, UserLogin, TokenResponse
import pytest

client = TestClient(app)

def test_register_success):
 response = client.post("/auth/register", json={"mobile": "1234567890", "password": "password123"})
 assert response.status_code == 201
 assert response.json()["mobile"] == "1234567890"

def test_register_duplicate_mobile():
 client.post("/auth/register", json={"mobile": "1234567890", "password": "password123"})
 response = client.post("/auth/register", json={"mobile": "1234567890", "password": "password123"})
 assert response.status_code == 409

def test_login_success():
 client.post("/auth/register", json={"mobile": "1234567890", "password": "password123"})
 response = client.post("/auth/login", json={"mobile": "1234567890", "password": "password123"})
 assert response.status_code == 200
 assert "access_token" in response.json()

def test_login_wrong_password():
 client.post("/auth/register", json={"mobile": "1234567890", "password": "password123"})
 response = client.post("/auth/login", json={"mobile": "1234567890", "password": "wrongpassword"})
 assert response.status_code == 401

def test_login_unknown_mobile():
 response = client.post("/auth/login", json={"mobile": "1234567890", "password": "password123"})
 assert response.status_code == 401