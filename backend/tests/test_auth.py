import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from backend.main import app

client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')

@pytest.mark.asyncio
async def test_register_success():
    response = await client.post('/auth/register', json={
        'mobile': '+1234567890',
        'password': 'strongpassword'
    })
    assert response.status_code == 201
    data = response.json()
    assert 'id' in data
    assert data['mobile'] == '+1234567890'

@pytest.mark.asyncio
async def test_register_duplicate_mobile():
    # First registration
    await client.post('/auth/register', json={
        'mobile': '+1234567890',
        'password': 'strongpassword'
    })
    # Second registration with same mobile
    response = await client.post('/auth/register', json={
        'mobile': '+1234567890',
        'password': 'anotherpassword'
    })
    assert response.status_code == 409
    assert response.json()['detail'] == 'Mobile number already registered'

@pytest.mark.asyncio
async def test_login_success():
    # Register first
    await client.post('/auth/register', json={
        'mobile': '+1234567890',
        'password': 'strongpassword'
    })
    # Then login
    response = await client.post('/auth/login', json={
        'mobile': '+1234567890',
        'password': 'strongpassword'
    })
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'

@pytest.mark.asyncio
async def test_login_wrong_password():
    # Register first
    await client.post('/auth/register', json={
        'mobile': '+1234567890',
        'password': 'strongpassword'
    })
    # Then login with wrong password
    response = await client.post('/auth/login', json={
        'mobile': '+1234567890',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid credentials'

@pytest.mark.asyncio
async def test_login_unknown_mobile():
    response = await client.post('/auth/login', json={
        'mobile': '+1234567890',
        'password': 'anypassword'
    })
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid credentials'

@pytest.mark.asyncio
async def test_register_missing_fields():
    # Test without mobile
    response = await client.post('/auth/register', json={
        'password': 'strongpassword'
    })
    assert response.status_code == 422
    # Test without password
    response = await client.post('/auth/register', json={
        'mobile': '+1234567890'
    })
    assert response.status_code == 422