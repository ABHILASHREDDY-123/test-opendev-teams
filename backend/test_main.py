"""
Comprehensive pytest tests for Contacts API.
Tests all 6 endpoints with happy paths, error cases, and edge cases.
"""

import pytest
from fastapi.testclient import TestClient
from main import app, users_db, mobile_to_user, contacts_db

client = TestClient(app)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def clear_db():
    """Clear in-memory databases before each test."""
    users_db.clear()
    mobile_to_user.clear()
    contacts_db.clear()
    yield
    users_db.clear()
    mobile_to_user.clear()
    contacts_db.clear()


@pytest.fixture
def registered_user():
    """Create a registered user and return mobile, password, and token."""
    mobile = "9876543210"
    password = "password123"
    
    response = client.post("/api/auth/register", json={
        "mobile": mobile,
        "password": password,
    })
    
    assert response.status_code == 201
    data = response.json()
    token = data["access_token"]
    
    return {
        "mobile": mobile,
        "password": password,
        "token": token,
        "user_id": data["user"]["id"],
    }


@pytest.fixture
def second_user():
    """Create a second registered user."""
    mobile = "9123456789"
    password = "password456"
    
    response = client.post("/api/auth/register", json={
        "mobile": mobile,
        "password": password,
    })
    
    assert response.status_code == 201
    data = response.json()
    token = data["access_token"]
    
    return {
        "mobile": mobile,
        "password": password,
        "token": token,
        "user_id": data["user"]["id"],
    }


# ============================================================================
# Auth Tests - Register
# ============================================================================

class TestRegister:
    """Tests for POST /api/auth/register"""
    
    def test_register_success(self):
        """Happy path: successful registration."""
        response = client.post("/api/auth/register", json={
            "mobile": "9876543210",
            "password": "password123",
        })
        
        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["mobile"] == "9876543210"
        assert "id" in data["user"]
    
    def test_register_mobile_too_short(self):
        """Error: mobile less than 10 digits."""
        response = client.post("/api/auth/register", json={
            "mobile": "123456789",  # 9 digits
            "password": "password123",
        })
        
        assert response.status_code == 422
    
    def test_register_mobile_non_digits(self):
        """Error: mobile contains non-digit characters."""
        response = client.post("/api/auth/register", json={
            "mobile": "987654321a",
            "password": "password123",
        })
        
        assert response.status_code == 422
    
    def test_register_password_too_short(self):
        """Error: password less than 6 characters."""
        response = client.post("/api/auth/register", json={
            "mobile": "9876543210",
            "password": "pass",  # 4 chars
        })
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_register_duplicate_mobile(self):
        """Error: mobile already registered."""
        mobile = "9876543210"
        
        # First registration
        response1 = client.post("/api/auth/register", json={
            "mobile": mobile,
            "password": "password123",
        })
        assert response1.status_code == 201
        
        # Second registration with same mobile
        response2 = client.post("/api/auth/register", json={
            "mobile": mobile,
            "password": "password456",
        })
        
        assert response2.status_code == 400
        assert "Mobile already registered" in response2.json()["detail"]
    
    def test_register_returns_valid_token(self, registered_user):
        """Verify returned token can be used for authenticated requests."""
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        
        # Should not get 401 Unauthorized
        assert response.status_code != 401


# ============================================================================
# Auth Tests - Login
# ============================================================================

class TestLogin:
    """Tests for POST /api/auth/login"""
    
    def test_login_success(self, registered_user):
        """Happy path: successful login."""
        response = client.post("/api/auth/login", json={
            "mobile": registered_user["mobile"],
            "password": registered_user["password"],
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_mobile(self):
        """Error: mobile not registered."""
        response = client.post("/api/auth/login", json={
            "mobile": "9999999999",
            "password": "password123",
        })
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_invalid_password(self, registered_user):
        """Error: wrong password."""
        response = client.post("/api/auth/login", json={
            "mobile": registered_user["mobile"],
            "password": "wrongpassword",
        })
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_returns_valid_token(self, registered_user):
        """Verify login token can be used for authenticated requests."""
        response = client.post("/api/auth/login", json={
            "mobile": registered_user["mobile"],
            "password": registered_user["password"],
        })
        
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        # Use token to access protected endpoint
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200


# ============================================================================
# Contacts Tests - Create
# ============================================================================

class TestCreateContact:
    """Tests for POST /api/contacts"""
    
    def test_create_contact_success(self, registered_user):
        """Happy path: create contact."""
        response = client.post(
            "/api/contacts",
            json={
                "name": "John Doe",
                "mobile": "9123456789",
            },
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["mobile"] == "9123456789"
        assert "id" in data
        assert "created_at" in data
        assert data["user_id"] == registered_user["user_id"]
    
    def test_create_contact_no_token(self):
        """Error: missing authorization header."""
        response = client.post(
            "/api/contacts",
            json={
                "name": "John Doe",
                "mobile": "9123456789",
            },
        )
        
        assert response.status_code == 401
        assert "Missing authorization header" in response.json()["detail"]
    
    def test_create_contact_invalid_token(self):
        """Error: invalid token."""
        response = client.post(
            "/api/contacts",
            json={
                "name": "John Doe",
                "mobile": "9123456789",
            },
            headers={"Authorization": "Bearer invalid_token"},
        )
        
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]
    
    def test_create_contact_mobile_too_short(self, registered_user):
        """Error: contact mobile less than 10 digits."""
        response = client.post(
            "/api/contacts",
            json={
                "name": "John Doe",
                "mobile": "123456789",
            },
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        
        assert response.status_code == 422
    
    def test_create_contact_mobile_non_digits(self, registered_user):
        """Error: contact mobile contains non-digits."""
        response = client.post(
            "/api/contacts",
            json={
                "name": "John Doe",
                "mobile": "912345678a",
            },
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        
        assert response.status_code == 422
    
    def test_create_contact_empty_name(self, registered_user):
        """Error: empty contact name."""
        response = client.post(
            "/api/contacts",
            json={
                "name": "",
                "mobile": "9123456789",
            },
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_create_multiple_contacts(self, registered_user):
        """Create multiple contacts for same user."""
        for i in range(3):
            response = client.post(
                "/api/contacts",
                json={
                    "name": f"Contact {i}",
                    "mobile": f"912345678{i}",
                },
                headers={"Authorization": f"Bearer {registered_user['token']}"},
            )
            assert response.status_code == 201
        
        # Verify all created
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 3


# ============================================================================
# Contacts Tests - List
# ============================================================================

class TestListContacts:
    """Tests for GET /api/contacts"""
    
    def test_list_contacts_empty(self, registered_user):
        """Happy path: list contacts when none exist."""
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_contacts_with_data(self, registered_user):
        """Happy path: list contacts with data."""
        # Create contacts
        client.post(
            "/api/contacts",
            json={"name": "Contact 1", "mobile": "9123456789"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        client.post(
            "/api/contacts",
            json={"name": "Contact 2", "mobile": "9987654321"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        
        # List contacts
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Contact 1"
        assert data[1]["name"] == "Contact 2"
    
    def test_list_contacts_no_token(self):
        """Error: missing authorization header."""
        response = client.get("/api/contacts")
        
        assert response.status_code == 401
        assert "Missing authorization header" in response.json()["detail"]
    
    def test_list_contacts_invalid_token(self):
        """Error: invalid token."""
        response = client.get(
            "/api/contacts",
            headers={"Authorization": "Bearer invalid_token"},
        )
        
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]
    
    def test_list_contacts_per_user_isolation(self, registered_user, second_user):
        """Verify per-user isolation: users only see their own contacts."""
        # User 1 creates contacts
        client.post(
            "/api/contacts",
            json={"name": "User1 Contact", "mobile": "9111111111"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        
        # User 2 creates contacts
        client.post(
            "/api/contacts",
            json={"name": "User2 Contact", "mobile": "9222222222"},
            headers={"Authorization": f"Bearer {second_user['token']}"},
        )
        
        # User 1 lists contacts
        response1 = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        
        # User 2 lists contacts
        response2 = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {second_user['token']}"},
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        assert len(data1) == 1
        assert len(data2) == 1
        assert data1[0]["name"] == "User1 Contact"
        assert data2[0]["name"] == "User2 Contact"


# ============================================================================
# Contacts Tests - Update
# ============================================================================

class TestUpdateContact:
    """Tests for PUT /api/contacts/{contact_id}"""
    
    def test_update_contact_success(self, registered_user):
        """Happy path: update contact."""
        # Create contact
        create_response = client.post(
            "/api/contacts",
            json={"name": "Old Name", "mobile": "9123456789"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        contact_id = create_response.json()["id"]
        
        # Update contact
        response = client.put(
            f"/api/contacts/{contact_id}",
            json={"name": "New Name", "mobile": "9987654321"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["mobile"] == "9987654321"
        assert data["id"] == contact_id
    
    def test_update_contact_no_token(self, registered_user):
        """Error: missing authorization header."""
        create_response = client.post(
            "/api/contacts",
            json={"name": "Contact", "mobile": "9123456789"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        contact_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/contacts/{contact_id}",
            json={"name": "New Name", "mobile": "9987654321"},
        )
        
        assert response.status_code == 401
        assert "Missing authorization header" in response.json()["detail"]
    
    def test_update_contact_not_found(self, registered_user):
        """Error: contact does not exist."""
        response = client.put(
            "/api/contacts/nonexistent_id",
            json={"name": "New Name", "mobile": "9987654321"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        
        assert response.status_code == 404
        assert "Contact not found" in response.json()["detail"]
    
    def test_update_contact_not_owner(self, registered_user, second_user):
        """Error: user tries to update another user's contact."""
        # User 1 creates contact
        create_response = client.post(
            "/api/contacts",
            json={"name": "Contact", "mobile": "9123456789"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        contact_id = create_response.json()["id"]
        
        # User 2 tries to update it
        response = client.put(
            f"/api/contacts/{contact_id}",
            json={"name": "New Name", "mobile": "9987654321"},
            headers={"Authorization": f"Bearer {second_user['token']}"},
        )
        
        assert response.status_code == 403
        assert "You can only update your own contacts" in response.json()["detail"]
    
    def test_update_contact_invalid_mobile(self, registered_user):
        """Error: invalid mobile format."""
        create_response = client.post(
            "/api/contacts",
            json={"name": "Contact", "mobile": "9123456789"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        contact_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/contacts/{contact_id}",
            json={"name": "New Name", "mobile": "123456789"},  # Too short
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        
        assert response.status_code == 422


# ============================================================================
# Contacts Tests - Delete
# ============================================================================

class TestDeleteContact:
    """Tests for DELETE /api/contacts/{contact_id}"""
    
    def test_delete_contact_success(self, registered_user):
        """Happy path: delete contact."""
        # Create contact
        create_response = client.post(
            "/api/contacts",
            json={"name": "Contact", "mobile": "9123456789"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        contact_id = create_response.json()["id"]
        
        # Delete contact
        response = client.delete(
            f"/api/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        
        assert response.status_code == 204
        
        # Verify deleted
        list_response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        assert len(list_response.json()) == 0
    
    def test_delete_contact_no_token(self, registered_user):
        """Error: missing authorization header."""
        create_response = client.post(
            "/api/contacts",
            json={"name": "Contact", "mobile": "9123456789"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        contact_id = create_response.json()["id"]
        
        response = client.delete(f"/api/contacts/{contact_id}")
        
        assert response.status_code == 401
        assert "Missing authorization header" in response.json()["detail"]
    
    def test_delete_contact_not_found(self, registered_user):
        """Error: contact does not exist."""
        response = client.delete(
            "/api/contacts/nonexistent_id",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        
        assert response.status_code == 404
        assert "Contact not found" in response.json()["detail"]
    
    def test_delete_contact_not_owner(self, registered_user, second_user):
        """Error: user tries to delete another user's contact."""
        # User 1 creates contact
        create_response = client.post(
            "/api/contacts",
            json={"name": "Contact", "mobile": "9123456789"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        contact_id = create_response.json()["id"]
        
        # User 2 tries to delete it
        response = client.delete(
            f"/api/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {second_user['token']}"},
        )
        
        assert response.status_code == 403
        assert "You can only delete your own contacts" in response.json()["detail"]
    
    def test_delete_contact_twice(self, registered_user):
        """Error: delete same contact twice."""
        # Create contact
        create_response = client.post(
            "/api/contacts",
            json={"name": "Contact", "mobile": "9123456789"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        contact_id = create_response.json()["id"]
        
        # Delete first time
        response1 = client.delete(
            f"/api/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        assert response1.status_code == 204
        
        # Delete second time
        response2 = client.delete(
            f"/api/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        assert response2.status_code == 404


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_workflow(self):
        """Complete workflow: register, create contacts, update, delete."""
        # Register
        reg_response = client.post("/api/auth/register", json={
            "mobile": "9876543210",
            "password": "password123",
        })
        assert reg_response.status_code == 201
        token = reg_response.json()["access_token"]
        
        # Create contact
        create_response = client.post(
            "/api/contacts",
            json={"name": "John", "mobile": "9123456789"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert create_response.status_code == 201
        contact_id = create_response.json()["id"]
        
        # List contacts
        list_response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1
        
        # Update contact
        update_response = client.put(
            f"/api/contacts/{contact_id}",
            json={"name": "Jane", "mobile": "9987654321"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Jane"
        
        # Delete contact
        delete_response = client.delete(
            f"/api/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert delete_response.status_code == 204
        
        # Verify deleted
        list_response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert len(list_response.json()) == 0
    
    def test_multiple_users_isolation(self):
        """Verify complete isolation between users."""
        # Register user 1
        user1_reg = client.post("/api/auth/register", json={
            "mobile": "9111111111",
            "password": "password111",
        })
        user1_token = user1_reg.json()["access_token"]
        
        # Register user 2
        user2_reg = client.post("/api/auth/register", json={
            "mobile": "9222222222",
            "password": "password222",
        })
        user2_token = user2_reg.json()["access_token"]
        
        # User 1 creates 2 contacts
        for i in range(2):
            client.post(
                "/api/contacts",
                json={"name": f"User1 Contact{i}", "mobile": f"911111111{i}"},
                headers={"Authorization": f"Bearer {user1_token}"},
            )
        
        # User 2 creates 1 contact
        client.post(
            "/api/contacts",
            json={"name": "User2 Contact", "mobile": "9222222223"},
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        
        # User 1 lists
        user1_list = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {user1_token}"},
        ).json()
        
        # User 2 lists
        user2_list = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {user2_token}"},
        ).json()
        
        assert len(user1_list) == 2
        assert len(user2_list) == 1
        assert all(c["name"].startswith("User1") for c in user1_list)
        assert all(c["name"].startswith("User2") for c in user2_list)


# ============================================================================
# Health Check
# ============================================================================

class TestHealth:
    """Tests for health check endpoint."""
    
    def test_health_check(self):
        """Health check endpoint works."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
