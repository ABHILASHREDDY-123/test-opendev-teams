import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from backend.main import app

@pytest.mark.asyncio
async def test_register_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        response = await ac.post('/auth/register', json={
            'mobile': '+1234567890',
            'password': 'strongpassword'
        })
        assert response.status_code == 201
        data = response.json()
        assert 'id' in data
        assert data['mobile'] == '+1234567890'

@pytest.mark.asyncio
async def test_register_duplicate_mobile():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        await ac.post('/auth/register', json={
            'mobile': '+1234567890',
            'password': 'strongpassword'
        })
        response = await ac.post('/auth/register', json={
            'mobile': '+1234567890',
            'password': 'anotherpassword'
        })
        assert response.status_code == 409

@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        await ac.post('/auth/register', json={
            'mobile': '+1234567890',
            'password': 'strongpassword'
        })
        response = await ac.post('/auth/login', json={
            'mobile': '+1234567890',
            'password': 'strongpassword'
        })
        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
        assert data['token_type'] == 'bearer'

@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        await ac.post('/auth/register', json={
            'mobile': '+1234567890',
            'password': 'strongpassword'
        })
        response = await ac.post('/auth/login', json={
            'mobile': '+1234567890',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_unknown_mobile():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        response = await ac.post('/auth/login', json={
            'mobile': '+1234567890',
            'password': 'strongpassword'
        })
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_register_missing_fields():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        response = await ac.post('/auth/register', json={})
        assert response.status_code == 422