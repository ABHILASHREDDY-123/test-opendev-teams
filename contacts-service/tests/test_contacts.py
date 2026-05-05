import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, users_db, contacts_db


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    """Clear databases before each test"""
    users_db.clear()
    contacts_db.clear()
    yield
    users_db.clear()
    contacts_db.clear()


# ==================== Auth Tests ====================

class TestAuthRegister:
    """Test user registration"""
    
    def test_register_success(self, client):
        """Test successful registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["mobile"] == "9876543210"
    
    def test_register_mobile_too_short(self, client):
        """Test registration with mobile < 10 digits"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "123456789",
                "password": "password123",
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_register_password_too_short(self, client):
        """Test registration with password < 6 chars"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "pass",
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_register_duplicate_mobile(self, client):
        """Test registration with duplicate mobile"""
        # First registration
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        
        # Second registration with same mobile
        response = client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password456",
            }
        )
        assert response.status_code == 409  # Conflict


class TestAuthLogin:
    """Test user login"""
    
    def test_login_success(self, client):
        """Test successful login"""
        # Register first
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        
        # Login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_mobile(self, client):
        """Test login with non-existent mobile"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9999999999",
                "password": "password123",
            }
        )
        assert response.status_code == 401
    
    def test_login_invalid_password(self, client):
        """Test login with wrong password"""
        # Register first
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        
        # Login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9876543210",
                "password": "wrongpassword",
            }
        )
        assert response.status_code == 401


# ==================== Contacts CRUD Tests ====================

class TestContactsCreate:
    """Test creating contacts"""
    
    def test_create_contact_success(self, client):
        """Test successful contact creation"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        token = login_response.json()["access_token"]
        
        # Create contact
        response = client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "mobile": "9123456789",
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "John Doe"
        assert data["mobile"] == "9123456789"
    
    def test_create_contact_no_jwt(self, client):
        """Test creating contact without JWT"""
        response = client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "mobile": "9123456789",
            }
        )
        assert response.status_code == 401
    
    def test_create_contact_invalid_jwt(self, client):
        """Test creating contact with invalid JWT"""
        response = client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "mobile": "9123456789",
            },
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    def test_create_contact_empty_name(self, client):
        """Test creating contact with empty name"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        token = login_response.json()["access_token"]
        
        # Create contact with empty name
        response = client.post(
            "/api/v1/contacts",
            json={
                "name": "",
                "mobile": "9123456789",
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 422
    
    def test_create_contact_mobile_too_short(self, client):
        """Test creating contact with mobile < 10 digits"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        token = login_response.json()["access_token"]
        
        # Create contact with short mobile
        response = client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "mobile": "123456789",
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 422


class TestContactsList:
    """Test listing contacts"""
    
    def test_list_contacts_empty(self, client):
        """Test listing contacts when none exist"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        token = login_response.json()["access_token"]
        
        # List contacts
        response = client.get(
            "/api/v1/contacts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_list_contacts_success(self, client):
        """Test listing contacts successfully"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        token = login_response.json()["access_token"]
        
        # Create multiple contacts
        client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "mobile": "9123456789",
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        client.post(
            "/api/v1/contacts",
            json={
                "name": "Jane Smith",
                "mobile": "9987654321",
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # List contacts
        response = client.get(
            "/api/v1/contacts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "John Doe"
        assert data[1]["name"] == "Jane Smith"
    
    def test_list_contacts_no_jwt(self, client):
        """Test listing contacts without JWT"""
        response = client.get("/api/v1/contacts")
        assert response.status_code == 401
    
    def test_list_contacts_user_isolation(self, client):
        """Test that users only see their own contacts"""
        # Register and login user 1
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        
        login_response_1 = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        token_1 = login_response_1.json()["access_token"]
        
        # Register and login user 2
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9111111111",
                "password": "password456",
            }
        )
        
        login_response_2 = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9111111111",
                "password": "password456",
            }
        )
        token_2 = login_response_2.json()["access_token"]
        
        # User 1 creates a contact
        client.post(
            "/api/v1/contacts",
            json={
                "name": "User 1 Contact",
                "mobile": "9123456789",
            },
            headers={"Authorization": f"Bearer {token_1}"}
        )
        
        # User 2 creates a contact
        client.post(
            "/api/v1/contacts",
            json={
                "name": "User 2 Contact",
                "mobile": "9987654321",
            },
            headers={"Authorization": f"Bearer {token_2}"}
        )
        
        # User 1 lists contacts - should only see their own
        response_1 = client.get(
            "/api/v1/contacts",
            headers={"Authorization": f"Bearer {token_1}"}
        )
        data_1 = response_1.json()
        assert len(data_1) == 1
        assert data_1[0]["name"] == "User 1 Contact"
        
        # User 2 lists contacts - should only see their own
        response_2 = client.get(
            "/api/v1/contacts",
            headers={"Authorization": f"Bearer {token_2}"}
        )
        data_2 = response_2.json()
        assert len(data_2) == 1
        assert data_2[0]["name"] == "User 2 Contact"


class TestContactsUpdate:
    """Test updating contacts"""
    
    def test_update_contact_success(self, client):
        """Test successful contact update"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        token = login_response.json()["access_token"]
        
        # Create contact
        create_response = client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "mobile": "9123456789",
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        contact_id = create_response.json()["id"]
        
        # Update contact
        response = client.put(
            f"/api/v1/contacts/{contact_id}",
            json={
                "name": "Jane Doe",
                "mobile": "9999999999",
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane Doe"
        assert data["mobile"] == "9999999999"
    
    def test_update_contact_not_found(self, client):
        """Test updating non-existent contact"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        token = login_response.json()["access_token"]
        
        # Update non-existent contact
        response = client.put(
            "/api/v1/contacts/nonexistent",
            json={
                "name": "Jane Doe",
                "mobile": "9999999999",
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404
    
    def test_update_contact_not_owner(self, client):
        """Test updating contact owned by another user"""
        # Register and login user 1
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        
        login_response_1 = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        token_1 = login_response_1.json()["access_token"]
        
        # Register and login user 2
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9111111111",
                "password": "password456",
            }
        )
        
        login_response_2 = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9111111111",
                "password": "password456",
            }
        )
        token_2 = login_response_2.json()["access_token"]
        
        # User 1 creates a contact
        create_response = client.post(
            "/api/v1/contacts",
            json={
                "name": "User 1 Contact",
                "mobile": "9123456789",
            },
            headers={"Authorization": f"Bearer {token_1}"}
        )
        contact_id = create_response.json()["id"]
        
        # User 2 tries to update user 1's contact
        response = client.put(
            f"/api/v1/contacts/{contact_id}",
            json={
                "name": "Hacked Contact",
                "mobile": "9999999999",
            },
            headers={"Authorization": f"Bearer {token_2}"}
        )
        assert response.status_code == 403
    
    def test_update_contact_no_jwt(self, client):
        """Test updating contact without JWT"""
        response = client.put(
            "/api/v1/contacts/someid",
            json={
                "name": "Jane Doe",
                "mobile": "9999999999",
            }
        )
        assert response.status_code == 401


class TestContactsDelete:
    """Test deleting contacts"""
    
    def test_delete_contact_success(self, client):
        """Test successful contact deletion"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        token = login_response.json()["access_token"]
        
        # Create contact
        create_response = client.post(
            "/api/v1/contacts",
            json={
                "name": "John Doe",
                "mobile": "9123456789",
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        contact_id = create_response.json()["id"]
        
        # Delete contact
        response = client.delete(
            f"/api/v1/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204
        
        # Verify contact is deleted
        list_response = client.get(
            "/api/v1/contacts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert len(list_response.json()) == 0
    
    def test_delete_contact_not_found(self, client):
        """Test deleting non-existent contact"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        token = login_response.json()["access_token"]
        
        # Delete non-existent contact
        response = client.delete(
            "/api/v1/contacts/nonexistent",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404
    
    def test_delete_contact_not_owner(self, client):
        """Test deleting contact owned by another user"""
        # Register and login user 1
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        
        login_response_1 = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9876543210",
                "password": "password123",
            }
        )
        token_1 = login_response_1.json()["access_token"]
        
        # Register and login user 2
        client.post(
            "/api/v1/auth/register",
            json={
                "mobile": "9111111111",
                "password": "password456",
            }
        )
        
        login_response_2 = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": "9111111111",
                "password": "password456",
            }
        )
        token_2 = login_response_2.json()["access_token"]
        
        # User 1 creates a contact
        create_response = client.post(
            "/api/v1/contacts",
            json={
                "name": "User 1 Contact",
                "mobile": "9123456789",
            },
            headers={"Authorization": f"Bearer {token_1}"}
        )
        contact_id = create_response.json()["id"]
        
        # User 2 tries to delete user 1's contact
        response = client.delete(
            f"/api/v1/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {token_2}"}
        )
        assert response.status_code == 403
    
    def test_delete_contact_no_jwt(self, client):
        """Test deleting contact without JWT"""
        response = client.delete("/api/v1/contacts/someid")
        assert response.status_code == 401
