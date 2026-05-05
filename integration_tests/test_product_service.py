"""Integration tests for Product Service."""

import pytest
import httpx

PRODUCT_SERVICE_URL = "http://localhost:8002"


@pytest.mark.usefixtures("start_services")
class TestProductService:
    """Product Service integration tests."""

    def test_health_check(self, http_client):
        """Test product service health check."""
        response = http_client.get(f"{PRODUCT_SERVICE_URL}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_list_products_empty(self, http_client):
        """Test listing products when none exist."""
        response = http_client.get(f"{PRODUCT_SERVICE_URL}/products")
        assert response.status_code == 200
        data = response.json()
        assert data["products"] == []

    def test_create_product_as_admin(self, http_client, admin_headers):
        """Test creating a product as admin."""
        payload = {
            "name": "Test Product",
            "description": "A test product",
            "price": 99.99,
            "inventory_count": 100,
            "category": "Electronics"
        }

        response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=payload,
            headers=admin_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Product"
        assert data["price"] == 99.99
        assert data["inventory_count"] == 100
        assert "id" in data

    def test_create_product_as_customer_fails(self, http_client, auth_headers):
        """Test that non-admin cannot create products."""
        payload = {
            "name": "Test Product",
            "description": "A test product",
            "price": 99.99,
            "inventory_count": 100,
            "category": "Electronics"
        }

        response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=payload,
            headers=auth_headers
        )
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()

    def test_create_product_no_auth_fails(self, http_client):
        """Test that creating product without auth fails."""
        payload = {
            "name": "Test Product",
            "description": "A test product",
            "price": 99.99,
            "inventory_count": 100,
            "category": "Electronics"
        }

        response = http_client.post(f"{PRODUCT_SERVICE_URL}/products", json=payload)
        assert response.status_code == 401

    def test_list_products_after_create(self, http_client, admin_headers):
        """Test listing products after creating some."""
        # Create two products
        for i in range(2):
            payload = {
                "name": f"Product {i}",
                "description": f"Description {i}",
                "price": 10.0 + i,
                "inventory_count": 50 + i,
                "category": "Category"
            }
            http_client.post(
                f"{PRODUCT_SERVICE_URL}/products",
                json=payload,
                headers=admin_headers
            )

        # List products
        response = http_client.get(f"{PRODUCT_SERVICE_URL}/products")
        assert response.status_code == 200
        data = response.json()
        assert len(data["products"]) >= 2

    def test_get_product_by_id(self, http_client, admin_headers):
        """Test getting a product by ID."""
        # Create product
        create_payload = {
            "name": "Get Test Product",
            "description": "A product to get",
            "price": 49.99,
            "inventory_count": 25,
            "category": "Test"
        }
        create_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=create_payload,
            headers=admin_headers
        )
        product_id = create_response.json()["id"]

        # Get product
        response = http_client.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == "Get Test Product"

    def test_get_nonexistent_product(self, http_client):
        """Test getting a non-existent product."""
        response = http_client.get(f"{PRODUCT_SERVICE_URL}/products/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_product(self, http_client, admin_headers):
        """Test updating a product."""
        # Create product
        create_payload = {
            "name": "Update Test Product",
            "description": "Original description",
            "price": 29.99,
            "inventory_count": 50,
            "category": "Test"
        }
        create_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=create_payload,
            headers=admin_headers
        )
        product_id = create_response.json()["id"]

        # Update product
        update_payload = {
            "name": "Updated Product",
            "price": 39.99
        }
        response = http_client.put(
            f"{PRODUCT_SERVICE_URL}/products/{product_id}",
            json=update_payload,
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product"
        assert data["price"] == 39.99
        assert data["description"] == "Original description"  # Unchanged

    def test_delete_product(self, http_client, admin_headers):
        """Test deleting a product."""
        # Create product
        create_payload = {
            "name": "Delete Test Product",
            "description": "To be deleted",
            "price": 19.99,
            "inventory_count": 10,
            "category": "Test"
        }
        create_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=create_payload,
            headers=admin_headers
        )
        product_id = create_response.json()["id"]

        # Delete product
        response = http_client.delete(
            f"{PRODUCT_SERVICE_URL}/products/{product_id}",
            headers=admin_headers
        )
        assert response.status_code == 204

        # Verify product is deleted
        response = http_client.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
        assert response.status_code == 404

    def test_reserve_inventory(self, http_client, admin_headers):
        """Test reserving inventory."""
        # Create product with inventory
        create_payload = {
            "name": "Reserve Test Product",
            "description": "For inventory test",
            "price": 15.99,
            "inventory_count": 100,
            "category": "Test"
        }
        create_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=create_payload,
            headers=admin_headers
        )
        product_id = create_response.json()["id"]

        # Reserve inventory
        reserve_payload = {"quantity": 30}
        response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products/{product_id}/reserve",
            json=reserve_payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["inventory_count"] == 70

    def test_reserve_inventory_insufficient(self, http_client, admin_headers):
        """Test reserving inventory when insufficient."""
        # Create product with low inventory
        create_payload = {
            "name": "Low Inventory Product",
            "description": "Low stock",
            "price": 5.99,
            "inventory_count": 10,
            "category": "Test"
        }
        create_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=create_payload,
            headers=admin_headers
        )
        product_id = create_response.json()["id"]

        # Try to reserve more than available
        reserve_payload = {"quantity": 50}
        response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products/{product_id}/reserve",
            json=reserve_payload
        )
        assert response.status_code == 400
        assert "insufficient" in response.json()["detail"].lower()

    def test_release_inventory(self, http_client, admin_headers):
        """Test releasing inventory."""
        # Create product
        create_payload = {
            "name": "Release Test Product",
            "description": "For release test",
            "price": 12.99,
            "inventory_count": 50,
            "category": "Test"
        }
        create_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=create_payload,
            headers=admin_headers
        )
        product_id = create_response.json()["id"]

        # Release inventory
        release_payload = {"quantity": 20}
        response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products/{product_id}/release",
            json=release_payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["inventory_count"] == 70
