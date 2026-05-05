"""
Unit tests for Auth Service
Covers happy paths, error cases, JWT validation, and password hashing.
"""

import pytest
from fastapi.testclient import TestClient
from jose import jwt
import os

from main import app, users_db, JWT_SECRET, JWT_ALGORITHM, hash_password, verify_password

client = TestClient(app)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def clear_users_db():
    """Clear users database before each test"""
    users_db.clear()
    yield
    users_db.clear()


# ============================================================================
# Registration Tests
# ============================================================================

class TestRegister:
    """Tests for /auth/register endpoint"""
    
    def test_register_success(self):
        """Test successful user registration"""
        response = client.post("/auth/register", json={
            "email": "user@example.com",
            "password": "password123",
            "name": "John Doe"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "user@example.com"
        assert data["name"] == "John Doe"
        assert data["role"] == "customer"
        assert "id" in data
        assert len(data["id"]) > 0
    
    def test_register_invalid_email_format(self):
        """Test registration with invalid email format"""
        response = client.post("/auth/register", json={
            "email": "invalid-email",
            "password": "password123",
            "name": "John Doe"
        })
        
        assert response.status_code == 400
        assert "Invalid email format" in response.json()["detail"]
    
    def test_register_password_too_short(self):
        """Test registration with password < 8 chars"""
        response = client.post("/auth/register", json={
            "email": "user@example.com",
            "password": "short",
            "name": "John Doe"
        })
        
        # Pydantic validation returns 422
        assert response.status_code == 422
    
    def test_register_empty_name(self):
        """Test registration with empty name"""
        response = client.post("/auth/register", json={
            "email": "user@example.com",
            "password": "password123",
            "name": ""
        })
        
        # Pydantic validation returns 422
        assert response.status_code == 422
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        # First registration
        client.post("/auth/register", json={
            "email": "user@example.com",
            "password": "password123",
            "name": "John Doe"
        })
        
        # Second registration with same email
        response = client.post("/auth/register", json={
            "email": "user@example.com",
            "password": "password456",
            "name": "Jane Doe"
        })
        
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"]
    
    def test_register_multiple_users(self):
        """Test registering multiple users"""
        response1 = client.post("/auth/register", json={
            "email": "user1@example.com",
            "password": "password123",
            "name": "User One"
        })
        
        response2 = client.post("/auth/register", json={
            "email": "user2@example.com",
            "password": "password456",
            "name": "User Two"
        })
        
        assert response1.status_code == 201
        assert response2.status_code == 201
        assert response1.json()["id"] != response2.json()["id"]


# ============================================================================
# Login Tests
# ============================================================================

class TestLogin:
    """Tests for /auth/login endpoint"""
    
    def test_login_success(self):
        """Test successful login"""
        # Register first
        client.post("/auth/register", json={
            "email": "user@example.com",
            "password": "password123",
            "name": "John Doe"
        })
        
        # Login
        response = client.post("/auth/login", json={
            "email": "user@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_invalid_email(self):
        """Test login with non-existent email"""
        response = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_wrong_password(self):
        """Test login with wrong password"""
        # Register first
        client.post("/auth/register", json={
            "email": "user@example.com",
            "password": "password123",
            "name": "John Doe"
        })
        
        # Login with wrong password
        response = client.post("/auth/login", json={
            "email": "user@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_token_format(self):
        """Test that login returns valid JWT token"""
        # Register
        client.post("/auth/register", json={
            "email": "user@example.com",
            "password": "password123",
            "name": "John Doe"
        })
        
        # Login
        response = client.post("/auth/login", json={
            "email": "user@example.com",
            "password": "password123"
        })
        
        token = response.json()["access_token"]
        
        # Decode token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["email"] == "user@example.com"
        assert payload["role"] == "customer"
        assert "sub" in payload  # user_id
        assert "exp" in payload  # expiry


# ============================================================================
# Get Current User Tests
# ============================================================================

class TestGetCurrentUser:
    """Tests for /auth/me endpoint"""
    
    def test_get_current_user_success(self):
        """Test getting current user profile with valid token"""
        # Register
        reg_response = client.post("/auth/register", json={
            "email": "user@example.com",
            "password": "password123",
            "name": "John Doe"
        })
        user_id = reg_response.json()["id"]
        
        # Login
        login_response = client.post("/auth/login", json={
            "email": "user@example.com",
            "password": "password123"
        })
        token = login_response.json()["access_token"]
        
        # Get current user
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == "user@example.com"
        assert data["name"] == "John Doe"
        assert data["role"] == "customer"
    
    def test_get_current_user_missing_token(self):
        """Test getting current user without token"""
        response = client.get("/auth/me")
        
        assert response.status_code == 403
    
    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == 401
        assert "Invalid or expired token" in response.json()["detail"]
    
    def test_get_current_user_expired_token(self):
        """Test getting current user with expired token"""
        from datetime import datetime, timedelta, timezone
        
        # Create an expired token
        now = datetime.now(timezone.utc)
        expired_time = now - timedelta(hours=25)  # Expired 1 hour ago
        
        payload = {
            "sub": "fake-user-id",
            "email": "user@example.com",
            "role": "customer",
            "exp": expired_time,
            "iat": now
        }
        
        expired_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401
        assert "Invalid or expired token" in response.json()["detail"]


# ============================================================================
# Password Hashing Tests
# ============================================================================

class TestPasswordHashing:
    """Tests for password hashing and verification"""
    
    def test_password_hashing(self):
        """Test that passwords are hashed with argon2"""
        password = "mypassword123"
        hashed = hash_password(password)
        
        # Hash should not equal plaintext
        assert hashed != password
        
        # Hash should be long (argon2 hashes are typically 100+ chars)
        assert len(hashed) > 50
    
    def test_password_verification(self):
        """Test password verification"""
        password = "mypassword123"
        hashed = hash_password(password)
        
        # Correct password should verify
        assert verify_password(password, hashed) is True
        
        # Wrong password should not verify
        assert verify_password("wrongpassword", hashed) is False
    
    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (argon2 salt)"""
        password = "mypassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Hashes should be different (due to salt)
        assert hash1 != hash2
        
        # But both should verify the same password
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


# ============================================================================
# JWT Token Tests
# ============================================================================

class TestJWTToken:
    """Tests for JWT token generation and validation"""
    
    def test_jwt_token_expiry(self):
        """Test that JWT token has 24h expiry"""
        from datetime import datetime, timezone
        
        # Register and login
        client.post("/auth/register", json={
            "email": "user@example.com",
            "password": "password123",
            "name": "John Doe"
        })
        
        login_response = client.post("/auth/login", json={
            "email": "user@example.com",
            "password": "password123"
        })
        
        token = login_response.json()["access_token"]
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Check expiry is approximately 24 hours from now
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = (exp_time - now).total_seconds()
        
        # Should be between 23 and 25 hours (in seconds)
        assert 82800 < diff < 90000  # 23h to 25h
    
    def test_jwt_token_payload(self):
        """Test JWT token contains correct payload"""
        # Register and login
        reg_response = client.post("/auth/register", json={
            "email": "user@example.com",
            "password": "password123",
            "name": "John Doe"
        })
        user_id = reg_response.json()["id"]
        
        login_response = client.post("/auth/login", json={
            "email": "user@example.com",
            "password": "password123"
        })
        
        token = login_response.json()["access_token"]
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        assert payload["sub"] == user_id
        assert payload["email"] == "user@example.com"
        assert payload["role"] == "customer"
        assert "exp" in payload
        assert "iat" in payload


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_register_login_get_profile_workflow(self):
        """Test complete workflow: register -> login -> get profile"""
        # Register
        reg_response = client.post("/auth/register", json={
            "email": "user@example.com",
            "password": "password123",
            "name": "John Doe"
        })
        assert reg_response.status_code == 201
        user_id = reg_response.json()["id"]
        
        # Login
        login_response = client.post("/auth/login", json={
            "email": "user@example.com",
            "password": "password123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Get profile
        profile_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_response.status_code == 200
        profile = profile_response.json()
        
        assert profile["id"] == user_id
        assert profile["email"] == "user@example.com"
        assert profile["name"] == "John Doe"
    
    def test_multiple_users_independent_tokens(self):
        """Test that multiple users have independent tokens"""
        # Register user 1
        client.post("/auth/register", json={
            "email": "user1@example.com",
            "password": "password123",
            "name": "User One"
        })
        
        # Register user 2
        client.post("/auth/register", json={
            "email": "user2@example.com",
            "password": "password456",
            "name": "User Two"
        })
        
        # Login user 1
        login1 = client.post("/auth/login", json={
            "email": "user1@example.com",
            "password": "password123"
        })
        token1 = login1.json()["access_token"]
        
        # Login user 2
        login2 = client.post("/auth/login", json={
            "email": "user2@example.com",
            "password": "password456"
        })
        token2 = login2.json()["access_token"]
        
        # Get profile with token 1
        profile1 = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token1}"}
        ).json()
        
        # Get profile with token 2
        profile2 = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token2}"}
        ).json()
        
        # Profiles should be different
        assert profile1["email"] == "user1@example.com"
        assert profile2["email"] == "user2@example.com"
        assert profile1["id"] != profile2["id"]


# ============================================================================
# Health Check Test
# ============================================================================

class TestHealth:
    """Tests for health check endpoint"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
