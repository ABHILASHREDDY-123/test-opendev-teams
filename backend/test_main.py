"""
Unit Tests for Contacts API Backend
Tests cover registration, login, contact CRUD, and per-user isolation.
"""

import pytest
from fastapi.testclient import TestClient
from main import app, users_db, contacts_db, contact_counter

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """Reset in-memory database before each test."""
    users_db.clear()
    contacts_db.clear()
    contact_counter.clear()
    yield


# ============================================================================
# REGISTRATION TESTS
# ============================================================================

def test_register_success():
    """Test successful user registration."""
    response = client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert "user_id" in data
    assert data["mobile"] == "9876543210"
    assert data["message"] == "User registered successfully"


def test_register_duplicate_mobile():
    """Test registration with duplicate mobile number."""
    client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    response = client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "different_password"
    })
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


def test_register_invalid_mobile_too_short():
    """Test registration with mobile number too short."""
    response = client.post("/auth/register", json={
        "mobile": "123456789",  # 9 digits
        "password": "password123"
    })
    assert response.status_code == 422


def test_register_invalid_mobile_non_numeric():
    """Test registration with non-numeric mobile."""
    response = client.post("/auth/register", json={
        "mobile": "98765abc10",
        "password": "password123"
    })
    assert response.status_code == 422


def test_register_invalid_password_too_short():
    """Test registration with password too short."""
    response = client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "12345"  # 5 chars
    })
    assert response.status_code == 422


def test_register_valid_10_digit_mobile():
    """Test registration with exactly 10-digit mobile."""
    response = client.post("/auth/register", json={
        "mobile": "1234567890",
        "password": "password123"
    })
    assert response.status_code == 201


def test_register_valid_15_digit_mobile():
    """Test registration with 15-digit mobile."""
    response = client.post("/auth/register", json={
        "mobile": "123456789012345",
        "password": "password123"
    })
    assert response.status_code == 201


# ============================================================================
# LOGIN TESTS
# ============================================================================

def test_login_success():
    """Test successful login."""
    # Register first
    client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })

    # Login
    response = client.post("/auth/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_mobile():
    """Test login with non-existent mobile."""
    response = client.post("/auth/login", json={
        "mobile": "9999999999",
        "password": "password123"
    })
    assert response.status_code == 401
    assert "Invalid mobile or password" in response.json()["detail"]


def test_login_invalid_password():
    """Test login with wrong password."""
    client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })

    response = client.post("/auth/login", json={
        "mobile": "9876543210",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Invalid mobile or password" in response.json()["detail"]


def test_login_returns_valid_token():
    """Test that login returns a valid JWT token."""
    client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })

    response = client.post("/auth/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = response.json()["access_token"]
    assert len(token) > 0
    assert "." in token  # JWT has 3 parts separated by dots


# ============================================================================
# CONTACT CREATION TESTS
# ============================================================================

def test_create_contact_success():
    """Test successful contact creation."""
    # Register and login
    reg_response = client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    user_id = reg_response.json()["user_id"]

    login_response = client.post("/auth/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    # Create contact
    response = client.post(
        "/contacts",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["phone"] == "1234567890"
    assert "id" in data
    assert "created_at" in data


def test_create_contact_missing_auth():
    """Test contact creation without authorization header."""
    response = client.post(
        "/contacts",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890"
        }
    )
    assert response.status_code == 401


def test_create_contact_invalid_token():
    """Test contact creation with invalid token."""
    response = client.post(
        "/contacts",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890"
        },
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_create_contact_empty_name():
    """Test contact creation with empty name."""
    login_response = client.post("/auth/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    # First register
    client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/auth/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    response = client.post(
        "/contacts",
        json={
            "name": "",
            "email": "john@example.com",
            "phone": "1234567890"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


# ============================================================================
# CONTACT LIST TESTS
# ============================================================================

def test_list_contacts_empty():
    """Test listing contacts when none exist."""
    client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/auth/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    response = client.get(
        "/contacts",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == []


def test_list_contacts_multiple():
    """Test listing multiple contacts."""
    client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/auth/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    # Create 3 contacts
    for i in range(3):
        client.post(
            "/contacts",
            json={
                "name": f"Contact {i}",
                "email": f"contact{i}@example.com",
                "phone": f"123456789{i}"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

    response = client.get(
        "/contacts",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_list_contacts_missing_auth():
    """Test listing contacts without authorization."""
    response = client.get("/contacts")
    assert response.status_code == 401


# ============================================================================
# CONTACT UPDATE TESTS
# ============================================================================

def test_update_contact_success():
    """Test successful contact update."""
    client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/auth/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    # Create contact
    create_response = client.post(
        "/contacts",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    contact_id = create_response.json()["id"]

    # Update contact
    response = client.put(
        f"/contacts/{contact_id}",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "0987654321"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["email"] == "jane@example.com"
    assert data["phone"] == "0987654321"


def test_update_contact_partial():
    """Test partial contact update (only name)."""
    client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/auth/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    # Create contact
    create_response = client.post(
        "/contacts",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    contact_id = create_response.json()["id"]

    # Update only name
    response = client.put(
        f"/contacts/{contact_id}",
        json={"name": "Jane Doe"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["email"] == "john@example.com"  # Unchanged
    assert data["phone"] == "1234567890"  # Unchanged


def test_update_contact_not_found():
    """Test updating non-existent contact."""
    client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/auth/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    response = client.put(
        "/contacts/nonexistent",
        json={"name": "Jane Doe"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_contact_missing_auth():
    """Test updating contact without authorization."""
    response = client.put(
        "/contacts/contact_1",
        json={"name": "Jane Doe"}
    )
    assert response.status_code == 401


# ============================================================================
# CONTACT DELETE TESTS
# ============================================================================

def test_delete_contact_success():
    """Test successful contact deletion."""
    client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/auth/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    # Create contact
    create_response = client.post(
        "/contacts",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    contact_id = create_response.json()["id"]

    # Delete contact
    response = client.delete(
        f"/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

    # Verify contact is deleted
    list_response = client.get(
        "/contacts",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert len(list_response.json()) == 0


def test_delete_contact_not_found():
    """Test deleting non-existent contact."""
    client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/auth/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    response = client.delete(
        "/contacts/nonexistent",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


def test_delete_contact_missing_auth():
    """Test deleting contact without authorization."""
    response = client.delete("/contacts/contact_1")
    assert response.status_code == 401


# ============================================================================
# PER-USER ISOLATION TESTS
# ============================================================================

def test_user_isolation_list_contacts():
    """Test that users can only see their own contacts."""
    # Register user 1
    client.post("/auth/register", json={
        "mobile": "1111111111",
        "password": "password123"
    })
    login1 = client.post("/auth/login", json={
        "mobile": "1111111111",
        "password": "password123"
    })
    token1 = login1.json()["access_token"]

    # Register user 2
    client.post("/auth/register", json={
        "mobile": "2222222222",
        "password": "password123"
    })
    login2 = client.post("/auth/login", json={
        "mobile": "2222222222",
        "password": "password123"
    })
    token2 = login2.json()["access_token"]

    # User 1 creates 2 contacts
    client.post(
        "/contacts",
        json={"name": "User1 Contact1", "email": "u1c1@example.com", "phone": "1111111111"},
        headers={"Authorization": f"Bearer {token1}"}
    )
    client.post(
        "/contacts",
        json={"name": "User1 Contact2", "email": "u1c2@example.com", "phone": "1111111112"},
        headers={"Authorization": f"Bearer {token1}"}
    )

    # User 2 creates 1 contact
    client.post(
        "/contacts",
        json={"name": "User2 Contact1", "email": "u2c1@example.com", "phone": "2222222222"},
        headers={"Authorization": f"Bearer {token2}"}
    )

    # User 1 lists contacts - should see only 2
    response1 = client.get(
        "/contacts",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert len(response1.json()) == 2
    names1 = [c["name"] for c in response1.json()]
    assert "User1 Contact1" in names1
    assert "User1 Contact2" in names1
    assert "User2 Contact1" not in names1

    # User 2 lists contacts - should see only 1
    response2 = client.get(
        "/contacts",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert len(response2.json()) == 1
    assert response2.json()[0]["name"] == "User2 Contact1"


def test_user_isolation_update_contact():
    """Test that users cannot update other users' contacts."""
    # Register user 1
    client.post("/auth/register", json={
        "mobile": "1111111111",
        "password": "password123"
    })
    login1 = client.post("/auth/login", json={
        "mobile": "1111111111",
        "password": "password123"
    })
    token1 = login1.json()["access_token"]

    # Register user 2
    client.post("/auth/register", json={
        "mobile": "2222222222",
        "password": "password123"
    })
    login2 = client.post("/auth/login", json={
        "mobile": "2222222222",
        "password": "password123"
    })
    token2 = login2.json()["access_token"]

    # User 1 creates contact
    create_response = client.post(
        "/contacts",
        json={"name": "User1 Contact", "email": "u1@example.com", "phone": "1111111111"},
        headers={"Authorization": f"Bearer {token1}"}
    )
    contact_id = create_response.json()["id"]

    # User 2 tries to update user 1's contact
    response = client.put(
        f"/contacts/{contact_id}",
        json={"name": "Hacked Contact"},
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 404  # Contact not found for user 2


def test_user_isolation_delete_contact():
    """Test that users cannot delete other users' contacts."""
    # Register user 1
    client.post("/auth/register", json={
        "mobile": "1111111111",
        "password": "password123"
    })
    login1 = client.post("/auth/login", json={
        "mobile": "1111111111",
        "password": "password123"
    })
    token1 = login1.json()["access_token"]

    # Register user 2
    client.post("/auth/register", json={
        "mobile": "2222222222",
        "password": "password123"
    })
    login2 = client.post("/auth/login", json={
        "mobile": "2222222222",
        "password": "password123"
    })
    token2 = login2.json()["access_token"]

    # User 1 creates contact
    create_response = client.post(
        "/contacts",
        json={"name": "User1 Contact", "email": "u1@example.com", "phone": "1111111111"},
        headers={"Authorization": f"Bearer {token1}"}
    )
    contact_id = create_response.json()["id"]

    # User 2 tries to delete user 1's contact
    response = client.delete(
        f"/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 404  # Contact not found for user 2

    # Verify contact still exists for user 1
    list_response = client.get(
        "/contacts",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert len(list_response.json()) == 1


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_contact_id_uniqueness_per_user():
    """Test that contact IDs are unique within user scope."""
    client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    login_response = client.post("/auth/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    # Create 2 contacts
    response1 = client.post(
        "/contacts",
        json={"name": "Contact1", "email": "c1@example.com", "phone": "1111111111"},
        headers={"Authorization": f"Bearer {token}"}
    )
    id1 = response1.json()["id"]

    response2 = client.post(
        "/contacts",
        json={"name": "Contact2", "email": "c2@example.com", "phone": "2222222222"},
        headers={"Authorization": f"Bearer {token}"}
    )
    id2 = response2.json()["id"]

    assert id1 != id2


def test_password_hashing():
    """Test that passwords are hashed and not stored in plaintext."""
    client.post("/auth/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })

    # Check that password is hashed in database
    user = users_db["9876543210"]
    assert user.password_hash != "password123"
    assert len(user.password_hash) > len("password123")
