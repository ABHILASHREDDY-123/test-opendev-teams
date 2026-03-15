from fastapi.testclient import TestClient
from main import app
import pytest

def register_and_login(client):
 register_response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 login_response = client.post('/auth/login', data={'grant_type': 'password', 'username': '1234567890', 'password': 'password'})
 return login_response.json()['access_token'
]

def test_create_contact():
 client = TestClient(app)
 access_token = register_and_login(client)
 response = client.post('/contacts', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 200
 assert 'id' in response.json()
 assert 'name' in response.json()
 assert 'mobile' in response.json()
 assert 'owner_id' in response.json()

def test_list_contacts():
 client = TestClient(app)
 access_token = register_and_login(client)
 client.post('/contacts', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {access_token}'})
 client.post('/contacts', json={'name': 'Jane Doe', 'mobile': '5555555555'}, headers={'Authorization': f'Bearer {access_token}'})
 response = client.get('/contacts', headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 200
 assert len(response.json()) == 2

def test_update_contact():
 client = TestClient(app)
 access_token = register_and_login(client)
 create_response = client.post('/contacts', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {access_token}'})
 contact_id = create_response.json()['id']
 response = client.put(f'/contacts/{contact_id}', json={'name': 'Jane Doe'}, headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 200
 assert response.json()['name'] == 'Jane Doe'

def test_delete_contact():
 client = TestClient(app)
 access_token = register_and_login(client)
 create_response = client.post('/contacts', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {access_token}'})
 contact_id = create_response.json()['id']
 response = client.delete(f'/contacts/{contact_id}', headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 200
 assert response.json()['message'] == 'Contact deleted successfully'

def test_contacts_require_auth():
 client = TestClient(app)
 response = client.get('/contacts')
 assert response.status_code == 401

def test_contacts_isolation():
 client = TestClient(app)
 access_token1 = register_and_login(client)
 access_token2 = register_and_login(client)
 client.post('/contacts', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {access_token1}'})
 response = client.get('/contacts', headers={'Authorization': f'Bearer {access_token2}'})
 assert response.status_code == 200
 assert len(response.json()) == 0

def test_update_other_users_contact():
 client = TestClient(app)
 access_token1 = register_and_login(client)
 access_token2 = register_and_login(client)
 create_response = client.post('/contacts', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {access_token1}'})
 contact_id = create_response.json()['id']
 response = client.put(f'/contacts/{contact_id}', json={'name': 'Jane Doe'}, headers={'Authorization': f'Bearer {access_token2}'})
 assert response.status_code == 404

def test_delete_nonexistent():
 client = TestClient(app)
 access_token = register_and_login(client)
 response = client.delete('/contacts/12345', headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 404