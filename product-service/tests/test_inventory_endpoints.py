"""
Tests for inventory management endpoints (reserve/release)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import products_db


class TestReserveInventory:
    """Tests for POST /products/{id}/reserve endpoint."""
    
    def test_reserve_inventory_success(self, client, admin_token, sample_product):
        """Test successfully reserving inventory."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product with 100 inventory
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Reserve 30 units
        response = client.post(
            f"/products/{product_id}/reserve",
            json={"quantity": 30}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["inventory_count"] == 70  # 100 - 30
    
    def test_reserve_inventory_insufficient(self, client, admin_token, sample_product):
        """Test reserving more inventory than available."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product with 100 inventory
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Try to reserve 150 units
        response = client.post(
            f"/products/{product_id}/reserve",
            json={"quantity": 150}
        )
        
        assert response.status_code == 400
        assert "Insufficient inventory" in response.json()["detail"]
    
    def test_reserve_inventory_exact_amount(self, client, admin_token, sample_product):
        """Test reserving exact amount of available inventory."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product with 100 inventory
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Reserve exactly 100 units
        response = client.post(
            f"/products/{product_id}/reserve",
            json={"quantity": 100}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["inventory_count"] == 0
    
    def test_reserve_inventory_not_found(self, client):
        """Test reserving inventory for non-existent product."""
        response = client.post(
            "/products/non-existent-id/reserve",
            json={"quantity": 10}
        )
        assert response.status_code == 404
    
    def test_reserve_inventory_zero_quantity(self, client, admin_token, sample_product):
        """Test reserving zero quantity."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Try to reserve 0 units
        response = client.post(
            f"/products/{product_id}/reserve",
            json={"quantity": 0}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_reserve_inventory_negative_quantity(self, client, admin_token, sample_product):
        """Test reserving negative quantity."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Try to reserve negative quantity
        response = client.post(
            f"/products/{product_id}/reserve",
            json={"quantity": -10}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_reserve_inventory_multiple_times(self, client, admin_token, sample_product):
        """Test reserving inventory multiple times."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product with 100 inventory
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Reserve 30 units
        response1 = client.post(
            f"/products/{product_id}/reserve",
            json={"quantity": 30}
        )
        assert response1.status_code == 200
        assert response1.json()["inventory_count"] == 70
        
        # Reserve 20 more units
        response2 = client.post(
            f"/products/{product_id}/reserve",
            json={"quantity": 20}
        )
        assert response2.status_code == 200
        assert response2.json()["inventory_count"] == 50
    
    def test_reserve_inventory_updates_db(self, client, admin_token, sample_product):
        """Test that reserve operation updates the database."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Reserve inventory
        client.post(f"/products/{product_id}/reserve", json={"quantity": 30})
        
        # Verify database is updated
        assert products_db[product_id]["inventory_count"] == 70


class TestReleaseInventory:
    """Tests for POST /products/{id}/release endpoint."""
    
    def test_release_inventory_success(self, client, admin_token, sample_product):
        """Test successfully releasing inventory."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product with 100 inventory
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Reserve 30 units
        client.post(f"/products/{product_id}/reserve", json={"quantity": 30})
        
        # Release 20 units
        response = client.post(
            f"/products/{product_id}/release",
            json={"quantity": 20}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["inventory_count"] == 90  # 70 + 20
    
    def test_release_inventory_not_found(self, client):
        """Test releasing inventory for non-existent product."""
        response = client.post(
            "/products/non-existent-id/release",
            json={"quantity": 10}
        )
        assert response.status_code == 404
    
    def test_release_inventory_zero_quantity(self, client, admin_token, sample_product):
        """Test releasing zero quantity."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Try to release 0 units
        response = client.post(
            f"/products/{product_id}/release",
            json={"quantity": 0}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_release_inventory_negative_quantity(self, client, admin_token, sample_product):
        """Test releasing negative quantity."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Try to release negative quantity
        response = client.post(
            f"/products/{product_id}/release",
            json={"quantity": -10}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_release_inventory_can_exceed_original(self, client, admin_token, sample_product):
        """Test that release can increase inventory beyond original amount."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product with 100 inventory
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Reserve 30 units
        client.post(f"/products/{product_id}/reserve", json={"quantity": 30})
        
        # Release 50 units (more than was reserved)
        response = client.post(
            f"/products/{product_id}/release",
            json={"quantity": 50}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["inventory_count"] == 120  # 70 + 50
    
    def test_release_inventory_multiple_times(self, client, admin_token, sample_product):
        """Test releasing inventory multiple times."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product with 100 inventory
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Reserve 50 units
        client.post(f"/products/{product_id}/reserve", json={"quantity": 50})
        
        # Release 20 units
        response1 = client.post(
            f"/products/{product_id}/release",
            json={"quantity": 20}
        )
        assert response1.status_code == 200
        assert response1.json()["inventory_count"] == 70
        
        # Release 15 more units
        response2 = client.post(
            f"/products/{product_id}/release",
            json={"quantity": 15}
        )
        assert response2.status_code == 200
        assert response2.json()["inventory_count"] == 85
    
    def test_release_inventory_updates_db(self, client, admin_token, sample_product):
        """Test that release operation updates the database."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Release inventory
        client.post(f"/products/{product_id}/release", json={"quantity": 20})
        
        # Verify database is updated
        assert products_db[product_id]["inventory_count"] == 120  # 100 + 20


class TestReserveReleaseFlow:
    """Tests for combined reserve/release flows."""
    
    def test_reserve_then_release(self, client, admin_token, sample_product):
        """Test reserving and then releasing inventory."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product with 100 inventory
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Reserve 30 units
        reserve_response = client.post(
            f"/products/{product_id}/reserve",
            json={"quantity": 30}
        )
        assert reserve_response.json()["inventory_count"] == 70
        
        # Release 30 units (cancel the order)
        release_response = client.post(
            f"/products/{product_id}/release",
            json={"quantity": 30}
        )
        assert release_response.json()["inventory_count"] == 100
    
    def test_reserve_partial_release(self, client, admin_token, sample_product):
        """Test reserving and then partially releasing inventory."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product with 100 inventory
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Reserve 30 units
        client.post(f"/products/{product_id}/reserve", json={"quantity": 30})
        
        # Release 10 units (partial cancellation)
        release_response = client.post(
            f"/products/{product_id}/release",
            json={"quantity": 10}
        )
        assert release_response.json()["inventory_count"] == 80
