"""
Comprehensive unit tests for Contacts API backend.
Tests all endpoints with happy path, error cases, and edge cases.
"""

import pytest
from fastapi.testclient import TestClient
from main import app, users_db, contacts_db, user_id_to_mobile

# Test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    """Clear in-memory databases before each test."""
    users_db.clear()
    contacts_db.clear()
    user_id_to_mobile.clear()
    yield
    users_db.clear()
    contacts_db.clear()
    user_id_to_mobile.clear()


# ============================================================================
# REGISTRATION TESTS
# ============================================================================


def test_register_success():
    """Test successful user registration."""
    response = client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["mobile"] == "9876543210"


def test_register_duplicate_mobile():
    """Test registration with duplicate mobile number."""
    # First registration
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"},
    )
    
    # Second registration with same mobile
    response = client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "different_password"},
    )
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


def test_register_invalid_mobile_too_short():
    """Test registration with mobile number too short."""
    response = client.post(
        "/api/auth/register",
        json={"mobile": "123456789", "password": "password123"},
    )
    assert response.status_code == 422


def test_register_invalid_mobile_non_numeric():
    """Test registration with non-numeric mobile."""
    response = client.post(
        "/api/auth/register",
        json={"mobile": "98765abc10", "password": "password123"},
    )
    assert response.status_code == 422


def test_register_invalid_password_too_short():
    """Test registration with password too short."""
    response = client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "12345"},
    )
    assert response.status_code == 422


def test_register_missing_fields():
    """Test registration with missing fields."""
    response = client.post("/api/auth/register", json={"mobile": "9876543210"})
    assert response.status_code == 422


# ============================================================================
# LOGIN TESTS
# ============================================================================


def test_login_success():
    """Test successful login."""
    # Register first
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"},
    )
    
    # Login
    response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_mobile():
    """Test login with non-existent mobile."""
    response = client.post(
        "/api/auth/login",
        json={"mobile": "9999999999", "password": "password123"},
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_invalid_password():
    """Test login with wrong password."""
    # Register first
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"},
    )
    
    # Login with wrong password
    response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_missing_fields():
    """Test login with missing fields."""
    response = client.post("/api/auth/login", json={"mobile": "9876543210"})
    assert response.status_code == 422


# ============================================================================
# CONTACTS - CREATE TESTS
# ============================================================================


def test_create_contact_success():
    """Test successful contact creation."""
    # Register and login
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"},
    )
    login_response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    
    # Create contact
    response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "9123456789"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["mobile"] == "9123456789"
    assert "id" in data
    assert "user_id" in data


def test_create_contact_missing_token():
    """Test contact creation without token."""
    response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "9123456789"},
    )
    assert response.status_code == 401
    assert "Missing authorization header" in response.json()["detail"]


def test_create_contact_invalid_token():
    """Test contact creation with invalid token."""
    response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "9123456789"},
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 401


def test_create_contact_invalid_authorization_header():
    """Test contact creation with malformed authorization header."""
    response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "9123456789"},
        headers={"Authorization": "InvalidFormat token"},
    )
    assert response.status_code == 401


def test_create_contact_invalid_mobile():
    """Test contact creation with invalid mobile."""
    # Register and login
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"},
    )
    login_response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    
    # Create contact with invalid mobile
    response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_create_contact_missing_fields():
    """Test contact creation with missing fields."""
    # Register and login
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"},
    )
    login_response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    
    # Create contact without name
    response = client.post(
        "/api/contacts",
        json={"mobile": "9123456789"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


# ============================================================================
# CONTACTS - LIST TESTS
# ============================================================================


def test_list_contacts_empty():
    """Test listing contacts when none exist."""
    # Register and login
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"},
    )
    login_response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    
    # List contacts
    response = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_list_contacts_success():
    """Test listing contacts successfully."""
    # Register and login
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"},
    )
    login_response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    
    # Create multiple contacts
    client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "9123456789"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/api/contacts",
        json={"name": "Jane Smith", "mobile": "9987654321"},
        headers={"Authorization": f"Bearer {token}"},
    )
    
    # List contacts
    response = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "John Doe"
    assert data[1]["name"] == "Jane Smith"


def test_list_contacts_per_user_isolation():
    """Test that users only see their own contacts."""
    # Register and login user 1
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"},
    )
    login_response1 = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"},
    )
    token1 = login_response1.json()["access_token"]
    
    # Register and login user 2
    client.post(
        "/api/auth/register",
        json={"mobile": "9111111111", "password": "password456"},
    )
    login_response2 = client.post(
        "/api/auth/login",
        json={"mobile": "9111111111", "password": "password456"},
    )
    token2 = login_response2.json()["access_token"]
    
    # User 1 creates contacts
    client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "9123456789"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    client.post(
        "/api/contacts",
        json={"name": "Jane Smith", "mobile": "9987654321"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    
    # User 2 creates contact
    client.post(
        "/api/contacts",
        json={"name": "Bob Johnson", "mobile": "9555555555"},
        headers={"Authorization": f"Bearer {token2}"},
    )
    
    # User 1 lists contacts - should see only their 2
    response1 = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert response1.status_code == 200
    assert len(response1.json()) == 2
    
    # User 2 lists contacts - should see only their 1
    response2 = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert response2.status_code == 200
    assert len(response2.json()) == 1
    assert response2.json()[0]["name"] == "Bob Johnson"


def test_list_contacts_missing_token():
    """Test listing contacts without token."""
    response = client.get("/api/contacts")
    assert response.status_code == 401


# ============================================================================
# CONTACTS - UPDATE TESTS
# ============================================================================


def test_update_contact_success():
    """Test successful contact update."""
    # Register and login
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"},
    )
    login_response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    
    # Create contact
    create_response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "9123456789"},
        headers={"Authorization": f"Bearer {token}"},
    )
    contact_id = create_response.json()["id"]
    
    # Update contact
    response = client.put(
        f"/api/contacts/{contact_id}",
        json={"name": "John Smith", "mobile": "9999999999"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Smith"
    assert data["mobile"] == "9999999999"
    assert data["id"] == contact_id


def test_update_contact_not_found():
    """Test updating non-existent contact."""
    # Register and login
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"},
    )
    login_response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    
    # Update non-existent contact
    response = client.put(
        "/api/contacts/nonexistent_id",
        json={"name": "John Smith", "mobile": "9999999999"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_contact_not_owner():
    """Test updating contact owned by another user."""
    # Register and login user 1
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"},
    )
    login_response1 = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"},
    )
    token1 = login_response1.json()["access_token"]
    
    # Register and login user 2
    client.post(
        "/api/auth/register",
        json={"mobile": "9111111111", "password": "password456"},
    )
    login_response2 = client.post(
        "/api/auth/login",
        json={"mobile": "9111111111", "password": "password456"},
    )
    token2 = login_response2.json()["access_token"]
    
    # User 1 creates contact
    create_response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "9123456789"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    contact_id = create_response.json()["id"]
    
    # User 2 tries to update user 1's contact
    response = client.put(
        f"/api/contacts/{contact_id}",
        json={"name": "Hacker", "mobile": "9999999999"},
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]


def test_update_contact_missing_token():
    """Test updating contact without token."""
    response = client.put(
        "/api/contacts/some_id",
        json={"name": "John Smith", "mobile": "9999999999"},
    )
    assert response.status_code == 401


# ============================================================================
# CONTACTS - DELETE TESTS
# ============================================================================


def test_delete_contact_success():
    """Test successful contact deletion."""
    # Register and login
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"},
    )
    login_response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    
    # Create contact
    create_response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "9123456789"},
        headers={"Authorization": f"Bearer {token}"},
    )
    contact_id = create_response.json()["id"]
    
    # Delete contact
    response = client.delete(
        f"/api/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204
    
    # Verify contact is deleted
    list_response = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert len(list_response.json()) == 0


def test_delete_contact_not_found():
    """Test deleting non-existent contact."""
    # Register and login
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"},
    )
    login_response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    
    # Delete non-existent contact
    response = client.delete(
        "/api/contacts/nonexistent_id",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_delete_contact_not_owner():
    """Test deleting contact owned by another user."""
    # Register and login user 1
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"},
    )
    login_response1 = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"},
    )
    token1 = login_response1.json()["access_token"]
    
    # Register and login user 2
    client.post(
        "/api/auth/register",
        json={"mobile": "9111111111", "password": "password456"},
    )
    login_response2 = client.post(
        "/api/auth/login",
        json={"mobile": "9111111111", "password": "password456"},
    )
    token2 = login_response2.json()["access_token"]
    
    # User 1 creates contact
    create_response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "9123456789"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    contact_id = create_response.json()["id"]
    
    # User 2 tries to delete user 1's contact
    response = client.delete(
        f"/api/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]


def test_delete_contact_missing_token():
    """Test deleting contact without token."""
    response = client.delete("/api/contacts/some_id")
    assert response.status_code == 401


# ============================================================================
# HEALTH CHECK TEST
# ============================================================================


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
