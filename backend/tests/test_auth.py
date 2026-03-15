from fastapi.testclient import TestClient
from main import app
from models import UserRegister, UserLogin
import pytest

client = TestClient(app)

def test_register_success):
 response = client.post(
 "/auth/register",
 json={"username": "testuser", "password": "testpassword"},
 )
 assert response.status_code == 200
 assert response.json()["message"] == "User created successfully"

def test_register_duplicate):
 client.post(
 "/auth/register",
 json={"username": "testuser", "password": "testpassword"},
 )
 response = client.post(
 "/auth/register",
 json={"username": "testuser", "password": "testpassword"},
 )
 assert response.status_code == 400
 assert response.json()["detail"] == "Username already exists"

def test_login_success):
 client.post(
 "/auth/register",
 json={"username": "testuser", "password": "testpassword"},
 )
 response = client.post(
 "/auth/login",
 json={"username": "testuser", "password": "testpassword"},
 )
 assert response.status_code == 200
 assert "access_token" in response.json()

def test_login_wrong_password):
 client.post(
 "/auth/register",
 json={"username": "testuser", "password": "testpassword"},
 )
 response = client.post(
 "/auth/login",
 json={"username": "testuser", "password": "wrongpassword"},
 )
 assert response.status_code == 401
 assert response.json()["detail"] == "Incorrect username or password"
