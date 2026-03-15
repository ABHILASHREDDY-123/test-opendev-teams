import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from backend.main import app

@pytest.mark.asyncio
async def test_register_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        response = await ac.post("/auth/register", json={"mobile": "1234567890", "password": "test123"})
        assert response.status_code == 201
        assert 'id' in response.json()
        assert response.json()['mobile'] == "1234567890"

@pytest.mark.asyncio
async def test_register_duplicate_mobile():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        await ac.post("/auth/register", json={"mobile": "1234567890", "password": "test123"})
        response = await ac.post("/auth/register", json={"mobile": "1234567890", "password": "test123"})
        assert response.status_code == 409

@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        await ac.post("/auth/register", json={"mobile": "1234567890", "password": "test123"})
        response = await ac.post("/auth/login", json={"mobile": "1234567890", "password": "test123"})
        assert response.status_code == 200
        assert 'access_token' in response.json()

@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        await ac.post("/auth/register", json={"mobile": "1234567890", "password": "test123"})
        response = await ac.post("/auth/login", json={"mobile": "1234567890", "password": "wrong"})
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_unknown_mobile():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        response = await ac.post("/auth/login", json={"mobile": "9999999999", "password": "test123"})
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_register_missing_fields():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        response = await ac.post("/auth/register", json={"mobile": "1234567890"})
        assert response.status_code == 422