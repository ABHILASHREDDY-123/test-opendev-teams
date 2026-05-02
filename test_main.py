"""
Comprehensive pytest test suite for Contacts API
Tests cover happy paths, error cases, edge cases, and per-user isolation.
"""

import pytest
from fastapi.testclient import TestClient
from main import app, users_db, contacts_db

client = TestClient(app)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def reset_db():
    """Reset in-memory database before each test"""
    users_db.clear()
    contacts_db.clear()
    yield
    users_db.clear()
    contacts_db.clear()


# ============================================================================
# Registration Tests
# ============================================================================

def test_register_success():
    """Test successful user registration"""
    response = client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.json()["message"] == "User registered successfully"
    assert "9876543210" in users_db


def test_register_duplicate_mobile():
    """Test registration with duplicate mobile fails"""
    # Register first user
    client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    
    # Try to register with same mobile
    response = client.post("/register", json={
        "mobile": "9876543210",
        "password": "different123"
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_register_invalid_mobile_too_short():
    """Test registration with mobile < 10 digits fails"""
    response = client.post("/register", json={
        "mobile": "123456789",
        "password": "password123"
    })
    assert response.status_code == 422


def test_register_invalid_mobile_non_digit():
    """Test registration with non-digit mobile fails"""
    response = client.post("/register", json={
        "mobile": "9876543210a",
        "password": "password123"
    })
    assert response.status_code == 422


def test_register_invalid_password_too_short():
    """Test registration with password < 6 chars fails"""
    response = client.post("/register", json={
        "mobile": "9876543210",
        "password": "pass"
    })
    assert response.status_code == 422


def test_register_mobile_exactly_10_digits():
    """Test registration with exactly 10 digit mobile succeeds"""
    response = client.post("/register", json={
        "mobile": "1234567890",
        "password": "password123"
    })
    assert response.status_code == 201


def test_register_password_exactly_6_chars():
    """Test registration with exactly 6 char password succeeds"""
    response = client.post("/register", json={
        "mobile": "9876543210",
        "password": "pass12"
    })
    assert response.status_code == 201


# ============================================================================
# Login Tests
# ============================================================================

def test_login_success():
    """Test successful login returns JWT token"""
    # Register user
    client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    
    # Login
    response = client.post("/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_mobile():
    """Test login with unregistered mobile fails"""
    response = client.post("/login", json={
        "mobile": "9999999999",
        "password": "password123"
    })
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_invalid_password():
    """Test login with wrong password fails"""
    # Register user
    client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    
    # Try login with wrong password
    response = client.post("/login", json={
        "mobile": "9876543210",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


# ============================================================================
# Get Contacts Tests
# ============================================================================

def test_get_contacts_no_auth():
    """Test get contacts without auth header fails"""
    response = client.get("/contacts")
    assert response.status_code == 401


def test_get_contacts_invalid_token():
    """Test get contacts with invalid token fails"""
    response = client.get("/contacts", headers={
        "Authorization": "Bearer invalid_token"
    })
    assert response.status_code == 401


def test_get_contacts_empty():
    """Test get contacts returns empty list for new user"""
    # Register and login
    client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Get contacts
    response = client.get("/contacts", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json() == []


def test_get_contacts_invalid_auth_format():
    """Test get contacts with invalid auth header format fails"""
    response = client.get("/contacts", headers={
        "Authorization": "InvalidFormat token"
    })
    assert response.status_code == 401


# ============================================================================
# Create Contact Tests
# ============================================================================

def test_create_contact_success():
    """Test successful contact creation"""
    # Register and login
    client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Create contact
    response = client.post("/contacts", json={
        "name": "John Doe",
        "mobile": "9999999999"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["mobile"] == "9999999999"
    assert "id" in data


def test_create_contact_no_auth():
    """Test create contact without auth fails"""
    response = client.post("/contacts", json={
        "name": "John Doe",
        "mobile": "9999999999"
    })
    assert response.status_code == 401


def test_create_contact_invalid_mobile():
    """Test create contact with invalid mobile fails"""
    # Register and login
    client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Try to create contact with invalid mobile
    response = client.post("/contacts", json={
        "name": "John Doe",
        "mobile": "123"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 422


def test_create_contact_empty_name():
    """Test create contact with empty name fails"""
    # Register and login
    client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Try to create contact with empty name
    response = client.post("/contacts", json={
        "name": "",
        "mobile": "9999999999"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 422


# ============================================================================
# Update Contact Tests
# ============================================================================

def test_update_contact_success():
    """Test successful contact update"""
    # Register, login, create contact
    client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    create_response = client.post("/contacts", json={
        "name": "John Doe",
        "mobile": "9999999999"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    contact_id = create_response.json()["id"]
    
    # Update contact
    response = client.put(f"/contacts/{contact_id}", json={
        "name": "Jane Doe",
        "mobile": "8888888888"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["mobile"] == "8888888888"


def test_update_contact_partial():
    """Test partial contact update (only name)"""
    # Register, login, create contact
    client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    create_response = client.post("/contacts", json={
        "name": "John Doe",
        "mobile": "9999999999"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    contact_id = create_response.json()["id"]
    
    # Update only name
    response = client.put(f"/contacts/{contact_id}", json={
        "name": "Jane Doe"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["mobile"] == "9999999999"


def test_update_contact_not_found():
    """Test update non-existent contact fails"""
    # Register and login
    client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Try to update non-existent contact
    response = client.put("/contacts/nonexistent", json={
        "name": "Jane Doe"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 404


def test_update_contact_no_auth():
    """Test update contact without auth fails"""
    response = client.put("/contacts/someid", json={
        "name": "Jane Doe"
    })
    assert response.status_code == 401


# ============================================================================
# Delete Contact Tests
# ============================================================================

def test_delete_contact_success():
    """Test successful contact deletion"""
    # Register, login, create contact
    client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    create_response = client.post("/contacts", json={
        "name": "John Doe",
        "mobile": "9999999999"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    contact_id = create_response.json()["id"]
    
    # Delete contact
    response = client.delete(f"/contacts/{contact_id}", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # Verify contact is deleted
    get_response = client.get("/contacts", headers={
        "Authorization": f"Bearer {token}"
    })
    assert len(get_response.json()) == 0


def test_delete_contact_not_found():
    """Test delete non-existent contact fails"""
    # Register and login
    client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Try to delete non-existent contact
    response = client.delete("/contacts/nonexistent", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 404


def test_delete_contact_no_auth():
    """Test delete contact without auth fails"""
    response = client.delete("/contacts/someid")
    assert response.status_code == 401


# ============================================================================
# Per-User Isolation Tests (CRITICAL)
# ============================================================================

def test_user_a_cannot_see_user_b_contacts():
    """Test User A cannot see User B's contacts"""
    # Register User A
    client.post("/register", json={
        "mobile": "1111111111",
        "password": "password123"
    })
    login_a = client.post("/login", json={
        "mobile": "1111111111",
        "password": "password123"
    })
    token_a = login_a.json()["access_token"]
    
    # Register User B
    client.post("/register", json={
        "mobile": "2222222222",
        "password": "password123"
    })
    login_b = client.post("/login", json={
        "mobile": "2222222222",
        "password": "password123"
    })
    token_b = login_b.json()["access_token"]
    
    # User A creates a contact
    client.post("/contacts", json={
        "name": "Contact A",
        "mobile": "9999999999"
    }, headers={
        "Authorization": f"Bearer {token_a}"
    })
    
    # User B should not see User A's contact
    response_b = client.get("/contacts", headers={
        "Authorization": f"Bearer {token_b}"
    })
    assert response_b.status_code == 200
    assert len(response_b.json()) == 0


def test_user_a_cannot_modify_user_b_contact():
    """Test User A cannot modify User B's contact"""
    # Register User A
    client.post("/register", json={
        "mobile": "1111111111",
        "password": "password123"
    })
    login_a = client.post("/login", json={
        "mobile": "1111111111",
        "password": "password123"
    })
    token_a = login_a.json()["access_token"]
    
    # Register User B
    client.post("/register", json={
        "mobile": "2222222222",
        "password": "password123"
    })
    login_b = client.post("/login", json={
        "mobile": "2222222222",
        "password": "password123"
    })
    token_b = login_b.json()["access_token"]
    
    # User A creates a contact
    create_response = client.post("/contacts", json={
        "name": "Contact A",
        "mobile": "9999999999"
    }, headers={
        "Authorization": f"Bearer {token_a}"
    })
    contact_id = create_response.json()["id"]
    
    # User B tries to update User A's contact
    response = client.put(f"/contacts/{contact_id}", json={
        "name": "Hacked Contact"
    }, headers={
        "Authorization": f"Bearer {token_b}"
    })
    assert response.status_code == 404


def test_user_a_cannot_delete_user_b_contact():
    """Test User A cannot delete User B's contact"""
    # Register User A
    client.post("/register", json={
        "mobile": "1111111111",
        "password": "password123"
    })
    login_a = client.post("/login", json={
        "mobile": "1111111111",
        "password": "password123"
    })
    token_a = login_a.json()["access_token"]
    
    # Register User B
    client.post("/register", json={
        "mobile": "2222222222",
        "password": "password123"
    })
    login_b = client.post("/login", json={
        "mobile": "2222222222",
        "password": "password123"
    })
    token_b = login_b.json()["access_token"]
    
    # User A creates a contact
    create_response = client.post("/contacts", json={
        "name": "Contact A",
        "mobile": "9999999999"
    }, headers={
        "Authorization": f"Bearer {token_a}"
    })
    contact_id = create_response.json()["id"]
    
    # User B tries to delete User A's contact
    response = client.delete(f"/contacts/{contact_id}", headers={
        "Authorization": f"Bearer {token_b}"
    })
    assert response.status_code == 404
    
    # Verify User A's contact still exists
    get_response = client.get("/contacts", headers={
        "Authorization": f"Bearer {token_a}"
    })
    assert len(get_response.json()) == 1


def test_multiple_users_independent_contacts():
    """Test multiple users can have independent contacts"""
    # Register User A
    client.post("/register", json={
        "mobile": "1111111111",
        "password": "password123"
    })
    login_a = client.post("/login", json={
        "mobile": "1111111111",
        "password": "password123"
    })
    token_a = login_a.json()["access_token"]
    
    # Register User B
    client.post("/register", json={
        "mobile": "2222222222",
        "password": "password123"
    })
    login_b = client.post("/login", json={
        "mobile": "2222222222",
        "password": "password123"
    })
    token_b = login_b.json()["access_token"]
    
    # User A creates 2 contacts
    client.post("/contacts", json={
        "name": "Contact A1",
        "mobile": "9999999999"
    }, headers={
        "Authorization": f"Bearer {token_a}"
    })
    client.post("/contacts", json={
        "name": "Contact A2",
        "mobile": "8888888888"
    }, headers={
        "Authorization": f"Bearer {token_a}"
    })
    
    # User B creates 1 contact
    client.post("/contacts", json={
        "name": "Contact B1",
        "mobile": "7777777777"
    }, headers={
        "Authorization": f"Bearer {token_b}"
    })
    
    # Verify User A has 2 contacts
    response_a = client.get("/contacts", headers={
        "Authorization": f"Bearer {token_a}"
    })
    assert len(response_a.json()) == 2
    
    # Verify User B has 1 contact
    response_b = client.get("/contacts", headers={
        "Authorization": f"Bearer {token_b}"
    })
    assert len(response_b.json()) == 1


# ============================================================================
# Edge Cases
# ============================================================================

def test_contact_with_max_length_name():
    """Test creating contact with maximum length name"""
    # Register and login
    client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Create contact with 100 char name
    long_name = "a" * 100
    response = client.post("/contacts", json={
        "name": long_name,
        "mobile": "9999999999"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 201


def test_contact_with_15_digit_mobile():
    """Test creating contact with maximum length mobile"""
    # Register and login
    client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Create contact with 15 digit mobile
    response = client.post("/contacts", json={
        "name": "John Doe",
        "mobile": "123456789012345"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 201


def test_multiple_contacts_same_mobile():
    """Test creating multiple contacts with same mobile (allowed)"""
    # Register and login
    client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Create two contacts with same mobile
    response1 = client.post("/contacts", json={
        "name": "John Doe",
        "mobile": "9999999999"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    response2 = client.post("/contacts", json={
        "name": "Jane Doe",
        "mobile": "9999999999"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response1.status_code == 201
    assert response2.status_code == 201
    
    # Verify both contacts exist
    get_response = client.get("/contacts", headers={
        "Authorization": f"Bearer {token}"
    })
    assert len(get_response.json()) == 2
