"""Cross-service integration tests for the e-commerce platform."""

import pytest
import httpx
import time

AUTH_SERVICE_URL = "http://localhost:8001"
PRODUCT_SERVICE_URL = "http://localhost:8002"
ORDER_SERVICE_URL = "http://localhost:8003"
NOTIFICATION_SERVICE_URL = "http://localhost:8004"


@pytest.mark.usefixtures("start_services")
class TestCrossServiceFlows:
    """Cross-service integration tests."""

    def test_complete_user_journey(self, http_client, admin_token):
        """Test complete user journey: register, browse products, add to cart, place order."""
        # Step 1: Register a new user
        register_payload = {
            "email": "journey@example.com",
            "password": "JourneyPassword123",
            "name": "Journey User"
        }
        register_response = http_client.post(
            f"{AUTH_SERVICE_URL}/auth/register",
            json=register_payload
        )
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]

        # Step 2: Login to get token
        login_payload = {
            "email": "journey@example.com",
            "password": "JourneyPassword123"
        }
        login_response = http_client.post(
            f"{AUTH_SERVICE_URL}/auth/login",
            json=login_payload
        )
        assert login_response.status_code == 200
        user_token = login_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Step 3: Create products (as admin)
        products = []
        for i in range(2):
            product_payload = {
                "name": f"Journey Product {i}",
                "description": f"Product for journey test {i}",
                "price": 29.99 + i,
                "inventory_count": 100,
                "category": "Test"
            }
            product_response = http_client.post(
                f"{PRODUCT_SERVICE_URL}/products",
                json=product_payload,
                headers=admin_headers
            )
            assert product_response.status_code == 201
            products.append(product_response.json())

        # Step 4: Browse products (public endpoint, no auth needed)
        list_response = http_client.get(f"{PRODUCT_SERVICE_URL}/products")
        assert list_response.status_code == 200
        assert len(list_response.json()["products"]) >= 2

        # Step 5: Add products to cart
        for product in products:
            cart_payload = {
                "product_id": product["id"],
                "quantity": 1
            }
            add_response = http_client.post(
                f"{ORDER_SERVICE_URL}/cart/add",
                json=cart_payload,
                headers=user_headers
            )
            assert add_response.status_code == 201

        # Step 6: View cart
        cart_response = http_client.get(
            f"{ORDER_SERVICE_URL}/cart",
            headers=user_headers
        )
        assert cart_response.status_code == 200
        assert len(cart_response.json()["items"]) == 2

        # Step 7: Place order
        order_response = http_client.post(
            f"{ORDER_SERVICE_URL}/orders",
            headers=user_headers
        )
        assert order_response.status_code == 201
        order_id = order_response.json()["id"]
        assert order_response.json()["status"] == "pending"

        # Step 8: Verify cart is cleared
        cart_response = http_client.get(
            f"{ORDER_SERVICE_URL}/cart",
            headers=user_headers
        )
        assert cart_response.status_code == 200
        assert len(cart_response.json()["items"]) == 0

        # Step 9: Get order details
        order_detail_response = http_client.get(
            f"{ORDER_SERVICE_URL}/orders/{order_id}",
            headers=user_headers
        )
        assert order_detail_response.status_code == 200
        assert order_detail_response.json()["id"] == order_id

    def test_inventory_management_on_order(self, http_client, admin_token):
        """Test that inventory is decremented when order is placed."""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Create a product with specific inventory
        product_payload = {
            "name": "Inventory Test Product",
            "description": "For inventory tracking",
            "price": 49.99,
            "inventory_count": 50,
            "category": "Test"
        }
        product_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=product_payload,
            headers=admin_headers
        )
        product_id = product_response.json()["id"]
        initial_inventory = product_response.json()["inventory_count"]

        # Get initial inventory
        get_response = http_client.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
        assert get_response.json()["inventory_count"] == 50

        # Create user and place order
        register_payload = {
            "email": "inventory@example.com",
            "password": "InventoryPassword123",
            "name": "Inventory User"
        }
        http_client.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_payload)

        login_payload = {
            "email": "inventory@example.com",
            "password": "InventoryPassword123"
        }
        login_response = http_client.post(f"{AUTH_SERVICE_URL}/auth/login", json=login_payload)
        user_token = login_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # Add to cart and place order
        cart_payload = {
            "product_id": product_id,
            "quantity": 10
        }
        http_client.post(
            f"{ORDER_SERVICE_URL}/cart/add",
            json=cart_payload,
            headers=user_headers
        )

        order_response = http_client.post(
            f"{ORDER_SERVICE_URL}/orders",
            headers=user_headers
        )
        assert order_response.status_code == 201

        # Check inventory was decremented
        get_response = http_client.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
        assert get_response.json()["inventory_count"] == 40

    def test_order_status_notification_flow(self, http_client, admin_token):
        """Test that order status changes trigger notifications."""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Create product
        product_payload = {
            "name": "Notification Test Product",
            "description": "For notification tracking",
            "price": 59.99,
            "inventory_count": 100,
            "category": "Test"
        }
        product_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=product_payload,
            headers=admin_headers
        )
        product_id = product_response.json()["id"]

        # Create user
        register_payload = {
            "email": "notification@example.com",
            "password": "NotificationPassword123",
            "name": "Notification User"
        }
        http_client.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_payload)

        login_payload = {
            "email": "notification@example.com",
            "password": "NotificationPassword123"
        }
        login_response = http_client.post(f"{AUTH_SERVICE_URL}/auth/login", json=login_payload)
        user_token = login_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # Place order
        cart_payload = {
            "product_id": product_id,
            "quantity": 1
        }
        http_client.post(
            f"{ORDER_SERVICE_URL}/cart/add",
            json=cart_payload,
            headers=user_headers
        )

        order_response = http_client.post(
            f"{ORDER_SERVICE_URL}/orders",
            headers=user_headers
        )
        order_id = order_response.json()["id"]

        # Wait a bit for webhook to be processed
        time.sleep(1)

        # Check notifications were created
        notifications_response = http_client.get(
            f"{NOTIFICATION_SERVICE_URL}/notifications",
            headers=user_headers
        )
        assert notifications_response.status_code == 200
        notifications = notifications_response.json()["notifications"]
        assert len(notifications) >= 1
        assert any(n["order_id"] == order_id for n in notifications)

        # Update order status
        status_payload = {"status": "confirmed"}
        http_client.patch(
            f"{ORDER_SERVICE_URL}/orders/{order_id}/status",
            json=status_payload,
            headers=admin_headers
        )

        # Wait for webhook
        time.sleep(1)

        # Check for new notification
        notifications_response = http_client.get(
            f"{NOTIFICATION_SERVICE_URL}/notifications",
            headers=user_headers
        )
        notifications = notifications_response.json()["notifications"]
        assert len(notifications) >= 2

    def test_multiple_users_isolation(self, http_client, admin_token):
        """Test that different users' data is isolated."""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Create product
        product_payload = {
            "name": "Isolation Test Product",
            "description": "For isolation test",
            "price": 69.99,
            "inventory_count": 100,
            "category": "Test"
        }
        product_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=product_payload,
            headers=admin_headers
        )
        product_id = product_response.json()["id"]

        # Create two users
        users = []
        for i in range(2):
            register_payload = {
                "email": f"user{i}@isolation.com",
                "password": "IsolationPassword123",
                "name": f"Isolation User {i}"
            }
            http_client.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_payload)

            login_payload = {
                "email": f"user{i}@isolation.com",
                "password": "IsolationPassword123"
            }
            login_response = http_client.post(f"{AUTH_SERVICE_URL}/auth/login", json=login_payload)
            token = login_response.json()["access_token"]
            users.append({
                "email": f"user{i}@isolation.com",
                "token": token,
                "headers": {"Authorization": f"Bearer {token}"}
            })

        # Each user places an order
        order_ids = []
        for user in users:
            cart_payload = {
                "product_id": product_id,
                "quantity": 1
            }
            http_client.post(
                f"{ORDER_SERVICE_URL}/cart/add",
                json=cart_payload,
                headers=user["headers"]
            )

            order_response = http_client.post(
                f"{ORDER_SERVICE_URL}/orders",
                headers=user["headers"]
            )
            order_ids.append(order_response.json()["id"])

        # Verify each user only sees their own orders
        for i, user in enumerate(users):
            orders_response = http_client.get(
                f"{ORDER_SERVICE_URL}/orders",
                headers=user["headers"]
            )
            user_orders = orders_response.json()["orders"]
            assert len(user_orders) >= 1
            assert any(o["id"] == order_ids[i] for o in user_orders)
            # User should not see other user's order
            assert not any(o["id"] == order_ids[1 - i] for o in user_orders)

    def test_insufficient_inventory_prevents_order(self, http_client, admin_token):
        """Test that order fails if inventory is insufficient."""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Create product with low inventory
        product_payload = {
            "name": "Low Stock Product",
            "description": "For low stock test",
            "price": 79.99,
            "inventory_count": 5,
            "category": "Test"
        }
        product_response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=product_payload,
            headers=admin_headers
        )
        product_id = product_response.json()["id"]

        # Create user
        register_payload = {
            "email": "lowstock@example.com",
            "password": "LowStockPassword123",
            "name": "Low Stock User"
        }
        http_client.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_payload)

        login_payload = {
            "email": "lowstock@example.com",
            "password": "LowStockPassword123"
        }
        login_response = http_client.post(f"{AUTH_SERVICE_URL}/auth/login", json=login_payload)
        user_token = login_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # Try to add more than available to cart
        cart_payload = {
            "product_id": product_id,
            "quantity": 10
        }
        add_response = http_client.post(
            f"{ORDER_SERVICE_URL}/cart/add",
            json=cart_payload,
            headers=user_headers
        )
        # Add should succeed (cart doesn't check inventory)
        assert add_response.status_code == 201

        # But order placement should fail
        order_response = http_client.post(
            f"{ORDER_SERVICE_URL}/orders",
            headers=user_headers
        )
        assert order_response.status_code == 400
        assert "insufficient" in order_response.json()["detail"].lower()

    def test_jwt_validation_across_services(self, http_client, admin_token):
        """Test that JWT tokens are validated consistently across services."""
        # Use admin token with product service
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        product_payload = {
            "name": "JWT Test Product",
            "description": "For JWT test",
            "price": 89.99,
            "inventory_count": 100,
            "category": "Test"
        }
        response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=product_payload,
            headers=admin_headers
        )
        assert response.status_code == 201

        # Use invalid token
        invalid_headers = {"Authorization": "Bearer invalid-token"}

        response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=product_payload,
            headers=invalid_headers
        )
        assert response.status_code == 401

        # Use expired token (we can't easily create one, so just verify invalid format)
        bad_headers = {"Authorization": "Bearer not.a.token"}

        response = http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=product_payload,
            headers=bad_headers
        )
        assert response.status_code == 401
