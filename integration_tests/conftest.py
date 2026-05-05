"""Pytest configuration and fixtures for integration tests."""

import sys
import os
import asyncio
import subprocess
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pytest
import httpx
from jose import jwt

# Test configuration
JWT_SECRET = "ecommerce-platform-secret-key-2026"
JWT_ALGORITHM = "HS256"

# Service URLs
AUTH_SERVICE_URL = "http://localhost:8001"
PRODUCT_SERVICE_URL = "http://localhost:8002"
ORDER_SERVICE_URL = "http://localhost:8003"
NOTIFICATION_SERVICE_URL = "http://localhost:8004"

# Service processes (started during fixtures)
service_processes = {}


def create_test_token(user_id: str = "test-user-1", email: str = "test@example.com", role: str = "customer") -> str:
    """Create a test JWT token."""
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


def create_admin_token(user_id: str = "admin-user-1", email: str = "admin@example.com") -> str:
    """Create an admin JWT token."""
    return create_test_token(user_id=user_id, email=email, role="admin")


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def start_services():
    """Start all services before running tests."""
    services = [
        ("auth-service", 8001),
        ("product-service", 8002),
        ("order-service", 8003),
        ("notification-service", 8004),
    ]

    # Set environment variables
    env = os.environ.copy()
    env["JWT_SECRET"] = JWT_SECRET
    env["AUTH_SERVICE_URL"] = AUTH_SERVICE_URL
    env["PRODUCT_SERVICE_URL"] = PRODUCT_SERVICE_URL
    env["ORDER_SERVICE_URL"] = ORDER_SERVICE_URL
    env["NOTIFICATION_SERVICE_URL"] = NOTIFICATION_SERVICE_URL

    # Start each service
    for service_name, port in services:
        service_path = Path(__file__).parent.parent / service_name
        main_file = service_path / "main.py"

        if not main_file.exists():
            pytest.skip(f"Service {service_name} not found at {main_file}")

        print(f"Starting {service_name} on port {port}...")

        proc = subprocess.Popen(
            [sys.executable, str(main_file)],
            cwd=str(service_path),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        service_processes[service_name] = proc

        # Wait for service to be ready
        max_retries = 30
        for i in range(max_retries):
            try:
                response = httpx.get(f"http://localhost:{port}/health", timeout=1.0)
                if response.status_code == 200:
                    print(f"✓ {service_name} is ready")
                    break
            except Exception:
                pass

            if i == max_retries - 1:
                # Print service output for debugging
                proc.terminate()
                stdout, stderr = proc.communicate(timeout=5)
                print(f"Failed to start {service_name}")
                print(f"STDOUT: {stdout.decode()}")
                print(f"STDERR: {stderr.decode()}")
                raise RuntimeError(f"Service {service_name} failed to start")

            time.sleep(0.5)

    yield

    # Cleanup: stop all services
    for service_name, proc in service_processes.items():
        print(f"Stopping {service_name}...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.fixture
def http_client():
    """Create an HTTP client for making requests."""
    return httpx.Client(timeout=10.0)


@pytest.fixture
def async_http_client():
    """Create an async HTTP client for making requests."""
    return httpx.AsyncClient(timeout=10.0)


@pytest.fixture
def test_token():
    """Create a test JWT token."""
    return create_test_token()


@pytest.fixture
def admin_token():
    """Create an admin JWT token."""
    return create_admin_token()


@pytest.fixture
def test_token_user2():
    """Create a test JWT token for a different user."""
    return create_test_token(user_id="test-user-2", email="user2@example.com")


@pytest.fixture
def auth_headers(test_token):
    """Create authorization headers with test token."""
    return {"Authorization": f"Bearer {test_token}"}


@pytest.fixture
def admin_headers(admin_token):
    """Create authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}
