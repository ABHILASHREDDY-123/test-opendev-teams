"""
Tests for public product endpoints (GET /products, GET /products/{id})
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import products_db


class TestListProducts:
    """Tests for GET /products endpoint."""
    
    def test_list_products_empty(self, client):
        """Test listing products when database is empty."""
        response = client.get("/products")
        assert response.status_code == 200
        assert response.json() == {"products": []}
    
    def test_list_products_with_items(self, client, admin_token, sample_product):
        """Test listing products when database has items."""
        # Create a product first
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_response = client.post("/products", json=sample_product, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # List products
        response = client.get("/products")
        assert response.status_code == 200
        data = response.json()
        assert len(data["products"]) == 1
        assert data["products"][0]["id"] == product_id
        assert data["products"][0]["name"] == sample_product["name"]
        assert data["products"][0]["price"] == sample_product["price"]
    
    def test_list_products_multiple(self, client, admin_token):
        """Test listing multiple products."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create 3 products
        product_ids = []
        for i in range(3):
            product_data = {
                "name": f"Product {i}",
                "description": f"Description {i}",
                "price": 10.0 + i,
                "inventory_count": 100 + i,
                "category": "Test"
            }
            response = client.post("/products", json=product_data, headers=headers)
            assert response.status_code == 201
            product_ids.append(response.json()["id"])
        
        # List all products
        response = client.get("/products")
        assert response.status_code == 200
        data = response.json()
        assert len(data["products"]) == 3
        
        # Verify all products are in the list
        returned_ids = [p["id"] for p in data["products"]]
        assert set(returned_ids) == set(product_ids)
    
    def test_list_products_no_auth_required(self, client, sample_product):
        """Test that listing products doesn't require authentication."""
        # Create a product (requires auth)
        # First, we need to add a product to the database directly for this test
        products_db["test-id"] = {
            "id": "test-id",
            **sample_product
        }
        
        # List products without auth header
        response = client.get("/products")
        assert response.status_code == 200
        assert len(response.json()["products"]) == 1


class TestGetProduct:
    """Tests for GET /products/{id} endpoint."""
    
    def test_get_product_success(self, client, admin_token, sample_product):
        """Test getting a product by ID."""
        # Create a product
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_response = client.post("/products", json=sample_product, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # Get the product
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == sample_product["name"]
        assert data["description"] == sample_product["description"]
        assert data["price"] == sample_product["price"]
        assert data["inventory_count"] == sample_product["inventory_count"]
        assert data["category"] == sample_product["category"]
    
    def test_get_product_not_found(self, client):
        """Test getting a non-existent product."""
        response = client.get("/products/non-existent-id")
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]
    
    def test_get_product_no_auth_required(self, client, sample_product):
        """Test that getting a product doesn't require authentication."""
        # Add product directly to database
        products_db["test-id"] = {
            "id": "test-id",
            **sample_product
        }
        
        # Get product without auth header
        response = client.get("/products/test-id")
        assert response.status_code == 200
        assert response.json()["id"] == "test-id"
    
    def test_get_product_returns_correct_format(self, client, admin_token, sample_product):
        """Test that product response has correct format."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_response = client.post("/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        required_fields = ["id", "name", "description", "price", "inventory_count", "category"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
