"""
Comprehensive unit tests for Contacts API
Tests cover happy paths, error cases, and edge cases
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from main import app, users_db, contacts_db

# ============================================================================
# Test Fixtures
# ============================================================================
@pytest.fixture(autouse=True)
def clear_db():
    """Clear in-memory databases before each test"""
    users_db.clear()
    contacts_db.clear()
    yield
    users_db.clear()
    contacts_db.clear()

client = TestClient(app)

# ============================================================================
# Helper Functions
# ============================================================================
def register_user(mobile="9876543210", password="password123"):
    """Helper to register a user"""
    response = client.post(
        "/api/auth/register",
        json={"mobile": mobile, "password": password}
    )
    return response

def login_user(mobile="9876543210", password="password123"):
    """Helper to login a user and return token"""
    response = client.post(
        "/api/auth/login",
        json={"mobile": mobile, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def get_auth_header(token):
    """Helper to create Authorization header"""
    return {"Authorization": f"Bearer {token}"}

# ============================================================================
# Registration Tests
# ============================================================================
class TestRegistration:
    def test_register_success(self):
        """Test successful user registration"""
        response = register_user()
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["mobile"] == "9876543210"
        assert "password" not in data

    def test_register_invalid_mobile_too_short(self):
        """Test registration with mobile < 10 digits"""
        response = register_user(mobile="123456789")
        assert response.status_code == 422

    def test_register_invalid_mobile_non_digits(self):
        """Test registration with non-digit mobile"""
        response = register_user(mobile="98765abc10")
        assert response.status_code == 422

    def test_register_invalid_password_too_short(self):
        """Test registration with password < 6 chars"""
        response = register_user(password="pass")
        assert response.status_code == 422

    def test_register_duplicate_mobile(self):
        """Test registration with duplicate mobile"""
        register_user(mobile="9876543210")
        response = register_user(mobile="9876543210")
        assert response.status_code == 409

    def test_register_multiple_users(self):
        """Test registering multiple users"""
        r1 = register_user(mobile="9876543210")
        r2 = register_user(mobile="9876543211")
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["id"] != r2.json()["id"]

# ============================================================================
# Login Tests
# ============================================================================
class TestLogin:
    def test_login_success(self):
        """Test successful login"""
        register_user()
        response = client.post(
            "/api/auth/login",
            json={"mobile": "9876543210", "password": "password123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_invalid_mobile(self):
        """Test login with non-existent mobile"""
        response = client.post(
            "/api/auth/login",
            json={"mobile": "9999999999", "password": "password123"}
        )
        assert response.status_code == 401

    def test_login_invalid_password(self):
        """Test login with wrong password"""
        register_user()
        response = client.post(
            "/api/auth/login",
            json={"mobile": "9876543210", "password": "wrongpassword"}
        )
        assert response.status_code == 401

    def test_login_returns_valid_token(self):
        """Test that login returns a valid JWT token"""
        register_user()
        token = login_user()
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

# ============================================================================
# Create Contact Tests
# ============================================================================
class TestCreateContact:
    def test_create_contact_success(self):
        """Test successful contact creation"""
        register_user()
        token = login_user()
        response = client.post(
            "/api/contacts",
            json={"name": "John Doe", "mobile": "9876543211"},
            headers=get_auth_header(token)
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["mobile"] == "9876543211"
        assert "id" in data
        assert "user_id" in data

    def test_create_contact_no_auth(self):
        """Test contact creation without authentication"""
        response = client.post(
            "/api/contacts",
            json={"name": "John Doe", "mobile": "9876543211"}
        )
        assert response.status_code == 401

    def test_create_contact_invalid_token(self):
        """Test contact creation with invalid token"""
        response = client.post(
            "/api/contacts",
            json={"name": "John Doe", "mobile": "9876543211"},
            headers=get_auth_header("invalid_token")
        )
        assert response.status_code == 401

    def test_create_contact_empty_name(self):
        """Test contact creation with empty name"""
        register_user()
        token = login_user()
        response = client.post(
            "/api/contacts",
            json={"name": "", "mobile": "9876543211"},
            headers=get_auth_header(token)
        )
        assert response.status_code == 422

    def test_create_contact_invalid_mobile_too_short(self):
        """Test contact creation with mobile < 10 digits"""
        register_user()
        token = login_user()
        response = client.post(
            "/api/contacts",
            json={"name": "John Doe", "mobile": "123456789"},
            headers=get_auth_header(token)
        )
        assert response.status_code == 422

    def test_create_contact_invalid_mobile_non_digits(self):
        """Test contact creation with non-digit mobile"""
        register_user()
        token = login_user()
        response = client.post(
            "/api/contacts",
            json={"name": "John Doe", "mobile": "98765abc11"},
            headers=get_auth_header(token)
        )
        assert response.status_code == 422

    def test_create_multiple_contacts(self):
        """Test creating multiple contacts for same user"""
        register_user()
        token = login_user()
        r1 = client.post(
            "/api/contacts",
            json={"name": "John Doe", "mobile": "9876543211"},
            headers=get_auth_header(token)
        )
        r2 = client.post(
            "/api/contacts",
            json={"name": "Jane Doe", "mobile": "9876543212"},
            headers=get_auth_header(token)
        )
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["id"] != r2.json()["id"]

# ============================================================================
# List Contacts Tests
# ============================================================================
class TestListContacts:
    def test_list_contacts_empty(self):
        """Test listing contacts when none exist"""
        register_user()
        token = login_user()
        response = client.get(
            "/api/contacts",
            headers=get_auth_header(token)
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_list_contacts_success(self):
        """Test listing user's contacts"""
        register_user()
        token = login_user()
        # Create contacts
        client.post(
            "/api/contacts",
            json={"name": "John Doe", "mobile": "9876543211"},
            headers=get_auth_header(token)
        )
        client.post(
            "/api/contacts",
            json={"name": "Jane Doe", "mobile": "9876543212"},
            headers=get_auth_header(token)
        )
        # List contacts
        response = client.get(
            "/api/contacts",
            headers=get_auth_header(token)
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] in ["John Doe", "Jane Doe"]
        assert data[1]["name"] in ["John Doe", "Jane Doe"]

    def test_list_contacts_no_auth(self):
        """Test listing contacts without authentication"""
        response = client.get("/api/contacts")
        assert response.status_code == 401

    def test_list_contacts_invalid_token(self):
        """Test listing contacts with invalid token"""
        response = client.get(
            "/api/contacts",
            headers=get_auth_header("invalid_token")
        )
        assert response.status_code == 401

    def test_list_contacts_per_user_isolation(self):
        """Test that users only see their own contacts"""
        # Register and create contacts for user 1
        register_user(mobile="9876543210")
        token1 = login_user(mobile="9876543210")
        client.post(
            "/api/contacts",
            json={"name": "User1 Contact", "mobile": "9876543211"},
            headers=get_auth_header(token1)
        )
        
        # Register and create contacts for user 2
        register_user(mobile="9876543220")
        token2 = login_user(mobile="9876543220")
        client.post(
            "/api/contacts",
            json={"name": "User2 Contact", "mobile": "9876543221"},
            headers=get_auth_header(token2)
        )
        
        # User 1 should only see their contact
        response1 = client.get(
            "/api/contacts",
            headers=get_auth_header(token1)
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1) == 1
        assert data1[0]["name"] == "User1 Contact"
        
        # User 2 should only see their contact
        response2 = client.get(
            "/api/contacts",
            headers=get_auth_header(token2)
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 1
        assert data2[0]["name"] == "User2 Contact"

# ============================================================================
# Update Contact Tests
# ============================================================================
class TestUpdateContact:
    def test_update_contact_success(self):
        """Test successful contact update"""
        register_user()
        token = login_user()
        # Create contact
        create_response = client.post(
            "/api/contacts",
            json={"name": "John Doe", "mobile": "9876543211"},
            headers=get_auth_header(token)
        )
        contact_id = create_response.json()["id"]
        # Update contact
        response = client.put(
            f"/api/contacts/{contact_id}",
            json={"name": "Jane Doe", "mobile": "9876543212"},
            headers=get_auth_header(token)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane Doe"
        assert data["mobile"] == "9876543212"

    def test_update_contact_no_auth(self):
        """Test updating contact without authentication"""
        response = client.put(
            "/api/contacts/some-id",
            json={"name": "John Doe", "mobile": "9876543211"}
        )
        assert response.status_code == 401

    def test_update_contact_not_found(self):
        """Test updating non-existent contact"""
        register_user()
        token = login_user()
        response = client.put(
            "/api/contacts/non-existent-id",
            json={"name": "John Doe", "mobile": "9876543211"},
            headers=get_auth_header(token)
        )
        assert response.status_code == 404

    def test_update_contact_not_owner(self):
        """Test updating contact owned by another user"""
        # User 1 creates contact
        register_user(mobile="9876543210")
        token1 = login_user(mobile="9876543210")
        create_response = client.post(
            "/api/contacts",
            json={"name": "User1 Contact", "mobile": "9876543211"},
            headers=get_auth_header(token1)
        )
        contact_id = create_response.json()["id"]
        
        # User 2 tries to update it
        register_user(mobile="9876543220")
        token2 = login_user(mobile="9876543220")
        response = client.put(
            f"/api/contacts/{contact_id}",
            json={"name": "Hacked", "mobile": "9876543212"},
            headers=get_auth_header(token2)
        )
        assert response.status_code == 403

    def test_update_contact_empty_name(self):
        """Test updating contact with empty name"""
        register_user()
        token = login_user()
        # Create contact
        create_response = client.post(
            "/api/contacts",
            json={"name": "John Doe", "mobile": "9876543211"},
            headers=get_auth_header(token)
        )
        contact_id = create_response.json()["id"]
        # Try to update with empty name
        response = client.put(
            f"/api/contacts/{contact_id}",
            json={"name": "", "mobile": "9876543212"},
            headers=get_auth_header(token)
        )
        assert response.status_code == 422

    def test_update_contact_invalid_mobile(self):
        """Test updating contact with invalid mobile"""
        register_user()
        token = login_user()
        # Create contact
        create_response = client.post(
            "/api/contacts",
            json={"name": "John Doe", "mobile": "9876543211"},
            headers=get_auth_header(token)
        )
        contact_id = create_response.json()["id"]
        # Try to update with invalid mobile
        response = client.put(
            f"/api/contacts/{contact_id}",
            json={"name": "Jane Doe", "mobile": "123"},
            headers=get_auth_header(token)
        )
        assert response.status_code == 422

# ============================================================================
# Delete Contact Tests
# ============================================================================
class TestDeleteContact:
    def test_delete_contact_success(self):
        """Test successful contact deletion"""
        register_user()
        token = login_user()
        # Create contact
        create_response = client.post(
            "/api/contacts",
            json={"name": "John Doe", "mobile": "9876543211"},
            headers=get_auth_header(token)
        )
        contact_id = create_response.json()["id"]
        # Delete contact
        response = client.delete(
            f"/api/contacts/{contact_id}",
            headers=get_auth_header(token)
        )
        assert response.status_code == 204
        # Verify it's deleted
        list_response = client.get(
            "/api/contacts",
            headers=get_auth_header(token)
        )
        assert len(list_response.json()) == 0

    def test_delete_contact_no_auth(self):
        """Test deleting contact without authentication"""
        response = client.delete("/api/contacts/some-id")
        assert response.status_code == 401

    def test_delete_contact_not_found(self):
        """Test deleting non-existent contact"""
        register_user()
        token = login_user()
        response = client.delete(
            "/api/contacts/non-existent-id",
            headers=get_auth_header(token)
        )
        assert response.status_code == 404

    def test_delete_contact_not_owner(self):
        """Test deleting contact owned by another user"""
        # User 1 creates contact
        register_user(mobile="9876543210")
        token1 = login_user(mobile="9876543210")
        create_response = client.post(
            "/api/contacts",
            json={"name": "User1 Contact", "mobile": "9876543211"},
            headers=get_auth_header(token1)
        )
        contact_id = create_response.json()["id"]
        
        # User 2 tries to delete it
        register_user(mobile="9876543220")
        token2 = login_user(mobile="9876543220")
        response = client.delete(
            f"/api/contacts/{contact_id}",
            headers=get_auth_header(token2)
        )
        assert response.status_code == 403

# ============================================================================
# Integration Tests
# ============================================================================
class TestIntegration:
    def test_full_workflow(self):
        """Test complete workflow: register, login, create, list, update, delete"""
        # Register
        reg_response = register_user()
        assert reg_response.status_code == 201
        user_id = reg_response.json()["id"]
        
        # Login
        token = login_user()
        assert token is not None
        
        # Create contact
        create_response = client.post(
            "/api/contacts",
            json={"name": "John Doe", "mobile": "9876543211"},
            headers=get_auth_header(token)
        )
        assert create_response.status_code == 201
        contact_id = create_response.json()["id"]
        
        # List contacts
        list_response = client.get(
            "/api/contacts",
            headers=get_auth_header(token)
        )
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1
        
        # Update contact
        update_response = client.put(
            f"/api/contacts/{contact_id}",
            json={"name": "Jane Doe", "mobile": "9876543212"},
            headers=get_auth_header(token)
        )
        assert update_response.status_code == 200
        
        # Delete contact
        delete_response = client.delete(
            f"/api/contacts/{contact_id}",
            headers=get_auth_header(token)
        )
        assert delete_response.status_code == 204
        
        # Verify deletion
        final_list = client.get(
            "/api/contacts",
            headers=get_auth_header(token)
        )
        assert len(final_list.json()) == 0

    def test_multiple_users_isolation(self):
        """Test complete isolation between multiple users"""
        # User 1 setup
        register_user(mobile="9876543210")
        token1 = login_user(mobile="9876543210")
        c1_response = client.post(
            "/api/contacts",
            json={"name": "Contact1", "mobile": "9876543211"},
            headers=get_auth_header(token1)
        )
        contact1_id = c1_response.json()["id"]
        
        # User 2 setup
        register_user(mobile="9876543220")
        token2 = login_user(mobile="9876543220")
        c2_response = client.post(
            "/api/contacts",
            json={"name": "Contact2", "mobile": "9876543221"},
            headers=get_auth_header(token2)
        )
        contact2_id = c2_response.json()["id"]
        
        # User 1 lists - should see only their contact
        list1 = client.get(
            "/api/contacts",
            headers=get_auth_header(token1)
        )
        assert len(list1.json()) == 1
        assert list1.json()[0]["id"] == contact1_id
        
        # User 2 lists - should see only their contact
        list2 = client.get(
            "/api/contacts",
            headers=get_auth_header(token2)
        )
        assert len(list2.json()) == 1
        assert list2.json()[0]["id"] == contact2_id
        
        # User 1 cannot update User 2's contact
        update_fail = client.put(
            f"/api/contacts/{contact2_id}",
            json={"name": "Hacked", "mobile": "9999999999"},
            headers=get_auth_header(token1)
        )
        assert update_fail.status_code == 403
        
        # User 1 cannot delete User 2's contact
        delete_fail = client.delete(
            f"/api/contacts/{contact2_id}",
            headers=get_auth_header(token1)
        )
        assert delete_fail.status_code == 403
        
        # User 2's contact should still exist
        list2_final = client.get(
            "/api/contacts",
            headers=get_auth_header(token2)
        )
        assert len(list2_final.json()) == 1
