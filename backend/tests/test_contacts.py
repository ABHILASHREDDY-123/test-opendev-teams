from fastapi.testclient import TestClient
from main import app
from models import ContactCreate
import pytest

client = TestClient(app)

@pytest.mark.asyncio
async def test_create_contact():
 # register and login to get a token
 register_response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 login_response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 token = login_response.json()['access_token']
 # create a contact
 response = client.post('/contacts/', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200
 assert 'id' in response.json()
 assert 'name' in response.json()
 assert 'mobile' in response.json()
 assert 'owner_id' in response.json()

@pytest.mark.asyncio
async def test_list_contacts():
 # register and login to get a token
 register_response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 login_response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 token = login_response.json()['access_token']
 # create two contacts
 client.post('/contacts/', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {token}'})
 client.post('/contacts/', json={'name': 'Jane Doe', 'mobile': '5555555555'}, headers={'Authorization': f'Bearer {token}'})
 # list contacts
 response = client.get('/contacts/', headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200
 assert len(response.json()) == 2

@pytest.mark.asyncio
async def test_update_contact():
 # register and login to get a token
 register_response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 login_response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 token = login_response.json()['access_token']
 # create a contact
 create_response = client.post('/contacts/', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {token}'})
 contact_id = create_response.json()['id']
 # update the contact
 response = client.put(f'/contacts/{contact_id}', json={'name': 'Jane Doe'}, headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200
 assert response.json()['name'] == 'Jane Doe'

@pytest.mark.asyncio
async def test_delete_contact():
 # register and login to get a token
 register_response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 login_response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 token = login_response.json()['access_token']
 # create a contact
 create_response = client.post('/contacts/', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {token}'})
 contact_id = create_response.json()['id']
 # delete the contact
 response = client.delete(f'/contacts/{contact_id}', headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200

@pytest.mark.asyncio
async def test_contacts_require_auth():
 response = client.get('/contacts/')
 assert response.status_code == 401

@pytest.mark.asyncio
async def test_contacts_isolation():
 # register and login to get a token for user1
 register_response1 = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 login_response1 = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 token1 = login_response1.json()['access_token']
 # register and login to get a token for user2
 register_response2 = client.post('/auth/register', json={'mobile': '9876543210', 'password': 'password123'})
 login_response2 = client.post('/auth/login', json={'mobile': '9876543210', 'password': 'password123'})
 token2 = login_response2.json()['access_token']
 # create a contact for user1
 client.post('/contacts/', json={'name': 'John Doe', 'mobile': '5555555555'}, headers={'Authorization': f'Bearer {token1}'})
 # list contacts for user2
 response = client.get('/contacts/', headers={'Authorization': f'Bearer {token2}'})
 assert response.status_code == 200
 assert len(response.json()) == 0

@pytest.mark.asyncio
async def test_update_other_users_contact():
 # register and login to get a token for user1
 register_response1 = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 login_response1 = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 token1 = login_response1.json()['access_token']
 # register and login to get a token for user2
 register_response2 = client.post('/auth/register', json={'mobile': '9876543210', 'password': 'password123'})
 login_response2 = client.post('/auth/login', json={'mobile': '9876543210', 'password': 'password123'})
 token2 = login_response2.json()['access_token']
 # create a contact for user1
 create_response = client.post('/contacts/', json={'name': 'John Doe', 'mobile': '5555555555'}, headers={'Authorization': f'Bearer {token1}'})
 contact_id = create_response.json()['id']
 # try to update the contact as user2
 response = client.put(f'/contacts/{contact_id}', json={'name': 'Jane Doe'}, headers={'Authorization': f'Bearer {token2}'})
 assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent():
 # register and login to get a token
 register_response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 login_response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 token = login_response.json()['access_token']
 # try to delete a nonexistent contact
 response = client.delete('/contacts/1', headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 404