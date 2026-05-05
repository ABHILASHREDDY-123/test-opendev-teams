"""
Unit tests for Contacts API Backend
Tests cover registration, login, and contacts CRUD operations with comprehensive scenarios.
"""

import pytest
from fastapi.testclient import TestClient
from main import app, users_db, contacts_db, user_id_counter, contact_id_counter

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def reset_db():
    """Reset database before each test."""
    users_db.clear()
    contacts_db.clear()
    # Reset counters
    import main
    main.user_id_counter = 0
    main.contact_id_counter = 0
    yield
    users_db.clear()
    contacts_db.clear()


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    """Register a test user and return mobile, password, and user_id."""
    mobile = "9876543210"
    password = "password123"
    response = client.post(
        "/api/v1/register",
        json={"mobile": mobile, "password": password},
    )
    assert response.status_code == 201
    data = response.json()
    return {
        "mobile": mobile,
        "password": password,
        "user_id": data["user_id"],
    }


@pytest.fixture
def login_token(client, registered_user):
    """Login and return JWT token."""
    response = client.post(
        "/api/v1/login",
        json={
            "mobile": registered_user["mobile"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


# ============================================================================
# Tests: User Registration
# ============================================================================


class TestUserRegistration:
    """Tests for user registration endpoint."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/register",
            json={"mobile": "9876543210", "password": "password123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == 1
        assert data["mobile"] == "9876543210"
        assert data["message"] == "User registered successfully"

    def test_register_multiple_users(self, client):
        """Test registering multiple users."""
        # Register first user
        response1 = client.post(
            "/api/v1/register",
            json={"mobile": "9876543210", "password": "password123"},
        )
        assert response1.status_code == 201
        assert response1.json()["user_id"] == 1

        # Register second user
        response2 = client.post(
            "/api/v1/register",
            json={"mobile": "9876543211", "password": "password456"},
        )
        assert response2.status_code == 201
        assert response2.json()["user_id"] == 2

    def test_register_duplicate_mobile(self, client):
        """Test registering with duplicate mobile number."""
        # Register first user
        client.post(
            "/api/v1/register",
            json={"mobile": "9876543210", "password": "password123"},
        )

        # Try to register with same mobile
        response = client.post(
            "/api/v1/register",
            json={"mobile": "9876543210", "password": "different_password"},
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"]

    def test_register_invalid_mobile_short(self, client):
        """Test registration with mobile number too short."""
        response = client.post(
            "/api/v1/register",
            json={"mobile": "123456789", "password": "password123"},
        )
        assert response.status_code == 422

    def test_register_invalid_mobile_non_digits(self, client):
        """Test registration with non-digit mobile number."""
        response = client.post(
            "/api/v1/register",
            json={"mobile": "987654321a", "password": "password123"},
        )
        assert response.status_code == 422

    def test_register_invalid_password_short(self, client):
        """Test registration with password too short."""
        response = client.post(
            "/api/v1/register",
            json={"mobile": "9876543210", "password": "pass"},
        )
        assert response.status_code == 422

    def test_register_missing_mobile(self, client):
        """Test registration with missing mobile."""
        response = client.post(
            "/api/v1/register",
            json={"password": "password123"},
        )
        assert response.status_code == 422

    def test_register_missing_password(self, client):
        """Test registration with missing password."""
        response = client.post(
            "/api/v1/register",
            json={"mobile": "9876543210"},
        )
        assert response.status_code == 422

    def test_register_empty_body(self, client):
        """Test registration with empty body."""
        response = client.post("/api/v1/register", json={})
        assert response.status_code == 422

    def test_register_long_mobile(self, client):
        """Test registration with long mobile number (10+ digits)."""
        response = client.post(
            "/api/v1/register",
            json={"mobile": "98765432101234", "password": "password123"},
        )
        assert response.status_code == 201

    def test_register_password_exactly_6_chars(self, client):
        """Test registration with password exactly 6 characters."""
        response = client.post(
            "/api/v1/register",
            json={"mobile": "9876543210", "password": "pass12"},
        )
        assert response.status_code == 201


# ============================================================================
# Tests: User Login
# ============================================================================


class TestUserLogin:
    """Tests for user login endpoint."""

    def test_login_success(self, client, registered_user):
        """Test successful login."""
        response = client.post(
            "/api/v1/login",
            json={
                "mobile": registered_user["mobile"],
                "password": registered_user["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_id"] == registered_user["user_id"]

    def test_login_invalid_mobile(self, client):
        """Test login with non-existent mobile."""
        response = client.post(
            "/api/v1/login",
            json={"mobile": "9999999999", "password": "password123"},
        )
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_invalid_password(self, client, registered_user):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/login",
            json={
                "mobile": registered_user["mobile"],
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_missing_mobile(self, client):
        """Test login with missing mobile."""
        response = client.post(
            "/api/v1/login",
            json={"password": "password123"},
        )
        assert response.status_code == 422

    def test_login_missing_password(self, client):
        """Test login with missing password."""
        response = client.post(
            "/api/v1/login",
            json={"mobile": "9876543210"},
        )
        assert response.status_code == 422

    def test_login_empty_body(self, client):
        """Test login with empty body."""
        response = client.post("/api/v1/login", json={})
        assert response.status_code == 422

    def test_login_token_format(self, client, registered_user):
        """Test that login returns valid JWT token."""
        response = client.post(
            "/api/v1/login",
            json={
                "mobile": registered_user["mobile"],
                "password": registered_user["password"],
            },
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        # JWT tokens have 3 parts separated by dots
        assert token.count(".") == 2


# ============================================================================
# Tests: Add Contact
# ============================================================================


class TestAddContact:
    """Tests for add contact endpoint."""

    def test_add_contact_success(self, client, login_token):
        """Test successful contact creation."""
        response = client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "phone": "9876543210",
                "email": "john@example.com",
            },
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "John Doe"
        assert data["phone"] == "9876543210"
        assert data["email"] == "john@example.com"
        assert "created_at" in data

    def test_add_multiple_contacts(self, client, login_token):
        """Test adding multiple contacts."""
        # Add first contact
        response1 = client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "phone": "9876543210",
                "email": "john@example.com",
            },
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert response1.status_code == 201
        assert response1.json()["id"] == 1

        # Add second contact
        response2 = client.post(
            "/api/v1/contacts",
            json={
                "name": "Jane Doe",
                "phone": "9876543211",
                "email": "jane@example.com",
            },
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert response2.status_code == 201
        assert response2.json()["id"] == 2

    def test_add_contact_missing_token(self, client):
        """Test adding contact without token."""
        response = client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "phone": "9876543210",
                "email": "john@example.com",
            },
        )
        assert response.status_code == 401

    def test_add_contact_invalid_token(self, client):
        """Test adding contact with invalid token."""
        response = client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "phone": "9876543210",
                "email": "john@example.com",
            },
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401

    def test_add_contact_invalid_phone(self, client, login_token):
        """Test adding contact with invalid phone."""
        response = client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "phone": "123456789",
                "email": "john@example.com",
            },
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert response.status_code == 422

    def test_add_contact_invalid_email(self, client, login_token):
        """Test adding contact with invalid email."""
        response = client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "phone": "9876543210",
                "email": "invalid_email",
            },
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert response.status_code == 422

    def test_add_contact_missing_name(self, client, login_token):
        """Test adding contact with missing name."""
        response = client.post(
            "/api/v1/contacts",
            json={
                "phone": "9876543210",
                "email": "john@example.com",
            },
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert response.status_code == 422

    def test_add_contact_empty_name(self, client, login_token):
        """Test adding contact with empty name."""
        response = client.post(
            "/api/v1/contacts",
            json={
                "name": "",
                "phone": "9876543210",
                "email": "john@example.com",
            },
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert response.status_code == 422


# ============================================================================
# Tests: List Contacts
# ============================================================================


class TestListContacts:
    """Tests for list contacts endpoint."""

    def test_list_contacts_empty(self, client, login_token):
        """Test listing contacts when none exist."""
        response = client.get(
            "/api/v1/contacts",
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_list_contacts_success(self, client, login_token):
        """Test listing contacts."""
        # Add a contact
        client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "phone": "9876543210",
                "email": "john@example.com",
            },
            headers={"Authorization": f"Bearer {login_token}"},
        )

        # List contacts
        response = client.get(
            "/api/v1/contacts",
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "John Doe"

    def test_list_contacts_multiple(self, client, login_token):
        """Test listing multiple contacts."""
        # Add multiple contacts
        for i in range(3):
            client.post(
                "/api/v1/contacts",
                json={
                    "name": f"Contact {i}",
                    "phone": f"987654321{i}",
                    "email": f"contact{i}@example.com",
                },
                headers={"Authorization": f"Bearer {login_token}"},
            )

        # List contacts
        response = client.get(
            "/api/v1/contacts",
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_list_contacts_missing_token(self, client):
        """Test listing contacts without token."""
        response = client.get("/api/v1/contacts")
        assert response.status_code == 401

    def test_list_contacts_invalid_token(self, client):
        """Test listing contacts with invalid token."""
        response = client.get(
            "/api/v1/contacts",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401

    def test_list_contacts_user_isolation(self, client):
        """Test that users only see their own contacts."""
        # Register and login first user
        client.post(
            "/api/v1/register",
            json={"mobile": "9876543210", "password": "password123"},
        )
        response1 = client.post(
            "/api/v1/login",
            json={"mobile": "9876543210", "password": "password123"},
        )
        token1 = response1.json()["access_token"]

        # Add contact for first user
        client.post(
            "/api/v1/contacts",
            json={
                "name": "User1 Contact",
                "phone": "1111111111",
                "email": "user1@example.com",
            },
            headers={"Authorization": f"Bearer {token1}"},
        )

        # Register and login second user
        client.post(
            "/api/v1/register",
            json={"mobile": "9876543211", "password": "password456"},
        )
        response2 = client.post(
            "/api/v1/login",
            json={"mobile": "9876543211", "password": "password456"},
        )
        token2 = response2.json()["access_token"]

        # Second user should not see first user's contacts
        response = client.get(
            "/api/v1/contacts",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 0

        # First user should still see their contact
        response = client.get(
            "/api/v1/contacts",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1


# ============================================================================
# Tests: Update Contact
# ============================================================================


class TestUpdateContact:
    """Tests for update contact endpoint."""

    def test_update_contact_success(self, client, login_token):
        """Test successful contact update."""
        # Add contact
        add_response = client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "phone": "9876543210",
                "email": "john@example.com",
            },
            headers={"Authorization": f"Bearer {login_token}"},
        )
        contact_id = add_response.json()["id"]

        # Update contact
        response = client.put(
            f"/api/v1/contacts/{contact_id}",
            json={
                "name": "Jane Doe",
                "phone": "9876543211",
                "email": "jane@example.com",
            },
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane Doe"
        assert data["phone"] == "9876543211"
        assert data["email"] == "jane@example.com"

    def test_update_contact_partial(self, client, login_token):
        """Test partial contact update."""
        # Add contact
        add_response = client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "phone": "9876543210",
                "email": "john@example.com",
            },
            headers={"Authorization": f"Bearer {login_token}"},
        )
        contact_id = add_response.json()["id"]

        # Update only name
        response = client.put(
            f"/api/v1/contacts/{contact_id}",
            json={"name": "Jane Doe"},
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane Doe"
        assert data["phone"] == "9876543210"  # Unchanged
        assert data["email"] == "john@example.com"  # Unchanged

    def test_update_contact_not_found(self, client, login_token):
        """Test updating non-existent contact."""
        response = client.put(
            "/api/v1/contacts/999",
            json={"name": "Jane Doe"},
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert response.status_code == 404

    def test_update_contact_missing_token(self, client):
        """Test updating contact without token."""
        response = client.put(
            "/api/v1/contacts/1",
            json={"name": "Jane Doe"},
        )
        assert response.status_code == 401

    def test_update_contact_invalid_token(self, client):
        """Test updating contact with invalid token."""
        response = client.put(
            "/api/v1/contacts/1",
            json={"name": "Jane Doe"},
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401

    def test_update_contact_invalid_phone(self, client, login_token):
        """Test updating contact with invalid phone."""
        # Add contact
        add_response = client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "phone": "9876543210",
                "email": "john@example.com",
            },
            headers={"Authorization": f"Bearer {login_token}"},
        )
        contact_id = add_response.json()["id"]

        # Try to update with invalid phone
        response = client.put(
            f"/api/v1/contacts/{contact_id}",
            json={"phone": "123456789"},
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert response.status_code == 422

    def test_update_contact_user_isolation(self, client):
        """Test that users cannot update other users' contacts."""
        # Register and login first user
        client.post(
            "/api/v1/register",
            json={"mobile": "9876543210", "password": "password123"},
        )
        response1 = client.post(
            "/api/v1/login",
            json={"mobile": "9876543210", "password": "password123"},
        )
        token1 = response1.json()["access_token"]

        # Add contact for first user
        add_response = client.post(
            "/api/v1/contacts",
            json={
                "name": "User1 Contact",
                "phone": "1111111111",
                "email": "user1@example.com",
            },
            headers={"Authorization": f"Bearer {token1}"},
        )
        contact_id = add_response.json()["id"]

        # Register and login second user
        client.post(
            "/api/v1/register",
            json={"mobile": "9876543211", "password": "password456"},
        )
        response2 = client.post(
            "/api/v1/login",
            json={"mobile": "9876543211", "password": "password456"},
        )
        token2 = response2.json()["access_token"]

        # Second user should not be able to update first user's contact
        response = client.put(
            f"/api/v1/contacts/{contact_id}",
            json={"name": "Hacked"},
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response.status_code == 404


# ============================================================================
# Tests: Delete Contact
# ============================================================================


class TestDeleteContact:
    """Tests for delete contact endpoint."""

    def test_delete_contact_success(self, client, login_token):
        """Test successful contact deletion."""
        # Add contact
        add_response = client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "phone": "9876543210",
                "email": "john@example.com",
            },
            headers={"Authorization": f"Bearer {login_token}"},
        )
        contact_id = add_response.json()["id"]

        # Delete contact
        response = client.delete(
            f"/api/v1/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert response.status_code == 204

        # Verify contact is deleted
        list_response = client.get(
            "/api/v1/contacts",
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert len(list_response.json()) == 0

    def test_delete_contact_not_found(self, client, login_token):
        """Test deleting non-existent contact."""
        response = client.delete(
            "/api/v1/contacts/999",
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert response.status_code == 404

    def test_delete_contact_missing_token(self, client):
        """Test deleting contact without token."""
        response = client.delete("/api/v1/contacts/1")
        assert response.status_code == 401

    def test_delete_contact_invalid_token(self, client):
        """Test deleting contact with invalid token."""
        response = client.delete(
            "/api/v1/contacts/1",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401

    def test_delete_contact_user_isolation(self, client):
        """Test that users cannot delete other users' contacts."""
        # Register and login first user
        client.post(
            "/api/v1/register",
            json={"mobile": "9876543210", "password": "password123"},
        )
        response1 = client.post(
            "/api/v1/login",
            json={"mobile": "9876543210", "password": "password123"},
        )
        token1 = response1.json()["access_token"]

        # Add contact for first user
        add_response = client.post(
            "/api/v1/contacts",
            json={
                "name": "User1 Contact",
                "phone": "1111111111",
                "email": "user1@example.com",
            },
            headers={"Authorization": f"Bearer {token1}"},
        )
        contact_id = add_response.json()["id"]

        # Register and login second user
        client.post(
            "/api/v1/register",
            json={"mobile": "9876543211", "password": "password456"},
        )
        response2 = client.post(
            "/api/v1/login",
            json={"mobile": "9876543211", "password": "password456"},
        )
        token2 = response2.json()["access_token"]

        # Second user should not be able to delete first user's contact
        response = client.delete(
            f"/api/v1/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response.status_code == 404

        # First user's contact should still exist
        list_response = client.get(
            "/api/v1/contacts",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert len(list_response.json()) == 1


# ============================================================================
# Tests: Health Check
# ============================================================================


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
