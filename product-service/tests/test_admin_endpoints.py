"""
Tests for admin product management endpoints (POST/PUT/DELETE /products)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import products_db


class TestCreateProduct:
    """Tests for POST /products endpoint."""
    
    def test_create_product_success(self, client, admin_token, sample_product):
        """Test creating a product with valid admin token."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post("/products", json=sample_product, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_product["name"]
        assert data["description"] == sample_product["description"]
        assert data["price"] == sample_product["price"]
        assert data["inventory_count"] == sample_product["inventory_count"]
        assert data["category"] == sample_product["category"]
        assert "id" in data
        assert len(data["id"]) > 0
    
    def test_create_product_no_auth(self, client, sample_product):
        """Test creating a product without authentication."""
        response = client.post("/products", json=sample_product)
        assert response.status_code == 401
        assert "authorization" in response.json()["detail"].lower()
    
    def test_create_product_invalid_token(self, client, sample_product):
        """Test creating a product with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.post("/products", json=sample_product, headers=headers)
        assert response.status_code == 401
    
    def test_create_product_customer_not_allowed(self, client, customer_token, sample_product):
        """Test that customer role cannot create products."""
        headers = {"Authorization": f"Bearer {customer_token}"}
        response = client.post("/products", json=sample_product, headers=headers)
        assert response.status_code == 403
        assert "Admin role required" in response.json()["detail"]
    
    def test_create_product_expired_token(self, client, expired_token, sample_product):
        """Test creating a product with expired token."""
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.post("/products", json=sample_product, headers=headers)
        assert response.status_code == 401
    
    def test_create_product_missing_field(self, client, admin_token):
        """Test creating a product with missing required field."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        incomplete_product = {
            "name": "Test Product",
            "description": "Test",
            # Missing price, inventory_count, category
        }
        response = client.post("/products", json=incomplete_product, headers=headers)
        assert response.status_code == 422  # Validation error
    
    def test_create_product_invalid_price(self, client, admin_token, sample_product):
        """Test creating a product with invalid price."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        invalid_product = {**sample_product, "price": -10}
        response = client.post("/products", json=invalid_product, headers=headers)
        assert response.status_code == 422
    
    def test_create_product_negative_inventory(self, client, admin_token, sample_product):
        """Test creating a product with negative inventory."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        invalid_product = {**sample_product, "inventory_count": -5}
        response = client.post("/products", json=invalid_product, headers=headers)
        assert response.status_code == 422
    
    def test_create_product_stored_in_db(self, client, admin_token, sample_product):
        """Test that created product is stored in database."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post("/products", json=sample_product, headers=headers)
        assert response.status_code == 201
        product_id = response.json()["id"]
        
        # Verify product is in database
        assert product_id in products_db
        assert products_db[product_id]["name"] == sample_product["name"]


class TestUpdateProduct:
    """Tests for PUT /products/{id} endpoint."""
    
    def test_update_product_success(self, client, admin_token, sample_product):
        """Test updating a product with valid admin token."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Update product
        updated_data = {
            "name": "Updated Product",
            "price": 199.99,
        }
        response = client.put(f"/products/{product_id}", json=updated_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product"
        assert data["price"] == 199.99
        # Other fields should remain unchanged
        assert data["description"] == sample_product["description"]
        assert data["inventory_count"] == sample_product["inventory_count"]
    
    def test_update_product_not_found(self, client, admin_token):
        """Test updating a non-existent product."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.put("/products/non-existent-id", json={"name": "New"}, headers=headers)
        assert response.status_code == 404
    
    def test_update_product_no_auth(self, client, sample_product):
        """Test updating a product without authentication."""
        response = client.put("/products/some-id", json={"name": "New"})
        assert response.status_code == 401
    
    def test_update_product_customer_not_allowed(self, client, customer_token, sample_product):
        """Test that customer role cannot update products."""
        headers = {"Authorization": f"Bearer {customer_token}"}
        response = client.put("/products/some-id", json={"name": "New"}, headers=headers)
        assert response.status_code == 403
    
    def test_update_product_partial(self, client, admin_token, sample_product):
        """Test partial product update."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Update only name
        response = client.put(f"/products/{product_id}", json={"name": "New Name"}, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["price"] == sample_product["price"]
    
    def test_update_product_all_fields(self, client, admin_token, sample_product):
        """Test updating all product fields."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Update all fields
        new_data = {
            "name": "New Name",
            "description": "New Description",
            "price": 299.99,
            "inventory_count": 50,
            "category": "New Category"
        }
        response = client.put(f"/products/{product_id}", json=new_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == new_data["name"]
        assert data["description"] == new_data["description"]
        assert data["price"] == new_data["price"]
        assert data["inventory_count"] == new_data["inventory_count"]
        assert data["category"] == new_data["category"]


class TestDeleteProduct:
    """Tests for DELETE /products/{id} endpoint."""
    
    def test_delete_product_success(self, client, admin_token, sample_product):
        """Test deleting a product with valid admin token."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Delete product
        response = client.delete(f"/products/{product_id}", headers=headers)
        assert response.status_code == 204
        
        # Verify product is deleted
        assert product_id not in products_db
    
    def test_delete_product_not_found(self, client, admin_token):
        """Test deleting a non-existent product."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.delete("/products/non-existent-id", headers=headers)
        assert response.status_code == 404
    
    def test_delete_product_no_auth(self, client):
        """Test deleting a product without authentication."""
        response = client.delete("/products/some-id")
        assert response.status_code == 401
    
    def test_delete_product_customer_not_allowed(self, client, customer_token):
        """Test that customer role cannot delete products."""
        headers = {"Authorization": f"Bearer {customer_token}"}
        response = client.delete("/products/some-id", headers=headers)
        assert response.status_code == 403
    
    def test_delete_product_removes_from_db(self, client, admin_token, sample_product):
        """Test that deleted product is removed from database."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        assert product_id in products_db
        
        # Delete product
        response = client.delete(f"/products/{product_id}", headers=headers)
        assert response.status_code == 204
        assert product_id not in products_db
