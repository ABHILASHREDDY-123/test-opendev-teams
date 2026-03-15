import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_create_contact():
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Register and login first
        await client.post("/auth/register", json={
            "mobile": "1234567890",
            "password": "testpass"
        })
        login_response = await client.post("/auth/login", json={
            "mobile": "1234567890",
            "password": "testpass"
        })
        token = login_response.json()['access_token']
        
        response = await client.post("/contacts", json={
            "name": "Test Contact",
            "mobile": "9876543210"
        }, headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 201
        data = response.json()
        assert data['name'] == "Test Contact"
        assert data['mobile'] == "9876543210"

@pytest.mark.asyncio
async def test_list_contacts():
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Register and login
        await client.post("/auth/register", json={
            "mobile": "1234567890",
            "password": "testpass"
        })
        login_response = await client.post("/auth/login", json={
            "mobile": "1234567890",
            "password": "testpass"
        })
        token = login_response.json()['access_token']
        
        # Create two contacts
        await client.post("/contacts", json={
            "name": "Contact 1",
            "mobile": "1111111111"
        }, headers={
            "Authorization": f"Bearer {token}"
        })
        await client.post("/contacts", json={
            "name": "Contact 2",
            "mobile": "2222222222"
        }, headers={
            "Authorization": f"Bearer {token}"
        })
        
        # List contacts
        response = await client.get("/contacts", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        contacts = response.json()
        assert len(contacts) == 2
