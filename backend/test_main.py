"""
Comprehensive unit tests for Contacts API.
Tests cover:
- Happy paths for all endpoints
- Validation errors
- Authentication errors
- Access control (per-user isolation)
- Edge cases
"""

import pytest
from fastapi.testclient import TestClient
from main import app, users_db, contacts_db

# ============================================================================
# Fixtures
# ============================================================================
@pytest.fixture(autouse=True)
def clear_db():
    """Clear database before each test"""
    users_db.clear()
    contacts_db.clear()
    yield
    users_db.clear()
    contacts_db.clear()


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def user1(client):
    """Create and return user1 with token"""
    resp = client.post("/register", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    assert resp.status_code == 201
    user_id = resp.json()["id"]
    
    login_resp = client.post("/login", json={
        "mobile": "9876543210",
        "password": "password123"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    
    return {"id": user_id, "mobile": "9876543210", "token": token}


@pytest.fixture
def user2(client):
    """Create and return user2 with token"""
    resp = client.post("/register", json={
        "mobile": "9123456789",
        "password": "password456"
    })
    assert resp.status_code == 201
    user_id = resp.json()["id"]
    
    login_resp = client.post("/login", json={
        "mobile": "9123456789",
        "password": "password456"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    
    return {"id": user_id, "mobile": "9123456789", "token": token}


# ============================================================================
# Registration Tests
# ============================================================================
class TestRegistration:
    """Test user registration endpoint"""
    
    def test_register_success(self, client):
        """Happy path: register new user"""
        resp = client.post("/register", json={
            "mobile": "9876543210",
            "password": "password123"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["mobile"] == "9876543210"
    
    def test_register_duplicate_mobile(self, client):
        """Error: duplicate mobile"""
        client.post("/register", json={
            "mobile": "9876543210",
            "password": "password123"
        })
        
        resp = client.post("/register", json={
            "mobile": "9876543210",
            "password": "different123"
        })
        assert resp.status_code == 409
        assert "already registered" in resp.json()["detail"]
    
    def test_register_mobile_too_short(self, client):
        """Error: mobile less than 10 digits"""
        resp = client.post("/register", json={
            "mobile": "123456789",
            "password": "password123"
        })
        assert resp.status_code == 422
    
    def test_register_mobile_non_numeric(self, client):
        """Error: mobile contains non-numeric characters"""
        resp = client.post("/register", json={
            "mobile": "98765ABC10",
            "password": "password123"
        })
        assert resp.status_code == 422
    
    def test_register_password_too_short(self, client):
        """Error: password less than 6 characters"""
        resp = client.post("/register", json={
            "mobile": "9876543210",
            "password": "pass"
        })
        assert resp.status_code == 422
    
    def test_register_missing_fields(self, client):
        """Error: missing required fields"""
        resp = client.post("/register", json={"mobile": "9876543210"})
        assert resp.status_code == 422
        
        resp = client.post("/register", json={"password": "password123"})
        assert resp.status_code == 422


# ============================================================================
# Login Tests
# ============================================================================
class TestLogin:
    """Test user login endpoint"""
    
    def test_login_success(self, client, user1):
        """Happy path: login with correct credentials"""
        resp = client.post("/login", json={
            "mobile": "9876543210",
            "password": "password123"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, user1):
        """Error: wrong password"""
        resp = client.post("/login", json={
            "mobile": "9876543210",
            "password": "wrongpassword"
        })
        assert resp.status_code == 401
        assert "Invalid credentials" in resp.json()["detail"]
    
    def test_login_nonexistent_mobile(self, client):
        """Error: mobile not registered"""
        resp = client.post("/login", json={
            "mobile": "9999999999",
            "password": "password123"
        })
        assert resp.status_code == 401
        assert "Invalid credentials" in resp.json()["detail"]
    
    def test_login_missing_fields(self, client):
        """Error: missing required fields"""
        resp = client.post("/login", json={"mobile": "9876543210"})
        assert resp.status_code == 422
        
        resp = client.post("/login", json={"password": "password123"})
        assert resp.status_code == 422


# ============================================================================
# Contacts CRUD Tests
# ============================================================================
class TestCreateContact:
    """Test contact creation"""
    
    def test_create_contact_success(self, client, user1):
        """Happy path: create contact"""
        resp = client.post(
            "/contacts",
            json={"name": "John Doe", "mobile": "9111111111"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "John Doe"
        assert data["mobile"] == "9111111111"
        assert "id" in data
        assert "created_at" in data
    
    def test_create_contact_no_token(self, client):
        """Error: no token provided"""
        resp = client.post("/contacts", json={
            "name": "John Doe",
            "mobile": "9111111111"
        })
        assert resp.status_code == 401
    
    def test_create_contact_invalid_token(self, client):
        """Error: invalid token"""
        resp = client.post(
            "/contacts",
            json={"name": "John Doe", "mobile": "9111111111"},
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert resp.status_code == 401
    
    def test_create_contact_invalid_mobile(self, client, user1):
        """Error: invalid mobile format"""
        resp = client.post(
            "/contacts",
            json={"name": "John Doe", "mobile": "123456789"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert resp.status_code == 422
    
    def test_create_contact_missing_name(self, client, user1):
        """Error: missing name"""
        resp = client.post(
            "/contacts",
            json={"mobile": "9111111111"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert resp.status_code == 422
    
    def test_create_contact_empty_name(self, client, user1):
        """Error: empty name"""
        resp = client.post(
            "/contacts",
            json={"name": "", "mobile": "9111111111"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert resp.status_code == 422


class TestListContacts:
    """Test contact listing"""
    
    def test_list_contacts_empty(self, client, user1):
        """Happy path: list contacts (empty)"""
        resp = client.get(
            "/contacts",
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert resp.status_code == 200
        assert resp.json() == []
    
    def test_list_contacts_multiple(self, client, user1):
        """Happy path: list multiple contacts"""
        # Create 3 contacts
        for i in range(3):
            client.post(
                "/contacts",
                json={"name": f"Contact {i}", "mobile": f"911111111{i}"},
                headers={"Authorization": f"Bearer {user1['token']}"}
            )
        
        resp = client.get(
            "/contacts",
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 3
    
    def test_list_contacts_no_token(self, client):
        """Error: no token provided"""
        resp = client.get("/contacts")
        assert resp.status_code == 401
    
    def test_list_contacts_invalid_token(self, client):
        """Error: invalid token"""
        resp = client.get(
            "/contacts",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert resp.status_code == 401


class TestUpdateContact:
    """Test contact updating"""
    
    def test_update_contact_name(self, client, user1):
        """Happy path: update contact name"""
        # Create contact
        create_resp = client.post(
            "/contacts",
            json={"name": "John Doe", "mobile": "9111111111"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        contact_id = create_resp.json()["id"]
        
        # Update name
        resp = client.put(
            f"/contacts/{contact_id}",
            json={"name": "Jane Doe"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Jane Doe"
        assert resp.json()["mobile"] == "9111111111"
    
    def test_update_contact_mobile(self, client, user1):
        """Happy path: update contact mobile"""
        # Create contact
        create_resp = client.post(
            "/contacts",
            json={"name": "John Doe", "mobile": "9111111111"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        contact_id = create_resp.json()["id"]
        
        # Update mobile
        resp = client.put(
            f"/contacts/{contact_id}",
            json={"mobile": "9222222222"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert resp.status_code == 200
        assert resp.json()["mobile"] == "9222222222"
        assert resp.json()["name"] == "John Doe"
    
    def test_update_contact_both(self, client, user1):
        """Happy path: update both name and mobile"""
        # Create contact
        create_resp = client.post(
            "/contacts",
            json={"name": "John Doe", "mobile": "9111111111"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        contact_id = create_resp.json()["id"]
        
        # Update both
        resp = client.put(
            f"/contacts/{contact_id}",
            json={"name": "Jane Smith", "mobile": "9222222222"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Jane Smith"
        assert resp.json()["mobile"] == "9222222222"
    
    def test_update_contact_not_found(self, client, user1):
        """Error: contact not found"""
        resp = client.put(
            "/contacts/nonexistent",
            json={"name": "Jane Doe"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert resp.status_code == 404
    
    def test_update_contact_no_token(self, client):
        """Error: no token provided"""
        resp = client.put(
            "/contacts/some_id",
            json={"name": "Jane Doe"}
        )
        assert resp.status_code == 401
    
    def test_update_contact_invalid_token(self, client):
        """Error: invalid token"""
        resp = client.put(
            "/contacts/some_id",
            json={"name": "Jane Doe"},
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert resp.status_code == 401
    
    def test_update_contact_invalid_mobile(self, client, user1):
        """Error: invalid mobile format"""
        # Create contact
        create_resp = client.post(
            "/contacts",
            json={"name": "John Doe", "mobile": "9111111111"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        contact_id = create_resp.json()["id"]
        
        # Try to update with invalid mobile
        resp = client.put(
            f"/contacts/{contact_id}",
            json={"mobile": "123"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert resp.status_code == 422


class TestDeleteContact:
    """Test contact deletion"""
    
    def test_delete_contact_success(self, client, user1):
        """Happy path: delete contact"""
        # Create contact
        create_resp = client.post(
            "/contacts",
            json={"name": "John Doe", "mobile": "9111111111"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        contact_id = create_resp.json()["id"]
        
        # Delete contact
        resp = client.delete(
            f"/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert resp.status_code == 204
        
        # Verify deletion
        list_resp = client.get(
            "/contacts",
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert len(list_resp.json()) == 0
    
    def test_delete_contact_not_found(self, client, user1):
        """Error: contact not found"""
        resp = client.delete(
            "/contacts/nonexistent",
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert resp.status_code == 404
    
    def test_delete_contact_no_token(self, client):
        """Error: no token provided"""
        resp = client.delete("/contacts/some_id")
        assert resp.status_code == 401
    
    def test_delete_contact_invalid_token(self, client):
        """Error: invalid token"""
        resp = client.delete(
            "/contacts/some_id",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert resp.status_code == 401


# ============================================================================
# Per-User Isolation Tests
# ============================================================================
class TestPerUserIsolation:
    """Test that users cannot access each other's contacts"""
    
    def test_user_cannot_see_other_user_contacts(self, client, user1, user2):
        """User A cannot see User B's contacts"""
        # User1 creates a contact
        client.post(
            "/contacts",
            json={"name": "User1 Contact", "mobile": "9111111111"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        
        # User2 lists contacts (should be empty)
        resp = client.get(
            "/contacts",
            headers={"Authorization": f"Bearer {user2['token']}"}
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 0
    
    def test_user_cannot_update_other_user_contact(self, client, user1, user2):
        """User A cannot update User B's contact"""
        # User1 creates a contact
        create_resp = client.post(
            "/contacts",
            json={"name": "User1 Contact", "mobile": "9111111111"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        contact_id = create_resp.json()["id"]
        
        # User2 tries to update it (should fail)
        resp = client.put(
            f"/contacts/{contact_id}",
            json={"name": "Hacked"},
            headers={"Authorization": f"Bearer {user2['token']}"}
        )
        assert resp.status_code == 404
    
    def test_user_cannot_delete_other_user_contact(self, client, user1, user2):
        """User A cannot delete User B's contact"""
        # User1 creates a contact
        create_resp = client.post(
            "/contacts",
            json={"name": "User1 Contact", "mobile": "9111111111"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        contact_id = create_resp.json()["id"]
        
        # User2 tries to delete it (should fail)
        resp = client.delete(
            f"/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {user2['token']}"}
        )
        assert resp.status_code == 404
        
        # Verify User1's contact still exists
        list_resp = client.get(
            "/contacts",
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert len(list_resp.json()) == 1
    
    def test_multiple_users_independent_contacts(self, client, user1, user2):
        """Multiple users can have independent contacts"""
        # User1 creates 2 contacts
        for i in range(2):
            client.post(
                "/contacts",
                json={"name": f"User1 Contact {i}", "mobile": f"911111111{i}"},
                headers={"Authorization": f"Bearer {user1['token']}"}
            )
        
        # User2 creates 3 contacts
        for i in range(3):
            client.post(
                "/contacts",
                json={"name": f"User2 Contact {i}", "mobile": f"912222222{i}"},
                headers={"Authorization": f"Bearer {user2['token']}"}
            )
        
        # Verify counts
        user1_resp = client.get(
            "/contacts",
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert len(user1_resp.json()) == 2
        
        user2_resp = client.get(
            "/contacts",
            headers={"Authorization": f"Bearer {user2['token']}"}
        )
        assert len(user2_resp.json()) == 3


# ============================================================================
# Edge Cases
# ============================================================================
class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_mobile_exactly_10_digits(self, client):
        """Mobile with exactly 10 digits should work"""
        resp = client.post("/register", json={
            "mobile": "1234567890",
            "password": "password123"
        })
        assert resp.status_code == 201
    
    def test_mobile_more_than_10_digits(self, client):
        """Mobile with more than 10 digits should work"""
        resp = client.post("/register", json={
            "mobile": "12345678901234",
            "password": "password123"
        })
        assert resp.status_code == 201
    
    def test_password_exactly_6_chars(self, client):
        """Password with exactly 6 characters should work"""
        resp = client.post("/register", json={
            "mobile": "9876543210",
            "password": "pass12"
        })
        assert resp.status_code == 201
    
    def test_contact_name_special_characters(self, client, user1):
        """Contact name with special characters should work"""
        resp = client.post(
            "/contacts",
            json={"name": "John O'Reilly-Smith", "mobile": "9111111111"},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "John O'Reilly-Smith"
    
    def test_create_multiple_contacts_same_user(self, client, user1):
        """User can create multiple contacts"""
        for i in range(5):
            resp = client.post(
                "/contacts",
                json={"name": f"Contact {i}", "mobile": f"911111111{i}"},
                headers={"Authorization": f"Bearer {user1['token']}"}
            )
            assert resp.status_code == 201
        
        # Verify all created
        list_resp = client.get(
            "/contacts",
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        assert len(list_resp.json()) == 5
    
    def test_health_check(self, client):
        """Health check endpoint works"""
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
