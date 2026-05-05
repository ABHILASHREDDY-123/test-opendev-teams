"""Integration tests for Auth Service."""

import pytest
import httpx

AUTH_SERVICE_URL = "http://localhost:8001"


@pytest.mark.usefixtures("start_services")
class TestAuthService:
    """Auth Service integration tests."""

    def test_health_check(self, http_client):
        """Test auth service health check."""
        response = http_client.get(f"{AUTH_SERVICE_URL}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_register_user(self, http_client):
        """Test user registration."""
        payload = {
            "email": "newuser@example.com",
            "password": "SecurePassword123",
            "name": "New User"
        }

        response = http_client.post(f"{AUTH_SERVICE_URL}/auth/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "id" in data
        assert data["role"] == "customer"

    def test_register_duplicate_email(self, http_client):
        """Test that duplicate email registration fails."""
        payload = {
            "email": "duplicate@example.com",
            "password": "SecurePassword123",
            "name": "User 1"
        }

        # First registration should succeed
        response = http_client.post(f"{AUTH_SERVICE_URL}/auth/register", json=payload)
        assert response.status_code == 201

        # Second registration with same email should fail
        response = http_client.post(f"{AUTH_SERVICE_URL}/auth/register", json=payload)
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, http_client):
        """Test registration with invalid email."""
        payload = {
            "email": "invalid-email",
            "password": "SecurePassword123",
            "name": "User"
        }

        response = http_client.post(f"{AUTH_SERVICE_URL}/auth/register", json=payload)
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    def test_register_short_password(self, http_client):
        """Test registration with password too short."""
        payload = {
            "email": "user@example.com",
            "password": "short",
            "name": "User"
        }

        response = http_client.post(f"{AUTH_SERVICE_URL}/auth/register", json=payload)
        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()

    def test_login_success(self, http_client):
        """Test successful login."""
        # Register user
        register_payload = {
            "email": "logintest@example.com",
            "password": "SecurePassword123",
            "name": "Login Test User"
        }
        http_client.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_payload)

        # Login
        login_payload = {
            "email": "logintest@example.com",
            "password": "SecurePassword123"
        }
        response = http_client.post(f"{AUTH_SERVICE_URL}/auth/login", json=login_payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_password(self, http_client):
        """Test login with invalid password."""
        # Register user
        register_payload = {
            "email": "wrongpass@example.com",
            "password": "SecurePassword123",
            "name": "User"
        }
        http_client.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_payload)

        # Try login with wrong password
        login_payload = {
            "email": "wrongpass@example.com",
            "password": "WrongPassword"
        }
        response = http_client.post(f"{AUTH_SERVICE_URL}/auth/login", json=login_payload)
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, http_client):
        """Test login with non-existent user."""
        login_payload = {
            "email": "nonexistent@example.com",
            "password": "SomePassword"
        }
        response = http_client.post(f"{AUTH_SERVICE_URL}/auth/login", json=login_payload)
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_get_user_profile(self, http_client, test_token):
        """Test getting current user profile."""
        response = http_client.get(
            f"{AUTH_SERVICE_URL}/auth/me",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["role"] == "customer"

    def test_get_user_profile_no_token(self, http_client):
        """Test getting user profile without token."""
        response = http_client.get(f"{AUTH_SERVICE_URL}/auth/me")
        assert response.status_code == 401

    def test_get_user_profile_invalid_token(self, http_client):
        """Test getting user profile with invalid token."""
        response = http_client.get(
            f"{AUTH_SERVICE_URL}/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
