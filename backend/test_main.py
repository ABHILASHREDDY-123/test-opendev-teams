"""
Comprehensive test suite for Contacts API.
Tests all endpoints with happy path, error cases, and edge cases.
"""

import pytest
from fastapi.testclient import TestClient
from main import app, users_db, contacts_db, mobile_to_user

client = TestClient(app)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def clear_db():
    """Clear database before each test."""
    users_db.clear()
    contacts_db.clear()
    mobile_to_user.clear()
    yield
    users_db.clear()
    contacts_db.clear()
    mobile_to_user.clear()


@pytest.fixture
def registered_user():
    """Create a registered user."""
    response = client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"}
    )
    return response.json()


@pytest.fixture
def user_token(registered_user):
    """Get JWT token for registered user."""
    response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"}
    )
    return response.json()["token"]


@pytest.fixture
def auth_header(user_token):
    """Get authorization header with token."""
    return {"Authorization": f"Bearer {user_token}"}


# ============================================================================
# POST /api/auth/register - Happy Path
# ============================================================================


def test_register_success():
    """Test successful user registration."""
    response = client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["mobile"] == "9876543210"
    assert len(data["id"]) > 0


def test_register_different_users():
    """Test registering multiple different users."""
    response1 = client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"}
    )
    assert response1.status_code == 201
    user1 = response1.json()
    
    response2 = client.post(
        "/api/auth/register",
        json={"mobile": "9876543211", "password": "password456"}
    )
    assert response2.status_code == 201
    user2 = response2.json()
    
    assert user1["id"] != user2["id"]
    assert user1["mobile"] != user2["mobile"]


# ============================================================================
# POST /api/auth/register - Error Cases
# ============================================================================


def test_register_duplicate_mobile():
    """Test registration with duplicate mobile number."""
    # Register first user
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"}
    )
    
    # Try to register with same mobile
    response = client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "different123"}
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_mobile_too_short():
    """Test registration with mobile number too short."""
    response = client.post(
        "/api/auth/register",
        json={"mobile": "123456789", "password": "password123"}
    )
    assert response.status_code == 422  # Validation error


def test_register_mobile_non_numeric():
    """Test registration with non-numeric mobile."""
    response = client.post(
        "/api/auth/register",
        json={"mobile": "987654321a", "password": "password123"}
    )
    assert response.status_code == 422


def test_register_password_too_short():
    """Test registration with password too short."""
    response = client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "pass"}
    )
    assert response.status_code == 422


def test_register_missing_mobile():
    """Test registration without mobile."""
    response = client.post(
        "/api/auth/register",
        json={"password": "password123"}
    )
    assert response.status_code == 422


def test_register_missing_password():
    """Test registration without password."""
    response = client.post(
        "/api/auth/register",
        json={"mobile": "9876543210"}
    )
    assert response.status_code == 422


def test_register_empty_mobile():
    """Test registration with empty mobile."""
    response = client.post(
        "/api/auth/register",
        json={"mobile": "", "password": "password123"}
    )
    assert response.status_code == 422


def test_register_empty_password():
    """Test registration with empty password."""
    response = client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": ""}
    )
    assert response.status_code == 422


# ============================================================================
# POST /api/auth/login - Happy Path
# ============================================================================


def test_login_success(registered_user):
    """Test successful login."""
    response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert len(data["token"]) > 0


def test_login_token_valid(user_token):
    """Test that login token is valid."""
    # Token should be a valid JWT string
    assert len(user_token) > 0
    assert user_token.count('.') == 2  # JWT has 3 parts separated by dots


# ============================================================================
# POST /api/auth/login - Error Cases
# ============================================================================


def test_login_invalid_mobile():
    """Test login with non-existent mobile."""
    response = client.post(
        "/api/auth/login",
        json={"mobile": "1234567890", "password": "password123"}
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_wrong_password(registered_user):
    """Test login with wrong password."""
    response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_missing_mobile():
    """Test login without mobile."""
    response = client.post(
        "/api/auth/login",
        json={"password": "password123"}
    )
    assert response.status_code == 422


def test_login_missing_password():
    """Test login without password."""
    response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210"}
    )
    assert response.status_code == 422


# ============================================================================
# POST /api/contacts - Happy Path
# ============================================================================


def test_create_contact_success(auth_header):
    """Test successful contact creation."""
    response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "1234567890"},
        headers=auth_header
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "John Doe"
    assert data["mobile"] == "1234567890"
    assert "user_id" in data


def test_create_multiple_contacts(auth_header):
    """Test creating multiple contacts."""
    response1 = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "1234567890"},
        headers=auth_header
    )
    assert response1.status_code == 201
    contact1 = response1.json()
    
    response2 = client.post(
        "/api/contacts",
        json={"name": "Jane Smith", "mobile": "0987654321"},
        headers=auth_header
    )
    assert response2.status_code == 201
    contact2 = response2.json()
    
    assert contact1["id"] != contact2["id"]
    assert contact1["name"] != contact2["name"]


# ============================================================================
# POST /api/contacts - Error Cases
# ============================================================================


def test_create_contact_missing_auth():
    """Test contact creation without authentication."""
    response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "1234567890"}
    )
    assert response.status_code == 401


def test_create_contact_invalid_token():
    """Test contact creation with invalid token."""
    response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "1234567890"},
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_create_contact_missing_name(auth_header):
    """Test contact creation without name."""
    response = client.post(
        "/api/contacts",
        json={"mobile": "1234567890"},
        headers=auth_header
    )
    assert response.status_code == 422


def test_create_contact_missing_mobile(auth_header):
    """Test contact creation without mobile."""
    response = client.post(
        "/api/contacts",
        json={"name": "John Doe"},
        headers=auth_header
    )
    assert response.status_code == 422


def test_create_contact_empty_name(auth_header):
    """Test contact creation with empty name."""
    response = client.post(
        "/api/contacts",
        json={"name": "", "mobile": "1234567890"},
        headers=auth_header
    )
    assert response.status_code == 422


def test_create_contact_mobile_too_short(auth_header):
    """Test contact creation with mobile too short."""
    response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "123456789"},
        headers=auth_header
    )
    assert response.status_code == 422


def test_create_contact_mobile_non_numeric(auth_header):
    """Test contact creation with non-numeric mobile."""
    response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "123456789a"},
        headers=auth_header
    )
    assert response.status_code == 422


def test_create_contact_wrong_auth_header(auth_header):
    """Test contact creation with malformed auth header."""
    response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "1234567890"},
        headers={"Authorization": "InvalidToken"}
    )
    assert response.status_code == 401


# ============================================================================
# GET /api/contacts - Happy Path
# ============================================================================


def test_list_contacts_empty(auth_header):
    """Test listing contacts when none exist."""
    response = client.get("/api/contacts", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_list_contacts_single(auth_header):
    """Test listing single contact."""
    # Create contact
    client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "1234567890"},
        headers=auth_header
    )
    
    # List contacts
    response = client.get("/api/contacts", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "John Doe"


def test_list_contacts_multiple(auth_header):
    """Test listing multiple contacts."""
    # Create contacts
    client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "1234567890"},
        headers=auth_header
    )
    client.post(
        "/api/contacts",
        json={"name": "Jane Smith", "mobile": "0987654321"},
        headers=auth_header
    )
    
    # List contacts
    response = client.get("/api/contacts", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


# ============================================================================
# GET /api/contacts - Per-User Isolation
# ============================================================================


def test_list_contacts_isolation():
    """Test that users can only see their own contacts."""
    # Register user 1
    response1 = client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"}
    )
    user1_id = response1.json()["id"]
    
    # Register user 2
    response2 = client.post(
        "/api/auth/register",
        json={"mobile": "9876543211", "password": "password456"}
    )
    user2_id = response2.json()["id"]
    
    # Login user 1 and create contact
    token1_response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"}
    )
    token1 = token1_response.json()["token"]
    
    client.post(
        "/api/contacts",
        json={"name": "User1 Contact", "mobile": "1111111111"},
        headers={"Authorization": f"Bearer {token1}"}
    )
    
    # Login user 2 and create contact
    token2_response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543211", "password": "password456"}
    )
    token2 = token2_response.json()["token"]
    
    client.post(
        "/api/contacts",
        json={"name": "User2 Contact", "mobile": "2222222222"},
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    # User 1 should only see their contact
    response = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {token1}"}
    )
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "User1 Contact"
    
    # User 2 should only see their contact
    response = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {token2}"}
    )
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "User2 Contact"


# ============================================================================
# GET /api/contacts - Error Cases
# ============================================================================


def test_list_contacts_missing_auth():
    """Test listing contacts without authentication."""
    response = client.get("/api/contacts")
    assert response.status_code == 401


def test_list_contacts_invalid_token():
    """Test listing contacts with invalid token."""
    response = client.get(
        "/api/contacts",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


# ============================================================================
# PUT /api/contacts/{id} - Happy Path
# ============================================================================


def test_update_contact_name(auth_header):
    """Test updating contact name."""
    # Create contact
    create_response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "1234567890"},
        headers=auth_header
    )
    contact_id = create_response.json()["id"]
    
    # Update contact
    response = client.put(
        f"/api/contacts/{contact_id}",
        json={"name": "Jane Doe"},
        headers=auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["mobile"] == "1234567890"


def test_update_contact_mobile(auth_header):
    """Test updating contact mobile."""
    # Create contact
    create_response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "1234567890"},
        headers=auth_header
    )
    contact_id = create_response.json()["id"]
    
    # Update contact
    response = client.put(
        f"/api/contacts/{contact_id}",
        json={"mobile": "0987654321"},
        headers=auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["mobile"] == "0987654321"


def test_update_contact_both_fields(auth_header):
    """Test updating both name and mobile."""
    # Create contact
    create_response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "1234567890"},
        headers=auth_header
    )
    contact_id = create_response.json()["id"]
    
    # Update contact
    response = client.put(
        f"/api/contacts/{contact_id}",
        json={"name": "Jane Smith", "mobile": "0987654321"},
        headers=auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jane Smith"
    assert data["mobile"] == "0987654321"


# ============================================================================
# PUT /api/contacts/{id} - Error Cases
# ============================================================================


def test_update_contact_not_found(auth_header):
    """Test updating non-existent contact."""
    response = client.put(
        "/api/contacts/nonexistent",
        json={"name": "Jane Doe"},
        headers=auth_header
    )
    assert response.status_code == 404


def test_update_contact_missing_auth():
    """Test updating contact without authentication."""
    response = client.put(
        "/api/contacts/someid",
        json={"name": "Jane Doe"}
    )
    assert response.status_code == 401


def test_update_contact_invalid_token():
    """Test updating contact with invalid token."""
    response = client.put(
        "/api/contacts/someid",
        json={"name": "Jane Doe"},
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_update_contact_isolation():
    """Test that user cannot update another user's contact."""
    # Register user 1
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"}
    )
    
    # Register user 2
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543211", "password": "password456"}
    )
    
    # Login user 1 and create contact
    token1_response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"}
    )
    token1 = token1_response.json()["token"]
    
    create_response = client.post(
        "/api/contacts",
        json={"name": "User1 Contact", "mobile": "1111111111"},
        headers={"Authorization": f"Bearer {token1}"}
    )
    contact_id = create_response.json()["id"]
    
    # Login user 2
    token2_response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543211", "password": "password456"}
    )
    token2 = token2_response.json()["token"]
    
    # User 2 tries to update user 1's contact
    response = client.put(
        f"/api/contacts/{contact_id}",
        json={"name": "Hacked"},
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 404


def test_update_contact_invalid_mobile(auth_header):
    """Test updating contact with invalid mobile."""
    # Create contact
    create_response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "1234567890"},
        headers=auth_header
    )
    contact_id = create_response.json()["id"]
    
    # Try to update with invalid mobile
    response = client.put(
        f"/api/contacts/{contact_id}",
        json={"mobile": "123456789"},
        headers=auth_header
    )
    assert response.status_code == 422


# ============================================================================
# DELETE /api/contacts/{id} - Happy Path
# ============================================================================


def test_delete_contact_success(auth_header):
    """Test successful contact deletion."""
    # Create contact
    create_response = client.post(
        "/api/contacts",
        json={"name": "John Doe", "mobile": "1234567890"},
        headers=auth_header
    )
    contact_id = create_response.json()["id"]
    
    # Delete contact
    response = client.delete(f"/api/contacts/{contact_id}", headers=auth_header)
    assert response.status_code == 204
    
    # Verify contact is deleted
    list_response = client.get("/api/contacts", headers=auth_header)
    assert len(list_response.json()) == 0


# ============================================================================
# DELETE /api/contacts/{id} - Error Cases
# ============================================================================


def test_delete_contact_not_found(auth_header):
    """Test deleting non-existent contact."""
    response = client.delete("/api/contacts/nonexistent", headers=auth_header)
    assert response.status_code == 404


def test_delete_contact_missing_auth():
    """Test deleting contact without authentication."""
    response = client.delete("/api/contacts/someid")
    assert response.status_code == 401


def test_delete_contact_invalid_token():
    """Test deleting contact with invalid token."""
    response = client.delete(
        "/api/contacts/someid",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_delete_contact_isolation():
    """Test that user cannot delete another user's contact."""
    # Register user 1
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543210", "password": "password123"}
    )
    
    # Register user 2
    client.post(
        "/api/auth/register",
        json={"mobile": "9876543211", "password": "password456"}
    )
    
    # Login user 1 and create contact
    token1_response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543210", "password": "password123"}
    )
    token1 = token1_response.json()["token"]
    
    create_response = client.post(
        "/api/contacts",
        json={"name": "User1 Contact", "mobile": "1111111111"},
        headers={"Authorization": f"Bearer {token1}"}
    )
    contact_id = create_response.json()["id"]
    
    # Login user 2
    token2_response = client.post(
        "/api/auth/login",
        json={"mobile": "9876543211", "password": "password456"}
    )
    token2 = token2_response.json()["token"]
    
    # User 2 tries to delete user 1's contact
    response = client.delete(
        f"/api/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 404
    
    # Verify contact still exists for user 1
    list_response = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert len(list_response.json()) == 1


# ============================================================================
# Health Check
# ============================================================================


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
