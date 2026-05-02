# Contacts API - Backend

A complete REST API for user authentication and contacts management built with FastAPI.

## Features

- **User Authentication**: Register and login with mobile number and password
- **JWT Tokens**: Secure authentication using JSON Web Tokens
- **Contacts Management**: Create, read, update, and delete contacts
- **Per-User Isolation**: Each user can only access their own contacts
- **Input Validation**: Comprehensive validation for all inputs
- **Password Security**: Passwords hashed with bcrypt

## Tech Stack

- **Framework**: FastAPI
- **Validation**: Pydantic v2
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Testing**: pytest
- **HTTP Client**: httpx

## API Endpoints

### Authentication

#### POST /api/auth/register
Register a new user.

**Request:**
```json
{
  "mobile": "9876543210",
  "password": "password123"
}
```

**Response (201):**
```json
{
  "id": "uuid-string",
  "mobile": "9876543210"
}
```

**Errors:**
- `400`: Mobile number already registered
- `422`: Validation error (mobile < 10 digits, password < 6 chars, etc.)

#### POST /api/auth/login
Login and receive JWT token.

**Request:**
```json
{
  "mobile": "9876543210",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors:**
- `401`: Invalid credentials
- `422`: Validation error

### Contacts

#### POST /api/contacts
Create a new contact (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "name": "John Doe",
  "mobile": "1234567890"
}
```

**Response (201):**
```json
{
  "id": "uuid-string",
  "name": "John Doe",
  "mobile": "1234567890",
  "user_id": "uuid-string"
}
```

**Errors:**
- `400`: Validation error
- `401`: Missing or invalid token

#### GET /api/contacts
List all contacts for authenticated user (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": "uuid-string",
    "name": "John Doe",
    "mobile": "1234567890",
    "user_id": "uuid-string"
  }
]
```

**Errors:**
- `401`: Missing or invalid token

#### PUT /api/contacts/{id}
Update a contact (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "name": "Jane Doe",
  "mobile": "0987654321"
}
```

**Response (200):**
```json
{
  "id": "uuid-string",
  "name": "Jane Doe",
  "mobile": "0987654321",
  "user_id": "uuid-string"
}
```

**Errors:**
- `404`: Contact not found or belongs to different user
- `401`: Missing or invalid token
- `422`: Validation error

#### DELETE /api/contacts/{id}
Delete a contact (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (204):** No content

**Errors:**
- `404`: Contact not found or belongs to different user
- `401`: Missing or invalid token

## Setup

### Install Dependencies

```bash
pip install fastapi pydantic python-jose passlib bcrypt pytest httpx
```

### Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Run Tests

```bash
pytest -v test_main.py
```

## Test Coverage

The test suite includes 46 comprehensive tests covering:

- **Registration**: Success, duplicates, validation errors
- **Login**: Success, invalid credentials, validation errors
- **Contact Creation**: Success, validation errors, authentication
- **Contact Listing**: Empty list, multiple contacts, per-user isolation
- **Contact Updates**: Name, mobile, both fields, validation, isolation
- **Contact Deletion**: Success, not found, isolation
- **Authentication**: Missing token, invalid token, malformed headers
- **Per-User Isolation**: Verifies users cannot access other users' contacts

All tests pass: **46/46 ✅**

## Key Implementation Details

### Password Security
- Passwords are hashed using bcrypt with automatic salt generation
- Plain text passwords are never stored
- Password verification uses constant-time comparison

### JWT Authentication
- Tokens include user_id and mobile in the payload
- Tokens expire after 30 minutes
- Token verification includes expiration check

### Per-User Isolation
- All contact operations verify the contact belongs to the authenticated user
- Users cannot access, modify, or delete other users' contacts
- Attempting to access another user's contact returns 404 (not found)

### Data Storage
- In-memory dictionary-based storage
- Mobile-to-user index for fast lookups
- No external database required

## Validation Rules

### Mobile Number
- Minimum 10 digits
- Must contain only numeric characters
- Must be unique across all users

### Password
- Minimum 6 characters
- No specific character requirements (can be customized)

### Contact Name
- Required field
- Cannot be empty or whitespace-only

### Contact Mobile
- Minimum 10 digits
- Must contain only numeric characters

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success (GET, PUT)
- `201`: Created (POST)
- `204`: No content (DELETE)
- `400`: Bad request (validation errors, duplicate mobile)
- `401`: Unauthorized (missing/invalid token)
- `404`: Not found (contact not found, or belongs to different user)
- `422`: Unprocessable entity (validation errors from Pydantic)

## Security Considerations

1. **Password Hashing**: All passwords are hashed with bcrypt
2. **JWT Tokens**: Secure token-based authentication
3. **Per-User Isolation**: Strict enforcement of user data boundaries
4. **Input Validation**: All inputs validated with Pydantic
5. **HTTPS**: Should be used in production (not enforced in this example)
6. **Secret Key**: Change `SECRET_KEY` in production

## Future Enhancements

- Database integration (PostgreSQL, MongoDB, etc.)
- Rate limiting
- CORS configuration
- Logging and monitoring
- API documentation (Swagger/OpenAPI)
- Refresh token mechanism
- Email verification
- Password reset functionality
