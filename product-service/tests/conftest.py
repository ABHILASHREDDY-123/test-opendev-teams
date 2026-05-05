"""
Test configuration and fixtures for Product Service tests.
"""

import pytest
from datetime import datetime, timedelta
from jose import jwt
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, products_db, JWT_SECRET


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    """Clear the products database before each test."""
    products_db.clear()
    yield
    products_db.clear()


def create_jwt_token(user_id: str, email: str, role: str = "customer", expires_in_hours: int = 24) -> str:
    """
    Create a JWT token for testing.
    
    Args:
        user_id: User ID
        email: User email
        role: User role (customer or admin)
        expires_in_hours: Token expiration time in hours
        
    Returns:
        JWT token string
    """
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=expires_in_hours)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token


@pytest.fixture
def admin_token():
    """Create an admin JWT token for testing."""
    return create_jwt_token("admin-user-1", "admin@example.com", role="admin")


@pytest.fixture
def customer_token():
    """Create a customer JWT token for testing."""
    return create_jwt_token("customer-user-1", "customer@example.com", role="customer")


@pytest.fixture
def expired_token():
    """Create an expired JWT token for testing."""
    payload = {
        "sub": "user-1",
        "email": "user@example.com",
        "role": "customer",
        "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token


@pytest.fixture
def sample_product():
    """Sample product data for testing."""
    return {
        "name": "Test Product",
        "description": "A test product",
        "price": 99.99,
        "inventory_count": 100,
        "category": "Electronics"
    }
