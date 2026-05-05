"""
Pytest configuration and fixtures for Notification Service tests.
"""

import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi.testclient import TestClient

# Import app after path setup
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, notifications_db, JWT_SECRET, JWT_ALGORITHM


def create_test_token(user_id: str = "test-user-1", email: str = "test@example.com") -> str:
    """Create a test JWT token"""
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(hours=24)
    
    payload = {
        "sub": user_id,
        "email": email,
        "role": "customer",
        "exp": expiry,
        "iat": now
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def clear_db():
    """Clear in-memory database before each test"""
    notifications_db.clear()
    yield
    notifications_db.clear()


@pytest.fixture
def auth_header():
    """Authorization header with valid token"""
    token = create_test_token()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_header_user2():
    """Authorization header for a different user"""
    token = create_test_token(user_id="test-user-2", email="user2@example.com")
    return {"Authorization": f"Bearer {token}"}
