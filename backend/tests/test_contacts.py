import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app, users_db, contacts_db

@pytest.mark.asyncio
async def test_create_contact():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        await ac.post("/auth/register", json={"mobile": "1234567890", "password": "test123"})
        login_response = await ac.post("/auth/login", json={"mobile": "1234567890", "password": "test123"})
        token = login_response.json()['access_token']
        response = await ac.post("/contacts", json={"name": "Test Contact", "mobile": "9876543210"}, headers={"Authorization": f"Bearer {token}"} )
        assert response.status_code == 201
        assert response.json()['name'] == "Test Contact"
        assert response.json()['mobile'] == "9876543210"

@pytest.mark.asyncio
async def test_list_contacts():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        await ac.post("/auth/register", json={"mobile": "1234567890", "password": "test123"})
        login_response = await ac.post("/auth/login", json={"mobile": "1234567890", "password": "test123"})
        token = login_response.json()['access_token']
        await ac.post("/contacts", json={"name": "Contact1", "mobile": "1111111111"}, headers={"Authorization": f"Bearer {token}"})
        await ac.post("/contacts", json={"name": "Contact2", "mobile": "2222222222"}, headers={"Authorization": f"Bearer {token}"})
        response = await ac.get("/contacts", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert len(response.json()) == 2

@pytest.mark.asyncio
async def test_update_contact():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        await ac.post("/auth/register", json={"mobile": "1234567890", "password": "test123"})
        login_response = await ac.post("/auth/login", json={"mobile": "1234567890", "password": "test123"})
        token = login_response.json()['access_token']
        create_response = await ac.post("/contacts", json={"name": "Old Name", "mobile": "9876543210"}, headers={"Authorization": f"Bearer {token}"})
        contact_id = create_response.json()['id']
        response = await ac.put(f"/contacts/{contact_id}", json={"name": "New Name"}, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()['name'] == "New Name"

@pytest.mark.asyncio
async def test_delete_contact():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        await ac.post("/auth/register", json={"mobile": "1234567890", "password": "test123"})
        login_response = await ac.post("/auth/login", json={"mobile": "1234567890", "password": "test123"})
        token = login_response.json()['access_token']
        create_response = await ac.post("/contacts", json={"name": "Test Contact", "mobile": "9876543210"}, headers={"Authorization": f"Bearer {token}"})
        contact_id = create_response.json()['id']
        response = await ac.delete(f"/contacts/{contact_id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        get_response = await ac.get("/contacts", headers={"Authorization": f"Bearer {token}"})
        assert len(get_response.json()) == 0

@pytest.mark.asyncio
async def test_contacts_require_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        response = await ac.get("/contacts")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_contacts_isolation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        # User 1 creates contact
        await ac.post("/auth/register", json={"mobile": "1234567890", "password": "test123"})
        login1_response = await ac.post("/auth/login", json={"mobile": "1234567890", "password": "test123"})
        token1 = login1_response.json()['access_token']
        await ac.post("/contacts", json={"name": "User1 Contact", "mobile": "1111111111"}, headers={"Authorization": f"Bearer {token1}"})
        
        # User 2 registers and logs in
        await ac.post("/auth/register", json={"mobile": "9999999999", "password": "test123"})
        login2_response = await ac.post("/auth/login", json={"mobile": "9999999999", "password": "test123"})
        token2 = login2_response.json()['access_token']
        
        # Check contacts for both users
        response1 = await ac.get("/contacts", headers={"Authorization": f"Bearer {token1}"})
        response2 = await ac.get("/contacts", headers={"Authorization": f"Bearer {token2}"})
        
        assert len(response1.json()) == 1
        assert len(response2.json()) == 0

@pytest.mark.asyncio
async def test_update_other_users_contact():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        # User 1 creates contact
        await ac.post("/auth/register", json={"mobile": "1234567890", "password": "test123"})
        login1_response = await ac.post("/auth/login", json={"mobile": "1234567890", "password": "test123"})
        token1 = login1_response.json()['access_token']
        create_response = await ac.post("/contacts", json={"name": "User1 Contact", "mobile": "1111111111"}, headers={"Authorization": f"Bearer {token1}"})
        contact_id = create_response.json()['id']
        
        # User 2 tries to update it
        await ac.post("/auth/register", json={"mobile": "9999999999", "password": "test123"})
        login2_response = await ac.post("/auth/login", json={"mobile": "9999999999", "password": "test123"})
        token2 = login2_response.json()['access_token']
        
        response = await ac.put(f"/contacts/{contact_id}", json={"name": "Hacker Name"}, headers={"Authorization": f"Bearer {token2}"})
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        await ac.post("/auth/register", json={"mobile": "1234567890", "password": "test123"})
        login_response = await ac.post("/auth/login", json={"mobile": "1234567890", "password": "test123"})
        token = login_response.json()['access_token']
        response = await ac.delete("/contacts/nonexistent-id", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404