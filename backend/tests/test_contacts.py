import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def register_and_login(client):
    await client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
    response = await client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password'})
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.mark.asyncio
async def test_create_contact():
    async with AsyncClient(app=app, base_url='http://test') as client:
        headers = await register_and_login(client)
        response = await client.post('/contacts', json={'name': 'John Doe', 'mobile': '9876543210'}, headers=headers)
        assert response.status_code == 201
        assert 'id' in response.json()
        assert response.json()['name'] == 'John Doe'
        assert response.json()['mobile'] == '9876543210'

@pytest.mark.asyncio
async def test_list_contacts():
    async with AsyncClient(app=app, base_url='http://test') as client:
        headers = await register_and_login(client)
        await client.post('/contacts', json={'name': 'John Doe', 'mobile': '9876543210'}, headers=headers)
        await client.post('/contacts', json={'name': 'Jane Doe', 'mobile': '9876543211'}, headers=headers)
        response = await client.get('/contacts', headers=headers)
        assert response.status_code == 200
        contacts = response.json()
        assert len(contacts) == 2

@pytest.mark.asyncio
async def test_update_contact():
    async with AsyncClient(app=app, base_url='http://test') as client:
        headers = await register_and_login(client)
        create_response = await client.post('/contacts', json={'name': 'John Doe', 'mobile': '9876543210'}, headers=headers)
        contact_id = create_response.json()['id']
        response = await client.put(f'/contacts/{contact_id}', json={'name': 'Jane Doe'}, headers=headers)
        assert response.status_code == 200
        assert response.json()['name'] == 'Jane Doe'

@pytest.mark.asyncio
async def test_delete_contact():
    async with AsyncClient(app=app, base_url='http://test') as client:
        headers = await register_and_login(client)
        create_response = await client.post('/contacts', json={'name': 'John Doe', 'mobile': '9876543210'}, headers=headers)
        contact_id = create_response.json()['id']
        response = await client.delete(f'/contacts/{contact_id}', headers=headers)
        assert response.status_code == 200
        list_response = await client.get('/contacts', headers=headers)
        assert len(list_response.json()) == 0

@pytest.mark.asyncio
async def test_contacts_require_auth():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get('/contacts')
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_contacts_isolation():
    async with AsyncClient(app=app, base_url='http://test') as client:
        headers1 = await register_and_login(client)
        headers2 = await register_and_login(client)
        await client.post('/contacts', json={'name': 'John Doe', 'mobile': '9876543210'}, headers=headers1)
        response = await client.get('/contacts', headers=headers2)
        assert response.status_code == 200
        assert len(response.json()) == 0

@pytest.mark.asyncio
async def test_update_other_users_contact():
    async with AsyncClient(app=app, base_url='http://test') as client:
        headers1 = await register_and_login(client)
        create_response = await client.post('/contacts', json={'name': 'John Doe', 'mobile': '9876543210'}, headers=headers1)
        contact_id = create_response.json()['id']
        headers2 = await register_and_login(client)
        response = await client.put(f'/contacts/{contact_id}', json={'name': 'Jane Doe'}, headers=headers2)
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent():
    async with AsyncClient(app=app, base_url='http://test') as client:
        headers = await register_and_login(client)
        response = await client.delete('/contacts/nonexistent', headers=headers)
        assert response.status_code == 404
