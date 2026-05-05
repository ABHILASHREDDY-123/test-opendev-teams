"""
Pytest configuration and fixtures for Order Service tests.
"""

import os
import sys
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from jose import jwt

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, carts_db, orders_db

# Test configuration
JWT_SECRET = "ecommerce-platform-secret-key-2026"
JWT_ALGORITHM = "HS256"


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def clear_db():
    """Clear in-memory databases before each test"""
    carts_db.clear()
    orders_db.clear()
    yield
    carts_db.clear()
    orders_db.clear()


def create_test_token(user_id: str = "test-user-1", email: str = "test@example.com", role: str = "customer") -> str:
    """Create a test JWT token"""
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(hours=24)
    
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": expiry,
        "iat": now
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


@pytest.fixture
def auth_header():
    """Authorization header with test token"""
    token = create_test_token()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_header():
    """Authorization header with admin test token"""
    token = create_test_token(role="admin")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_product_service(monkeypatch):
    """Mock product service responses"""
    
    # Mock product data
    products = {
        "product-1": {
            "id": "product-1",
            "name": "Test Product 1",
            "description": "A test product",
            "price": 99.99,
            "inventory_count": 100,
            "category": "electronics"
        },
        "product-2": {
            "id": "product-2",
            "name": "Test Product 2",
            "description": "Another test product",
            "price": 49.99,
            "inventory_count": 50,
            "category": "books"
        }
    }
    
    inventory_reserved = {}
    
    async def mock_get_product(product_id: str):
        """Mock get_product function"""
        return products.get(product_id)
    
    async def mock_reserve_inventory(product_id: str, quantity: int):
        """Mock reserve_inventory function"""
        if product_id not in products:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        product = products[product_id]
        if product["inventory_count"] < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient inventory"
            )
        
        product["inventory_count"] -= quantity
        if product_id not in inventory_reserved:
            inventory_reserved[product_id] = 0
        inventory_reserved[product_id] += quantity
        return True
    
    async def mock_release_inventory(product_id: str, quantity: int):
        """Mock release_inventory function"""
        if product_id not in products:
            return False
        
        product = products[product_id]
        product["inventory_count"] += quantity
        if product_id in inventory_reserved:
            inventory_reserved[product_id] -= quantity
        return True
    
    async def mock_send_notification(order_id: str, user_email: str, status_str: str):
        """Mock send_notification function"""
        return True
    
    # Patch the functions
    import main
    monkeypatch.setattr(main, "get_product", mock_get_product)
    monkeypatch.setattr(main, "reserve_inventory", mock_reserve_inventory)
    monkeypatch.setattr(main, "release_inventory", mock_release_inventory)
    monkeypatch.setattr(main, "send_notification", mock_send_notification)
    
    return {
        "products": products,
        "inventory_reserved": inventory_reserved
    }
