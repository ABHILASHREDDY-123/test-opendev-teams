"""Integration tests for Order Service."""

import pytest
import httpx
import time

AUTH_SERVICE_URL = "http://localhost:8001"
PRODUCT_SERVICE_URL = "http://localhost:8002"
ORDER_SERVICE_URL = "http://localhost:8003"


@pytest.mark.usefixtures("start_services")
class TestOrderService:
    """Order Service integration tests."""

    def test_health_check(self, http_client):
        """Test order service health check."""
        response = http_client.get(f"{ORDER_SERVICE_URL}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_get_empty_cart(self, http_client, auth_headers):
        """Test getting empty cart."""
        response = http_client.get(
            f"{ORDER_SERVICE_URL}/cart",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    def test_add_to_cart_requires_auth(self, http_client, admin_headers):
        """Test that adding to cart requires authentication."""
        # First create a product
        product_payload = {
            "name": "Cart Test Product",
            "description": "For cart test",
            "price": 29.99,
            "inventory_count": 100,
            "category": "Test"
        }
        product_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=product_payload,
            headers=admin_headers
        )
        product_id = product_response.json()["id"]

        # Try to add to cart without auth
        cart_payload = {
            "product_id": product_id,
            "quantity": 1
        }
        response = http_client.post(
            f"{ORDER_SERVICE_URL}/cart/add",
            json=cart_payload
        )
        assert response.status_code == 401

    def test_add_to_cart_success(self, http_client, auth_headers, admin_headers):
        """Test adding product to cart."""
        # Create a product
        product_payload = {
            "name": "Add to Cart Product",
            "description": "For cart test",
            "price": 34.99,
            "inventory_count": 100,
            "category": "Test"
        }
        product_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=product_payload,
            headers=admin_headers
        )
        product_id = product_response.json()["id"]

        # Add to cart
        cart_payload = {
            "product_id": product_id,
            "quantity": 2
        }
        response = http_client.post(
            f"{ORDER_SERVICE_URL}/cart/add",
            json=cart_payload,
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["product_id"] == product_id
        assert data["items"][0]["quantity"] == 2

    def test_get_cart_after_add(self, http_client, auth_headers, admin_headers):
        """Test getting cart after adding items."""
        # Create a product
        product_payload = {
            "name": "Get Cart Product",
            "description": "For cart test",
            "price": 44.99,
            "inventory_count": 100,
            "category": "Test"
        }
        product_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=product_payload,
            headers=admin_headers
        )
        product_id = product_response.json()["id"]

        # Add to cart
        cart_payload = {
            "product_id": product_id,
            "quantity": 3
        }
        http_client.post(
            f"{ORDER_SERVICE_URL}/cart/add",
            json=cart_payload,
            headers=auth_headers
        )

        # Get cart
        response = http_client.get(
            f"{ORDER_SERVICE_URL}/cart",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["product_id"] == product_id

    def test_remove_from_cart(self, http_client, auth_headers, admin_headers):
        """Test removing item from cart."""
        # Create a product and add to cart
        product_payload = {
            "name": "Remove Cart Product",
            "description": "For cart test",
            "price": 24.99,
            "inventory_count": 100,
            "category": "Test"
        }
        product_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=product_payload,
            headers=admin_headers
        )
        product_id = product_response.json()["id"]

        cart_payload = {
            "product_id": product_id,
            "quantity": 1
        }
        add_response = http_client.post(
            f"{ORDER_SERVICE_URL}/cart/add",
            json=cart_payload,
            headers=auth_headers
        )
        item_id = add_response.json()["items"][0]["id"]

        # Remove from cart
        response = http_client.delete(
            f"{ORDER_SERVICE_URL}/cart/{item_id}",
            headers=auth_headers
        )
        assert response.status_code == 204

        # Verify cart is empty
        response = http_client.get(
            f"{ORDER_SERVICE_URL}/cart",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["items"] == []

    def test_place_order_success(self, http_client, auth_headers, admin_headers):
        """Test placing an order."""
        # Create a product
        product_payload = {
            "name": "Order Product",
            "description": "For order test",
            "price": 54.99,
            "inventory_count": 100,
            "category": "Test"
        }
        product_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=product_payload,
            headers=admin_headers
        )
        product_id = product_response.json()["id"]

        # Add to cart
        cart_payload = {
            "product_id": product_id,
            "quantity": 2
        }
        http_client.post(
            f"{ORDER_SERVICE_URL}/cart/add",
            json=cart_payload,
            headers=auth_headers
        )

        # Place order
        response = http_client.post(
            f"{ORDER_SERVICE_URL}/orders",
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"
        assert len(data["items"]) == 1

    def test_place_order_empty_cart_fails(self, http_client, auth_headers):
        """Test that placing order with empty cart fails."""
        response = http_client.post(
            f"{ORDER_SERVICE_URL}/orders",
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_get_user_orders(self, http_client, auth_headers, admin_headers):
        """Test getting user's orders."""
        # Create product and place order
        product_payload = {
            "name": "Get Orders Product",
            "description": "For orders test",
            "price": 64.99,
            "inventory_count": 100,
            "category": "Test"
        }
        product_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=product_payload,
            headers=admin_headers
        )
        product_id = product_response.json()["id"]

        cart_payload = {
            "product_id": product_id,
            "quantity": 1
        }
        http_client.post(
            f"{ORDER_SERVICE_URL}/cart/add",
            json=cart_payload,
            headers=auth_headers
        )

        order_response = http_client.post(
            f"{ORDER_SERVICE_URL}/orders",
            headers=auth_headers
        )
        order_id = order_response.json()["id"]

        # Get orders
        response = http_client.get(
            f"{ORDER_SERVICE_URL}/orders",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["orders"]) >= 1
        assert any(o["id"] == order_id for o in data["orders"])

    def test_get_order_by_id(self, http_client, auth_headers, admin_headers):
        """Test getting a specific order."""
        # Create product and place order
        product_payload = {
            "name": "Get Order Product",
            "description": "For order test",
            "price": 74.99,
            "inventory_count": 100,
            "category": "Test"
        }
        product_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=product_payload,
            headers=admin_headers
        )
        product_id = product_response.json()["id"]

        cart_payload = {
            "product_id": product_id,
            "quantity": 1
        }
        http_client.post(
            f"{ORDER_SERVICE_URL}/cart/add",
            json=cart_payload,
            headers=auth_headers
        )

        order_response = http_client.post(
            f"{ORDER_SERVICE_URL}/orders",
            headers=auth_headers
        )
        order_id = order_response.json()["id"]

        # Get order
        response = http_client.get(
            f"{ORDER_SERVICE_URL}/orders/{order_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id
        assert data["status"] == "pending"

    def test_update_order_status(self, http_client, auth_headers, admin_headers):
        """Test updating order status."""
        # Create product and place order
        product_payload = {
            "name": "Status Update Product",
            "description": "For status test",
            "price": 84.99,
            "inventory_count": 100,
            "category": "Test"
        }
        product_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=product_payload,
            headers=admin_headers
        )
        product_id = product_response.json()["id"]

        cart_payload = {
            "product_id": product_id,
            "quantity": 1
        }
        http_client.post(
            f"{ORDER_SERVICE_URL}/cart/add",
            json=cart_payload,
            headers=auth_headers
        )

        order_response = http_client.post(
            f"{ORDER_SERVICE_URL}/orders",
            headers=auth_headers
        )
        order_id = order_response.json()["id"]

        # Update status as admin
        status_payload = {"status": "confirmed"}
        response = http_client.patch(
            f"{ORDER_SERVICE_URL}/orders/{order_id}/status",
            json=status_payload,
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"

    def test_update_order_status_non_admin_fails(self, http_client, auth_headers, admin_headers):
        """Test that non-admin cannot update order status."""
        # Create product and place order
        product_payload = {
            "name": "Status Auth Product",
            "description": "For auth test",
            "price": 94.99,
            "inventory_count": 100,
            "category": "Test"
        }
        product_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=product_payload,
            headers=admin_headers
        )
        product_id = product_response.json()["id"]

        cart_payload = {
            "product_id": product_id,
            "quantity": 1
        }
        http_client.post(
            f"{ORDER_SERVICE_URL}/cart/add",
            json=cart_payload,
            headers=auth_headers
        )

        order_response = http_client.post(
            f"{ORDER_SERVICE_URL}/orders",
            headers=auth_headers
        )
        order_id = order_response.json()["id"]

        # Try to update status as non-admin
        status_payload = {"status": "confirmed"}
        response = http_client.patch(
            f"{ORDER_SERVICE_URL}/orders/{order_id}/status",
            json=status_payload,
            headers=auth_headers
        )
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()
