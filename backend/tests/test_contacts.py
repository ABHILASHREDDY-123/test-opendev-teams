from backend.main import app
from httpx import AsyncClient
import pytest

class TestContacts:
 @pytest.mark.asyncio
 async def test_create_contact(self):
 async with AsyncClient(app=app, base_url='http://test') as ac:
 register_response = await ac.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 login_response = await ac.post('/auth/login', json={'mobile': '1234567890', 'password': 'password'})
 token = login_response.json()['access_token']
 response = await ac.post('/contacts', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200

 @pytest.mark.asyncio
 async def test_list_contacts(self):
 async with AsyncClient(app=app, base_url='http://test') as ac:
 register_response = await ac.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 login_response = await ac.post('/auth/login', json={'mobile': '1234567890', 'password': 'password'})
 token = login_response.json()['access_token']
 await ac.post('/contacts', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {token}'})
 await ac.post('/contacts', json={'name': 'Jane Doe', 'mobile': '5555555555'}, headers={'Authorization': f'Bearer {token}'})
 response = await ac.get('/contacts', headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200
 assert len(response.json()) == 2

 @pytest.mark.asyncio
 async def test_update_contact(self):
 async with AsyncClient(app=app, base_url='http://test') as ac:
 register_response = await ac.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 login_response = await ac.post('/auth/login', json={'mobile': '1234567890', 'password': 'password'})
 token = login_response.json()['access_token']
 create_response = await ac.post('/contacts', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {token}'})
 contact_id = create_response.json()['id']
 response = await ac.put(f'/contacts/{contact_id}', json={'name': 'Jane Doe'}, headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200
 assert response.json()['name'] == 'Jane Doe'

 @pytest.mark.asyncio
 async def test_delete_contact(self):
 async with AsyncClient(app=app, base_url='http://test') as ac:
 register_response = await ac.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 login_response = await ac.post('/auth/login', json={'mobile': '1234567890', 'password': 'password'})
 token = login_response.json()['access_token']
 create_response = await ac.post('/contacts', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {token}'})
 contact_id = create_response.json()['id']
 response = await ac.delete(f'/contacts/{contact_id}', headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200