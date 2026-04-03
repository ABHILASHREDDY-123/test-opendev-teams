import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_create_contact():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        # First register and login
        await client.post('/auth/register', json={'mobile': '1234567890', 'password': 'testpass'})
        login_response = await client.post('/auth/login', json={'mobile': '1234567890', 'password': 'testpass'})
        token = login_response.json()['access_token']
        
        # Create contact
        response = await client.post('/contacts', json={'name': 'Test Contact', 'mobile': '9876543210'},
                                    headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 201
        data = response.json()
        assert data['name'] == 'Test Contact'
        assert data['mobile'] == '9876543210'

@pytest.mark.asyncio
async def test_list_contacts():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        # Register and login
        await client.post('/auth/register', json={'mobile': '1234567890', 'password': 'testpass'})
        login_response = await client.post('/auth/login', json={'mobile': '1234567890', 'password': 'testpass'})
        token = login_response.json()['access_token']
        
        # Create two contacts
        await client.post('/contacts', json={'name': 'Contact1', 'mobile': '1111111111'},
                         headers={'Authorization': f'Bearer {token}'})
        await client.post('/contacts', json={'name': 'Contact2', 'mobile': '2222222222'},
                         headers={'Authorization': f'Bearer {token}'})
        
        # List contacts
        response = await client.get('/contacts', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        contacts = response.json()
        assert len(contacts) == 2

@pytest.mark.asyncio
async def test_update_contact():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        # Register and login
        await client.post('/auth/register', json={'mobile': '1234567890', 'password': 'testpass'})
        login_response = await client.post('/auth/login', json={'mobile': '1234567890', 'password': 'testpass'})
        token = login_response.json()['access_token']
        
        # Create contact
        create_response = await client.post('/contacts', json={'name': 'Original Name', 'mobile': '9876543210'},
                                           headers={'Authorization': f'Bearer {token}'})
        contact_id = create_response.json()['id']
        
        # Update contact
        response = await client.put(f'/contacts/{contact_id}', json={'name': 'Updated Name'},
                                   headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'Updated Name'
        assert data['mobile'] == '9876543210'

@pytest.mark.asyncio
async def test_delete_contact():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        # Register and login
        await client.post('/auth/register', json={'mobile': '1234567890', 'password': 'testpass'})
        login_response = await client.post('/auth/login', json={'mobile': '1234567890', 'password': 'testpass'})
        token = login_response.json()['access_token']
        
        # Create contact
        create_response = await client.post('/contacts', json={'name': 'To Delete', 'mobile': '9876543210'},
                                           headers={'Authorization': f'Bearer {token}'})
        contact_id = create_response.json()['id']
        
        # Delete contact
        response = await client.delete(f'/contacts/{contact_id}', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        assert response.json()['message'] == 'Contact deleted successfully'
        
        # Verify it's deleted
        list_response = await client.get('/contacts', headers={'Authorization': f'Bearer {token}'})
        assert len(list_response.json()) == 0

@pytest.mark.asyncio
async def test_contacts_require_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        response = await client.get('/contacts')
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_contacts_isolation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        # User1 creates contact
        await client.post('/auth/register', json={'mobile': '1234567890', 'password': 'testpass'})
        login1_response = await client.post('/auth/login', json={'mobile': '1234567890', 'password': 'testpass'})
        token1 = login1_response.json()['access_token']
        await client.post('/contacts', json={'name': 'User1 Contact', 'mobile': '1111111111'},
                         headers={'Authorization': f'Bearer {token1}'})
        
        # User2 registers/login but shouldn't see User1's contact
        await client.post('/auth/register', json={'mobile': '9999999999', 'password': 'testpass2'})
        login2_response = await client.post('/auth/login', json={'mobile': '9999999999', 'password': 'testpass2'})
        token2 = login2_response.json()['access_token']
        
        response = await client.get('/contacts', headers={'Authorization': f'Bearer {token2}'})
        assert response.status_code == 200
        assert len(response.json()) == 0

@pytest.mark.asyncio
async def test_update_other_users_contact():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        # User1 creates contact
        await client.post('/auth/register', json={'mobile': '1234567890', 'password': 'testpass'})
        login1_response = await client.post('/auth/login', json={'mobile': '1234567890', 'password': 'testpass'})
        token1 = login1_response.json()['access_token']
        create_response = await client.post('/contacts', json={'name': 'User1 Contact', 'mobile': '1111111111'},
                                           headers={'Authorization': f'Bearer {token1}'})
        contact_id = create_response.json()['id']
        
        # User2 tries to update it
        await client.post('/auth/register', json={'mobile': '9999999999', 'password': 'testpass2'})
        login2_response = await client.post('/auth/login', json={'mobile': '9999999999', 'password': 'testpass2'})
        token2 = login2_response.json()['access_token']
        
        response = await client.put(f'/contacts/{contact_id}', json={'name': 'Hacker Name'},
                                   headers={'Authorization': f'Bearer {token2}'})
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        # Register and login
        await client.post('/auth/register', json={'mobile': '1234567890', 'password': 'testpass'})
        login_response = await client.post('/auth/login', json={'mobile': '1234567890', 'password': 'testpass'})
        token = login_response.json()['access_token']
        
        # Try delete non-existent contact
        response = await client.delete('/contacts/99999', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 404