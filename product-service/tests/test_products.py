import pytest
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime, timedelta
from jose import jwt

# Add parent directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, products_store, JWT_SECRET

client = TestClient(app)

# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def clear_products():
    """Clear products store before each test."""
    products_store.clear()
    yield
    products_store.clear()

def create_token(user_id: str, email: str, role: str = "customer") -> str:
    """Create a JWT token for testing."""
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def create_admin_token() -> str:
    """Create an admin JWT token."""
    return create_token("admin-user", "admin@example.com", role="admin")

def create_customer_token() -> str:
    """Create a customer JWT token."""
    return create_token("customer-user", "customer@example.com", role="customer")

# ============================================================================
# Public Endpoints Tests
# ============================================================================

class TestListProducts:
    def test_list_products_empty(self):
        """Test listing products when store is empty."""
        response = client.get("/products")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_products_with_items(self):
        """Test listing products with items in store."""
        # Create a product first
        admin_token = create_admin_token()
        product_data = {
            "name": "Laptop",
            "description": "High-performance laptop",
            "price": 999.99,
            "inventory_count": 10,
            "category": "Electronics"
        }
        response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        
        # List products
        response = client.get("/products")
        assert response.status_code == 200
        products = response.json()
        assert len(products) == 1
        assert products[0]["name"] == "Laptop"

class TestGetProduct:
    def test_get_product_success(self):
        """Test getting a product by ID."""
        admin_token = create_admin_token()
        product_data = {
            "name": "Mouse",
            "description": "Wireless mouse",
            "price": 29.99,
            "inventory_count": 50,
            "category": "Accessories"
        }
        create_response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_response.json()["id"]
        
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Mouse"
        assert data["price"] == 29.99

    def test_get_product_not_found(self):
        """Test getting a non-existent product."""
        response = client.get("/products/invalid-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

# ============================================================================
# Admin Endpoints Tests - Create Product
# ============================================================================

class TestCreateProduct:
    def test_create_product_success(self):
        """Test creating a product with admin token."""
        admin_token = create_admin_token()
        product_data = {
            "name": "Keyboard",
            "description": "Mechanical keyboard",
            "price": 149.99,
            "inventory_count": 25,
            "category": "Accessories"
        }
        response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Keyboard"
        assert data["price"] == 149.99
        assert data["inventory_count"] == 25
        assert "id" in data

    def test_create_product_missing_auth(self):
        """Test creating a product without authorization."""
        product_data = {
            "name": "Monitor",
            "description": "4K monitor",
            "price": 399.99,
            "inventory_count": 15,
            "category": "Electronics"
        }
        response = client.post("/products", json=product_data)
        assert response.status_code == 401

    def test_create_product_customer_role(self):
        """Test creating a product with customer role (should fail)."""
        customer_token = create_customer_token()
        product_data = {
            "name": "Monitor",
            "description": "4K monitor",
            "price": 399.99,
            "inventory_count": 15,
            "category": "Electronics"
        }
        response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 403

    def test_create_product_invalid_price(self):
        """Test creating a product with negative price."""
        admin_token = create_admin_token()
        product_data = {
            "name": "Invalid Product",
            "description": "Test",
            "price": -10.0,
            "inventory_count": 5,
            "category": "Test"
        }
        response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400

    def test_create_product_invalid_inventory(self):
        """Test creating a product with negative inventory."""
        admin_token = create_admin_token()
        product_data = {
            "name": "Invalid Product",
            "description": "Test",
            "price": 10.0,
            "inventory_count": -5,
            "category": "Test"
        }
        response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400

    def test_create_product_empty_name(self):
        """Test creating a product with empty name."""
        admin_token = create_admin_token()
        product_data = {
            "name": "",
            "description": "Test",
            "price": 10.0,
            "inventory_count": 5,
            "category": "Test"
        }
        response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400

# ============================================================================
# Admin Endpoints Tests - Update Product
# ============================================================================

class TestUpdateProduct:
    def test_update_product_success(self):
        """Test updating a product."""
        admin_token = create_admin_token()
        
        # Create product
        product_data = {
            "name": "Original Name",
            "description": "Original description",
            "price": 100.0,
            "inventory_count": 10,
            "category": "Test"
        }
        create_response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_response.json()["id"]
        
        # Update product
        update_data = {
            "name": "Updated Name",
            "price": 150.0
        }
        response = client.put(
            f"/products/{product_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["price"] == 150.0
        assert data["description"] == "Original description"  # Unchanged

    def test_update_product_not_found(self):
        """Test updating a non-existent product."""
        admin_token = create_admin_token()
        update_data = {"name": "Updated"}
        response = client.put(
            "/products/invalid-id",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404

    def test_update_product_customer_role(self):
        """Test updating a product with customer role."""
        admin_token = create_admin_token()
        customer_token = create_customer_token()
        
        # Create product
        product_data = {
            "name": "Test",
            "description": "Test",
            "price": 100.0,
            "inventory_count": 10,
            "category": "Test"
        }
        create_response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_response.json()["id"]
        
        # Try to update with customer token
        update_data = {"name": "Updated"}
        response = client.put(
            f"/products/{product_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 403

    def test_update_product_invalid_price(self):
        """Test updating a product with negative price."""
        admin_token = create_admin_token()
        
        # Create product
        product_data = {
            "name": "Test",
            "description": "Test",
            "price": 100.0,
            "inventory_count": 10,
            "category": "Test"
        }
        create_response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_response.json()["id"]
        
        # Try to update with negative price
        update_data = {"price": -50.0}
        response = client.put(
            f"/products/{product_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400

# ============================================================================
# Admin Endpoints Tests - Delete Product
# ============================================================================

class TestDeleteProduct:
    def test_delete_product_success(self):
        """Test deleting a product."""
        admin_token = create_admin_token()
        
        # Create product
        product_data = {
            "name": "To Delete",
            "description": "Test",
            "price": 100.0,
            "inventory_count": 10,
            "category": "Test"
        }
        create_response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_response.json()["id"]
        
        # Delete product
        response = client.delete(
            f"/products/{product_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 404

    def test_delete_product_not_found(self):
        """Test deleting a non-existent product."""
        admin_token = create_admin_token()
        response = client.delete(
            "/products/invalid-id",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404

    def test_delete_product_customer_role(self):
        """Test deleting a product with customer role."""
        admin_token = create_admin_token()
        customer_token = create_customer_token()
        
        # Create product
        product_data = {
            "name": "Test",
            "description": "Test",
            "price": 100.0,
            "inventory_count": 10,
            "category": "Test"
        }
        create_response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_response.json()["id"]
        
        # Try to delete with customer token
        response = client.delete(
            f"/products/{product_id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 403

# ============================================================================
# Inventory Management Tests - Reserve
# ============================================================================

class TestReserveInventory:
    def test_reserve_inventory_success(self):
        """Test reserving inventory."""
        admin_token = create_admin_token()
        
        # Create product
        product_data = {
            "name": "Test Product",
            "description": "Test",
            "price": 100.0,
            "inventory_count": 50,
            "category": "Test"
        }
        create_response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_response.json()["id"]
        
        # Reserve inventory
        response = client.post(
            f"/products/{product_id}/reserve",
            json={"quantity": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["inventory_count"] == 40

    def test_reserve_inventory_insufficient(self):
        """Test reserving more inventory than available."""
        admin_token = create_admin_token()
        
        # Create product
        product_data = {
            "name": "Test Product",
            "description": "Test",
            "price": 100.0,
            "inventory_count": 10,
            "category": "Test"
        }
        create_response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_response.json()["id"]
        
        # Try to reserve more than available
        response = client.post(
            f"/products/{product_id}/reserve",
            json={"quantity": 20}
        )
        assert response.status_code == 400
        assert "insufficient" in response.json()["detail"].lower()

    def test_reserve_inventory_not_found(self):
        """Test reserving inventory for non-existent product."""
        response = client.post(
            "/products/invalid-id/reserve",
            json={"quantity": 10}
        )
        assert response.status_code == 404

    def test_reserve_inventory_invalid_quantity(self):
        """Test reserving with invalid quantity."""
        admin_token = create_admin_token()
        
        # Create product
        product_data = {
            "name": "Test Product",
            "description": "Test",
            "price": 100.0,
            "inventory_count": 50,
            "category": "Test"
        }
        create_response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_response.json()["id"]
        
        # Try to reserve with zero quantity
        response = client.post(
            f"/products/{product_id}/reserve",
            json={"quantity": 0}
        )
        assert response.status_code == 400

# ============================================================================
# Inventory Management Tests - Release
# ============================================================================

class TestReleaseInventory:
    def test_release_inventory_success(self):
        """Test releasing inventory."""
        admin_token = create_admin_token()
        
        # Create product
        product_data = {
            "name": "Test Product",
            "description": "Test",
            "price": 100.0,
            "inventory_count": 50,
            "category": "Test"
        }
        create_response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_response.json()["id"]
        
        # Release inventory
        response = client.post(
            f"/products/{product_id}/release",
            json={"quantity": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["inventory_count"] == 60

    def test_release_inventory_not_found(self):
        """Test releasing inventory for non-existent product."""
        response = client.post(
            "/products/invalid-id/release",
            json={"quantity": 10}
        )
        assert response.status_code == 404

    def test_release_inventory_invalid_quantity(self):
        """Test releasing with invalid quantity."""
        admin_token = create_admin_token()
        
        # Create product
        product_data = {
            "name": "Test Product",
            "description": "Test",
            "price": 100.0,
            "inventory_count": 50,
            "category": "Test"
        }
        create_response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_response.json()["id"]
        
        # Try to release with negative quantity
        response = client.post(
            f"/products/{product_id}/release",
            json={"quantity": -10}
        )
        assert response.status_code == 400

# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    def test_full_workflow(self):
        """Test a complete workflow: create, read, update, reserve, release, delete."""
        admin_token = create_admin_token()
        
        # Create product
        product_data = {
            "name": "Workflow Test",
            "description": "Testing full workflow",
            "price": 199.99,
            "inventory_count": 100,
            "category": "Electronics"
        }
        create_response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # Read product
        read_response = client.get(f"/products/{product_id}")
        assert read_response.status_code == 200
        assert read_response.json()["name"] == "Workflow Test"
        
        # Update product
        update_response = client.put(
            f"/products/{product_id}",
            json={"price": 249.99},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["price"] == 249.99
        
        # Reserve inventory
        reserve_response = client.post(
            f"/products/{product_id}/reserve",
            json={"quantity": 30}
        )
        assert reserve_response.status_code == 200
        assert reserve_response.json()["inventory_count"] == 70
        
        # Release inventory
        release_response = client.post(
            f"/products/{product_id}/release",
            json={"quantity": 10}
        )
        assert release_response.status_code == 200
        assert release_response.json()["inventory_count"] == 80
        
        # Delete product
        delete_response = client.delete(
            f"/products/{product_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_response.status_code == 204
        
        # Verify deletion
        get_response = client.get(f"/products/{product_id}")
        assert get_response.status_code == 404

# ============================================================================
# Health Check Test
# ============================================================================

class TestHealthCheck:
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "product-service"
