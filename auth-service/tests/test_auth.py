import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from jose import jwt
import sys
import os

# Add parent directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, users_db, JWT_SECRET, JWT_ALGORITHM, hash_password

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_users_db():
    """Clear users database before each test"""
    users_db.clear()
    yield
    users_db.clear()


class TestRegistration:
    """Test user registration endpoint"""

    def test_valid_registration(self):
        """Test successful user registration"""
        response = client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
                "name": "Test User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "user@example.com"
        assert data["name"] == "Test User"
        assert "user_id" in data
        assert "created_at" in data
        assert data["role"] == "customer"

    def test_invalid_email_format(self):
        """Test registration with invalid email format"""
        response = client.post(
            "/auth/register",
            json={
                "email": "invalid-email",
                "password": "password123",
                "name": "Test User",
            },
        )
        assert response.status_code == 422

    def test_password_too_short(self):
        """Test registration with password less than 8 characters"""
        response = client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "short",
                "name": "Test User",
            },
        )
        assert response.status_code == 422

    def test_empty_name(self):
        """Test registration with empty name"""
        response = client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
                "name": "",
            },
        )
        assert response.status_code == 422

    def test_duplicate_email(self):
        """Test registration with duplicate email"""
        # First registration
        response1 = client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
                "name": "Test User",
            },
        )
        assert response1.status_code == 201

        # Second registration with same email
        response2 = client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "password456",
                "name": "Another User",
            },
        )
        assert response2.status_code == 409
        assert "already registered" in response2.json()["detail"].lower()

    def test_duplicate_email_case_insensitive(self):
        """Test that email uniqueness is case-insensitive"""
        # First registration
        client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
                "name": "Test User",
            },
        )

        # Second registration with different case
        response = client.post(
            "/auth/register",
            json={
                "email": "USER@EXAMPLE.COM",
                "password": "password456",
                "name": "Another User",
            },
        )
        assert response.status_code == 409


class TestLogin:
    """Test user login endpoint"""

    @pytest.fixture
    def registered_user(self):
        """Create a registered user for testing"""
        response = client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
                "name": "Test User",
            },
        )
        return response.json()

    def test_valid_login(self, registered_user):
        """Test successful login"""
        response = client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["expires_in"] > 0

    def test_invalid_email(self, registered_user):
        """Test login with non-existent email"""
        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_invalid_password(self, registered_user):
        """Test login with incorrect password"""
        response = client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_user_not_found(self):
        """Test login when user doesn't exist"""
        response = client.post(
            "/auth/login",
            json={
                "email": "notfound@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 401

    def test_jwt_token_structure(self, registered_user):
        """Test that JWT token has correct structure and payload"""
        response = client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        token = response.json()["access_token"]

        # Decode token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["sub"] == registered_user["user_id"]
        assert payload["email"] == "user@example.com"
        assert payload["role"] == "customer"
        assert "exp" in payload

    def test_token_expiration_24_hours(self, registered_user):
        """Test that token expires in 24 hours"""
        response = client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        expires_in = response.json()["expires_in"]

        # Verify expiration is approximately 24 hours (within 5 minutes tolerance)
        assert 85900 < expires_in <= 86400  # 23:55 to 24:00 hours in seconds

        # Decode and verify exp claim
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        now = datetime.utcnow().timestamp()
        exp_time = payload["exp"]
        
        # Should be approximately 24 hours from now
        time_diff = exp_time - now
        assert 85900 < time_diff <= 86400


class TestProfile:
    """Test user profile endpoint"""

    @pytest.fixture
    def registered_user_with_token(self):
        """Create a registered user and get token"""
        reg_response = client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
                "name": "Test User",
            },
        )
        user = reg_response.json()

        login_response = client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )
        token = login_response.json()["access_token"]
        return user, token

    def test_valid_token(self, registered_user_with_token):
        """Test getting profile with valid token"""
        user, token = registered_user_with_token
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user["user_id"]
        assert data["email"] == user["email"]
        assert data["name"] == user["name"]
        assert data["role"] == "customer"

    def test_missing_token(self):
        """Test getting profile without token"""
        response = client.get("/auth/me")
        assert response.status_code == 403

    def test_invalid_token(self):
        """Test getting profile with invalid token"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    def test_expired_token(self, registered_user_with_token):
        """Test getting profile with expired token"""
        user, _ = registered_user_with_token
        
        # Create an expired token
        expired_payload = {
            "sub": user["user_id"],
            "email": user["email"],
            "role": "customer",
            "exp": int((datetime.utcnow() - timedelta(hours=1)).timestamp()),
        }
        expired_token = jwt.encode(
            expired_payload, JWT_SECRET, algorithm=JWT_ALGORITHM
        )

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    def test_user_not_found_in_store(self, registered_user_with_token):
        """Test getting profile when user was deleted from store"""
        user, token = registered_user_with_token
        
        # Remove user from store
        users_db.clear()

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404


class TestIntegration:
    """Integration tests for full workflows"""

    def test_register_login_profile_flow(self):
        """Test complete flow: register -> login -> get profile"""
        # Register
        reg_response = client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
                "name": "Test User",
            },
        )
        assert reg_response.status_code == 201
        user = reg_response.json()

        # Login
        login_response = client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Get profile
        profile_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert profile_response.status_code == 200
        profile = profile_response.json()
        assert profile["user_id"] == user["user_id"]
        assert profile["email"] == user["email"]
        assert profile["name"] == user["name"]

    def test_multiple_users(self):
        """Test that multiple users can be registered and logged in independently"""
        # Register user 1
        user1_reg = client.post(
            "/auth/register",
            json={
                "email": "user1@example.com",
                "password": "password123",
                "name": "User One",
            },
        )
        user1 = user1_reg.json()

        # Register user 2
        user2_reg = client.post(
            "/auth/register",
            json={
                "email": "user2@example.com",
                "password": "password456",
                "name": "User Two",
            },
        )
        user2 = user2_reg.json()

        # Login user 1
        login1 = client.post(
            "/auth/login",
            json={
                "email": "user1@example.com",
                "password": "password123",
            },
        )
        token1 = login1.json()["access_token"]

        # Login user 2
        login2 = client.post(
            "/auth/login",
            json={
                "email": "user2@example.com",
                "password": "password456",
            },
        )
        token2 = login2.json()["access_token"]

        # Verify user 1 profile
        profile1 = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert profile1.json()["user_id"] == user1["user_id"]

        # Verify user 2 profile
        profile2 = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert profile2.json()["user_id"] == user2["user_id"]


class TestErrorCodes:
    """Test that proper HTTP error codes are returned"""

    def test_registration_validation_errors_return_422(self):
        """Test that validation errors return 422"""
        response = client.post(
            "/auth/register",
            json={
                "email": "invalid",
                "password": "short",
                "name": "",
            },
        )
        assert response.status_code == 422

    def test_duplicate_email_returns_409(self):
        """Test that duplicate email returns 409"""
        client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
                "name": "User",
            },
        )
        response = client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "password456",
                "name": "User2",
            },
        )
        assert response.status_code == 409

    def test_invalid_credentials_return_401(self):
        """Test that invalid credentials return 401"""
        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 401

    def test_missing_token_returns_403(self):
        """Test that missing token returns 403"""
        response = client.get("/auth/me")
        assert response.status_code == 403

    def test_invalid_token_returns_401(self):
        """Test that invalid token returns 401"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid"},
        )
        assert response.status_code == 401

    def test_user_not_found_returns_404(self):
        """Test that user not found returns 404"""
        # Create a token for a non-existent user
        fake_payload = {
            "sub": "nonexistent-user-id",
            "email": "fake@example.com",
            "role": "customer",
            "exp": int((datetime.utcnow() + timedelta(hours=24)).timestamp()),
        }
        fake_token = jwt.encode(
            fake_payload, JWT_SECRET, algorithm=JWT_ALGORITHM
        )

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {fake_token}"},
        )
        assert response.status_code == 404


class TestAdminRole:
    """Test admin role support in registration"""

    def test_register_admin_user(self):
        """Test registering an admin user"""
        response = client.post(
            "/auth/register",
            json={
                "email": "admin@example.com",
                "password": "adminpass123",
                "name": "Admin User",
                "role": "admin",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "admin@example.com"
        assert data["name"] == "Admin User"
        assert data["role"] == "admin"

    def test_register_customer_user_explicit(self):
        """Test registering a customer user with explicit role"""
        response = client.post(
            "/auth/register",
            json={
                "email": "customer@example.com",
                "password": "custpass123",
                "name": "Customer User",
                "role": "customer",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "customer"

    def test_register_default_customer_role(self):
        """Test that default role is customer when not specified"""
        response = client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
                "name": "Test User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "customer"

    def test_invalid_role(self):
        """Test registration with invalid role"""
        response = client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
                "name": "Test User",
                "role": "superuser",
            },
        )
        assert response.status_code == 422

    def test_admin_token_contains_admin_role(self):
        """Test that admin user's JWT token contains admin role"""
        # Register admin user
        reg_response = client.post(
            "/auth/register",
            json={
                "email": "admin@example.com",
                "password": "adminpass123",
                "name": "Admin User",
                "role": "admin",
            },
        )
        assert reg_response.status_code == 201

        # Login
        login_response = client.post(
            "/auth/login",
            json={
                "email": "admin@example.com",
                "password": "adminpass123",
            },
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Decode token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["role"] == "admin"

    def test_admin_user_profile_shows_admin_role(self):
        """Test that admin user's profile shows admin role"""
        # Register admin user
        client.post(
            "/auth/register",
            json={
                "email": "admin@example.com",
                "password": "adminpass123",
                "name": "Admin User",
                "role": "admin",
            },
        )

        # Login
        login_response = client.post(
            "/auth/login",
            json={
                "email": "admin@example.com",
                "password": "adminpass123",
            },
        )
        token = login_response.json()["access_token"]

        # Get profile
        profile_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert profile_response.status_code == 200
        data = profile_response.json()
        assert data["role"] == "admin"

    def test_multiple_admin_users(self):
        """Test registering multiple admin users"""
        # Register first admin
        response1 = client.post(
            "/auth/register",
            json={
                "email": "admin1@example.com",
                "password": "adminpass123",
                "name": "Admin 1",
                "role": "admin",
            },
        )
        assert response1.status_code == 201

        # Register second admin
        response2 = client.post(
            "/auth/register",
            json={
                "email": "admin2@example.com",
                "password": "adminpass456",
                "name": "Admin 2",
                "role": "admin",
            },
        )
        assert response2.status_code == 201
        assert response2.json()["role"] == "admin"

    def test_mixed_admin_and_customer_users(self):
        """Test registering both admin and customer users"""
        # Register admin
        admin_response = client.post(
            "/auth/register",
            json={
                "email": "admin@example.com",
                "password": "adminpass123",
                "name": "Admin User",
                "role": "admin",
            },
        )
        assert admin_response.status_code == 201
        assert admin_response.json()["role"] == "admin"

        # Register customer
        customer_response = client.post(
            "/auth/register",
            json={
                "email": "customer@example.com",
                "password": "custpass123",
                "name": "Customer User",
                "role": "customer",
            },
        )
        assert customer_response.status_code == 201
        assert customer_response.json()["role"] == "customer"
