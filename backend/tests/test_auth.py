import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_register_success():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
        assert response.status_code == 201
        assert 'id' in response.json()
        assert response.json()['mobile'] == '1234567890'

@pytest.mark.asyncio
async def test_register_duplicate_mobile():
    async with AsyncClient(app=app, base_url='http://test') as client:
        await client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
        response = await client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
        assert response.status_code == 409

@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(app=app, base_url='http://test') as client:
        await client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
        response = await client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password'})
        assert response.status_code == 200
        assert 'access_token' in response.json()

@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(app=app, base_url='http://test') as client:
        await client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
        response = await client.post('/auth/login', json={'mobile': '1234567890', 'password': 'wrong_password'})
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_unknown_mobile():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password'})
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_register_missing_fields():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.post('/auth/register', json={'mobile': '1234567890'})
        assert response.status_code == 422
