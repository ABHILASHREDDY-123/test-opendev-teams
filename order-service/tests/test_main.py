"""
Unit tests for Order Service endpoints.
"""

import pytest
from .conftest import create_test_token


# ============================================================================
# Cart Endpoints Tests
# ============================================================================

class TestCartEndpoints:
    """Tests for cart endpoints"""
    
    def test_add_to_cart_success(self, client, clear_db, auth_header, mock_product_service):
        """Test adding product to cart successfully"""
        response = client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 2},
            headers=auth_header
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == "product-1"
        assert data["quantity"] == 2
        assert data["price"] == 99.99
        assert "item_id" in data
    
    def test_add_to_cart_product_not_found(self, client, clear_db, auth_header, mock_product_service):
        """Test adding non-existent product to cart"""
        response = client.post(
            "/cart/add",
            json={"product_id": "invalid-product", "quantity": 1},
            headers=auth_header
        )
        
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]
    
    def test_add_to_cart_invalid_quantity(self, client, clear_db, auth_header, mock_product_service):
        """Test adding product with invalid quantity"""
        response = client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 0},
            headers=auth_header
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_add_to_cart_no_auth(self, client, clear_db, mock_product_service):
        """Test adding to cart without authentication"""
        response = client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 1}
        )
        
        assert response.status_code == 403  # Forbidden (no auth header)
    
    def test_add_to_cart_duplicate_product(self, client, clear_db, auth_header, mock_product_service):
        """Test adding same product twice increases quantity"""
        # Add first time
        response1 = client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 2},
            headers=auth_header
        )
        assert response1.status_code == 201
        item_id_1 = response1.json()["item_id"]
        
        # Add same product again
        response2 = client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 3},
            headers=auth_header
        )
        assert response2.status_code == 201
        item_id_2 = response2.json()["item_id"]
        
        # Should be same item with updated quantity
        assert item_id_1 == item_id_2
        assert response2.json()["quantity"] == 3
    
    def test_get_cart_empty(self, client, clear_db, auth_header, mock_product_service):
        """Test getting empty cart"""
        response = client.get("/cart", headers=auth_header)
        
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0.0
    
    def test_get_cart_with_items(self, client, clear_db, auth_header, mock_product_service):
        """Test getting cart with items"""
        # Add items to cart
        client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 2},
            headers=auth_header
        )
        client.post(
            "/cart/add",
            json={"product_id": "product-2", "quantity": 1},
            headers=auth_header
        )
        
        # Get cart
        response = client.get("/cart", headers=auth_header)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        # Total: (99.99 * 2) + (49.99 * 1) = 249.97
        assert abs(data["total"] - 249.97) < 0.01
    
    def test_get_cart_no_auth(self, client, clear_db, mock_product_service):
        """Test getting cart without authentication"""
        response = client.get("/cart")
        
        assert response.status_code == 403
    
    def test_remove_from_cart_success(self, client, clear_db, auth_header, mock_product_service):
        """Test removing item from cart"""
        # Add item
        add_response = client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 2},
            headers=auth_header
        )
        item_id = add_response.json()["item_id"]
        
        # Remove item
        response = client.delete(f"/cart/{item_id}", headers=auth_header)
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Verify cart is empty
        cart_response = client.get("/cart", headers=auth_header)
        assert len(cart_response.json()["items"]) == 0
    
    def test_remove_from_cart_not_found(self, client, clear_db, auth_header, mock_product_service):
        """Test removing non-existent item from cart"""
        response = client.delete("/cart/invalid-item-id", headers=auth_header)
        
        assert response.status_code == 404
        assert "Cart item not found" in response.json()["detail"]
    
    def test_remove_from_cart_no_auth(self, client, clear_db, mock_product_service):
        """Test removing from cart without authentication"""
        response = client.delete("/cart/item-1")
        
        assert response.status_code == 403
    
    def test_per_user_cart_isolation(self, client, clear_db, mock_product_service):
        """Test that carts are isolated per user"""
        user1_token = create_test_token(user_id="user-1", email="user1@example.com")
        user2_token = create_test_token(user_id="user-2", email="user2@example.com")
        
        user1_header = {"Authorization": f"Bearer {user1_token}"}
        user2_header = {"Authorization": f"Bearer {user2_token}"}
        
        # User 1 adds to cart
        client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 2},
            headers=user1_header
        )
        
        # User 2 adds to cart
        client.post(
            "/cart/add",
            json={"product_id": "product-2", "quantity": 1},
            headers=user2_header
        )
        
        # Verify isolation
        user1_cart = client.get("/cart", headers=user1_header).json()
        user2_cart = client.get("/cart", headers=user2_header).json()
        
        assert len(user1_cart["items"]) == 1
        assert user1_cart["items"][0]["product_id"] == "product-1"
        
        assert len(user2_cart["items"]) == 1
        assert user2_cart["items"][0]["product_id"] == "product-2"


# ============================================================================
# Order Endpoints Tests
# ============================================================================

class TestOrderEndpoints:
    """Tests for order endpoints"""
    
    def test_create_order_success(self, client, clear_db, auth_header, mock_product_service):
        """Test creating order from cart"""
        # Add items to cart
        client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 2},
            headers=auth_header
        )
        
        # Create order
        response = client.post("/orders", headers=auth_header)
        
        assert response.status_code == 201
        data = response.json()
        assert "order_id" in data
        assert data["user_id"] == "test-user-1"
        assert len(data["items"]) == 1
        assert data["items"][0]["product_id"] == "product-1"
        assert data["items"][0]["quantity"] == 2
        assert data["status"] == "pending"
        assert "created_at" in data
    
    def test_create_order_empty_cart(self, client, clear_db, auth_header, mock_product_service):
        """Test creating order from empty cart"""
        response = client.post("/orders", headers=auth_header)
        
        assert response.status_code == 400
        assert "empty cart" in response.json()["detail"]
    
    def test_create_order_insufficient_inventory(self, client, clear_db, auth_header, mock_product_service):
        """Test creating order with insufficient inventory"""
        # Try to add more than available
        response = client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 200},  # Only 100 available
            headers=auth_header
        )
        
        # Should succeed in adding to cart
        assert response.status_code == 201
        
        # But order creation should fail
        order_response = client.post("/orders", headers=auth_header)
        assert order_response.status_code == 400
        assert "Insufficient inventory" in order_response.json()["detail"]
    
    def test_create_order_clears_cart(self, client, clear_db, auth_header, mock_product_service):
        """Test that creating order clears cart"""
        # Add items
        client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 1},
            headers=auth_header
        )
        
        # Create order
        client.post("/orders", headers=auth_header)
        
        # Verify cart is empty
        cart_response = client.get("/cart", headers=auth_header)
        assert len(cart_response.json()["items"]) == 0
        assert cart_response.json()["total"] == 0.0
    
    def test_create_order_no_auth(self, client, clear_db, mock_product_service):
        """Test creating order without authentication"""
        response = client.post("/orders")
        
        assert response.status_code == 403
    
    def test_list_orders_empty(self, client, clear_db, auth_header, mock_product_service):
        """Test listing orders when none exist"""
        response = client.get("/orders", headers=auth_header)
        
        assert response.status_code == 200
        data = response.json()
        assert data["orders"] == []
    
    def test_list_orders_with_items(self, client, clear_db, auth_header, mock_product_service):
        """Test listing orders"""
        # Create order
        client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 1},
            headers=auth_header
        )
        client.post("/orders", headers=auth_header)
        
        # List orders
        response = client.get("/orders", headers=auth_header)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["orders"]) == 1
        assert data["orders"][0]["status"] == "pending"
    
    def test_list_orders_no_auth(self, client, clear_db, mock_product_service):
        """Test listing orders without authentication"""
        response = client.get("/orders")
        
        assert response.status_code == 403
    
    def test_get_order_success(self, client, clear_db, auth_header, mock_product_service):
        """Test getting order details"""
        # Create order
        create_response = client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 2},
            headers=auth_header
        )
        order_response = client.post("/orders", headers=auth_header)
        order_id = order_response.json()["order_id"]
        
        # Get order
        response = client.get(f"/orders/{order_id}", headers=auth_header)
        
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == order_id
        assert data["user_id"] == "test-user-1"
        assert len(data["items"]) == 1
        assert data["items"][0]["product_id"] == "product-1"
    
    def test_get_order_not_found(self, client, clear_db, auth_header, mock_product_service):
        """Test getting non-existent order"""
        response = client.get("/orders/invalid-order-id", headers=auth_header)
        
        assert response.status_code == 404
        assert "Order not found" in response.json()["detail"]
    
    def test_get_order_no_auth(self, client, clear_db, mock_product_service):
        """Test getting order without authentication"""
        response = client.get("/orders/order-1")
        
        assert response.status_code == 403
    
    def test_per_user_order_isolation(self, client, clear_db, mock_product_service):
        """Test that orders are isolated per user"""
        user1_token = create_test_token(user_id="user-1", email="user1@example.com")
        user2_token = create_test_token(user_id="user-2", email="user2@example.com")
        
        user1_header = {"Authorization": f"Bearer {user1_token}"}
        user2_header = {"Authorization": f"Bearer {user2_token}"}
        
        # User 1 creates order
        client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 1},
            headers=user1_header
        )
        user1_order = client.post("/orders", headers=user1_header).json()
        
        # User 2 creates order
        client.post(
            "/cart/add",
            json={"product_id": "product-2", "quantity": 1},
            headers=user2_header
        )
        user2_order = client.post("/orders", headers=user2_header).json()
        
        # User 1 can only see their order
        user1_orders = client.get("/orders", headers=user1_header).json()
        assert len(user1_orders["orders"]) == 1
        assert user1_orders["orders"][0]["order_id"] == user1_order["order_id"]
        
        # User 2 can only see their order
        user2_orders = client.get("/orders", headers=user2_header).json()
        assert len(user2_orders["orders"]) == 1
        assert user2_orders["orders"][0]["order_id"] == user2_order["order_id"]
    
    def test_update_order_status_success(self, client, clear_db, auth_header, admin_auth_header, mock_product_service):
        """Test updating order status"""
        # Create order
        client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 1},
            headers=auth_header
        )
        order = client.post("/orders", headers=auth_header).json()
        order_id = order["order_id"]
        
        # Update status
        response = client.patch(
            f"/orders/{order_id}/status",
            json={"status": "confirmed"},
            headers=admin_auth_header
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == order_id
        assert data["status"] == "confirmed"
        assert "updated_at" in data
    
    def test_update_order_status_non_admin(self, client, clear_db, auth_header, mock_product_service):
        """Test updating order status as non-admin"""
        # Create order
        client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 1},
            headers=auth_header
        )
        order = client.post("/orders", headers=auth_header).json()
        order_id = order["order_id"]
        
        # Try to update status as non-admin
        response = client.patch(
            f"/orders/{order_id}/status",
            json={"status": "confirmed"},
            headers=auth_header
        )
        
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]
    
    def test_update_order_status_invalid_transition(self, client, clear_db, auth_header, admin_auth_header, mock_product_service):
        """Test invalid order status transition"""
        # Create order
        client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 1},
            headers=auth_header
        )
        order = client.post("/orders", headers=auth_header).json()
        order_id = order["order_id"]
        
        # Try invalid transition (pending -> shipped)
        response = client.patch(
            f"/orders/{order_id}/status",
            json={"status": "shipped"},
            headers=admin_auth_header
        )
        
        assert response.status_code == 400
        assert "Cannot transition" in response.json()["detail"]
    
    def test_update_order_status_not_found(self, client, clear_db, admin_auth_header, mock_product_service):
        """Test updating non-existent order status"""
        response = client.patch(
            "/orders/invalid-order-id/status",
            json={"status": "confirmed"},
            headers=admin_auth_header
        )
        
        assert response.status_code == 404
        assert "Order not found" in response.json()["detail"]
    
    def test_order_status_transitions(self, client, clear_db, auth_header, admin_auth_header, mock_product_service):
        """Test valid order status transitions"""
        # Create order
        client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 1},
            headers=auth_header
        )
        order = client.post("/orders", headers=auth_header).json()
        order_id = order["order_id"]
        
        # pending -> confirmed
        response = client.patch(
            f"/orders/{order_id}/status",
            json={"status": "confirmed"},
            headers=admin_auth_header
        )
        assert response.status_code == 200
        
        # confirmed -> shipped
        response = client.patch(
            f"/orders/{order_id}/status",
            json={"status": "shipped"},
            headers=admin_auth_header
        )
        assert response.status_code == 200
        
        # shipped -> delivered
        response = client.patch(
            f"/orders/{order_id}/status",
            json={"status": "delivered"},
            headers=admin_auth_header
        )
        assert response.status_code == 200
    
    def test_cancel_order_releases_inventory(self, client, clear_db, auth_header, admin_auth_header, mock_product_service):
        """Test that cancelling order releases inventory"""
        # Create order
        client.post(
            "/cart/add",
            json={"product_id": "product-1", "quantity": 10},
            headers=auth_header
        )
        order = client.post("/orders", headers=auth_header).json()
        order_id = order["order_id"]
        
        # Check inventory before cancel
        initial_inventory = mock_product_service["products"]["product-1"]["inventory_count"]
        
        # Cancel order
        client.patch(
            f"/orders/{order_id}/status",
            json={"status": "cancelled"},
            headers=admin_auth_header
        )
        
        # Check inventory after cancel
        final_inventory = mock_product_service["products"]["product-1"]["inventory_count"]
        
        # Inventory should be released
        assert final_inventory == initial_inventory + 10


# ============================================================================
# Health Check Tests
# ============================================================================

class TestHealthCheck:
    """Tests for health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
