from fastapi.testclient import TestClient
from backend.auth import app
import pytest
from pydantic import BaseModel
from passlib.context import CryptContext

# OAuth2 schema
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

# User model
class User(BaseModel):
    email: str
    hashed_password: str

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

class TestAuth:
    def test_register_user(self):
        client = TestClient(app)
        response = client.post("/auth/register", json={"email": "user@example.com", "hashed_password": "password"})
        assert response.status_code == 200
        assert response.json()["message"] == "User created successfully"

    def test_register_duplicate_user(self):
        client = TestClient(app)
        client.post("/auth/register", json={"email": "user@example.com", "hashed_password": "password"})
        response = client.post("/auth/register", json={"email": "user@example.com", "hashed_password": "password"})
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

    def test_login_user(self):
        client = TestClient(app)
        client.post("/auth/register", json={"email": "user@example.com", "hashed_password": "password"})
        response = client.post("/auth/login", data={"username": "user@example.com", "password": "password"})
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "token_type" in response.json()

    def test_login_wrong_password(self):
        client = TestClient(app)
        client.post("/auth/register", json={"email": "user@example.com", "hashed_password": "password"})
        response = client.post("/auth/login", data={"username": "user@example.com", "password": "wrongpassword"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_login_invalid_email(self):
        client = TestClient(app)
        response = client.post("/auth/login", data={"username": "invalid@example.com", "password": "password"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"