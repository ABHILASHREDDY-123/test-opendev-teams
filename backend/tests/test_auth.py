from fastapi.testclient import TestClient
from main import app
from auth import Auth
import pytest

client = TestClient(app)
auth = Auth(
 secret_key="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
 algorithm="HS256",
 access_token_expire_minutes=30
)

def test_register_success():
 response = client.post(
 "/register",
 json={"username": "testuser", "password": "testpassword"}
 )
 assert response.status_code == 200
 assert response.json()["message"] == "User created successfully"

def test_register_duplicate():
 client.post(
 "/register",
 json={"username": "testuser", "password": "testpassword"}
 )
 response = client.post(
 "/register",
 json={"username": "testuser", "password": "testpassword"}
 )
 assert response.status_code == 400
 assert response.json()["detail"] == "Username already registered"

def test_login_success():
 client.post(
 "/register",
 json={"username": "testuser", "password": "testpassword"}
 )
 response = client.post(
 "/login",
 data={"grant_type": "password", "username": "testuser", "password": "testpassword"}
 )
 assert response.status_code == 200
 assert "access_token" in response.json()

def test_login_wrong_password():
 client.post(
 "/register",
 json={"username": "testuser", "password": "testpassword"}
 )
 response = client.post(
 "/login",
 data={"grant_type": "password", "username": "testuser", "password": "wrongpassword"}
 )
 assert response.status_code == 401
 assert response.json()["detail"] == "Incorrect username or password"
