import pytest
from fastapi.testclient import TestClient
from jose import jwt
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
import sys
import os

# Add parent directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, JWT_SECRET, carts, orders, order_counter

client = TestClient(app)

# ==================== Test Fixtures ====================

@pytest.fixture(autouse=True)
def reset_state():
    """Reset in-memory state before each test."""
    carts.clear()
    orders.clear()
    yield


def create_token(user_id: str, role: str = "user") -> str:
    """Create a JWT token for testing."""
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def create_auth_header(token: str) -> dict:
    """Create authorization header."""
    return {"Authorization": f"Bearer {token}"}


# ==================== Health Check Tests ====================

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ==================== Cart Tests ====================

@patch('main.verify_product_exists')
def test_add_to_cart_success(mock_verify):
    """Test adding item to cart successfully."""
    mock_verify.return_value = {"id": "prod1", "name": "Test Product", "price": 100.0}
    
    token = create_token("user1")
    headers = create_auth_header(token)
    
    response = client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 2, "price": 100.0},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user1"
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == "prod1"
    assert data["items"][0]["quantity"] == 2
    assert data["total"] == 200.0


def test_add_to_cart_missing_auth():
    """Test adding to cart without authentication."""
    response = client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 2, "price": 100.0}
    )
    
    assert response.status_code == 401


def test_add_to_cart_invalid_token():
    """Test adding to cart with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 2, "price": 100.0},
        headers=headers
    )
    
    assert response.status_code == 401


def test_get_cart_empty():
    """Test getting empty cart."""
    token = create_token("user1")
    headers = create_auth_header(token)
    
    response = client.get("/cart", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user1"
    assert len(data["items"]) == 0
    assert data["total"] == 0.0


@patch('main.verify_product_exists')
def test_get_cart_with_items(mock_verify):
    """Test getting cart with items."""
    mock_verify.return_value = {"id": "prod1", "name": "Test Product", "price": 100.0}
    
    token = create_token("user1")
    headers = create_auth_header(token)
    
    # Add items to cart
    client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 2, "price": 100.0},
        headers=headers
    )
    client.post(
        "/cart/add",
        json={"product_id": "prod2", "quantity": 1, "price": 50.0},
        headers=headers
    )
    
    # Get cart
    response = client.get("/cart", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 250.0


@patch('main.verify_product_exists')
def test_remove_from_cart_success(mock_verify):
    """Test removing item from cart."""
    mock_verify.return_value = {"id": "prod1", "name": "Test Product", "price": 100.0}
    
    token = create_token("user1")
    headers = create_auth_header(token)
    
    # Add item to cart
    client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 2, "price": 100.0},
        headers=headers
    )
    
    # Remove item
    response = client.delete("/cart/prod1", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0
    assert data["total"] == 0.0


def test_remove_from_cart_not_found():
    """Test removing non-existent item from cart."""
    token = create_token("user1")
    headers = create_auth_header(token)
    
    response = client.delete("/cart/nonexistent", headers=headers)
    
    assert response.status_code == 404


# ==================== Order Tests ====================

@patch('main.reserve_product')
@patch('main.verify_product_exists')
def test_place_order_success(mock_verify, mock_reserve):
    """Test placing order successfully."""
    mock_verify.return_value = {"id": "prod1", "name": "Test Product", "price": 100.0}
    mock_reserve.return_value = True
    
    token = create_token("user1")
    headers = create_auth_header(token)
    
    # Add item to cart
    client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 2, "price": 100.0},
        headers=headers
    )
    
    # Place order
    response = client.post("/orders", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user1"
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == "prod1"
    assert data["total"] == 200.0
    assert data["status"] == "pending"
    assert "order_id" in data


def test_place_order_empty_cart():
    """Test placing order with empty cart."""
    token = create_token("user1")
    headers = create_auth_header(token)
    
    response = client.post("/orders", headers=headers)
    
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


@patch('main.reserve_product')
@patch('main.verify_product_exists')
def test_place_order_clears_cart(mock_verify, mock_reserve):
    """Test that placing order clears the cart."""
    mock_verify.return_value = {"id": "prod1", "name": "Test Product", "price": 100.0}
    mock_reserve.return_value = True
    
    token = create_token("user1")
    headers = create_auth_header(token)
    
    # Add item to cart
    client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 2, "price": 100.0},
        headers=headers
    )
    
    # Place order
    client.post("/orders", headers=headers)
    
    # Check cart is empty
    response = client.get("/cart", headers=headers)
    assert len(response.json()["items"]) == 0


def test_list_orders_empty():
    """Test listing orders when none exist."""
    token = create_token("user1")
    headers = create_auth_header(token)
    
    response = client.get("/orders", headers=headers)
    
    assert response.status_code == 200
    assert response.json() == []


@patch('main.reserve_product')
@patch('main.verify_product_exists')
def test_list_orders_user_isolation(mock_verify, mock_reserve):
    """Test that users only see their own orders."""
    mock_verify.return_value = {"id": "prod1", "name": "Test Product", "price": 100.0}
    mock_reserve.return_value = True
    
    # User 1 places order
    token1 = create_token("user1")
    headers1 = create_auth_header(token1)
    
    client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 1, "price": 100.0},
        headers=headers1
    )
    client.post("/orders", headers=headers1)
    
    # User 2 places order
    token2 = create_token("user2")
    headers2 = create_auth_header(token2)
    
    client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 1, "price": 100.0},
        headers=headers2
    )
    client.post("/orders", headers=headers2)
    
    # User 1 should see only their order
    response1 = client.get("/orders", headers=headers1)
    assert len(response1.json()) == 1
    assert response1.json()[0]["user_id"] == "user1"
    
    # User 2 should see only their order
    response2 = client.get("/orders", headers=headers2)
    assert len(response2.json()) == 1
    assert response2.json()[0]["user_id"] == "user2"


@patch('main.reserve_product')
@patch('main.verify_product_exists')
def test_get_order_success(mock_verify, mock_reserve):
    """Test getting order details."""
    mock_verify.return_value = {"id": "prod1", "name": "Test Product", "price": 100.0}
    mock_reserve.return_value = True
    
    token = create_token("user1")
    headers = create_auth_header(token)
    
    # Place order
    client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 2, "price": 100.0},
        headers=headers
    )
    place_response = client.post("/orders", headers=headers)
    order_id = place_response.json()["order_id"]
    
    # Get order
    response = client.get(f"/orders/{order_id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == order_id
    assert data["user_id"] == "user1"


def test_get_order_not_found():
    """Test getting non-existent order."""
    token = create_token("user1")
    headers = create_auth_header(token)
    
    response = client.get("/orders/nonexistent", headers=headers)
    
    assert response.status_code == 404


@patch('main.reserve_product')
@patch('main.verify_product_exists')
def test_get_order_access_denied(mock_verify, mock_reserve):
    """Test that users cannot access other users' orders."""
    mock_verify.return_value = {"id": "prod1", "name": "Test Product", "price": 100.0}
    mock_reserve.return_value = True
    
    # User 1 places order
    token1 = create_token("user1")
    headers1 = create_auth_header(token1)
    
    client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 1, "price": 100.0},
        headers=headers1
    )
    place_response = client.post("/orders", headers=headers1)
    order_id = place_response.json()["order_id"]
    
    # User 2 tries to access User 1's order
    token2 = create_token("user2")
    headers2 = create_auth_header(token2)
    
    response = client.get(f"/orders/{order_id}", headers=headers2)
    
    assert response.status_code == 403


@patch('main.send_notification')
@patch('main.reserve_product')
@patch('main.verify_product_exists')
def test_update_order_status_admin_only(mock_verify, mock_reserve, mock_notify):
    """Test that only admins can update order status."""
    mock_verify.return_value = {"id": "prod1", "name": "Test Product", "price": 100.0}
    mock_reserve.return_value = True
    mock_notify.return_value = True
    
    # User places order
    token_user = create_token("user1")
    headers_user = create_auth_header(token_user)
    
    client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 1, "price": 100.0},
        headers=headers_user
    )
    place_response = client.post("/orders", headers=headers_user)
    order_id = place_response.json()["order_id"]
    
    # Non-admin tries to update status
    response = client.patch(
        f"/orders/{order_id}/status",
        json={"status": "confirmed"},
        headers=headers_user
    )
    
    assert response.status_code == 403


@patch('main.send_notification')
@patch('main.reserve_product')
@patch('main.verify_product_exists')
def test_update_order_status_success(mock_verify, mock_reserve, mock_notify):
    """Test updating order status as admin."""
    mock_verify.return_value = {"id": "prod1", "name": "Test Product", "price": 100.0}
    mock_reserve.return_value = True
    mock_notify.return_value = True
    
    # User places order
    token_user = create_token("user1")
    headers_user = create_auth_header(token_user)
    
    client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 1, "price": 100.0},
        headers=headers_user
    )
    place_response = client.post("/orders", headers=headers_user)
    order_id = place_response.json()["order_id"]
    
    # Admin updates status
    token_admin = create_token("admin1", role="admin")
    headers_admin = create_auth_header(token_admin)
    
    response = client.patch(
        f"/orders/{order_id}/status",
        json={"status": "confirmed"},
        headers=headers_admin
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "confirmed"


@patch('main.release_product')
@patch('main.send_notification')
@patch('main.reserve_product')
@patch('main.verify_product_exists')
def test_cancel_order_releases_inventory(mock_verify, mock_reserve, mock_notify, mock_release):
    """Test that cancelling order releases inventory."""
    mock_verify.return_value = {"id": "prod1", "name": "Test Product", "price": 100.0}
    mock_reserve.return_value = True
    mock_notify.return_value = True
    mock_release.return_value = True
    
    # User places order
    token_user = create_token("user1")
    headers_user = create_auth_header(token_user)
    
    client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 2, "price": 100.0},
        headers=headers_user
    )
    place_response = client.post("/orders", headers=headers_user)
    order_id = place_response.json()["order_id"]
    
    # Admin cancels order
    token_admin = create_token("admin1", role="admin")
    headers_admin = create_auth_header(token_admin)
    
    response = client.patch(
        f"/orders/{order_id}/status",
        json={"status": "cancelled"},
        headers=headers_admin
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    # Verify release was called
    mock_release.assert_called()


# ==================== Edge Cases ====================

@patch('main.verify_product_exists')
def test_add_multiple_items_same_product(mock_verify):
    """Test adding same product multiple times increases quantity."""
    mock_verify.return_value = {"id": "prod1", "name": "Test Product", "price": 100.0}
    
    token = create_token("user1")
    headers = create_auth_header(token)
    
    # Add same product twice
    client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 2, "price": 100.0},
        headers=headers
    )
    response = client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 3, "price": 100.0},
        headers=headers
    )
    
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 5
    assert data["total"] == 500.0


def test_missing_authorization_header():
    """Test missing authorization header."""
    response = client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 1, "price": 100.0}
    )
    assert response.status_code == 401


def test_invalid_authorization_scheme():
    """Test invalid authorization scheme."""
    headers = {"Authorization": "Basic dXNlcjpwYXNz"}
    response = client.post(
        "/cart/add",
        json={"product_id": "prod1", "quantity": 1, "price": 100.0},
        headers=headers
    )
    assert response.status_code == 401
