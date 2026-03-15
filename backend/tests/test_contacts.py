import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app, users_db, contacts_db

@pytest.fixture(autouse=True)
def clear_databases():
    users_db.clear()
    contacts_db.clear()
    yield

@pytest.mark.asyncio
async def register_and_login(mobile: str, password: str) -> dict:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        await ac.post('/auth/register', json={'mobile': mobile, 'password': password})
        login_response = await ac.post('/auth/login', json={'mobile': mobile, 'password': password})
        token = login_response.json()['access_token']
        return {'Authorization': f'Bearer {token}'}

@pytest.mark.asyncio
async def test_create_contact():
    headers = await register_and_login('+1234567890', 'strongpassword')
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test', headers=headers) as ac:
        response = await ac.post('/contacts', json={'name': 'Test Contact', 'mobile': '+9876543210'})
        assert response.status_code == 201
        data = response.json()
        assert data['name'] == 'Test Contact'
        assert data['mobile'] == '+9876543210'
        assert 'id' in data
        assert 'owner_id' in data

@pytest.mark.asyncio
async def test_list_contacts():
    headers = await register_and_login('+1234567890', 'strongpassword')
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test', headers=headers) as ac:
        await ac.post('/contacts', json={'name': 'Contact 1', 'mobile': '+1111111111'})
        await ac.post('/contacts', json={'name': 'Contact 2', 'mobile': '+2222222222'})
        response = await ac.get('/contacts')
        assert response.status_code == 200
        contacts = response.json()
        assert len(contacts) == 2

@pytest.mark.asyncio
async def test_update_contact():
    headers = await register_and_login('+1234567890', 'strongpassword')
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test', headers=headers) as ac:
        create_response = await ac.post('/contacts', json={'name': 'Old Name', 'mobile': '+9876543210'})
        contact_id = create_response.json()['id']
        update_response = await ac.put(f'/contacts/{contact_id}', json={'name': 'New Name'})
        assert update_response.status_code == 200
        data = update_response.json()
        assert data['name'] == 'New Name'
        assert data['mobile'] == '+9876543210'

@pytest.mark.asyncio
async def test_delete_contact():
    headers = await register_and_login('+1234567890', 'strongpassword')
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test', headers=headers) as ac:
        create_response = await ac.post('/contacts', json={'name': 'Test Contact', 'mobile': '+9876543210'})
        contact_id = create_response.json()['id']
        delete_response = await ac.delete(f'/contacts/{contact_id}')
        assert delete_response.status_code == 200
        list_response = await ac.get('/contacts')
        assert len(list_response.json()) == 0

@pytest.mark.asyncio
async def test_contacts_require_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        response = await ac.get('/contacts')
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_contacts_isolation():
    headers1 = await register_and_login('+1234567890', 'password1')
    headers2 = await register_and_login('+9876543210', 'password2')
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test', headers=headers1) as ac1:
        create_response = await ac1.post('/contacts', json={'name': 'User1 Contact', 'mobile': '+1111111111'})
        contact_id = create_response.json()['id']
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test', headers=headers2) as ac2:
            list_response = await ac2.get('/contacts')
            assert len(list_response.json()) == 0
            
            update_response = await ac2.put(f'/contacts/{contact_id}', json={'name': 'Hacker Name'})
            assert update_response.status_code == 404

@pytest.mark.asyncio
async def test_update_other_users_contact():
    headers1 = await register_and_login('+1234567890', 'password1')
    headers2 = await register_and_login('+9876543210', 'password2')
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test', headers=headers1) as ac1:
        create_response = await ac1.post('/contacts', json={'name': 'User1 Contact', 'mobile': '+1111111111'})
        contact_id = create_response.json()['id']
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test', headers=headers2) as ac2:
            update_response = await ac2.put(f'/contacts/{contact_id}', json={'name': 'Hacker Name'})
            assert update_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent():
    headers = await register_and_login('+1234567890', 'strongpassword')
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test', headers=headers) as ac:
        response = await ac.delete('/contacts/nonexistent-id')
        assert response.status_code == 404