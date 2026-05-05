# E-Commerce Platform Integration Tests

Comprehensive integration test suite for the e-commerce platform with 4 services:
- Auth Service (port 8001)
- Product Service (port 8002)
- Order Service (port 8003)
- Notification Service (port 8004)

## Test Coverage

### Service-Specific Tests
- **test_auth_service.py**: Auth service endpoints (register, login, profile)
- **test_product_service.py**: Product CRUD, inventory management
- **test_order_service.py**: Cart, order placement, order management
- **test_notification_service.py**: Webhook reception, notification retrieval

### Cross-Service Integration Tests
- **test_cross_service_flows.py**: Complete user journeys and multi-service scenarios

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install -r integration_tests/requirements.txt

# Install service dependencies (each service)
pip install -r auth-service/requirements.txt
pip install -r product-service/requirements.txt
pip install -r order-service/requirements.txt
pip install -r notification-service/requirements.txt
```

### Run All Integration Tests
```bash
pytest integration_tests/ -v
```

### Run Specific Test File
```bash
pytest integration_tests/test_cross_service_flows.py -v
```

### Run Specific Test
```bash
pytest integration_tests/test_cross_service_flows.py::TestCrossServiceFlows::test_complete_user_journey -v
```

## Test Scenarios

### Complete User Journey
1. User registration
2. User login (JWT token generation)
3. Admin creates products
4. User browses products
5. User adds products to cart
6. User places order
7. Order status changes trigger notifications
8. User receives notifications

### Inventory Management
- Products are created with inventory count
- Inventory is decremented when order is placed
- Order fails if insufficient inventory
- Inventory can be reserved and released

### Multi-User Isolation
- Different users see only their own orders
- Different users see only their own notifications
- Cart is per-user

### Authentication & Authorization
- JWT tokens are validated across all services
- Admin-only endpoints require admin role
- Public endpoints don't require auth
- Invalid tokens are rejected

## Test Fixtures

### HTTP Client
- `http_client`: Synchronous HTTP client for making requests
- `async_http_client`: Async HTTP client

### Authentication
- `test_token`: Regular user JWT token (test@example.com)
- `admin_token`: Admin user JWT token (admin@example.com)
- `test_token_user2`: Different user JWT token (user2@example.com)
- `auth_headers`: Headers with test_token
- `admin_headers`: Headers with admin_token

### Service Management
- `start_services`: Fixture that starts all 4 services before tests

## Environment Variables

The integration tests set these environment variables for the services:
- `JWT_SECRET`: ecommerce-platform-secret-key-2026
- `AUTH_SERVICE_URL`: http://localhost:8001
- `PRODUCT_SERVICE_URL`: http://localhost:8002
- `ORDER_SERVICE_URL`: http://localhost:8003
- `NOTIFICATION_SERVICE_URL`: http://localhost:8004

## Test Results

All tests verify:
- ✓ HTTP status codes (201, 200, 400, 401, 403, 404, etc.)
- ✓ Response JSON structure and data
- ✓ Cross-service communication
- ✓ Data isolation between users
- ✓ Authorization and authentication
- ✓ Inventory management
- ✓ Order workflow
- ✓ Notification delivery

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
1. All services are started automatically
2. Tests wait for services to be ready
3. Tests clean up after themselves
4. Services are stopped after tests complete
